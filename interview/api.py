import os
import tempfile
import requests
from ninja import Router, File, Schema
from ninja.files import UploadedFile
from interview.services.pdftext import extract_text
from interview.services.llmcall import extract_resume_data, generate_round_three_reply

interview_router = Router()


class ChatMessage(Schema):
    role: str
    content: str


class RoundThreeIn(Schema):
    messages: list[ChatMessage]
    resume_context: dict = {}
    start: bool = False


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

