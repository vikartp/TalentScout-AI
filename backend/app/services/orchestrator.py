"""
Multi-Agent Orchestrator — LangGraph-powered workflow that runs the full
TalentScout pipeline end-to-end:

  Supervisor → JD Parser → Resume Processor → Matching Engine
            → Conversation Agent → Shortlist Ranker → END

Each specialist agent wraps the existing service functions as LangGraph nodes,
so all existing manual flows keep working unchanged.

Architecture: Sequential multi-agent pipeline using LangGraph StateGraph.
A supervisor node starts the pipeline, then each specialist agent executes
in sequence, with error-aware short-circuiting at each step.
"""

import json
import operator
import os
import tempfile
import zipfile
from typing import TypedDict, Annotated, Optional

from langgraph.graph import END, StateGraph

from app.services.jd_parser import parse_jd
from app.services.resume_parser import extract_text, parse_resume
from app.services.matching_engine import compute_match_score, generate_match_explanation
from app.services.conversation_agent import run_conversation, score_conversation
from app.services.ranking_engine import rank_candidates
from app.db.vector_store import embeddings, get_or_create_collection
from app.db.database import async_session
from app.models.jd import JobDescription
from app.models.candidate import Candidate
from app.models.match import MatchResult
from app.models.conversation import Conversation

from sqlmodel import select, delete


# ---------------------------------------------------------------------------
# State schema shared across all agents
# ---------------------------------------------------------------------------
class PipelineState(TypedDict):
    """Typed state flowing through the multi-agent graph.

    `steps_log` uses an Annotated reducer (operator.add) so each agent
    can return new log entries that get APPENDED to the existing list
    instead of replacing it.
    """
    raw_jd_text: str
    zip_path: str
    jd_id: Optional[int]
    jd_parsed: dict
    candidate_ids: list[int]
    match_results: list[dict]
    conversation_results: list[dict]
    shortlist: list[dict]
    current_step: str
    steps_log: Annotated[list[str], operator.add]
    error: str


# ---------------------------------------------------------------------------
# Supervisor Node — orchestrates the pipeline
# ---------------------------------------------------------------------------
def supervisor_node(state: PipelineState) -> dict:
    """Supervisor agent: initializes the pipeline and coordinates specialists."""
    return {"steps_log": ["🧠 Supervisor: Dispatching work to specialist agents..."], "current_step": "supervising"}


# ---------------------------------------------------------------------------
# Agent 1: JD Parser
# ---------------------------------------------------------------------------
async def jd_parser_agent(state: PipelineState) -> dict:
    """Parse the raw JD text and persist to DB."""
    if state.get("error"):
        return {}

    logs = ["🔍 Agent 1 (JD Parser): Parsing Job Description with AI..."]
    try:
        parsed = await parse_jd(state["raw_jd_text"])

        async with async_session() as session:
            jd = JobDescription(
                raw_text=state["raw_jd_text"],
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
            jd_id = jd.id

        logs.append(f"✅ JD parsed — \"{parsed.get('title', 'Untitled')}\" (ID: {jd_id})")
        return {"jd_id": jd_id, "jd_parsed": parsed, "steps_log": logs, "current_step": "jd_parsed"}
    except Exception as e:
        logs.append(f"❌ JD parsing failed: {e}")
        return {"error": str(e), "steps_log": logs}


# ---------------------------------------------------------------------------
# Agent 2: Resume Processor
# ---------------------------------------------------------------------------
async def resume_processor_agent(state: PipelineState) -> dict:
    """Extract resumes from the zip, parse each, embed, and persist."""
    if state.get("error"):
        return {}

    logs = ["📄 Agent 2 (Resume Processor): Extracting and processing resumes..."]
    zip_path = state["zip_path"]
    candidate_ids: list[int] = []
    collection = get_or_create_collection("resumes")

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            all_entries = zf.namelist()
            resume_files = [
                name for name in all_entries
                if (name.lower().endswith(".pdf") or name.lower().endswith(".docx"))
                and not name.startswith("__MACOSX") and not os.path.basename(name).startswith(".")
            ]

            logs.append(f"   Found {len(resume_files)} resume(s) in ZIP (total entries: {len(all_entries)})")

            if not resume_files:
                if all_entries:
                    logs.append(f"   ⚠️ ZIP contains these files: {', '.join(all_entries[:20])}")
                    logs.append("   ❌ No .pdf or .docx files found — please re-upload a ZIP containing resumes")
                else:
                    logs.append("   ❌ ZIP file is empty — please create a ZIP with PDF/DOCX resume files")
                return {"error": "No resume files (PDF/DOCX) found in the uploaded ZIP", "steps_log": logs}

            for filename in resume_files:
                basename = os.path.basename(filename)
                tmp_path = None
                try:
                    suffix = ".pdf" if basename.lower().endswith(".pdf") else ".docx"
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                        tmp.write(zf.read(filename))
                        tmp_path = tmp.name

                    resume_text = await extract_text(tmp_path, basename)
                    parsed = await parse_resume(resume_text)

                    async with async_session() as session:
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
                            filename=basename,
                        )
                        session.add(candidate)
                        await session.commit()
                        await session.refresh(candidate)
                        cand_id = candidate.id

                    # Embed into ChromaDB
                    emb = embeddings.embed_query(resume_text)
                    collection.upsert(
                        ids=[str(cand_id)],
                        embeddings=[emb],
                        metadatas=[{"candidate_id": cand_id, "name": parsed.get("name", "Unknown")}],
                        documents=[resume_text],
                    )

                    candidate_ids.append(cand_id)
                    logs.append(f"   ✅ Processed: {parsed.get('name', basename)}")

                except Exception as e:
                    logs.append(f"   ⚠️ Failed to process {basename}: {e}")
                finally:
                    if tmp_path and os.path.exists(tmp_path):
                        os.remove(tmp_path)

        logs.append(f"✅ {len(candidate_ids)} candidate(s) processed and embedded")
        return {"candidate_ids": candidate_ids, "steps_log": logs, "current_step": "resumes_processed"}
    except Exception as e:
        logs.append(f"❌ Resume processing failed: {e}")
        return {"error": str(e), "steps_log": logs}


