from rest_framework import serializers
from .models import AnalysisReport
import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from django.db import transaction
load_dotenv()

client = genai.Client(
    api_key=os.getenv("GOOGLE_GEMINI_API")
)

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


class AnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisReport
        fields = ["resume_text"]

    def create(self, validated_data):
        job = self.context["job"]

        job_description = job.description
        resume_text = validated_data["resume_text"]

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
        try:
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
                            "items": QUESTION_SCHEMA
                        },
                        "behavioral_questions": {
                            "type": "array",
                            "items": QUESTION_SCHEMA
                        },
                        "skill_gaps": {
                            "type": "array",
                            "items": SKILL_GAP_SCHEMA
                        },
                        "preparation_plan": {
                            "type": "array",
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
            data = json.loads(response.text)
        except Exception:
            raise serializers.ValidationError({"error":"Try after some time"})
    
        return AnalysisReport.objects.create(
            candidate=self.context["request"].user.candidate_profile,
            job=job,
            resume_text=resume_text,
            match_score=data["match_score"],
            technical_questions=data["technical_questions"],
            behavioral_questions=data["behavioral_questions"],
            skill_gaps=data["skill_gaps"],
            preparation_plan=data["preparation_plan"],
        )