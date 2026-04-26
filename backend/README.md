# TalentScout AI — Backend

FastAPI backend powering JD parsing, resume processing, candidate matching, conversational outreach, multi-agent orchestration, and shortlist ranking — with real-time WebSocket progress streaming.

> For the full project documentation, see the [root README](../README.md).

## Setup

```bash
cd backend
cp .env.example .env   # then edit with your API keys
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | *(required)* | OpenAI-compatible API key |
| `OPENAI_API_BASE` | `https://api.openai.com/v1` | API base URL |
| `DATABASE_URL` | `sqlite+aiosqlite:///./talentscout.db` | SQLite connection string |
| `CHROMA_PERSIST_DIR` | `./chroma_db` | ChromaDB storage path |
| `EMBEDDING_MODEL` | `text-embedding-3-large` | Embedding model name |
| `CHAT_MODEL` | `gpt-4o` | Chat model name |

## API Endpoints

### Health & Admin

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `DELETE` | `/api/reset` | Drop and recreate all database tables + clear ChromaDB |

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
| `DELETE` | `/api/candidates/{id}` | Delete candidate + cascade (matches, conversations, embeddings) |
| `DELETE` | `/api/candidates/clear` | Clear all candidates + cascade all related data |

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

### Autopilot — `/api/autopilot`

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/autopilot/run` | Run full multi-agent pipeline (JD text + resume ZIP → shortlist). Accepts optional `run_id` form field to link with WebSocket. |
| `GET` | `/api/autopilot/sample-zip` | Download pre-packaged sample resumes ZIP for testing |
| `WS` | `/api/autopilot/ws/{run_id}` | WebSocket endpoint for real-time pipeline progress streaming |

## Services

| Service | File | Description |
|---|---|---|
| **JD Parser** | `services/jd_parser.py` | LLM-based JD parsing into structured fields |
| **Resume Parser** | `services/resume_parser.py` | PDF/DOCX text extraction + LLM parsing into structured candidate data |
| **Matching Engine** | `services/matching_engine.py` | Multi-signal scoring: semantic similarity (40%), fuzzy skill match (30%), experience fit (15%), education match (15%) |
| **Conversation Agent** | `services/conversation_agent.py` | Simulates multi-turn recruiter-candidate dialogue (4 turns), then scores enthusiasm, availability, salary alignment, cultural fit |
| **Ranking Engine** | `services/ranking_engine.py` | Combines match_score and interest_score with configurable weights (default 60/40) into final ranked shortlist |
| **Orchestrator** | `services/orchestrator.py` | LangGraph-powered sequential multi-agent pipeline (Supervisor → JD Parser → Resume Processor → Matching → Conversation → Shortlist) with `astream` for real-time WebSocket broadcasting |
| **WS Manager** | `services/ws_manager.py` | WebSocket connection manager — tracks active connections by `run_id` and broadcasts JSON state updates |

## Data Models

### JobDescription
`id`, `raw_text`, `title`, `department`, `seniority`, `skills_must_have`, `skills_nice_to_have`, `experience_min/max`, `education`, `location`, `responsibilities`, `salary_min/max`, `parsed_json`, `created_at`

### Candidate
`id`, `name`, `email`, `phone`, `current_role`, `current_company`, `skills`, `total_experience_years`, `education`, `work_history`, `achievements`, `resume_text`, `parsed_json`, `filename`, `created_at`

### MatchResult
`id`, `jd_id`, `candidate_id`, `semantic_score`, `skill_score`, `experience_score`, `education_score`, `match_score`, `explanation`, `matched_skills`, `missing_skills`, `created_at`

### Conversation
`id`, `jd_id`, `candidate_id`, `transcript`, `interest_score`, `enthusiasm`, `availability`, `salary_alignment`, `cultural_fit`, `score_explanation`, `status`, `created_at`

## Tech Stack

- **FastAPI** + **Uvicorn** — async web framework
- **LangGraph** — multi-agent orchestration (StateGraph with sequential edges)
- **SQLModel** + **aiosqlite** — async SQLite ORM
- **ChromaDB** — persistent vector database for resume embeddings
- **OpenAI SDK** + **LangChain** — LLM calls and embedding generation
- **pdfplumber** / **python-docx** — document text extraction
- **WebSocket** — native FastAPI WebSocket for real-time progress streaming
