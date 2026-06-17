# MockIQ — AI-Powered Mock Interview Platform

MockIQ is a full-stack AI-powered mock interview platform built with **FastAPI** (Python) on the backend and **Next.js** (TypeScript) on the frontend, powered by **OpenRouter** free LLMs.

---

## Architecture

```
Interview/
├── Backend/        # FastAPI + MongoDB + OpenRouter LLM integration
│   ├── app/
│   │   ├── api/          # REST API routes (auth, resume, jd, interview, answer, report)
│   │   ├── core/         # Config, exceptions, logging, JWT security
│   │   ├── database/     # MongoDB connection & index setup
│   │   ├── llm/          # OpenRouter async client with retry & fallback
│   │   ├── models/       # Pydantic domain models
│   │   ├── parsers/      # PDF, DOCX, TXT text extractors
│   │   ├── prompts/      # LLM prompt templates (resume, JD, questions, evaluation)
│   │   ├── repositories/ # MongoDB CRUD repositories
│   │   ├── schemas/      # Request/response schemas
│   │   └── services/     # Business logic (evaluation, interview, feedback, scoring)
│   ├── tests/            # Unit tests (pytest)
│   └── docker-compose.yml
│
└── Frontend/       # Next.js 14 + Zustand + Axios
    ├── app/              # Pages (dashboard, upload, configure, interview, report)
    ├── components/       # Reusable UI components
    ├── services/         # Axios API client with JWT interceptors
    ├── store/            # Zustand auth state
    └── types/            # TypeScript type definitions
```

---

## Features

- 📄 **Resume Parsing** — Upload PDF/DOCX/TXT. LLM extracts name, skills, experience, education.
- 📋 **Job Description Parsing** — Paste or upload JDs. LLM extracts role, required skills, responsibilities.
- 🤖 **AI Question Generation** — Personalized 10-question interview tailored to resume + job requirements.
- 💬 **Live Interview Session** — Answer questions one by one with a countdown timer.
- 📊 **Answer Evaluation** — Real-time scoring (0-10) with category breakdown and coaching feedback.
- 📝 **Final Report** — Overall score, hire recommendation, session summary.
- 🔐 **JWT Authentication** — Secure registration/login with access + refresh tokens.
- 🐳 **Docker Compose** — One-command deployment of all services.

---

## Quick Start (Docker)

**Prerequisites:** Docker Desktop installed and running.

```bash
# Clone the repository
git clone https://github.com/VenuKXN-95/Interview.git
cd Interview

# Copy and configure environment
cp Backend/.env.example Backend/.env
# Edit Backend/.env and add your OPENROUTER_API_KEY

# Start all services (MongoDB + Backend API + Frontend)
docker compose up --build -d

# Open the app
http://localhost:3000
```

---

## Environment Variables

Create `Backend/.env` from `Backend/.env.example`:

| Variable | Description |
|---|---|
| `OPENROUTER_API_KEY` | **Required.** Get a free key at [openrouter.ai](https://openrouter.ai) |
| `OPENROUTER_MODEL` | Primary LLM model (default: `meta-llama/llama-3.3-70b-instruct:free`) |
| `OPENROUTER_FALLBACK_MODEL` | Fallback LLM model (default: `google/gemma-4-31b-it:free`) |
| `JWT_SECRET_KEY` | Secret key for signing JWT tokens |
| `MONGODB_URL` | MongoDB connection URL (auto-set in Docker) |

> **Note on Rate Limits:** OpenRouter free keys have a 50-request/day limit. Adding $10 credits unlocks 1,000 requests/day.

---

## How the LLM Works

The application uses LLMs in four specialized roles:

1. **Resume Extractor** — Reads raw resume text, extracts structured entities (name, skills, experience).
2. **JD Analyzer** — Reads job descriptions, separates required vs. preferred skills and responsibilities.
3. **Question Generator** — Creates personalized interview questions by comparing resume against JD.
4. **Answer Evaluator** — Scores answers on accuracy, completeness, relevance, and communication — and generates coaching feedback — all in a single LLM call.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, TypeScript, Zustand, Axios |
| Backend | FastAPI, Python 3.12, Pydantic v2 |
| Database | MongoDB 7 |
| LLM | OpenRouter (free models) |
| Auth | JWT (access + refresh tokens), bcrypt |
| Infrastructure | Docker, Docker Compose |
