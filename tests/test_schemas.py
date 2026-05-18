import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from modules.llm_validation import validate_against_schema, validate_or_retry
from modules.schemas import JD_ANALYSIS_SCHEMA, QUESTION_SCHEMA, EVALUATION_SCHEMA, SUMMARY_SCHEMA


class TestJDAnalysisSchema:
    def test_valid_jd_analysis(self):
        data = {
            "title": "Python Developer",
            "role": "Backend Developer",
            "seniority": "Mid",
            "key_skills": ["Python", "Django", "PostgreSQL"],
        }
        valid, errors = validate_against_schema(data, JD_ANALYSIS_SCHEMA)
        assert valid, errors

    def test_missing_title(self):
        data = {"role": "Backend", "seniority": "Mid", "key_skills": ["Python"]}
        valid, errors = validate_against_schema(data, JD_ANALYSIS_SCHEMA)
        assert not valid

    def test_invalid_seniority(self):
        data = {"title": "Dev", "role": "Dev", "seniority": "Super Senior", "key_skills": []}
        valid, errors = validate_against_schema(data, JD_ANALYSIS_SCHEMA)
        assert not valid


class TestQuestionSchema:
    VALID_QUESTIONS = {
        "title": "Python Dev",
        "role": "Developer",
        "seniority": "Mid",
        "questions": [
            {
                "id": 1,
                "category": "Technical",
                "difficulty": "Medium",
                "question": "What is Python?",
                "key_concepts": ["Python"],
            }
        ],
    }

    def test_valid(self):
        valid, errors = validate_against_schema(self.VALID_QUESTIONS, QUESTION_SCHEMA)
        assert valid, errors

    def test_missing_questions(self):
        data = {**self.VALID_QUESTIONS}
        data.pop("questions")
        valid, _ = validate_against_schema(data, QUESTION_SCHEMA)
        assert not valid

    def test_invalid_category(self):
        data = {**self.VALID_QUESTIONS}
        data["questions"][0]["category"] = "InvalidCat"
        valid, _ = validate_against_schema(data, QUESTION_SCHEMA)
        assert not valid


class TestEvaluationSchema:
    VALID_EVAL = {
        "score": 8,
        "verdict": "Good",
        "strengths": ["Clear explanation"],
        "missing_concepts": ["Auth"],
        "improvement_suggestions": ["Study JWT"],
        "ideal_answer": "REST is stateless.",
    }

    def test_valid(self):
        valid, errors = validate_against_schema(self.VALID_EVAL, EVALUATION_SCHEMA)
        assert valid, errors

    def test_score_out_of_range(self):
        data = {**self.VALID_EVAL, "score": 15}
        valid, _ = validate_against_schema(data, EVALUATION_SCHEMA)
        assert not valid

    def test_invalid_verdict(self):
        data = {**self.VALID_EVAL, "verdict": "Superb"}
        valid, _ = validate_against_schema(data, EVALUATION_SCHEMA)
        assert not valid


class TestSummarySchema:
    VALID_SUMMARY = {
        "overall_score": 75,
        "readiness": "Good",
        "strong_areas": ["Python"],
        "weak_areas": ["System Design"],
        "recommendations": ["Study microservices", "Practice coding", "Review algorithms"],
    }

    def test_valid(self):
        valid, errors = validate_against_schema(self.VALID_SUMMARY, SUMMARY_SCHEMA)
        assert valid, errors

    def test_score_out_of_range(self):
        data = {**self.VALID_SUMMARY, "overall_score": 150}
        valid, _ = validate_against_schema(data, SUMMARY_SCHEMA)
        assert not valid

    def test_too_few_recommendations(self):
        data = {**self.VALID_SUMMARY, "recommendations": ["Only one"]}
        valid, _ = validate_against_schema(data, SUMMARY_SCHEMA)
        assert not valid


class TestValidateOrRetry:
    def test_valid_on_first_try(self):
        data = {
            "title": "Dev", "role": "Dev", "seniority": "Junior", "key_skills": ["A"],
        }
        call_count = 0

        def producer():
            nonlocal call_count
            call_count += 1
            return data

        result = validate_or_retry(producer, JD_ANALYSIS_SCHEMA, max_retries=3)
        assert result is not None
        assert call_count == 1

    def test_invalid_all_retries(self):
        data = {"title": "Dev"}
        call_count = 0

        def producer():
            nonlocal call_count
            call_count += 1
            return data

        result = validate_or_retry(producer, JD_ANALYSIS_SCHEMA, max_retries=3, delay=0)
        assert result is None
        assert call_count == 3
