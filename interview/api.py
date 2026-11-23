import os
import math
import tempfile
import requests
from ninja import Router, File, Schema
from ninja.files import UploadedFile
from interview.services.pdftext import extract_text
from interview.services.llmcall import (
    evaluate_interview,
    extract_resume_data,
    generate_round_three_reply,
)

interview_router = Router()


class ChatMessage(Schema):
    role: str
    content: str


class RoundThreeIn(Schema):
    messages: list[ChatMessage]
    resume_context: dict = {}
    start: bool = False


class RoundOneGradeIn(Schema):
    ideal_answer: str
    user_answer: str


class InterviewEvaluationIn(Schema):
    r1_messages: list[ChatMessage]
    r3_messages: list[ChatMessage]
    r1_vector: list[dict] = []
    resume_context: dict = {}


def grade_answer(ideal_answer: str, user_answer: str) -> dict:
    """Grade a Round 1 answer with Cloudflare Workers AI, falling back to medium."""
    if len(user_answer.strip()) < 5:
        return {
            "grade": -1,
            "status": "Bad - Answer too short",
            "raw_score": 0.0,
            "fallback": False,
        }

    account_id = os.getenv("CF_ACCOUNT_ID")
    api_token = os.getenv("CF_API_TOKEN")
    if not account_id or not api_token:
        return {
            "grade": 0,
            "status": "Medium - Cloudflare AI is not configured; using fallback score",
            "raw_score": 0.5,
            "fallback": True,
        }

    model = "@cf/baai/bge-reranker-base"
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model}"
    try:
        response = requests.post(
            url,
            headers={"Authorization": f"Bearer {api_token}"},
            json={
                "query": ideal_answer,
                "contexts": [{"text": user_answer}],
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        if not data.get("success"):
            raise ValueError("Cloudflare AI returned an unsuccessful response")

        score = float(data["result"]["response"][0]["score"])
        if not math.isfinite(score):
            raise ValueError("Cloudflare AI returned an invalid score")
    except Exception:
        return {
            "grade": 0,
            "status": "Medium - Cloudflare AI unavailable; using fallback score",
            "raw_score": 0.5,
            "fallback": True,
        }

    if score < 0.35:
        grade, status = -1, "Bad - Lacks understanding"
    elif score < 0.75:
        grade, status = 0, "Medium - Partial knowledge"
    else:
        grade, status = 1, "Excellent - Strong match"
    return {"grade": grade, "status": status, "raw_score": round(score, 4), "fallback": False}


@interview_router.post("/extract-skills")
def extract_skills_from_resume(request, file: UploadedFile = File(...)):
    suffix = os.path.splitext(file.name)[1] or ".pdf"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(file.read())
        tmp_path = tmp.name
        
    try:
        result = extract_resume_data(extract_text(tmp_path))
        return {
            "skills": result.skills,
            "projects": [p.model_dump() for p in result.projects],
        }
    finally:
        os.remove(tmp_path)


@interview_router.post("/round-one/grade")
def round_one_grade(request, payload: RoundOneGradeIn):
    if not payload.ideal_answer.strip() or not payload.user_answer.strip():
        return 400, {"message": "An ideal answer and user answer are required."}
    return grade_answer(payload.ideal_answer, payload.user_answer)


@interview_router.post("/round-three")
def round_three(request, payload: RoundThreeIn):
    messages = [message.dict() for message in payload.messages]
    if not payload.start and (not messages or messages[-1]["role"] != "user"):
        return 400, {"message": "Send a user message to continue the interview."}
    if any(message["role"] not in {"user", "assistant"} for message in messages):
        return 400, {"message": "Invalid conversation role."}
    try:
        return {"reply": generate_round_three_reply(messages, payload.resume_context, payload.start)}
    except requests.RequestException as error:
        upstream_message = "The interview model is temporarily unavailable. Please try again."
        response = getattr(error, "response", None)
        if response is not None:
            try:
                upstream_message = response.json().get("error", {}).get("message") or upstream_message
            except (ValueError, AttributeError):
                pass
        return 502, {"message": upstream_message}
    except RuntimeError as error:
        return 503, {"message": str(error)}


@interview_router.post("/evaluate-interview")
def evaluate_completed_interview(request, payload: InterviewEvaluationIn):
    r1_messages = [message.dict() for message in payload.r1_messages]
    r3_messages = [message.dict() for message in payload.r3_messages]
    messages = [*r1_messages, *r3_messages]
    if not messages:
        return 400, {"message": "Interview messages are required for evaluation."}
    if any(message["role"] not in {"user", "assistant"} for message in messages):
        return 400, {"message": "Invalid conversation role."}
    if not any(message["role"] == "user" for message in messages):
        return 400, {"message": "At least one candidate answer is required for evaluation."}

    try:
        evaluation = evaluate_interview(
            r1_messages,
            r3_messages,
            payload.r1_vector,
            payload.resume_context,
        )
        return {"evaluation": evaluation}
    except RuntimeError as error:
        return 503, {"message": str(error)}
    except Exception:
        return 502, {"message": "The evaluation model is temporarily unavailable. Please try again."}

