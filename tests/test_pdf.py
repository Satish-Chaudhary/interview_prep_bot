import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from modules.pdf_generator import generate_pdf_report, get_pdf_filename


SAMPLE_QUESTIONS = [
    {"id": 1, "category": "Technical", "difficulty": "Medium", "question": "Explain REST API principles.", "key_concepts": ["REST", "HTTP"]},
    {"id": 2, "category": "Behavioral", "difficulty": "Easy", "question": "Tell me about a time you worked under pressure.", "key_concepts": ["teamwork"]},
]

SAMPLE_ANSWERS = ["REST uses HTTP methods.", "I prioritized tasks."]

SAMPLE_EVALUATIONS = [
    {"success": True, "data": {"score": 8, "verdict": "Good", "strengths": ["Good understanding"], "missing_concepts": ["Auth"], "improvement_suggestions": ["Study JWT"], "ideal_answer": "REST is stateless."}},
    {"success": True, "data": {"score": 7, "verdict": "Good", "strengths": ["Problem-solving"], "missing_concepts": [], "improvement_suggestions": ["Add metrics"], "ideal_answer": "Use STAR method."}},
]

SAMPLE_SUMMARY = {"overall_score": 75, "readiness": "Good", "strong_areas": ["Python"], "weak_areas": ["System Design"], "recommendations": ["Study microservices", "Practice coding", "Review algorithms"]}

SAMPLE_META = {"title": "Python Developer", "role": "Developer", "seniority": "Mid"}


class TestGeneratePdfReport:
    def test_returns_bytes(self):
        pdf = generate_pdf_report(SAMPLE_QUESTIONS, SAMPLE_ANSWERS, SAMPLE_EVALUATIONS, SAMPLE_SUMMARY, SAMPLE_META)
        assert isinstance(pdf, bytes)

    def test_pdf_not_empty(self):
        pdf = generate_pdf_report(SAMPLE_QUESTIONS, SAMPLE_ANSWERS, SAMPLE_EVALUATIONS, SAMPLE_SUMMARY, SAMPLE_META)
        assert len(pdf) > 1000

    def test_pdf_magic_number(self):
        pdf = generate_pdf_report(SAMPLE_QUESTIONS, SAMPLE_ANSWERS, SAMPLE_EVALUATIONS, SAMPLE_SUMMARY, SAMPLE_META)
        assert pdf[:5] == b"%PDF-"

    def test_minimal_data_no_crash(self):
        pdf = generate_pdf_report(SAMPLE_QUESTIONS, ["", ""], [], None, None)
        assert isinstance(pdf, bytes)
        assert pdf[:5] == b"%PDF-"

    def test_failed_evaluation_handled(self):
        bad_evals = [{"success": False, "error": "LLM timeout"}, {"success": True, "data": SAMPLE_EVALUATIONS[1]["data"]}]
        pdf = generate_pdf_report(SAMPLE_QUESTIONS, SAMPLE_ANSWERS, bad_evals, SAMPLE_SUMMARY, SAMPLE_META)
        assert pdf[:5] == b"%PDF-"


class TestGetPdfFilename:
    def test_returns_string(self):
        name = get_pdf_filename(SAMPLE_META)
        assert isinstance(name, str)

    def test_ends_with_pdf(self):
        name = get_pdf_filename(SAMPLE_META)
        assert name.endswith(".pdf")

    def test_no_spaces(self):
        name = get_pdf_filename(SAMPLE_META)
        assert " " not in name

    def test_no_meta(self):
        name = get_pdf_filename(None)
        assert name.endswith(".pdf")
