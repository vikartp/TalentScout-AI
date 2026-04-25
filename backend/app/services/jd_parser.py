import json
from openai import OpenAI
from app.config import OPENAI_API_KEY, OPENAI_API_BASE, CHAT_MODEL

client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE)

PARSE_SYSTEM_PROMPT = """You are an expert recruiter assistant. Parse the given Job Description and extract structured information.
Return a JSON object with exactly these keys:
{
  "title": "Job title",
  "department": "Department or team",
  "seniority": "Junior/Mid/Senior/Lead/Principal/Director",
  "skills_must_have": ["skill1", "skill2"],
  "skills_nice_to_have": ["skill1", "skill2"],
  "experience_min": 3,
  "experience_max": 7,
  "education": "Required education level",
  "location": "Location or Remote",
  "responsibilities": ["resp1", "resp2"],
  "salary_min": null,
  "salary_max": null
}
Use null for fields not mentioned. Return ONLY valid JSON, no markdown or explanation."""


async def parse_jd(raw_text: str) -> dict:
    response = client.chat.completions.create(
        model=CHAT_MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": PARSE_SYSTEM_PROMPT},
            {"role": "user", "content": raw_text},
        ],
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)
