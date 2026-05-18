import sys
import os
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from modules.utils import validate_job_description
from modules.question_generator import generate_questions


VALID_JD = (
    "We are hiring a Python Backend Developer with experience in FastAPI, "
    "PostgreSQL, Docker, and REST API design. Candidates should have 2+ years "
    "of experience, be comfortable with Git and CI/CD, and work well in Agile teams. "
    "The role involves building scalable microservices and collaborating with frontend teams."
)


class TestValidateJobDescription:
    def test_empty(self):
        valid, err = validate_job_description("")
        assert valid is False

    def test_short(self):
        valid, err = validate_job_description("Too short")
        assert valid is False

    def test_valid(self):
        valid, err = validate_job_description(VALID_JD)
        assert valid is True

    def test_too_long(self):
        valid, err = validate_job_description(" ".join(["word"] * 3001))
        assert valid is False


class TestGenerateQuestions:
    def test_empty_jd_error(self):
        result = generate_questions("")
        assert result["success"] is False

    @patch("modules.question_generator.get_provider")
    def test_valid_jd(self, mock_get_provider):
        mock_provider = mock_get_provider.return_value
        mock_provider.generate_json.side_effect = [
            {
                "title": "Python Developer",
                "role": "Backend Developer",
                "seniority": "Mid",
                "key_skills": ["Python", "FastAPI"],
            },
            {
                "title": "Python Developer",
                "role": "Backend Developer",
                "seniority": "Mid",
                "questions": [
                    {"id": 1, "category": "Technical", "difficulty": "Medium",
                     "question": "Explain FastAPI async.", "key_concepts": ["FastAPI"]},
                    {"id": 2, "category": "Technical", "difficulty": "Medium",
                     "question": "Explain Docker.", "key_concepts": ["Docker"]},
                ],
            },
        ]
        result = generate_questions(VALID_JD, level="Medium", question_count=2)
        assert result["success"] is True
        assert len(result["data"]["questions"]) == 2

    @patch("modules.question_generator.get_provider")
    def test_invalid_json(self, mock_get_provider):
        mock_provider = mock_get_provider.return_value
        mock_provider.generate_json.return_value = None
        result = generate_questions(VALID_JD)
        assert result["success"] is False
