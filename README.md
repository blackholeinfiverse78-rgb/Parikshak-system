# Live Task Review Agent

An autonomous task evaluation system that scores GitHub project submissions across three dimensions — title quality, description depth, and repository analysis — and assigns the next task based on performance.

**Stack:** FastAPI · React 18 · Tailwind CSS · gTTS (Vaani TTS) · GitHub API

---

## How It Works

1. Submit a task with a title, description, GitHub repo link, and optional PDF
2. The system evaluates it across three dimensions (100 points total)
3. A score, status, and next task assignment are returned
4. Audio feedback is available via the TTS button on the review page

### Scoring Model

| Dimension | Weight | What's Measured |
|---|---|---|
| Title Analysis | 20 pts | Technical keywords, clarity, domain relevance |
| Description Analysis | 40 pts | Content depth, technical density, structure |
| Repository Analysis | 40 pts | File structure, architecture layers, documentation |

**Score → Status:**
- 80–100 → `pass` → advancement task assigned
- 50–79 → `borderline` → reinforcement task assigned
- 0–49 → `fail` → correction task assigned

### Registry Validation

Every submission is validated against the Blueprint Registry before evaluation. The module ID and schema version must match. Invalid combinations are rejected with a stored failure record (no 404).

---

## Quick Start

### Backend

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env — add your GITHUB_TOKEN

# Start server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

API available at `http://localhost:8000` · Docs at `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm start
```

UI available at `http://localhost:3000`

### Environment Variables

```env
# Required — get from https://github.com/settings/tokens (public_repo scope)
GITHUB_TOKEN=ghp_your_token_here

# Optional — enables translation in TTS
GROQ_API_KEY=gsk_your_key_here

# Update with your deployed frontend URL
ALLOWED_ORIGINS=["http://localhost:3000"]
```

---

## API Reference

### Submit Task
```http
POST /api/v1/lifecycle/submit
Content-Type: multipart/form-data

task_title        string  required  5–100 chars
task_description  string  required  10–100000 chars
submitted_by      string  required  2–50 chars
github_repo_link  string  optional  GitHub repo URL
module_id         string  optional  default: task-review-agent
schema_version    string  optional  auto-set from module
pdf_file          file    optional  .pdf
```

Response:
```json
{
  "submission_id": "sub-abc123",
  "review_summary": { "score": 72, "status": "borderline", "readiness_percent": 72 },
  "next_task_summary": { "task_id": "next-def456", "task_type": "reinforcement", "title": "...", "difficulty": "intermediate" }
}
```

### Get Review
```http
GET /api/v1/lifecycle/review/{submission_id}
```

Returns full review with `score`, `status`, `title_score`, `description_score`, `repository_score`, `failure_reasons`, `improvement_hints`, `missing_features`, `registry_validation`.

### Get Next Task
```http
GET /api/v1/lifecycle/next/{submission_id}
```

### Submission History
```http
GET /api/v1/lifecycle/history
```

### TTS
```http
GET /api/v1/tts/speak?text=<text>&lang=en&tone=neutral
```
Returns `audio/mpeg` (MP3). Max 500 characters.

---

## Project Structure

```
├── app/
│   ├── api/
│   │   ├── lifecycle.py          # Submit, review, next task, history endpoints
│   │   └── tts.py                # Vaani TTS endpoint
│   ├── core/
│   │   └── interfaces/           # Abstract interfaces
│   ├── models/
│   │   ├── schemas.py            # Pydantic models
│   │   └── persistent_storage.py # In-memory storage
│   ├── services/
│   │   ├── final_convergence.py  # Main orchestration pipeline
│   │   ├── signal_collector.py   # Collects evaluation signals
│   │   ├── repository_analyzer.py# GitHub API analysis
│   │   ├── title_analyzer.py     # Title signal extraction
│   │   ├── description_analyzer.py# Description signal extraction
│   │   ├── feature_matcher.py    # Requirement vs implementation matching
│   │   ├── intent_extractor.py   # Expected feature extraction
│   │   ├── registry_validator.py # Blueprint Registry validation
│   │   ├── shraddha_validation.py# Output contract validation
│   │   ├── product_orchestrator.py# Storage and response assembly
│   │   ├── review_engine.py      # ReviewOutput adapter
│   │   └── pdf_analyzer.py       # PDF text extraction
│   └── main.py                   # FastAPI app entry point
├── intelligence-integration-module-main/
│   └── engine/
│       └── canonical_intelligence_engine.py  # Scoring authority
├── VaaniTTS_Standalone/
│   ├── tts_service.py            # gTTS + pyttsx3 fallback
│   └── prosody_mapper.py         # Prosody configuration
├── frontend/
│   └── src/
│       ├── pages/                # Dashboard, SubmitTask, ReviewResult, NextTask, TaskHistory
│       ├── components/           # TtsButton, ReviewResultCard, StatusBadge, etc.
│       └── services/             # apiClient, taskService
├── tests/
│   └── test_bug_fixes.py         # 28 unit tests (all passing)
├── docs/                         # Architecture and deployment docs
├── .env.example                  # Environment variable reference
├── railway.toml                  # Railway deployment config
├── vercel.json                   # Vercel deployment config
├── Dockerfile                    # Container config
└── requirements.txt
```

---

## Deployment

### Railway (Backend)

1. Push to GitHub
2. Railway → New Project → Deploy from GitHub repo
3. Set environment variables in Railway dashboard:
   - `GITHUB_TOKEN`
   - `GROQ_API_KEY` (optional)
   - `ALLOWED_ORIGINS` → `["https://your-app.vercel.app"]`
4. Railway auto-detects `railway.toml` and uses the Dockerfile

### Vercel (Frontend)

1. Vercel → New Project → Import from GitHub
2. Set environment variables in Vercel dashboard:
   - `REACT_APP_API_BASE` → `https://your-railway-app.up.railway.app/api/v1`
   - `REACT_APP_BACKEND_URL` → `https://your-railway-app.up.railway.app`
3. Vercel auto-detects `vercel.json` — builds `frontend/` and handles SPA routing

---

## TTS (Vaani)

Audio feedback is generated server-side using **gTTS** (Google Text-to-Speech) with a **pyttsx3** offline fallback.

- Click the **Listen** button on any review result or improvement hint
- Supports English, Arabic, Spanish, French, German, and more
- Falls back to pyttsx3 if Google TTS is unreachable (local dev only)
- Max text length: 500 characters per request

---

## Tests

```bash
python -m pytest tests/test_bug_fixes.py -v
# 28 passed
```

Covers: repo availability logic, network failure scoring, feature matching synonyms, title signal extraction, delivery ratio defaults, failure indicator deduplication, intent extractor false positives, description analyzer normalization.

---

## Modules (Blueprint Registry)

| Module ID | Schema | Description |
|---|---|---|
| `task-review-agent` | v1.0 | General task review |
| `core-development` | v1.0 | Core system development |
| `advanced-features` | v1.0 | Advanced feature implementation |
| `system-integration` | v1.0 | System integration |
| `performance-optimization` | v1.0 | Performance tuning |
| `security-implementation` | v1.0 | Security features |
| `evaluation-engine` | v3.0 | Evaluation and scoring systems |
| `lifecycle-orchestrator` | v1.1 | Lifecycle management |

Schema version is auto-set when you select a module in the UI.
