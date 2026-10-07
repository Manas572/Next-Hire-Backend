import os
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

class SkillList(BaseModel):
    skills: list[str]

def extract_skills(text: str) -> list[str]:
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        google_api_key=os.getenv("GOOGLE_GEMINI_API"),
    ).with_structured_output(SkillList)

    prompt = PromptTemplate.from_template(
        "Extract all technical skills from the resume text below.\n\n{text}/ return in lower case like ['c++','mern','python','mysql','postgresql','django','drf','django-ninja','javascript','machine-learning','deep-learning','generative-ai' etc]"
    )

    result: SkillList = (prompt | llm).invoke({"text": text})
    return result.skills


