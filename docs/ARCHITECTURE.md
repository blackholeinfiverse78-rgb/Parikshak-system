# 🏗️ System Architecture (v5.1)

The Live Task Review Agent is a full-stack autonomous evaluation platform. It analyzes GitHub repositories against task requirements and produces deterministic, structured feedback with audio readback.

---

## Component Overview

### 1. Frontend (React + TanStack Query)

- **Role**: Full SPA for task submission, review display, history, and next task
- **Tech**: React 18, React Router v6, TanStack Query v5, Lucide Icons, TailwindCSS
- **Key Pages**:
  - `/` — Dashboard with recent activity and stats
  - `/submit` — Task submission form (title, description, GitHub URL, optional PDF)
  - `/review/:id` — Full review result with score breakdown and 🔊 TTS playback
  - `/next/:id` — Next task recommendation
  - `/history` — Full submission history

---

### 2. Backend (FastAPI)

- **Role**: REST API, evaluation orchestration, TTS
- **Tech**: FastAPI, Pydantic v2, uvicorn, python-dotenv
- **Routers**:

  | Router | Prefix | Purpose |
  |--------|--------|---------|
  | `lifecycle.py` | `/api/v1/lifecycle` | Submit, review, history, next task |
  | `tts.py` | `/api/v1/tts` | Vaani TTS speak & prosody endpoints |
  | `task_submit.py` | `/api/v1/task` | (Legacy) direct task submission |
  | `orchestration.py` | `/api/v1/orchestration` | V2 autonomous orchestration |

---

### 3. Evaluation Engine (v5.1 — 5-Step Pipeline)

```
ProductOrchestrator.process_submission()
  └─► ReviewEngine.review_task()
        └─► EvaluationEngine.evaluate()
              ├── Step 1: IntentExtractor.extract(title, desc, pdf_text)
              │           → expected_features, expected_tech_stack, expected_architecture
              │
              ├── Step 2: RepositoryAnalyzer.analyze(github_url)
              │           → structure, components, architecture, quality
              │           (authenticated via GITHUB_TOKEN)
              │
              ├── Step 3: FeatureMatcher.compute_match(intent, repo_signals)
              │           → feature_match_ratio, tech_stack_match, architecture_match
              │           → missing_features list
              │
              ├── Step 4: ScoringEngine.calculate_final_score(...)
              │           → score (0–100), requirement_match, all sub-scores
              │           → evaluation_summary, documentation_alignment
              │
              └── Step 5: PDFAnalyzer.analyze_content(pdf_text)
                          → documented_features, architecture_description, technical_stack
```

---

### 4. Vaani TTS Standalone

Provides audio readback of evaluation results.

- **Engine**: gTTS (Google TTS) → returns MP3; pyttsx3 → WAV fallback
- **Translation**: Optional, via Groq API (`GROQ_API_KEY`) for non-English languages
- **Prosody**: `prosody_mapper.py` maps language+tone to pitch/speed/emphasis hints
- **Integration**: `app/api/tts.py` exposes REST endpoints; `TtsButton.js` in frontend plays audio inline

---

### 5. Storage Layer (In-Memory)

Three entity types stored in `ProductStorage`:

| Entity | ID Format | Key Fields |
|--------|-----------|-----------|
| `TaskSubmission` | `sub-{hex12}` | task_id, pdf_file_path, pdf_extracted_text |
| `ReviewRecord` | `rev-{hex12}` | score, requirement_match, all sub-scores, missing_features |
| `NextTaskRecord` | `next-{hex12}` | task_type, title, objective, difficulty |

> ⚠️ Storage is in-memory and resets on backend restart. Add a database adapter to `ProductStorage` for persistence.

---

## Data Flow: Full Lifecycle

```
Browser
  │
  ├─ POST /api/v1/lifecycle/submit (multipart/form-data)
  │     task_title, task_description, github_repo_link, pdf_file
  │
  ▼
ProductOrchestrator
  ├─ Creates TaskSubmission (sub-xxx)
  ├─ Calls ReviewEngine → EvaluationEngine (5 steps)
  ├─ Creates ReviewRecord (rev-xxx) with all scores
  ├─ Calls NextTaskGenerator (based on score)
  └─ Creates NextTaskRecord (next-xxx)
  │
  └─► Returns { submission_id, review_summary, next_task_summary }

Browser polls:
  GET /api/v1/lifecycle/review/{submission_id}   → Full ReviewDetailResponse
  GET /api/v1/lifecycle/next/{submission_id}     → NextTaskDetailResponse
  GET /api/v1/lifecycle/history                  → All SubmissionHistoryItems

TTS:
  GET /api/v1/tts/speak?text=...&lang=en         → MP3 audio bytes
```

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Requirement-matching over text analysis** | Text length/keyword presence doesn't correlate with implementation quality |
| **GitHub API (not clone)** | File tree analysis via API is fast, stateless, and requires no disk space |
| **gTTS over neural TTS** | Free, reliable, 30+ languages, no GPU required |
| **In-memory storage** | Zero-dependency for demos; swap to Redis/Postgres via `ProductStorage` adapter |
| **Pydantic v2** | Fast validation, strict schema enforcement, great OpenAPI generation |
| **No LLM in scoring** | Ensures full determinism — identical inputs always yield identical scores |
