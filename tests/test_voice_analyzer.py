import pytest
from modules.voice_analyzer import analyze_filler_words

def test_analyze_filler_words_no_fillers():
    """Test that a clean sentence returns 0 fillers."""
    text = "I implemented the binary search tree efficiently."
    result = analyze_filler_words(text)
    
    assert result["total"] == 0
    assert result["feedback"] == ""

def test_analyze_filler_words_with_fillers():
    """Test that filler words are correctly counted."""
    text = "Um, I think, like, we should actually use a database, you know?"
    result = analyze_filler_words(text)
    
    assert result["total"] == 4
    assert result["counts"]["um"] == 1
    assert result["counts"]["like"] == 1
    assert result["counts"]["actually"] == 1
    assert result["counts"]["you know"] == 1
    assert "Communication Tip" in result["feedback"]

def test_analyze_filler_words_penalty_severity():
    """Test that more than 3 fillers triggers the stronger warning."""
    text = "Um uh like basically actually you know literally"
    result = analyze_filler_words(text)
    
    assert result["total"] == 7
    assert "quite a few filler words" in result["feedback"]
