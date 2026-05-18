import sqlite3
import json
import os
from datetime import datetime

# Define the path to the database file in the 'data' directory
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'database.db')

def get_connection():
    """Establish and return a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name
    return conn

def init_db():
    """Initialize the database and create tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Table to store interview sessions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            level TEXT NOT NULL,
            question_count INTEGER NOT NULL,
            final_score INTEGER NOT NULL,
            readiness_level TEXT,
            strengths TEXT,
            weak_areas TEXT,
            improvements TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def save_interview_summary(level: str, question_count: int, final_score: int, 
                           readiness_level: str, strengths: list, weak_areas: list, improvements: list):
    """Save an interview summary to the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Convert lists to JSON strings for storage
    cursor.execute('''
        INSERT INTO interviews (date, level, question_count, final_score, readiness_level, strengths, weak_areas, improvements)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        date_str, 
        level, 
        question_count, 
        final_score, 
        readiness_level, 
        json.dumps(strengths), 
        json.dumps(weak_areas), 
        json.dumps(improvements)
    ))
    
    conn.commit()
    conn.close()

def get_all_interviews():
    """Retrieve all past interviews for the dashboard, ordered by newest first."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM interviews ORDER BY id DESC')
    rows = cursor.fetchall()
    
    conn.close()
    
    # Parse JSON back to lists for UI
    result = []
    for row in rows:
        result.append({
            "id": row["id"],
            "date": row["date"],
            "level": row["level"],
            "question_count": row["question_count"],
            "final_score": row["final_score"],
            "readiness_level": row["readiness_level"],
            "strengths": json.loads(row["strengths"]) if row["strengths"] else [],
            "weak_areas": json.loads(row["weak_areas"]) if row["weak_areas"] else [],
            "improvements": json.loads(row["improvements"]) if row["improvements"] else []
        })
        
    return result

# Automatically initialize database when module is loaded
init_db()
