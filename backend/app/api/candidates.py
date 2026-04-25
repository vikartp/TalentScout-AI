import json
import tempfile
import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, delete

from app.db.database import get_session
from app.db.vector_store import embeddings, get_or_create_collection
from app.models.candidate import Candidate
from app.models.match import MatchResult
from app.models.conversation import Conversation
from app.services.resume_parser import extract_text, parse_resume

router = APIRouter()


@router.post("/upload")
async def upload_resumes(
    files: list[UploadFile] = File(...),
    session: AsyncSession = Depends(get_session),
):
    results = []
    collection = get_or_create_collection("resumes")

    for file in files:
        if not file.filename:
            continue
        lower = file.filename.lower()
        if not (lower.endswith(".pdf") or lower.endswith(".docx")):
            results.append({"filename": file.filename, "status": "skipped", "error": "Unsupported format"})
            continue

        tmp_path = None
        try:
            suffix = ".pdf" if lower.endswith(".pdf") else ".docx"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                contents = await file.read()
                tmp.write(contents)
                tmp_path = tmp.name

            resume_text = await extract_text(tmp_path, file.filename)
            parsed = await parse_resume(resume_text)

            candidate = Candidate(
                name=parsed.get("name", "Unknown"),
                email=parsed.get("email"),
                phone=parsed.get("phone"),
                current_role=parsed.get("current_role"),
                current_company=parsed.get("current_company"),
                skills=json.dumps(parsed.get("skills", [])),
                total_experience_years=parsed.get("total_experience_years"),
                education=json.dumps(parsed.get("education", [])),
                work_history=json.dumps(parsed.get("work_history", [])),
                achievements=json.dumps(parsed.get("achievements", [])),
                resume_text=resume_text,
                parsed_json=json.dumps(parsed),
                filename=file.filename,
            )
            session.add(candidate)
            await session.commit()
            await session.refresh(candidate)

            # Store embedding in ChromaDB
            emb = embeddings.embed_query(resume_text)
            collection.upsert(
                ids=[str(candidate.id)],
                embeddings=[emb],
                metadatas=[{"candidate_id": candidate.id, "name": candidate.name}],
                documents=[resume_text],
            )

            results.append({
                "filename": file.filename,
                "status": "success",
                "candidate_id": candidate.id,
                "name": candidate.name,
            })
        except Exception as e:
            results.append({"filename": file.filename, "status": "error", "error": str(e)})
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)

    return {"results": results}


@router.get("")
async def list_candidates(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Candidate).order_by(Candidate.id.desc()))
    candidates = result.scalars().all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "email": c.email,
            "current_role": c.current_role,
            "current_company": c.current_company,
            "skills": json.loads(c.skills) if c.skills else [],
            "total_experience_years": c.total_experience_years,
            "filename": c.filename,
            "created_at": c.created_at,
        }
        for c in candidates
    ]


@router.get("/{candidate_id}")
async def get_candidate(candidate_id: int, session: AsyncSession = Depends(get_session)):
    candidate = await session.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return {
        "id": candidate.id,
        "name": candidate.name,
        "email": candidate.email,
        "phone": candidate.phone,
        "current_role": candidate.current_role,
        "current_company": candidate.current_company,
        "skills": json.loads(candidate.skills) if candidate.skills else [],
        "total_experience_years": candidate.total_experience_years,
        "education": json.loads(candidate.education) if candidate.education else [],
        "work_history": json.loads(candidate.work_history) if candidate.work_history else [],
        "achievements": json.loads(candidate.achievements) if candidate.achievements else [],
        "filename": candidate.filename,
        "created_at": candidate.created_at,
    }


@router.delete("/{candidate_id}")
async def delete_candidate(candidate_id: int, session: AsyncSession = Depends(get_session)):
    candidate = await session.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Cascade: delete related matches and conversations
    await session.execute(delete(MatchResult).where(MatchResult.candidate_id == candidate_id))
    await session.execute(delete(Conversation).where(Conversation.candidate_id == candidate_id))

    # Remove from ChromaDB
    try:
        collection = get_or_create_collection("resumes")
        collection.delete(ids=[str(candidate_id)])
    except Exception:
        pass

    await session.delete(candidate)
    await session.commit()
    return {"message": f"Candidate {candidate_id} and related data deleted"}


@router.delete("/clear")
async def clear_candidates(session: AsyncSession = Depends(get_session)):
    await session.execute(delete(Candidate))
    await session.commit()
    return {"message": "All candidates cleared"}
