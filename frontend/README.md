# TalentScout AI — Frontend

Next.js frontend for the AI-Powered Talent Scouting & Engagement Agent — featuring a premium dark/light theme, real-time WebSocket pipeline tracking, and session-persistent Autopilot mode.

> For the full project documentation, see the [root README](../README.md).

## Setup

```bash
cd frontend
cp .env.example .env.local   # set NEXT_PUBLIC_API_URL (default: http://localhost:8000)
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend API URL |

## Pages

| Route | Page | Description |
|-------|------|-------------|
| `/` | **Dashboard** | Entry point with workflow cards, clear database button, and autopilot banner |
| `/autopilot` | **Autopilot** | One-click pipeline: JD + resume ZIP → fully automated with live WebSocket progress bar & agent log |
| `/jd` | **Job Descriptions** | Paste & parse JDs manually via LLM |
| `/candidates` | **Candidates** | Upload resumes, view parsed profiles, delete individually or clear all (with cascade) |
| `/matching` | **Matching** | Run matching against a JD, view detailed 4-signal score breakdowns |
| `/conversations` | **Conversations** | Trigger AI conversations, view transcripts & interest scores |
| `/shortlist` | **Shortlist** | Final ranked shortlist — auto-loads latest JD and expands top candidate on page visit |

## Key Features

- **Real-Time WebSocket Streaming** — Autopilot opens a `ws://` connection using `crypto.randomUUID()` as `run_id`. The LangGraph orchestrator pushes state updates after each agent node completes, instantly updating the progress bar and live log.
- **Session Persistence** — Autopilot state (JD text, file metadata, logs, completion status) is cached in `sessionStorage`. Navigating away and back restores the full state.
- **Dark/Light Theme** — Toggle via `next-themes` in the sidebar footer (dark mode default).
- **Load Sample Data** — One-click button fetches pre-packaged JD + 12 sample resumes from the backend for instant testing.
- **Auto-Expand Top Candidate** — Shortlist page auto-opens the #1 ranked candidate accordion on load.
- **Cascade Deletes** — Clearing candidates also removes their matches, conversations, and ChromaDB embeddings.

## Tech Stack

- **Next.js 16** + **React 19** — App Router, Server Components
- **TypeScript** — Full type safety
- **Tailwind CSS v4** — Utility-first styling with dark mode
- **next-themes** — Dark/light theme toggle
- **Lucide React** — Icon library
- **Native WebSocket** — Real-time pipeline streaming (no socket.io dependency)
