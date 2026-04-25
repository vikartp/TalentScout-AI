# TalentScout AI — AI-Powered Talent Scouting & Engagement Agent

An AI agent that takes a Job Description as input, discovers matching candidates from uploaded resumes, engages them conversationally to assess interest, and outputs a ranked shortlist scored on **Match Score** and **Interest Score**.

## Docker Quick Start (Recommended)

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) installed
- OpenAI-compatible API key

### Setup & Run

1. **Clone the repository**
   ```bash
   git clone https://github.com/vikartp/TalentScout-AI.git
   cd TalentScout-AI
   ```

2. **Configure backend environment**
   ```bash
   cp backend/.env.example backend/.env
   ```
   
   Edit `backend/.env` and add your API credentials:
   ```bash
   OPENAI_API_KEY=your-api-key-here
   OPENAI_API_BASE=https://api.openai.com/v1  # or your custom endpoint
   ```

3. **Start all services**
   ```bash
   docker compose up --build
   ```
   
   First run will take a few minutes to build images.

4. **Access the application**
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - Backend API: [http://localhost:8000](http://localhost:8000)
   - API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

5. **Stop services**
   ```bash
   docker compose down
   ```
   
   To also remove data volumes:
   ```bash
   docker compose down -v
   ```

### Notes
- All data (SQLite DB + ChromaDB embeddings) persists in the `backend-data` Docker volume
- Changes to code require rebuilding: `docker compose up --build`
- Logs: `docker compose logs -f backend` or `docker compose logs -f frontend`

## Local Development Setup

### Prerequisites
- Python 3.12+, [uv](https://docs.astral.sh/uv/)
- Node.js 20+
- OpenAI-compatible API key

### 1. Clone & Configure

```bash
git clone https://github.com/vikartp/TalentScout-AI.git
cd TalentScout-AI
```

Copy environment files and set your API keys:
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
```

### 2. Run Backend
```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

### 3. Run Frontend
```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Project Structure

```
├── backend/          # FastAPI + OpenAI + ChromaDB
├── frontend/         # Next.js + TypeScript + Tailwind
├── sample-data/      # Example JDs and resumes
└── docker-compose.yml
```

See [backend/README.md](backend/README.md) and [frontend/README.md](frontend/README.md) for details.

## How It Works

1. **Paste a Job Description** → AI parses it into structured requirements
2. **Upload Resumes** → AI extracts candidate profiles & generates embeddings
3. **Match** → Semantic + structured scoring ranks candidates against the JD
4. **Engage** → AI simulates outreach conversations to gauge candidate interest
5. **Shortlist** → Combined Match Score + Interest Score → ranked output
