import os
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

class Project(BaseModel):
    name: str = Field(description="Name of the project")
    what: str = Field(description="What the project is or does")
    how: str = Field(description="How the project was implemented")
    techstack: list[str] = Field(description="List of technologies used")

class ResumeData(BaseModel):
    skills: list[str] = Field(description="List of technical skills in lowercase")
    projects: list[Project] = Field(description="List of extracted projects")

def extract_resume_data(text: str) -> ResumeData:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GOOGLE_GEMINI_API"),
    ).with_structured_output(ResumeData)

    prompt = PromptTemplate.from_template(
        """Extract all technical skills and projects from the resume text below.
        Resume Text:
        {text}
        Instructions:
        - Skills: Return as a list of lowercase strings like ['c++','mern','python','mysql','django'].
        - Projects: Extract the project name, what it does, how it was built, and its tech stack.
        """
    )

    result: ResumeData = (prompt | llm).invoke({"text": text})
    return result