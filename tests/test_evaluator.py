import pytest
from modules.answer_evaluator import evaluate_answer

# For tests, we can skip actual LLM calls if we want to unit test the logic wrapper, 
# or we can do live integration tests if Ollama is running.
# Here we'll test the edge cases built into the logic wrapper.

def test_empty_answer_returns_zero():
    """Test that submitting an empty or whitespace-only answer immediately returns a score of 0."""
    result = evaluate_answer(
        question="What is dependency injection?",
        answer="   ",
        category="Technical",
        provider_name="ollama"  # Should not even hit Ollama
    )
    
    assert result["success"] is True
    assert result["data"]["score"] == 0
    assert result["data"]["verdict"] == "Poor"
    assert "No answer provided." in result["data"]["missing_concepts"]

def test_none_answer_returns_zero():
    """Test that submitting a None answer immediately returns a score of 0."""
    result = evaluate_answer(
        question="Tell me about a time you failed.",
        answer=None,
        category="Behavioral",
        provider_name="ollama"
    )
    
    assert result["success"] is True
    assert result["data"]["score"] == 0
    assert "No answer provided." in result["data"]["missing_concepts"]
