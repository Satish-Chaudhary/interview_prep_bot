from typing import Any

JD_ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "role": {"type": "string"},
        "seniority": {"type": "string", "enum": ["Junior", "Mid", "Senior"]},
        "key_skills": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["title", "role", "seniority", "key_skills"],
}

QUESTION_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "role": {"type": "string"},
        "seniority": {"type": "string"},
        "questions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "category": {"type": "string", "enum": ["Technical", "Behavioral", "Situational", "HR", "System Design"]},
                    "difficulty": {"type": "string", "enum": ["Easy", "Medium", "Hard"]},
                    "question": {"type": "string"},
                    "key_concepts": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["id", "category", "difficulty", "question", "key_concepts"],
            },
        },
    },
    "required": ["title", "role", "seniority", "questions"],
}

SINGLE_QUESTION_SCHEMA = {
    "type": "object",
    "properties": {
        "category": {"type": "string", "enum": ["Technical", "Behavioral", "Situational", "HR", "System Design"]},
        "difficulty": {"type": "string", "enum": ["Easy", "Medium", "Hard"]},
        "question": {"type": "string"},
        "key_concepts": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["category", "difficulty", "question", "key_concepts"],
}

EVALUATION_SCHEMA = {
    "type": "object",
    "properties": {
        "score": {"type": "number", "minimum": 0, "maximum": 10},
        "verdict": {"type": "string", "enum": ["Poor", "Fair", "Good", "Excellent"]},
        "strengths": {"type": "array", "items": {"type": "string"}},
        "missing_concepts": {"type": "array", "items": {"type": "string"}},
        "improvement_suggestions": {"type": "array", "items": {"type": "string"}},
        "ideal_answer": {"type": "string"},
    },
    "required": ["score", "verdict", "strengths", "missing_concepts", "improvement_suggestions", "ideal_answer"],
}

BEHAVIORAL_EVALUATION_SCHEMA = {
    "type": "object",
    "properties": {
        "score": {"type": "number", "minimum": 0, "maximum": 10},
        "verdict": {"type": "string", "enum": ["Poor", "Fair", "Good", "Excellent"]},
        "used_star_method": {"type": "boolean"},
        "missing_concepts": {"type": "array", "items": {"type": "string"}},
        "strengths": {"type": "array", "items": {"type": "string"}},
        "improvement_suggestions": {"type": "array", "items": {"type": "string"}},
        "ideal_answer": {"type": "string"},
    },
    "required": ["score", "verdict", "used_star_method", "missing_concepts", "strengths", "improvement_suggestions", "ideal_answer"],
}

SUMMARY_SCHEMA = {
    "type": "object",
    "properties": {
        "overall_score": {"type": "number", "minimum": 0, "maximum": 100},
        "readiness": {"type": "string", "enum": ["Not Ready", "Needs Practice", "Good", "Interview Ready"]},
        "strong_areas": {"type": "array", "items": {"type": "string"}},
        "weak_areas": {"type": "array", "items": {"type": "string"}},
        "recommendations": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 3,
            "maxItems": 10,
        },
    },
    "required": ["overall_score", "readiness", "strong_areas", "weak_areas", "recommendations"],
}

SCHEMA_MAP: dict[str, dict[str, Any]] = {
    "jd_analysis": JD_ANALYSIS_SCHEMA,
    "questions": QUESTION_SCHEMA,
    "single_question": SINGLE_QUESTION_SCHEMA,
    "evaluation": EVALUATION_SCHEMA,
    "behavioral_evaluation": BEHAVIORAL_EVALUATION_SCHEMA,
    "summary": SUMMARY_SCHEMA,
}
