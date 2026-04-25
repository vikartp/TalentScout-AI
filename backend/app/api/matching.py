import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, delete

from app.db.database import get_session
from app.models.jd import JobDescription
from app.models.candidate import Candidate
from app.models.match import MatchResult
from app.services.matching_engine import compute_match_score, generate_match_explanation

router = APIRouter()


class MatchRequest(BaseModel):
    jd_id: int


@router.post("/run")
async def run_matching(body: MatchRequest, session: AsyncSession = Depends(get_session)):
    jd = await session.get(JobDescription, body.jd_id)
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")

    jd_parsed = json.loads(jd.parsed_json) if jd.parsed_json else {}

    # Delete previous match results for this JD so re-runs don't duplicate
    await session.execute(delete(MatchResult).where(MatchResult.jd_id == body.jd_id))
    await session.flush()

    # Get all candidates
    result = await session.execute(select(Candidate))
    candidates = result.scalars().all()
    if not candidates:
        raise HTTPException(status_code=404, detail="No candidates found. Upload resumes first.")

    match_results = []
    for candidate in candidates:
        cand_parsed = json.loads(candidate.parsed_json) if candidate.parsed_json else {}

        scores = await compute_match_score(
            jd_text=jd.raw_text,
            jd_parsed=jd_parsed,
            candidate_text=candidate.resume_text,
            candidate_parsed=cand_parsed,
        )

        explanation = await generate_match_explanation(
            jd_title=jd.title or "Unknown Role",
            candidate_name=candidate.name,
            scores=scores,
        )

        match = MatchResult(
            jd_id=jd.id,
            candidate_id=candidate.id,
            semantic_score=scores["semantic_score"],
            skill_score=scores["skill_score"],
            experience_score=scores["experience_score"],
            education_score=scores["education_score"],
            match_score=scores["match_score"],
            explanation=explanation,
            matched_skills=json.dumps(scores["matched_skills"]),
            missing_skills=json.dumps(scores["missing_skills"]),
        )
        session.add(match)
        match_results.append({
            "candidate_id": candidate.id,
            "candidate_name": candidate.name,
            "current_role": candidate.current_role,
            **scores,
            "explanation": explanation,
        })

    await session.commit()

    match_results.sort(key=lambda x: x["match_score"], reverse=True)
    return {"jd_id": jd.id, "jd_title": jd.title, "matches": match_results}


@router.get("/results/{jd_id}")
async def get_match_results(jd_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(MatchResult).where(MatchResult.jd_id == jd_id).order_by(MatchResult.match_score.desc())
    )
    matches = result.scalars().all()
    out = []
    for m in matches:
        candidate = await session.get(Candidate, m.candidate_id)
        out.append({
            "candidate_id": m.candidate_id,
            "candidate_name": candidate.name if candidate else "Unknown",
            "current_role": candidate.current_role if candidate else None,
            "match_score": m.match_score,
            "semantic_score": m.semantic_score,
            "skill_score": m.skill_score,
            "experience_score": m.experience_score,
            "education_score": m.education_score,
            "matched_skills": json.loads(m.matched_skills) if m.matched_skills else [],
            "missing_skills": json.loads(m.missing_skills) if m.missing_skills else [],
            "explanation": m.explanation,
        })
    return {"jd_id": jd_id, "matches": out}


@router.delete("/clear")
async def clear_match_results(session: AsyncSession = Depends(get_session)):
    await session.execute(delete(MatchResult))
    await session.commit()
    return {"message": "All match results cleared"}
