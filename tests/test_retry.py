import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from modules.llm_validation import validate_or_retry
from modules.schemas import EVALUATION_SCHEMA


def test_retry_eventually_succeeds():
    call_count = [0]
    invalid_data = {"score": 999, "verdict": "bad", "strengths": [], "missing_concepts": [], "improvement_suggestions": [], "ideal_answer": ""}

    def producer():
        call_count[0] += 1
        if call_count[0] < 2:
            return invalid_data
        return {
            "score": 7,
            "verdict": "Good",
            "strengths": ["Good"],
            "missing_concepts": ["Missing"],
            "improvement_suggestions": ["Study"],
            "ideal_answer": "Ideal answer here.",
        }

    result = validate_or_retry(producer, EVALUATION_SCHEMA, max_retries=3, delay=0)
    assert result is not None
    assert result["score"] == 7
    assert call_count[0] == 2


def test_retry_all_fail():
    data = {"score": "invalid", "verdict": "bad", "strengths": [], "missing_concepts": [], "improvement_suggestions": [], "ideal_answer": ""}
    call_count = [0]

    def producer():
        call_count[0] += 1
        return data

    result = validate_or_retry(producer, EVALUATION_SCHEMA, max_retries=3, delay=0)
    assert result is None
    assert call_count[0] == 3


def test_retry_with_dict_direct():
    invalid = {"score": 99, "verdict": "BAD", "strengths": [], "missing_concepts": [], "improvement_suggestions": [], "ideal_answer": ""}
    result = validate_or_retry(invalid, EVALUATION_SCHEMA, max_retries=2, delay=0)
    assert result is None


def test_retry_empty_data():
    result = validate_or_retry({}, EVALUATION_SCHEMA, max_retries=2, delay=0)
    assert result is None
