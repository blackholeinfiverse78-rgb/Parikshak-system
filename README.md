# 🤖 Live Task Review Agent

> **Autonomous requirement-matching evaluation system** — reviews GitHub repositories against task requirements extracted from title, description, and PDF documentation. Produces deterministic, measurable scores with structured feedback and Vaani TTS audio readback.

---

## 🚀 Quick Start

### Backend (FastAPI)

```bash
cd "Live Task Review Agent - 1"
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- API: `http://localhost:8000`
- Swagger Docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

### Frontend (React)

```bash
cd frontend
npm install
npm start
```

- UI: `http://localhost:3000`

### Environment

Copy `.env` to project root and set:

```env
GITHUB_TOKEN=ghp_...         # GitHub API token — avoids 60 req/hr rate limit
GROQ_API_KEY=gsk_...         # (Optional) Enables TTS translation via Groq LLM
```

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         React Frontend                          │
│  Submit Task → Review Result → Next Task → History              │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTP / multipart form
┌─────────────────────────▼───────────────────────────────────────┐
│                   FastAPI Backend (port 8000)                   │
│  /lifecycle/submit  →  ProductOrchestrator                      │
│  /lifecycle/review  →  ReviewRecord (in-memory)                 │
│  /lifecycle/next    →  NextTaskRecord                           │
│  /lifecycle/history →  All submissions                          │
│  /tts/speak         →  Vaani TTS (gTTS + pyttsx3)              │
└───────────┬───────────────────────────────────┬─────────────────┘
            │                                   │
┌───────────▼──────────┐           ┌────────────▼──────────────┐
│  EvaluationEngine    │           │  VaaniTTS Standalone       │
│  v5.1 (5-Step)       │           │  text_to_speech_stream()   │
└───────────┬──────────┘           │  prosody_mapper            │
            │                      └────────────────────────────┘
  ┌─────────▼──────────────────────────┐
  │  Step 1: IntentExtractor           │ Title + Desc + PDF
  │  Step 2: RepositoryAnalyzer        │ GitHub API (authenticated)
  │  Step 3: FeatureMatcher.compute_match() │ Multi-signal matching
  │  Step 4: ScoringEngine v3.0        │ 5-dimension weighted score
  │  Step 5: Missing Feature Detection │ Gap analysis
  └────────────────────────────────────┘
```

---

## 📐 Scoring Model (v3.0)

The scoring engine uses **requirement-matching** as its primary driver, not text length or keyword presence. Each submission is scored across 5 weighted dimensions:

| # | Dimension | Weight | What It Measures |
|---|-----------|--------|-----------------|
| 1 | **Requirement Match** | **40 pts** | How closely the repo implements the features, tech stack, and architecture specified in the task |
| 2 | **Repository Completeness** | **20 pts** | File/directory count relative to task complexity |
| 3 | **Architecture Quality** | **20 pts** | Layer separation, modularity, interface usage |
| 4 | **Code Quality** | **10 pts** | README depth, documentation density |
| 5 | **PDF Documentation Alignment** | **10 pts** | Depth of explanation, architecture description, feature listing |

**Total: 100 points**

### Score → Status Mapping

| Score | Status |
|-------|--------|
| ≥ 80 | ✅ **PASS** |
| 50–79 | ⚠️ **BORDERLINE** |
| < 50 | ❌ **FAIL** |

---

## 🔬 Evaluation Pipeline (Step-by-Step)

### Step 1 — Requirement Extraction

**Service**: `IntentExtractor`

Combines `task_title` + `task_description` + `pdf_text` into a unified requirement model:

```json
{
  "task_objective": "...",
  "expected_features": ["authentication", "REST API", "database"],
  "expected_modules": ["auth", "routes", "models"],
  "expected_tech_stack": ["fastapi", "python", "postgresql"],
  "expected_architecture": "layered",
  "expected_complexity": "medium"
}
```

### Step 2 — Repository Analysis

**Service**: `RepositoryAnalyzer`

Calls the GitHub API (authenticated via `GITHUB_TOKEN`):

```json
{
  "structure": { "total_files": 34, "languages": { "py": 18, "js": 12 } },
  "components": { "routes": [...], "services": [...], "models": [...] },
  "architecture": { "has_layers": true, "layer_count": 4, "modular": true },
  "quality": { "readme_score": 3, "documentation_density": 0.22 }
}
```

### Step 3 — Requirement Matching

**Service**: `FeatureMatcher.compute_match()`

Computes three ratios:

| Metric | Formula | Weight in Req Score |
|--------|---------|---------------------|
| `feature_match_ratio` | matched features / expected features | 60% |
| `tech_stack_match` | matched stack / expected stack | 20% |
| `architecture_match` | repo arch matches expected pattern | 20% |

Final `req_match_ratio = (feature * 0.6) + (stack * 0.2) + (arch * 0.2)`

### Step 4 — Score Calculation

**Service**: `ScoringEngine.calculate_final_score()`

```python
req_match_score     = req_match_ratio * 40
completeness_score  = completeness_ratio * 20
architecture_score  = architecture_ratio * 20
quality_score       = quality_ratio * 10
doc_align_score     = doc_ratio * 10
total = req_match_score + completeness_score + architecture_score + quality_score + doc_align_score
```

### Step 5 — Missing Features

The `missing_features` list is derived directly from Step 3 — any expected feature not found in the repository's file tree or component analysis.

---

## 🔊 TTS Integration (Vaani TTS Standalone)

The evaluation results can be read aloud using the integrated **Vaani TTS** service.

### Endpoint

```
GET /api/v1/tts/speak?text=<text>&lang=en&tone=neutral
```

Returns `audio/mpeg` (MP3 from gTTS) or falls back to `audio/wav` (pyttsx3 offline).

### Prosody Hints

```
GET /api/v1/tts/prosody?text=<text>&lang=ar&tone=educational
```

Returns pitch, speed, and emphasis metadata for the Vaani RL-TTS prosody system.

### Frontend Usage

- **🔊 Listen** button appears on the **Evaluation Summary**
- **🔊 Listen** button on each **Strategic Hint**
- Plays inline — no page reload required

---

## 📡 API Reference

### Submit Task

```http
POST /api/v1/lifecycle/submit
Content-Type: multipart/form-data

