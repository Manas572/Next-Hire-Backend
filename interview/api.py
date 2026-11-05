import os
import tempfile
from ninja import Router, File
from ninja.files import UploadedFile
from interview.services.pdftext import extract_text
from interview.services.llmcall import extract_resume_data

interview_router = Router()

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
