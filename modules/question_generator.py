import os
from typing import Any, Optional

from modules.config import get_question_count, get_temperature_questions
from modules.llm_validation import validate_against_schema
from modules.providers.factory import get_provider
from modules.schemas import JD_ANALYSIS_SCHEMA, QUESTION_SCHEMA, SINGLE_QUESTION_SCHEMA
from modules.utils import validate_job_description

PROMPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "prompts")


def _read_prompt(filename: str) -> str:
    path = os.path.join(PROMPTS_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def generate_questions(
    job_description: str,
    level: str = "Medium",
    question_count: int | None = None,
    provider_name: str | None = None,
) -> dict:
    valid, error = validate_job_description(job_description)
    if not valid:
        return {"success": False, "error": error}

    count = question_count or get_question_count()
    provider = get_provider(provider_name)
    temp = get_temperature_questions()

    jd_prompt = _read_prompt("jd_analyzer.txt").format(job_description=job_description)

    try:
        jd_analysis = provider.generate_json(
            jd_prompt,
            max_retries=2,
            temperature=temp,
        )
        if not jd_analysis:
            return {"success": False, "error": "Failed to analyze job description. Please try again."}

        valid_jd, jd_errors = validate_against_schema(jd_analysis, JD_ANALYSIS_SCHEMA)
        if not valid_jd:
            return {"success": False, "error": f"JD analysis failed validation: {jd_errors[0] if jd_errors else 'unknown'}"}

    except Exception as e:
        return {"success": False, "error": f"JD analysis failed: {e}"}

    q_prompt = _read_prompt("question_generator.txt").format(
        question_count=count,
        level=level,
        jd_analysis=str(jd_analysis),
    )

    try:
        questions_data = provider.generate_json(
            q_prompt,
            max_retries=3,
            temperature=temp,
        )
        if not questions_data:
            return {"success": False, "error": "Question generation returned invalid data. Try again."}

        valid_q, q_errors = validate_against_schema(questions_data, QUESTION_SCHEMA)
        if not valid_q:
            return {"success": False, "error": f"Question validation failed: {q_errors[0] if q_errors else 'unknown'}"}

        questions = questions_data.get("questions", [])
        if len(questions) < 1:
            return {
                "success": False,
                "error": "Failed to generate initial question. Please regenerate.",
            }

        # Pad with empty templates for the remaining questions
        initial_q = questions[0]
        full_questions = [initial_q]
        for i in range(1, count):
            full_questions.append({
                "id": i + 1,
                "category": "TBD",
                "difficulty": "TBD",
                "question": "Loading dynamically...",
                "key_concepts": []
            })

        return {
            "success": True,
            "data": {
                "title": jd_analysis.get("title", questions_data.get("title", "Interview")),
                "role": jd_analysis.get("role", questions_data.get("role", "")),
                "seniority": jd_analysis.get("seniority", questions_data.get("seniority", "")),
                "key_skills": jd_analysis.get("key_skills", []),
                "questions": full_questions,
                "jd_analysis": jd_analysis,
            },
        }

    except Exception as e:
        return {"success": False, "error": f"Question generation error: {e}"}

def generate_dynamic_question(
    jd_analysis: dict,
    level: str,
    previous_score: float = -1.0,
    provider_name: str | None = None,
) -> dict:
    provider = get_provider(provider_name)
    temp = get_temperature_questions()

    dynamic_instruction = ""
    if previous_score >= 8:
        dynamic_instruction = "The candidate answered the last question perfectly. Make this next question significantly harder and more advanced."
    elif 0 <= previous_score <= 4 and previous_score >= 0:
        dynamic_instruction = "The candidate struggled with the last question. Ask a fundamental, core-concept question."
    elif previous_score == -1.0:
        dynamic_instruction = "The candidate skipped the last question, meaning they likely did not know the answer. Make this next question slightly easier and more fundamental."
    else:
        dynamic_instruction = "The candidate did okay. Maintain the current difficulty level."

    q_prompt = _read_prompt("dynamic_question_generator.txt").format(
        level=level,
        previous_score=previous_score,
        dynamic_instruction=dynamic_instruction,
        jd_analysis=str(jd_analysis),
    )

    try:
        data = provider.generate_json(q_prompt, max_retries=3, temperature=temp)
        if not data:
            return {"success": False, "error": "AI returned empty JSON for next question"}
            
        valid, errors = validate_against_schema(data, SINGLE_QUESTION_SCHEMA)
        if valid:
            return {"success": True, "data": data}
        return {"success": False, "error": f"Invalid schema: {errors[0] if errors else 'unknown'}"}
    except Exception as e:
        return {"success": False, "error": str(e)}
