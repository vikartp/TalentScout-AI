# TalentScout AI — Backend

FastAPI backend powering JD parsing, resume processing, candidate matching, conversational outreach, and shortlist ranking.

## Setup

```bash
cd backend
cp .env.example .env   # then edit with your API keys
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## Environment Variables

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | OpenAI-compatible API key |
| `OPENAI_API_BASE` | API base URL (default: `https://api.openai.com/v1`) |
| `DATABASE_URL` | SQLite connection string (default: `sqlite+aiosqlite:///./talentscout.db`) |
| `CHROMA_PERSIST_DIR` | ChromaDB storage path (default: `./chroma_db`) |
| `EMBEDDING_MODEL` | Embedding model name (default: `text-embedding-3-large`) |
| `CHAT_MODEL` | Chat model name (default: `gpt-4o`) |

## API Endpoints

### Health & Admin

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `DELETE` | `/api/reset` | Drop and recreate all database tables |

### Job Descriptions — `/api/jd`

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/jd/parse` | Parse a JD text via LLM and store it |
| `GET` | `/api/jd/` | List all JDs (id, title, seniority, location) |
| `GET` | `/api/jd/{jd_id}` | Get full JD detail |
| `DELETE` | `/api/jd/clear` | Clear all JD records |

### Candidates — `/api/candidates`

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/candidates/upload` | Upload resumes (PDF/DOCX), parse via LLM, store embeddings |
| `GET` | `/api/candidates/` | List all candidates |
| `GET` | `/api/candidates/{id}` | Get full candidate detail |
| `DELETE` | `/api/candidates/clear` | Clear all candidates and embeddings |

### Matching — `/api/matching`

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/matching/run` | Run matching for a JD against all candidates |
| `GET` | `/api/matching/results/{jd_id}` | Get stored match results with score breakdown |
| `DELETE` | `/api/matching/clear` | Clear all match results |

### Conversations — `/api/conversations`

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/conversations/start` | Simulate recruiter-candidate conversation and score interest |
| `GET` | `/api/conversations/{id}` | Get conversation transcript and scores |
| `GET` | `/api/conversations/by-jd/{jd_id}` | List all conversations for a JD |
| `DELETE` | `/api/conversations/clear` | Clear all conversations |

### Shortlist — `/api/shortlist`

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/shortlist/{jd_id}` | Ranked shortlist combining match and interest scores |

> Query param: `match_weight` (0–1, default 0.6) controls the match vs interest balance.

## Data Models

### JobDescription
`id`, `raw_text`, `title`, `department`, `seniority`, `skills_must_have`, `skills_nice_to_have`, `experience_min/max`, `education`, `location`, `responsibilities`, `salary_min/max`, `parsed_json`, `created_at`

### Candidate
`id`, `name`, `email`, `phone`, `current_role`, `current_company`, `skills`, `total_experience_years`, `education`, `work_history`, `achievements`, `resume_text`, `parsed_json`, `filename`, `created_at`

### MatchResult
`id`, `jd_id`, `candidate_id`, `semantic_score`, `skill_score`, `experience_score`, `education_score`, `match_score`, `explanation`, `matched_skills`, `missing_skills`, `created_at`

### Conversation
`id`, `jd_id`, `candidate_id`, `transcript`, `interest_score`, `enthusiasm`, `availability`, `salary_alignment`, `cultural_fit`, `score_explanation`, `status`, `created_at`

## Services

| Service | Description |
|---|---|
| `jd_parser.py` | LLM-based JD parsing into structured fields |
| `resume_parser.py` | PDF/DOCX text extraction + LLM parsing into structured candidate data |
| `matching_engine.py` | Multi-signal scoring: semantic similarity (40%), fuzzy skill match (30%), experience fit (15%), education match (15%) |
| `conversation_agent.py` | Simulates multi-turn recruiter-candidate dialogue (4 turns), then scores enthusiasm, availability, salary alignment, cultural fit |
| `ranking_engine.py` | Combines match_score and interest_score with configurable weights (default 60/40) into final ranked shortlist |

## Data Flow

```
Upload Resume → extract text → parse via LLM → store Candidate + embedding in ChromaDB

Parse JD → parse via LLM → store JobDescription

Run Matching (for a JD)
  → For each candidate: semantic + skill + experience + education scoring
  → LLM generates match explanation
  → Store MatchResult (replaces previous results for same JD)

Start Conversation (JD + Candidate)
  → LLM simulates 4-turn recruiter-candidate dialogue
  → LLM scores the transcript for interest signals
  → Store Conversation with scores

Get Shortlist (for a JD)
  → Fetch MatchResults + Conversations
  → Combine match_score & interest_score with configurable weights
  → Return ranked shortlist
```

## Tech Stack

- **FastAPI** + **Uvicorn** — async web framework
- **SQLModel** + **aiosqlite** — async SQLite ORM
- **ChromaDB** — persistent vector database for resume embeddings
- **OpenAI SDK** + **LangChain** — LLM calls and embedding generation
- **pdfplumber** / **python-docx** — document text extraction
