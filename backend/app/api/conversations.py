import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, delete

from app.db.database import get_session
from app.models.jd import JobDescription
from app.models.candidate import Candidate
from app.models.conversation import Conversation
from app.models.match import MatchResult
from app.services.conversation_agent import run_conversation, score_conversation

router = APIRouter()


class ConversationStartRequest(BaseModel):
    jd_id: int
    candidate_id: int


@router.post("/start")
async def start_conversation(body: ConversationStartRequest, session: AsyncSession = Depends(get_session)):
    jd = await session.get(JobDescription, body.jd_id)
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")

    candidate = await session.get(Candidate, body.candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    jd_parsed = json.loads(jd.parsed_json) if jd.parsed_json else {}

    # Get match highlights if available
    result = await session.execute(
        select(MatchResult)
        .where(MatchResult.jd_id == body.jd_id, MatchResult.candidate_id == body.candidate_id)
    )
    match = result.scalars().first()
    match_highlights = match.explanation if match else "Based on resume review, this candidate appears to be a good fit."

    # Build candidate profile summary
    cand_parsed = json.loads(candidate.parsed_json) if candidate.parsed_json else {}
    profile_summary = f"""Name: {candidate.name}
Current Role: {candidate.current_role or 'N/A'} at {candidate.current_company or 'N/A'}
Experience: {candidate.total_experience_years or 'N/A'} years
Skills: {', '.join(cand_parsed.get('skills', [])[:10])}"""

    jd_summary = f"""Title: {jd.title}
Seniority: {jd_parsed.get('seniority', 'N/A')}
Key Skills: {', '.join(jd_parsed.get('skills_must_have', [])[:5])}
Location: {jd_parsed.get('location', 'N/A')}"""

    # Run simulated conversation
    transcript = await run_conversation(
        jd_title=jd.title or "Open Role",
        jd_summary=jd_summary,
        candidate_name=candidate.name,
        candidate_profile=profile_summary,
        match_highlights=match_highlights,
    )

    # Score the conversation
    scores = await score_conversation(transcript, jd.title or "Open Role")

    # Save to DB
    convo = Conversation(
        jd_id=body.jd_id,
        candidate_id=body.candidate_id,
        transcript=json.dumps(transcript),
        interest_score=scores["interest_score"],
        enthusiasm=scores["enthusiasm"],
        availability=scores["availability"],
        salary_alignment=scores["salary_alignment"],
        cultural_fit=scores["cultural_fit"],
        score_explanation=scores.get("explanation", ""),
        status="completed",
    )
    session.add(convo)
    await session.commit()
    await session.refresh(convo)

    return {
        "id": convo.id,
        "jd_id": body.jd_id,
        "candidate_id": body.candidate_id,
        "candidate_name": candidate.name,
        "transcript": transcript,
        "scores": scores,
        "status": "completed",
    }


@router.get("/{conversation_id}")
async def get_conversation(conversation_id: int, session: AsyncSession = Depends(get_session)):
    convo = await session.get(Conversation, conversation_id)
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")

    candidate = await session.get(Candidate, convo.candidate_id)
    return {
        "id": convo.id,
        "jd_id": convo.jd_id,
        "candidate_id": convo.candidate_id,
        "candidate_name": candidate.name if candidate else "Unknown",
        "transcript": json.loads(convo.transcript) if convo.transcript else [],
        "scores": {
            "interest_score": convo.interest_score,
            "enthusiasm": convo.enthusiasm,
            "availability": convo.availability,
            "salary_alignment": convo.salary_alignment,
            "cultural_fit": convo.cultural_fit,
            "explanation": convo.score_explanation,
        },
        "status": convo.status,
    }


@router.get("/by-jd/{jd_id}")
async def list_conversations_by_jd(jd_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Conversation).where(Conversation.jd_id == jd_id)
    )
    convos = result.scalars().all()
    out = []
    for c in convos:
        candidate = await session.get(Candidate, c.candidate_id)
        out.append({
            "id": c.id,
            "candidate_id": c.candidate_id,
            "candidate_name": candidate.name if candidate else "Unknown",
            "interest_score": c.interest_score,
            "status": c.status,
        })
    return out


@router.delete("/clear")
async def clear_conversations(session: AsyncSession = Depends(get_session)):
    await session.execute(delete(Conversation))
    await session.commit()
    return {"message": "All conversations cleared"}
