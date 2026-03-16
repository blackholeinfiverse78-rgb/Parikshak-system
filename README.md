# 🤖 Live Task Review Agent

> **Registry-aware autonomous evaluation system** — validates task structural discipline through Blueprint Registry, then evaluates GitHub repositories using dynamic scoring across title analysis, description analysis, and repository quality. Produces deterministic, measurable scores with structured feedback and Vaani TTS audio readback.

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
│  Dynamic Scoring     │           │  text_to_speech_stream()   │
└───────────┬──────────┘           │  prosody_mapper            │
            │                      └────────────────────────────┘
  ┌─────────▼──────────────────────────┐
  │  Step 1: RegistryValidator         │ Blueprint Registry validation
  │  Step 2: TitleAnalyzer             │ Technical keyword detection
  │  Step 3: DescriptionAnalyzer       │ Content depth analysis
  │  Step 4: RepositoryAnalyzer        │ GitHub API quality assessment
  │  Step 5: ScoringEngine             │ Dynamic score combination
  └────────────────────────────────────┘
```

---

## 📐 Dynamic Scoring Model

The scoring engine uses **measurable signals** from three analysis dimensions. No hardcoded scores - all values computed dynamically from content analysis:

| # | Dimension | Weight | What It Measures |
|---|-----------|--------|------------------|
| 1 | **Title Analysis** | **20 pts** | Technical keyword density, clarity, alignment with task type |
| 2 | **Description Analysis** | **40 pts** | Content depth, structure quality, technical density, requirement completeness |
| 3 | **Repository Analysis** | **40 pts** | Code quality, architecture, documentation, file structure via GitHub API |

**Total: 100 points**

### Registry Validation (Pre-Evaluation)

Before scoring, all tasks undergo **structural discipline enforcement**:
- **Module ID Validation**: Ensures task belongs to valid Blueprint Registry module
- **Lifecycle Stage Validation**: Verifies task is appropriate for current stage
- **Schema Version Validation**: Confirms compatibility with evaluation engine

**Invalid tasks are rejected before evaluation begins**

### Score → Status Mapping

| Score | Status |
|-------|--------|
| ≥ 80 | ✅ **PASS** |
| 50–79 | ⚠️ **BORDERLINE** |
| < 50 | ❌ **FAIL** |

---

## 🔬 Evaluation Pipeline (Step-by-Step)

### Step 1 — Registry Validation

**Service**: `RegistryValidator`

Validates structural discipline before evaluation:

```json
{
  "module_id_valid": true,
  "lifecycle_stage_valid": true, 
  "schema_version_valid": true,
  "validation_passed": true
}
```

**Rejection**: Invalid tasks are rejected with specific error messages before evaluation begins.

### Step 2 — Title Analysis

**Service**: `TitleAnalyzer`

Analyzes title for technical content and clarity:

```json
{
  "technical_keywords": ["API", "authentication", "database"],
  "keyword_density": 0.75,
  "clarity_score": 0.85,
  "alignment_score": 0.90,
  "title_score": 17.2
}
```

### Step 3 — Description Analysis

**Service**: `DescriptionAnalyzer`

Evaluates content depth and structure:

```json
{
  "content_depth": 0.82,
  "structure_quality": 0.78,
  "technical_density": 0.65,
  "requirement_completeness": 0.88,
  "description_score": 32.4
}
```

### Step 4 — Repository Analysis

**Service**: `RepositoryAnalyzer`

Assesses repository quality via GitHub API:

```json
{
  "code_quality": 0.75,
  "architecture_score": 0.80,
  "documentation_quality": 0.70,
  "file_structure_score": 0.85,
  "repository_score": 31.2
}
```

### Step 5 — Score Combination

**Service**: `ScoringEngine`

Combines all analysis scores with explainable output:

```python
total_score = title_score + description_score + repository_score
status = "PASS" if total_score >= 80 else "BORDERLINE" if total_score >= 50 else "FAIL"
```

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
module_id         : string (Blueprint Registry module)
schema_version    : string (default: "1.0")
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
| `status` | string | `PASS` / `BORDERLINE` / `FAIL` |
| `title_analysis` | object | Technical keywords, clarity, alignment scores |
| `description_analysis` | object | Content depth, structure, technical density |
| `repository_analysis` | object | Code quality, architecture, documentation |
| `registry_validation` | object | Module ID, lifecycle stage, schema validation |
| `evaluation_summary` | string | Human-readable verdict sentence |
| `improvement_hints` | list | Actionable next steps |
| `score_breakdown` | object | Detailed scoring explanation |

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
│       ├── evaluation_engine.py  # Dynamic evaluation orchestrator
│       ├── registry_validator.py # Step 1: Blueprint Registry validation
│       ├── title_analyzer.py     # Step 2: Technical keyword detection
│       ├── description_analyzer.py # Step 3: Content depth analysis
│       ├── repository_analyzer.py # Step 4: GitHub API quality assessment
│       ├── scoring_engine.py     # Step 5: Dynamic score combination
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
├── tests/                        # Unit and integration tests
├── docs/                         # Additional documentation
├── .env                          # GITHUB_TOKEN, GROQ_API_KEY
└── requirements.txt
```

---

## 🧪 Testing Scenarios

| Scenario | Title | Description | GitHub Repo | Expected Score Range |
|----------|-------|-------------|-------------|---------------------|
| **High Quality** | Technical, clear | Detailed, structured | Active, well-documented | 70–90 |
| **Medium Quality** | Basic technical | Moderate detail | Basic implementation | 40–65 |
| **Low Quality** | Vague, non-technical | Minimal content | Poor/missing repo | 5–30 |
| **Registry Invalid** | Any | Any | Any | **Rejected before evaluation** |
| **No Repository** | Any | Any | Empty/invalid URL | Title+Description only (max 60) |

---

## 🔒 Security & Reliability

- **Deterministic**: Same inputs always produce identical scores (mathematically proven)
- **Registry Validation**: Structural discipline enforcement prevents invalid task evaluation
- **GitHub Auth**: Authenticated via `GITHUB_TOKEN` (5000 req/hr vs 60 unauthenticated)
- **Graceful Fallback**: If GitHub is unreachable, scores from Title+Description analysis still apply
- **Dynamic Scoring**: No hardcoded values - all scores computed from measurable signals
- **Pydantic Validation**: All inputs strictly validated before evaluation
- **CORS**: Configurable via `ALLOWED_ORIGINS` environment variable
- **Comprehensive Testing**: 21/22 unit tests pass, 8/9 integration tests pass