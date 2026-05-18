import pytest
import os
import sqlite3
from modules.database import get_connection, init_db, save_interview_summary, get_all_interviews, DB_PATH

@pytest.fixture(autouse=True)
def setup_test_db():
    # Ensure we use a clean state for testing by initializing
    init_db()
    # Clear the table before testing
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM interviews')
    conn.commit()
    conn.close()
    yield
    # Teardown: clear table again
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM interviews')
    conn.commit()
    conn.close()

def test_save_and_retrieve_interview_summary():
    """Test that the analytics dashboard accurately saves and reads interviews."""
    # Action: Save a mock interview
    save_interview_summary(
        level="Medium",
        question_count=10,
        final_score=85,
        readiness_level="Good",
        strengths=["Python", "SQL"],
        weak_areas=["System Design"],
        improvements=["Study more architecture patterns"]
    )
    
    # Action: Retrieve for the dashboard
    interviews = get_all_interviews()
    
    # Assertions
    assert len(interviews) == 1
    assert interviews[0]["final_score"] == 85
    assert interviews[0]["level"] == "Medium"
    assert interviews[0]["question_count"] == 10
    assert "System Design" in interviews[0]["weak_areas"]
    assert "Python" in interviews[0]["strengths"]

def test_multiple_interviews_ordering():
    """Test that the dashboard retrieves interviews in descending order (newest first)."""
    save_interview_summary("Basic", 5, 20, "Needs Work", [], [], [])
    save_interview_summary("Advanced", 15, 95, "Interview Ready", [], [], [])
    
    interviews = get_all_interviews()
    
    assert len(interviews) == 2
    # The newest one should be first
    assert interviews[0]["final_score"] == 95
    assert interviews[1]["final_score"] == 20
