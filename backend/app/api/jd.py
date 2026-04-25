import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, delete

from app.db.database import get_session
from app.models.jd import JobDescription
from app.services.jd_parser import parse_jd

router = APIRouter()


class JDInput(BaseModel):
    text: str


@router.post("/parse")
async def parse_job_description(body: JDInput, session: AsyncSession = Depends(get_session)):
    parsed = await parse_jd(body.text)

    jd = JobDescription(
        raw_text=body.text,
        title=parsed.get("title"),
        department=parsed.get("department"),
        seniority=parsed.get("seniority"),
        skills_must_have=json.dumps(parsed.get("skills_must_have", [])),
        skills_nice_to_have=json.dumps(parsed.get("skills_nice_to_have", [])),
        experience_min=parsed.get("experience_min"),
        experience_max=parsed.get("experience_max"),
        education=parsed.get("education"),
        location=parsed.get("location"),
        responsibilities=json.dumps(parsed.get("responsibilities", [])),
        salary_min=parsed.get("salary_min"),
        salary_max=parsed.get("salary_max"),
        parsed_json=json.dumps(parsed),
    )
    session.add(jd)
    await session.commit()
    await session.refresh(jd)

    return {"id": jd.id, "parsed": parsed}


@router.get("/{jd_id}")
async def get_job_description(jd_id: int, session: AsyncSession = Depends(get_session)):
    jd = await session.get(JobDescription, jd_id)
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")
    return {
        "id": jd.id,
        "raw_text": jd.raw_text,
        "parsed": json.loads(jd.parsed_json) if jd.parsed_json else None,
        "created_at": jd.created_at,
    }


@router.get("")
async def list_job_descriptions(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(JobDescription).order_by(JobDescription.id.desc()))
    jds = result.scalars().all()
    return [
        {
            "id": jd.id,
            "title": jd.title,
            "seniority": jd.seniority,
            "location": jd.location,
            "created_at": jd.created_at,
        }
        for jd in jds
    ]


@router.delete("/clear")
async def clear_job_descriptions(session: AsyncSession = Depends(get_session)):
    await session.execute(delete(JobDescription))
    await session.commit()
    return {"message": "All job descriptions cleared"}
