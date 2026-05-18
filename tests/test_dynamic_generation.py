import pytest
from modules.question_generator import generate_dynamic_question
from unittest.mock import patch, MagicMock

@patch("modules.question_generator.get_provider")
def test_dynamic_question_harder_instruction(mock_get_provider):
    """Test that scoring 8 or higher injects the 'harder' instruction."""
    mock_provider = MagicMock()
    mock_get_provider.return_value = mock_provider
    
    # Mock the LLM to return valid JSON
    mock_provider.generate_json.return_value = {
        "category": "Technical",
        "difficulty": "Hard",
        "question": "What are the trade-offs of using GraphQL over REST?",
        "key_concepts": ["Over-fetching", "N+1 problem"]
    }

    generate_dynamic_question(
        jd_analysis={"title": "Software Engineer"},
        level="Medium",
        previous_score=9.0,
        provider_name="mock"
    )
    
    # Check that generate_json was called
    assert mock_provider.generate_json.called
    
    # Get the prompt passed to the LLM
    call_args = mock_provider.generate_json.call_args[0]
    prompt = call_args[0]
    
    # Verify the specific dynamic instruction was injected
    assert "Make this next question significantly harder" in prompt

@patch("modules.question_generator.get_provider")
def test_dynamic_question_easier_instruction(mock_get_provider):
    """Test that scoring 4 or lower injects the 'easier' instruction."""
    mock_provider = MagicMock()
    mock_get_provider.return_value = mock_provider
    
    mock_provider.generate_json.return_value = {
        "category": "Technical",
        "difficulty": "Easy",
        "question": "What is an API?",
        "key_concepts": ["API"]
    }

    generate_dynamic_question(
        jd_analysis={"title": "Software Engineer"},
        level="Medium",
        previous_score=3.0,
        provider_name="mock"
    )
    
    call_args = mock_provider.generate_json.call_args[0]
    prompt = call_args[0]
    
    assert "struggled with the last question" in prompt
    assert "Ask a fundamental, core-concept question" in prompt
