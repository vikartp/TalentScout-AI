import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.db.database import get_session
from app.models.jd import JobDescription
from app.models.candidate import Candidate
from app.models.match import MatchResult
from app.models.conversation import Conversation
from app.services.ranking_engine import rank_candidates

router = APIRouter()


@router.get("/{jd_id}")
async def get_shortlist(
    jd_id: int,
    match_weight: float = Query(0.6, ge=0, le=1),
    session: AsyncSession = Depends(get_session),
):
    jd = await session.get(JobDescription, jd_id)
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")

    # Get all match results for this JD
    match_result = await session.execute(
        select(MatchResult).where(MatchResult.jd_id == jd_id)
    )
    matches = match_result.scalars().all()
    if not matches:
        raise HTTPException(status_code=404, detail="No match results found. Run matching first.")

    # Build candidate list with both scores
    candidates_data = []
    for m in matches:
        candidate = await session.get(Candidate, m.candidate_id)
        if not candidate:
            continue

        # Check for conversation/interest score
        convo_result = await session.execute(
            select(Conversation).where(
                Conversation.jd_id == jd_id,
                Conversation.candidate_id == m.candidate_id,
                Conversation.status == "completed",
            )
        )
        convo = convo_result.scalars().first()

        candidates_data.append({
            "candidate_id": candidate.id,
            "name": candidate.name,
            "current_role": candidate.current_role,
            "current_company": candidate.current_company,
            "experience_years": candidate.total_experience_years,
            "match_score": m.match_score,
            "semantic_score": m.semantic_score,
            "skill_score": m.skill_score,
            "experience_score": m.experience_score,
            "education_score": m.education_score,
            "matched_skills": json.loads(m.matched_skills) if m.matched_skills else [],
            "missing_skills": json.loads(m.missing_skills) if m.missing_skills else [],
            "match_explanation": m.explanation,
            "interest_score": convo.interest_score if convo else 0,
            "enthusiasm": convo.enthusiasm if convo else None,
            "availability": convo.availability if convo else None,
            "salary_alignment": convo.salary_alignment if convo else None,
            "cultural_fit": convo.cultural_fit if convo else None,
            "interest_explanation": convo.score_explanation if convo else None,
            "conversation_id": convo.id if convo else None,
            "conversation_status": convo.status if convo else "not_started",
        })

    ranked = rank_candidates(candidates_data, match_weight)

    return {
        "jd_id": jd_id,
        "jd_title": jd.title,
        "match_weight": match_weight,
        "interest_weight": round(1 - match_weight, 2),
        "shortlist": ranked,
    }
