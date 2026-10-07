import os
import tempfile
from ninja import Router, File
from ninja.files import UploadedFile
from interview.services.pdftext import extract_text
from interview.services.llmcall import extract_skills
interview_router = Router()
@interview_router.post("/extract-skills")
def extract_skills_from_resume(request, file: UploadedFile = File(...)):
    suffix = os.path.splitext(file.name)[1] or ".pdf"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(file.read())
        tmp_path = tmp.name
    try:
        return {"skills": extract_skills(extract_text(tmp_path))}
    finally:
        os.remove(tmp_path)
