import json
import tempfile
import os
from openai import OpenAI
import pdfplumber
from docx import Document as DocxDocument

from app.config import OPENAI_API_KEY, OPENAI_API_BASE, CHAT_MODEL

client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE)

PARSE_SYSTEM_PROMPT = """You are an expert resume parser. Extract structured information from the given resume text.
Return a JSON object with exactly these keys:
{
  "name": "Full Name",
  "email": "email@example.com",
  "phone": "phone number or null",
  "current_role": "Current or most recent job title",
  "current_company": "Current or most recent company",
  "skills": ["skill1", "skill2", ...],
  "total_experience_years": 5.0,
  "education": [{"degree": "B.S.", "field": "Computer Science", "institution": "MIT", "year": 2018}],
  "work_history": [{"role": "title", "company": "name", "duration": "2y", "highlights": ["..."]}],
  "achievements": ["achievement1", "achievement2"]
}
Use null for fields not found. Return ONLY valid JSON, no markdown or explanation."""


def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


def extract_text_from_docx(file_path: str) -> str:
    doc = DocxDocument(file_path)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


async def extract_text(file_path: str, filename: str) -> str:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif lower.endswith(".docx"):
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {filename}")


async def parse_resume(resume_text: str) -> dict:
    response = client.chat.completions.create(
        model=CHAT_MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": PARSE_SYSTEM_PROMPT},
            {"role": "user", "content": resume_text},
        ],
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)
