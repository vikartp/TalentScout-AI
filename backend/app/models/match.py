from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class MatchResult(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    jd_id: int = Field(foreign_key="jobdescription.id")
    candidate_id: int = Field(foreign_key="candidate.id")
    semantic_score: float = 0.0
    skill_score: float = 0.0
    experience_score: float = 0.0
    education_score: float = 0.0
    match_score: float = 0.0  # weighted combination
    explanation: Optional[str] = None  # human-readable match summary
    matched_skills: Optional[str] = None  # JSON list
    missing_skills: Optional[str] = None  # JSON list
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
