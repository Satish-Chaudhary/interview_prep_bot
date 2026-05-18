import os
from typing import Any

from modules.config import get_temperature_evaluation
from modules.llm_validation import validate_against_schema
from modules.providers.factory import get_provider
from modules.schemas import EVALUATION_SCHEMA, BEHAVIORAL_EVALUATION_SCHEMA
from modules.utils import safe_score

PROMPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "prompts")


def _read_prompt(filename: str) -> str:
    path = os.path.join(PROMPTS_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _score_to_verdict(score: float) -> str:
    if score >= 8:
        return "Excellent"
    if score >= 6:
        return "Good"
    if score >= 4:
        return "Fair"
    return "Poor"


def evaluate_answer(
    question: str,
    answer: str,
    category: str = "Technical",
    provider_name: str | None = None,
) -> dict:
    if not question or not question.strip():
        return {"success": False, "error": "Question cannot be empty."}

    if not answer or not answer.strip():
        return {
            "success": True,
            "data": {
                "score": 0,
                "verdict": "Poor",
                "strengths": [],
                "missing_concepts": ["No answer provided."],
                "improvement_suggestions": ["Provide an answer to receive feedback."],
                "ideal_answer": "",
            },
        }

    provider = get_provider(provider_name)
    temp = get_temperature_evaluation()

    is_behavioral = category in ["Behavioral", "Situational", "HR"]
    prompt_file = "behavioral_evaluation.txt" if is_behavioral else "evaluation.txt"
    schema = BEHAVIORAL_EVALUATION_SCHEMA if is_behavioral else EVALUATION_SCHEMA

    prompt = _read_prompt(prompt_file).format(question=question, answer=answer)

    try:
        parsed = provider.generate_json(prompt, max_retries=3, temperature=temp)

        if not parsed:
            return {"success": False, "error": "AI returned invalid JSON after retries."}

        valid, errors = validate_against_schema(parsed, schema)
        if not valid:
            score = safe_score(parsed.get("score", 0))
            return {
                "success": True,
                "data": {
                    "score": score,
                    "verdict": parsed.get("verdict") or _score_to_verdict(score),
                    "strengths": parsed.get("strengths", []),
                    "missing_concepts": parsed.get("missing_concepts", []),
                    "improvement_suggestions": parsed.get("improvement_suggestions", []),
                    "ideal_answer": parsed.get("ideal_answer", ""),
                },
            }

        score = safe_score(parsed.get("score", 0))
        return {
            "success": True,
            "data": {
                "score": score,
                "verdict": parsed.get("verdict") or _score_to_verdict(score),
                "strengths": parsed.get("strengths", []),
                "missing_concepts": parsed.get("missing_concepts", []),
                "improvement_suggestions": parsed.get("improvement_suggestions", []),
                "ideal_answer": parsed.get("ideal_answer", ""),
            },
        }

    except Exception as e:
        return {"success": False, "error": f"Evaluation error: {e}"}