# ---------------------------------------------------------------------------
# Agent 3: Matching Engine
# ---------------------------------------------------------------------------
async def matching_agent(state: PipelineState) -> dict:
    """Run match scoring for every candidate against the JD."""
    if state.get("error"):
        return {}

    logs = ["🎯 Agent 3 (Matching Engine): Computing match scores..."]
    jd_id = state["jd_id"]
    jd_parsed = state["jd_parsed"]
    match_results = []

    try:
        async with async_session() as session:
            jd = await session.get(JobDescription, jd_id)
            if not jd:
                logs.append("❌ JD not found in DB")
                return {"error": "JD not found", "steps_log": logs}

            # Delete previous match results for this JD
            await session.execute(delete(MatchResult).where(MatchResult.jd_id == jd_id))
            await session.flush()

            for cand_id in state["candidate_ids"]:
                candidate = await session.get(Candidate, cand_id)
                if not candidate:
                    continue

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
                    jd_id=jd_id,
                    candidate_id=cand_id,
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
                    "candidate_id": cand_id,
                    "candidate_name": candidate.name,
                    **scores,
                    "explanation": explanation,
                })
                logs.append(f"   ✅ Matched: {candidate.name} → Score: {scores['match_score']}")

            await session.commit()

        logs.append(f"✅ Matching complete for {len(match_results)} candidate(s)")
        return {"match_results": match_results, "steps_log": logs, "current_step": "matching_done"}
    except Exception as e:
        logs.append(f"❌ Matching failed: {e}")
        return {"error": str(e), "steps_log": logs}


