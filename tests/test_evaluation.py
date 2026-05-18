import sys
import os
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from modules.answer_evaluator import evaluate_answer
from modules.utils import safe_score


SAMPLE_QUESTION = "Explain REST APIs."


class TestSafeScore:
    def test_normal(self):
        assert safe_score(7) == 7.0

    def test_clamp(self):
        assert safe_score(15) == 10.0
        assert safe_score(-5) == 0.0

    def test_string(self):
        assert safe_score("8.5") == 8.5

    def test_invalid(self):
        assert safe_score("bad") == 0.0
        assert safe_score(None) == 0.0


class TestEvaluateAnswer:
    def test_empty_answer_zero_score(self):
        result = evaluate_answer(SAMPLE_QUESTION, "")
        assert result["success"] is True
        assert result["data"]["score"] == 0

    def test_empty_question_error(self):
        result = evaluate_answer("", "Some answer")
        assert result["success"] is False

    @patch("modules.answer_evaluator.get_provider")
    def test_valid_answer(self, mock_get_provider):
        mock_provider = mock_get_provider.return_value
        mock_provider.generate_json.return_value = {
            "score": 8,
            "verdict": "Good",
            "strengths": ["Clear"],
            "missing_concepts": ["Auth"],
            "improvement_suggestions": ["Study JWT"],
            "ideal_answer": "REST is stateless.",
        }
        result = evaluate_answer(SAMPLE_QUESTION, "REST uses HTTP.")
        assert result["success"] is True
        assert result["data"]["score"] == 8

    @patch("modules.answer_evaluator.get_provider")
    def test_llm_failure(self, mock_get_provider):
        mock_provider = mock_get_provider.return_value
        mock_provider.generate_json.side_effect = Exception("API error")
        result = evaluate_answer(SAMPLE_QUESTION, "Some answer.")
        assert result["success"] is False
        assert "error" in result

    @patch("modules.answer_evaluator.get_provider")
    def test_invalid_json(self, mock_get_provider):
        mock_provider = mock_get_provider.return_value
        mock_provider.generate_json.return_value = None
        result = evaluate_answer(SAMPLE_QUESTION, "Some answer.")
        assert result["success"] is False
