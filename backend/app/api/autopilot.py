"""Autopilot API — accepts JD text + resume ZIP and runs the full multi-agent pipeline."""

import os
import tempfile
import zipfile
from pathlib import Path
from fastapi import APIRouter, File, Form, UploadFile, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, FileResponse
import asyncio

from app.services.orchestrator import run_full_pipeline
from app.services.ws_manager import manager

router = APIRouter()

# Path to sample resumes — check both local dev and Docker container locations
LOCAL_PATH = Path(__file__).resolve().parent.parent.parent.parent / "sample-data" / "resumes"
DOCKER_PATH = Path("/app/sample-data/resumes")

SAMPLE_RESUMES_DIR = DOCKER_PATH if DOCKER_PATH.exists() else LOCAL_PATH


@router.get("/sample-zip")
async def download_sample_zip():
    """Generate and return a ZIP of sample resumes for testing."""
    if not SAMPLE_RESUMES_DIR.exists():
        raise HTTPException(status_code=404, detail="Sample resumes directory not found.")

    pdfs = list(SAMPLE_RESUMES_DIR.glob("*.pdf")) + list(SAMPLE_RESUMES_DIR.glob("*.docx"))
    if not pdfs:
        raise HTTPException(status_code=404, detail="No sample resume PDFs found.")

    zip_path = os.path.join(tempfile.gettempdir(), "sample_resumes.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for pdf in pdfs:
            zf.write(str(pdf), pdf.name)

    return FileResponse(zip_path, filename="sample_resumes.zip", media_type="application/zip")

@router.websocket("/ws/{run_id}")
async def websocket_endpoint(websocket: WebSocket, run_id: str):
    await manager.connect(run_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(run_id)


@router.post("/run")
async def run_autopilot(
    jd_text: str = Form(...),
    resumes_zip: UploadFile = File(...),
    run_id: str = Form(None),
):
    """
    Accepts a JD (plain text) and a ZIP of resume PDFs/DOCXs.
    Runs the full multi-agent pipeline:
      JD Parse → Resume Process → Matching → Conversations → Shortlist
    Returns the final state including the ranked shortlist and step logs.
    """
    # Validate zip upload
    if not resumes_zip.filename or not resumes_zip.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Please upload a .zip file containing resumes (PDF/DOCX).")

    if not jd_text.strip():
        raise HTTPException(status_code=400, detail="Job Description text cannot be empty.")

    # Save uploaded zip to temp location
    zip_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
            content = await resumes_zip.read()
            tmp.write(content)
            zip_path = tmp.name

        print(f"[Autopilot] Saved ZIP: {zip_path} ({len(content)} bytes, original: {resumes_zip.filename})")

        # Run the full multi-agent pipeline
        final_state = await run_full_pipeline(jd_text.strip(), zip_path, run_id)

        return JSONResponse(content={
            "status": "completed" if not final_state.get("error") else "error",
            "jd_id": final_state.get("jd_id", 0),
            "jd_parsed": final_state.get("jd_parsed", {}),
            "candidates_processed": len(final_state.get("candidate_ids", [])),
            "shortlist": final_state.get("shortlist", []),
            "steps_log": final_state.get("steps_log", []),
            "error": final_state.get("error", ""),
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {str(e)}")
    finally:
        if zip_path and os.path.exists(zip_path):
            os.remove(zip_path)