# ---------------------------------------------------------------------------
# Agent 4: Conversation Agent
# ---------------------------------------------------------------------------
async def conversation_agent_node(state: PipelineState) -> dict:
    """Simulate outreach conversations with all candidates."""
    if state.get("error"):
        return {}

    logs = ["💬 Agent 4 (Conversation Agent): Engaging all candidates..."]
    jd_id = state["jd_id"]
    jd_parsed = state["jd_parsed"]
    conversation_results = []

    try:
        async with async_session() as session:
            jd = await session.get(JobDescription, jd_id)
            if not jd:
                logs.append("❌ JD not found")
                return {"error": "JD not found", "steps_log": logs}

            for cand_id in state["candidate_ids"]:
                candidate = await session.get(Candidate, cand_id)
                if not candidate:
                    continue

                # Get match highlights
                result = await session.execute(
                    select(MatchResult).where(
                        MatchResult.jd_id == jd_id,
                        MatchResult.candidate_id == cand_id,
                    )
                )
                match = result.scalars().first()
                match_highlights = match.explanation if match else "Based on resume review, this candidate appears to be a good fit."

                cand_parsed = json.loads(candidate.parsed_json) if candidate.parsed_json else {}
                profile_summary = f"""Name: {candidate.name}
Current Role: {candidate.current_role or 'N/A'} at {candidate.current_company or 'N/A'}
Experience: {candidate.total_experience_years or 'N/A'} years
Skills: {', '.join(cand_parsed.get('skills', [])[:10])}"""

                jd_summary = f"""Title: {jd.title}
Seniority: {jd_parsed.get('seniority', 'N/A')}
Key Skills: {', '.join(jd_parsed.get('skills_must_have', [])[:5])}
Location: {jd_parsed.get('location', 'N/A')}"""

                logs.append(f"   🗣️ Engaging: {candidate.name}...")

                transcript = await run_conversation(
                    jd_title=jd.title or "Open Role",
                    jd_summary=jd_summary,
                    candidate_name=candidate.name,
                    candidate_profile=profile_summary,
                    match_highlights=match_highlights,
                )

                scores = await score_conversation(transcript, jd.title or "Open Role")

                convo = Conversation(
                    jd_id=jd_id,
                    candidate_id=cand_id,
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

                conversation_results.append({
                    "candidate_id": cand_id,
                    "candidate_name": candidate.name,
                    "interest_score": scores["interest_score"],
                })
                logs.append(f"   ✅ Conversation complete: {candidate.name} → Interest: {scores['interest_score']}")

            await session.commit()

        logs.append(f"✅ Conversations complete for {len(conversation_results)} candidate(s)")
        return {"conversation_results": conversation_results, "steps_log": logs, "current_step": "conversations_done"}
    except Exception as e:
        logs.append(f"❌ Conversations failed: {e}")
        return {"error": str(e), "steps_log": logs}


# ---------------------------------------------------------------------------
# Agent 5: Shortlist Ranker
# ---------------------------------------------------------------------------
async def shortlist_agent(state: PipelineState) -> dict:
    """Combine all scores and produce the final ranked shortlist."""
    if state.get("error"):
        return {}

    logs = ["🏆 Agent 5 (Ranking Engine): Computing final rankings..."]
    jd_id = state["jd_id"]

    try:
        async with async_session() as session:
            jd = await session.get(JobDescription, jd_id)
            match_result = await session.execute(
                select(MatchResult).where(MatchResult.jd_id == jd_id)
            )
            matches = match_result.scalars().all()

            candidates_data = []
            for m in matches:
                candidate = await session.get(Candidate, m.candidate_id)
                if not candidate:
                    continue

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
                    "interest_score": convo.interest_score if convo else 0,
                })

        ranked = rank_candidates(candidates_data)

        logs.append("✅ Final shortlist ready!")
        for idx, c in enumerate(ranked[:5]):
            logs.append(
                f"   #{idx+1} {c['name']} — Final: {c['final_score']} "
                f"(Match: {c['match_score']}, Interest: {c.get('interest_score', 0)})"
            )

        return {"shortlist": ranked, "current_step": "completed", "steps_log": logs}
    except Exception as e:
        logs.append(f"❌ Ranking failed: {e}")
        return {"error": str(e), "steps_log": logs}


# ---------------------------------------------------------------------------
# Build the LangGraph workflow — Sequential multi-agent pipeline
# ---------------------------------------------------------------------------
def build_pipeline():
    """Build and compile the multi-agent LangGraph pipeline.

    Uses direct sequential edges:
      supervisor → jd_parser → resume_processor → matching
               → conversation → shortlist → END

    This ensures each agent runs exactly once in order, eliminating
    any possibility of infinite loops while still demonstrating a
    proper multi-agent LangGraph architecture with shared state.
    """
    workflow = StateGraph(PipelineState)

    # Add all agent nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("jd_parser", jd_parser_agent)
    workflow.add_node("resume_processor", resume_processor_agent)
    workflow.add_node("matching", matching_agent)
    workflow.add_node("conversation", conversation_agent_node)
    workflow.add_node("shortlist", shortlist_agent)

    # Sequential pipeline: each agent feeds into the next
    workflow.set_entry_point("supervisor")
    workflow.add_edge("supervisor", "jd_parser")
    workflow.add_edge("jd_parser", "resume_processor")
    workflow.add_edge("resume_processor", "matching")
    workflow.add_edge("matching", "conversation")
    workflow.add_edge("conversation", "shortlist")
    workflow.add_edge("shortlist", END)

    return workflow.compile()


# Singleton compiled graph
pipeline = build_pipeline()


async def run_full_pipeline(raw_jd_text: str, zip_path: str, run_id: Optional[str] = None) -> PipelineState:
    """Execute the full multi-agent pipeline end-to-end with real-time websocket updates."""
    from app.services.ws_manager import manager
    
    initial_state: PipelineState = {
        "raw_jd_text": raw_jd_text,
        "zip_path": zip_path,
        "jd_id": None,
        "jd_parsed": {},
        "candidate_ids": [],
        "match_results": [],
        "conversation_results": [],
        "shortlist": [],
        "current_step": "starting",
        "steps_log": ["🚀 Multi-Agent Autopilot Pipeline started!"],
        "error": "",
    }

    final_state = initial_state

    # Optional: Initial WS ping
    if run_id:
        await manager.send_json({
            "type": "state_update", 
            "steps_log": final_state["steps_log"],
            "candidates_processed": 0,
            "error": ""
        }, run_id)

    # Stream the full state after each node completes
    async for state_event in pipeline.astream(initial_state, stream_mode="values", config={"recursion_limit": 100}):
        final_state = state_event

        if run_id:
            await manager.send_json({
                "type": "state_update",
                "steps_log": final_state.get("steps_log", []),
                "candidates_processed": len(final_state.get("candidate_ids", [])),
                "error": final_state.get("error", ""),
            }, run_id)

    return final_state
