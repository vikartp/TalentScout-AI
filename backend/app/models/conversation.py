from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class Conversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    jd_id: int = Field(foreign_key="jobdescription.id")
    candidate_id: int = Field(foreign_key="candidate.id")
    transcript: Optional[str] = None  # JSON list of messages
    interest_score: Optional[float] = None
    enthusiasm: Optional[float] = None
    availability: Optional[float] = None
    salary_alignment: Optional[float] = None
    cultural_fit: Optional[float] = None
    score_explanation: Optional[str] = None
    status: str = "pending"  # pending, in_progress, completed
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
