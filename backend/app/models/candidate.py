from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class Candidate(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    current_role: Optional[str] = None
    current_company: Optional[str] = None
    skills: Optional[str] = None  # JSON string list
    total_experience_years: Optional[float] = None
    education: Optional[str] = None  # JSON string
    work_history: Optional[str] = None  # JSON string
    achievements: Optional[str] = None  # JSON string list
    resume_text: str = ""
    parsed_json: Optional[str] = None  # full parsed output as JSON
    filename: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
