import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GOOGLE_GEMINI_API")
)

# -------------------------
# Test Data
# -------------------------

job_description = """
We are looking for a React + Django Developer.

Requirements:
- React
- Django
- Django REST Framework
- PostgreSQL
- Git
- Docker
- AWS

Responsibilities:
- Build scalable web applications
- Design REST APIs
- Deploy applications to cloud infrastructure
"""

resume_text = """
Manas

Skills:
React, Django, Django REST Framework, PostgreSQL, Git

Projects:
1. Work Sphere (Employee Management System)
   - React frontend
   - Django backend
   - PostgreSQL database

2. Code Sphere
   - Coding platform built using React and Django

Achievements:
- Solved 1000+ DSA problems
- Codeforces Rating: 1392
- CodeChef Rating: 1520
"""

# -------------------------
# Schemas
# -------------------------

QUESTION_SCHEMA = {
    "type": "object",
    "properties": {
        "question": {
            "type": "string",
            "description": "Interview question"
        },
        "intention": {
            "type": "string",
            "description": "Purpose of asking this question"
        },
        "answer": {
            "type": "string",
            "description": "Expected ideal answer"
        }
    },
    "required": ["question", "intention", "answer"]
}

SKILL_GAP_SCHEMA = {
    "type": "object",
    "properties": {
        "skill": {
            "type": "string"
        },
        "severity": {
            "type": "string",
            "enum": ["low", "medium", "high"]
        }
    },
    "required": ["skill", "severity"]
}

PREP_PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "day": {
            "type": "integer"
        },
        "focus": {
            "type": "string"
        },
        "task": {
            "type": "string"
        }
    },
    "required": ["day", "focus", "task"]
}

# -------------------------
# Prompt
# -------------------------

prompt = f"""
You are an expert technical recruiter.

Job Description:
{job_description}

Candidate Resume:
{resume_text}

Analyze the candidate.

Return:
1. Match score (0-100)
2. 5 Technical interview questions
3. 5 Behavioral interview questions
4. 3 Skill gaps
5. 3-day preparation plan

Be realistic and base the analysis on the provided resume and job description.
"""

# -------------------------
# Gemini Request
# -------------------------

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema={
            "type": "object",
            "properties": {
                "match_score": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 100
                },
                "technical_questions": {
                    "type": "array",
                    "number of Q" :5,
                    "items": QUESTION_SCHEMA
                },
                "behavioral_questions": {
                    "type": "array",
                    "number of Q" :5,
                    "items": QUESTION_SCHEMA
                },
                "skill_gaps": {
                    "type": "array",
                    "number of gaps" :3,
                    "items": SKILL_GAP_SCHEMA
                },
                "preparation_plan": {
                    "type": "array",
                    "number of days to plan" :3,
                    "items": PREP_PLAN_SCHEMA
                }
            },
            "required": [
                "match_score",
                "technical_questions",
                "behavioral_questions",
                "skill_gaps",
                "preparation_plan"
            ]
        }
    )
)

# -------------------------
# Output
# -------------------------

print(response.text)

data = json.loads(response.text)

print("\nParsed Successfully")
print(type(data))
print("Match Score:", data["match_score"])