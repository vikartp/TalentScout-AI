from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class JobDescription(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    raw_text: str
    title: Optional[str] = None
    department: Optional[str] = None
    seniority: Optional[str] = None
    skills_must_have: Optional[str] = None  # JSON string list
    skills_nice_to_have: Optional[str] = None  # JSON string list
    experience_min: Optional[int] = None
    experience_max: Optional[int] = None
    education: Optional[str] = None
    location: Optional[str] = None
    responsibilities: Optional[str] = None  # JSON string list
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    parsed_json: Optional[str] = None  # full parsed output as JSON
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
