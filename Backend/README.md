# 🎯 Mock Interview Backend

AI-powered backend for a Mock Interview Platform. Accepts resumes and job descriptions, generates personalized interview questions using LLMs, evaluates answers, computes scores, and produces PDF reports.

---

## ✨ Features

| Module | Description |
|---|---|
| Resume Parser | PDF / DOCX / TXT parsing + LLM-structured extraction |
| JD Parser | File upload or raw text + LLM structuring |
| Question Bank | 300+ curated questions (HR, Technical, Telephonic, Virtual) |
| AI Question Generator | Personalized questions using candidate profile + JD |
| Interview Generator | 40% bank + 60% AI mixed question set |
| Session Manager | State machine: Created → Running → Completed |
| Answer Evaluator | Per-answer LLM scoring (0-10) with 4 dimensions |
| Feedback Generator | Per-answer and session-level coaching feedback |
| Score Engine | Weighted multi-dimensional scoring + hire recommendation |
| Report Generator | Downloadable PDF with full interview breakdown |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- MongoDB 7.x (local or Docker)
- OpenRouter API Key (free tier available at https://openrouter.ai)

### 1. Clone and Install

```bash
git clone <repo>
cd Backend

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and fill in:
#   OPENROUTER_API_KEY=your_key_here
#   MONGODB_URL=mongodb://localhost:27017
```

### 3. Start MongoDB

```bash
# Option A: Docker
docker run -d -p 27017:27017 --name mongo mongo:7

# Option B: Use Docker Compose (starts everything)
docker-compose up -d
```

### 4. Seed Question Bank

```bash
python scripts/seed_questions.py
```

### 5. Run the API

```bash
uvicorn main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

---

## 🐳 Docker Deployment

```bash
# Copy and fill .env
cp .env.example .env

# Build and start all services
docker-compose up --build -d

# View logs
docker-compose logs -f api

# Seed questions (first time only)
docker-compose exec api python scripts/seed_questions.py
```

---

## 📡 API Reference

### Base URL: `http://localhost:8000/api/v1`

#### Resume
| Method | Endpoint | Description |
|---|---|---|
| POST | `/resume/upload` | Upload PDF/DOCX/TXT resume |
| GET | `/resume/{id}` | Get parsed resume |

#### Job Description
| Method | Endpoint | Description |
|---|---|---|
| POST | `/jd/upload` | Upload JD file |
| POST | `/jd/raw` | Submit raw text JD |
| GET | `/jd/{id}` | Get parsed JD |

#### Interview
| Method | Endpoint | Description |
|---|---|---|
| POST | `/interview/generate` | Generate interview questions |
| GET | `/interview/{session_id}` | Get interview details |

#### Session
| Method | Endpoint | Description |
|---|---|---|
| POST | `/session/{id}/start` | Start session |
| POST | `/session/{id}/end` | End session |
| GET | `/session/{id}` | Get session state |

#### Answer
| Method | Endpoint | Description |
|---|---|---|
| POST | `/answer/submit` | Submit answer (triggers LLM eval) |
| GET | `/answer/session/{id}` | Get all answers for session |

#### Report
| Method | Endpoint | Description |
|---|---|---|
| GET | `/report/{session_id}` | Download PDF report |
| GET | `/report/{session_id}/json` | Get report as JSON |

---

## 🔄 Complete Interview Flow

```
1. POST /resume/upload              → resume_id
2. POST /jd/upload (or /jd/raw)    → jd_id
3. POST /interview/generate         → session_id + questions
4. POST /session/{id}/start         → status: running
5. POST /answer/submit × N          → score + feedback per answer
6. POST /session/{id}/end           → status: completed
7. GET  /report/{id}                → PDF download
```

---

## 🤖 LLM Configuration

The platform uses [OpenRouter](https://openrouter.ai) to access LLMs.

```env
OPENROUTER_API_KEY=your_key
OPENROUTER_MODEL=deepseek/deepseek-r1        # Primary (free)
OPENROUTER_FALLBACK_MODEL=qwen/qwen3-32b     # Fallback (free)
```

Automatic retry: 3 attempts with exponential backoff on rate limits / server errors.

---

## 📊 Scoring Formula

```
overall_score =
  technical_score      * 0.35 +
  communication_score  * 0.25 +
  problem_solving_score* 0.25 +
  project_score        * 0.15

Recommendation:
  8.5–10.0 → STRONG HIRE
  7.0–8.4  → HIRE
  5.5–6.9  → MAYBE
  0.0–5.4  → NO HIRE
```

---

## 🧪 Testing

```bash
# Run all tests with coverage
pytest tests/ -v --cov=app --cov-report=term-missing

# Run only unit tests
pytest tests/unit/ -v

# Run with HTML coverage report
pytest tests/ --cov=app --cov-report=html
```

---

## 🏗️ Architecture

```
API Layer (FastAPI routes)
    ↓
Service Layer (business logic)
    ↓
Repository Layer (Motor async)
    ↓
MongoDB

LLM Client (OpenRouter)
    ↑ used by: Evaluation, JD Parser, Question Gen, Feedback

File Parsers (pdfplumber, pymupdf, python-docx)
    ↑ used by: Resume Service, JD Service

PDF Builder (ReportLab)
    ↑ used by: Report Service
```

---

## 🔧 Environment Variables

| Variable | Default | Description |
|---|---|---|
| `OPENROUTER_API_KEY` | **required** | OpenRouter API key |
| `OPENROUTER_MODEL` | `deepseek/deepseek-r1` | Primary LLM model |
| `OPENROUTER_FALLBACK_MODEL` | `qwen/qwen3-32b` | Fallback LLM model |
| `MONGODB_URL` | `mongodb://localhost:27017` | MongoDB connection |
| `MONGODB_DB_NAME` | `mock_interview_db` | Database name |
| `MAX_FILE_SIZE_MB` | `10` | Max upload file size |
| `REPORTS_DIR` | `./generated_reports` | PDF storage directory |
| `LOG_LEVEL` | `INFO` | Logging level |
| `LOG_FORMAT` | `json` | `json` or `text` |
| `DEBUG` | `false` | Enable debug mode |

---

## 📁 Project Structure

```
app/
├── api/            # FastAPI routes (thin controllers)
├── core/           # Config, logging, exceptions, security
├── database/       # Motor client + index definitions
├── models/         # Pure domain models
├── schemas/        # Pydantic V2 request/response schemas
├── repositories/   # DB access layer (Motor)
├── services/       # Business logic
├── parsers/        # File text extractors
├── llm/            # OpenRouter client + JSON parser
├── prompts/        # All LLM prompt templates
├── reports/        # ReportLab PDF builder
└── utils/          # File, ID, and validation utilities
scripts/            # Seed scripts
tests/              # Unit + integration tests
```

---

## 🗺️ Roadmap (V2)

- [ ] Voice interview support (WebSockets + STT)
- [ ] Real-time conversation mode
- [ ] Coding execution engine
- [ ] Panel interview personas
- [ ] Video processing
- [ ] Async answer evaluation (background queue)
- [ ] User authentication (JWT)
- [ ] Dashboard with historical sessions