task_title        : string (5–100 chars)
task_description  : string (10–100000 chars)
submitted_by      : string (2–50 chars)
github_repo_link  : string (GitHub URL)
pdf_file          : file (optional, .pdf)
previous_task_id  : string (optional)
```

**Response:**

```json
{
  "submission_id": "sub-abc123",
  "review_summary": { "score": 72, "status": "borderline", "readiness_percent": 72 },
  "next_task_summary": { "task_id": "...", "task_type": "advancement", "title": "...", "difficulty": "intermediate" }
}
```

### Get Full Review

```http
GET /api/v1/lifecycle/review/{submission_id}
```

**Response fields:**

| Field | Type | Description |
|-------|------|-------------|
| `score` | int | Total score (0–100) |
| `requirement_match` | float | Ratio of matched requirements (0.0–1.0) |
| `architecture_score` | float | Architecture quality sub-score (0–20) |
| `completeness_score` | float | File completeness sub-score (0–20) |
| `code_quality_score` | float | Code quality sub-score (0–10) |
| `documentation_score` | float | PDF documentation sub-score (0–10) |
| `documentation_alignment` | string | `high` / `moderate` / `low` |
| `missing_features` | list | Features required but not found in repo |
| `evaluation_summary` | string | Human-readable verdict sentence |
| `improvement_hints` | list | Actionable next steps |
| `analysis_pdf` | object | Extracted PDF insights (stack, features, arch) |

---

## 🏗️ Project Structure

```
Live Task Review Agent - 1/
├── app/
│   ├── api/
│   │   ├── lifecycle.py          # Main submit/review/history/next endpoints
│   │   └── tts.py                # Vaani TTS /speak and /prosody endpoints
│   ├── models/
│   │   ├── schemas.py            # Pydantic models (Task, ReviewOutput, etc.)
│   │   └── persistent_storage.py # In-memory storage (TaskSubmission, ReviewRecord)
│   └── services/
│       ├── evaluation_engine.py  # Pipeline orchestrator (Steps 1–5)
│       ├── intent_extractor.py   # Step 1: extract requirements from all inputs
│       ├── repository_analyzer.py # Step 2: GitHub repo signals via API
│       ├── feature_matcher.py    # Step 3: compute_match() — requirement matching
│       ├── scoring_engine.py     # Step 4: ScoringEngine v3.0 — 5-dimension scoring
│       ├── pdf_analyzer.py       # PDF text extraction and analysis
│       ├── review_engine.py      # Bridge: maps EvaluationEngine → ReviewOutput schema
│       └── product_orchestrator.py # Full lifecycle: submit → review → next task
├── VaaniTTS_Standalone/
│   ├── tts_service.py            # gTTS + pyttsx3 TTS engine
│   └── prosody_mapper.py         # Language/tone → prosody hints
├── frontend/
│   └── src/
│       ├── pages/                # Dashboard, SubmitTask, ReviewResult, etc.
│       ├── components/
│       │   ├── ReviewResultCard.js  # Score display with TTS buttons
│       │   ├── TtsButton.js         # 🔊 Listen inline audio component
│       │   └── PdfAnalysisCard.js   # PDF insights display
│       └── services/taskService.js  # API client + TTS URL builder
├── docs/                         # Additional documentation
├── .env                          # GITHUB_TOKEN, GROQ_API_KEY
└── requirements.txt
```

---

## 🧪 Testing Scenarios

| Scenario | Title | GitHub Repo | Expected Score Range |
|----------|-------|-------------|---------------------|
| **Strong Match** | Matches repo purpose exactly | Active repo with matching stack | 70–90 |
| **Partial Match** | Vague title, specific desc | Partially matching repo | 40–65 |
| **No Match** | Unrelated task | Unrelated repo | 5–30 |
| **No Repo** | Any | Empty / no URL | Architecture+Quality only |
| **With PDF** | Any | Any | +10 pts if PDF is detailed |

---

## 🔒 Security & Reliability

- **Deterministic**: Same inputs always produce the same score
- **GitHub Auth**: Authenticated via `GITHUB_TOKEN` (5000 req/hr vs 60 unauthenticated)
- **Graceful Fallback**: If GitHub is unreachable, scores from Title+Desc+PDF still apply
- **Pydantic Validation**: All inputs strictly validated before evaluation
- **CORS**: Configurable via `ALLOWED_ORIGINS` environment variable
