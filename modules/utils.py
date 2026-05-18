import json
import os
from typing import Any, Optional

AUTOSAVE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "session_data",
    "autosave.json",
)


def validate_job_description(text: str) -> tuple[bool, Optional[str]]:
    if not text or not text.strip():
        return False, "Job description cannot be empty."
    word_count = len(text.split())
    if word_count < 20:
        return False, f"Too short ({word_count} words). Please provide at least 20 words."
    if word_count > 3000:
        return False, f"Too long ({word_count} words). Maximum is 3,000 words."
    lower = text.lower()
    injection_patterns = ["ignore previous", "ignore all instructions", "disregard above"]
    for pattern in injection_patterns:
        if pattern in lower:
            return False, "Invalid input detected."
    return True, None


def validate_answer(answer: str) -> tuple[bool, Optional[str]]:
    if not answer or not answer.strip():
        return False, "Answer cannot be empty."
    return True, None


def safe_score(value: Any, default: float = 0.0) -> float:
    try:
        score = float(value)
        return max(0.0, min(10.0, score))
    except (TypeError, ValueError):
        return default


def autosave_session(session_data: dict[str, Any]) -> bool:
    try:
        os.makedirs(os.path.dirname(AUTOSAVE_PATH), exist_ok=True)
        with open(AUTOSAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False


def restore_session() -> Optional[dict[str, Any]]:
    if not os.path.exists(AUTOSAVE_PATH):
        return None
    try:
        with open(AUTOSAVE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def clear_autosave() -> None:
    if os.path.exists(AUTOSAVE_PATH):
        try:
            os.remove(AUTOSAVE_PATH)
        except Exception:
            pass
