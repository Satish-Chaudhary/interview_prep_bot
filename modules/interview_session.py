import json
import os
from typing import Any, Optional

from modules.config import get_temperature_evaluation
from modules.llm_validation import validate_against_schema
from modules.providers.factory import get_provider
from modules.schemas import SUMMARY_SCHEMA

PROMPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "prompts")


def _read_prompt(filename: str) -> str:
    path = os.path.join(PROMPTS_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _empty_state() -> dict[str, Any]:
    return {
        "questions": [],
        "answers": [],
        "skipped": [],
        "evaluations": [],
        "current_index": 0,
        "meta": {},
        "finished": False,
        "summary": None,
    }


class InterviewSession:
    def __init__(self):
        self._state: dict[str, Any] = _empty_state()

    def start(self, questions: list[dict[str, Any]], meta: Optional[dict] = None) -> None:
        self._state = _empty_state()
        self._state["questions"] = questions
        self._state["answers"] = ["" for _ in questions]
        self._state["meta"] = meta or {}

    def restart(self) -> None:
        questions = self._state["questions"]
        meta = self._state["meta"]
        self._state = _empty_state()
        self._state["questions"] = questions
        self._state["answers"] = ["" for _ in questions]
        self._state["meta"] = meta

    def reset_all(self) -> None:
        self._state = _empty_state()

    @property
    def current_index(self) -> int:
        return self._state["current_index"]

    @property
    def total_questions(self) -> int:
        return len(self._state["questions"])

    @property
    def is_finished(self) -> bool:
        return self._state["finished"]

    def current_question(self) -> Optional[dict[str, Any]]:
        idx = self._state["current_index"]
        qs = self._state["questions"]
        if 0 <= idx < len(qs):
            return qs[idx]
        return None

    def next_question(self) -> bool:
        idx = self._state["current_index"]
        if idx < self.total_questions - 1:
            self._state["current_index"] = idx + 1
            return True
        return False

    def previous_question(self) -> bool:
        idx = self._state["current_index"]
        if idx > 0:
            self._state["current_index"] = idx - 1
            return True
        return False

    def go_to(self, index: int) -> bool:
        if 0 <= index < self.total_questions:
            self._state["current_index"] = index
            return True
        return False

    def record_answer(self, index: int, text: str) -> None:
        answers = self._state["answers"]
        while len(answers) <= index:
            answers.append("")
        answers[index] = text
        if index in self._state["skipped"] and text.strip():
            self._state["skipped"].remove(index)

    def skip_question(self, index: Optional[int] = None) -> None:
        if index is None:
            index = self._state["current_index"]
        if index not in self._state["skipped"]:
            self._state["skipped"].append(index)

    def store_evaluations(self, evaluations: list[dict[str, Any]]) -> None:
        self._state["evaluations"] = evaluations

    def finish(self) -> None:
        self._state["finished"] = True

    def generate_summary(self, provider_name: str | None = None) -> dict[str, Any]:
        evaluations = self._state.get("evaluations", [])
        questions = self._state.get("questions", [])
        answers = self._state.get("answers", [])

        scores_list = []
        interview_data = []
        for i, q in enumerate(questions):
            q_text = q.get("question") or q.get("q") or str(q) if isinstance(q, dict) else str(q)
            ans = answers[i] if i < len(answers) else ""
            entry = {"question": q_text, "answer": ans}
            if i < len(evaluations) and evaluations[i].get("success"):
                score = evaluations[i].get("data", {}).get("score", 0)
            else:
                score = 0
            entry["score"] = score
            scores_list.append(score)
            interview_data.append(entry)

        # Force strict mathematical calculation for score (each q is /10, total is /100)
        math_overall = round((sum(scores_list) / len(questions)) * 10) if questions else 0

        prompt = _read_prompt("summary.txt").format(
            interview_data=json.dumps(interview_data, indent=2)
        )

        provider = get_provider(provider_name)
        temp = get_temperature_evaluation()

        try:
            parsed = provider.generate_json(prompt, max_retries=2, temperature=temp)
            if parsed:
                valid, _ = validate_against_schema(parsed, SUMMARY_SCHEMA)
                if valid:
                    summary = {
                        "overall_score": math_overall, # Overwrite LLM hallucinated score
                        "readiness": parsed.get("readiness", "Unknown"),
                        "strong_areas": parsed.get("strong_areas", []),
                        "weak_areas": parsed.get("weak_areas", []),
                        "recommendations": parsed.get("recommendations", []),
                    }
                else:
                    summary = self._fallback_summary(scores_list)
            else:
                summary = self._fallback_summary(scores_list)
        except Exception:
            summary = self._fallback_summary(scores_list)

        self._state["summary"] = summary
        
        # Save to SQLite Database permanently
        import streamlit as st
        from modules.database import save_interview_summary
        try:
            level = st.session_state.get("level", "Medium")
            q_count = len(self._state.get("questions", []))
            save_interview_summary(
                level=level,
                question_count=q_count,
                final_score=summary.get("overall_score", 0),
                readiness_level=summary.get("readiness", "Unknown"),
                strengths=summary.get("strong_areas", []),
                weak_areas=summary.get("weak_areas", []),
                improvements=summary.get("recommendations", [])
            )
        except Exception as e:
            print(f"Failed to save to database: {e}")

        return summary

    def _fallback_summary(self, scores_list: list[int]) -> dict[str, Any]:
        math_overall = round((sum(scores_list) / len(scores_list)) * 10) if scores_list else 0
        avg = round(sum(scores_list) / len(scores_list), 1) if scores_list else 0.0
        return {
            "overall_score": math_overall,
            "readiness": self._score_to_readiness(avg),
            "strong_areas": [],
            "weak_areas": [],
            "recommendations": ["Review individual question feedback above."],
        }

    @staticmethod
    def _score_to_readiness(score: float) -> str:
        if score >= 8:
            return "Interview Ready"
        if score >= 6:
            return "Good"
        if score >= 4:
            return "Needs Practice"
        return "Not Ready"

    @property
    def state(self) -> dict[str, Any]:
        return dict(self._state)

    def progress_info(self) -> dict[str, int]:
        answered = sum(1 for a in self._state["answers"] if a and a.strip())
        skipped = len(self._state["skipped"])
        return {
            "total": self.total_questions,
            "current": self._state["current_index"] + 1,
            "answered": answered,
            "skipped": skipped,
            "remaining": self.total_questions - answered - skipped,
        }
