from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from app.api import jd, candidates, matching, conversations, shortlist
from app.db.database import create_db_and_tables, engine

app = FastAPI(
    title="TalentScout AI",
    description="AI-Powered Talent Scouting & Engagement Agent",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jd.router, prefix="/api/jd", tags=["Job Descriptions"])
app.include_router(candidates.router, prefix="/api/candidates", tags=["Candidates"])
app.include_router(matching.router, prefix="/api/matching", tags=["Matching"])
app.include_router(conversations.router, prefix="/api/conversations", tags=["Conversations"])
app.include_router(shortlist.router, prefix="/api/shortlist", tags=["Shortlist"])


@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()


@app.get("/")
def root():
    return {"message": "TalentScout AI API is running"}


@app.delete("/api/reset")
async def reset_database():
    """Drop all tables and recreate them — clears all data."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
    return {"message": "Database cleared successfully"}
