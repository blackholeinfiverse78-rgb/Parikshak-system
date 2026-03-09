# 📡 API Contracts Reference (v5.1)

> Base URL: `http://localhost:8000/api/v1`  
> Interactive Docs: `http://localhost:8000/docs`

---

## Task Lifecycle Endpoints

### `POST /lifecycle/submit`

Submit a task for evaluation.

**Request** — `multipart/form-data`

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `task_title` | string | ✅ | 5–100 chars |
| `task_description` | string | ✅ | 10–100,000 chars |
| `submitted_by` | string | ✅ | 2–50 chars |
| `github_repo_link` | string | ✅ | Valid GitHub URL |
| `pdf_file` | file | ❌ | `.pdf` only |
| `previous_task_id` | string | ❌ | Previous submission ID |

**Response** `200 OK`

```json
{
  "submission_id": "sub-a1b2c3d4e5f6",
  "review_summary": {
    "score": 72,
    "status": "borderline",
    "readiness_percent": 72
  },
  "next_task_summary": {
    "task_id": "next-a1b2c3d4e5f6",
    "task_type": "advancement",
    "title": "Add Redis Caching Layer",
    "difficulty": "intermediate"
  }
}
```

---

### `GET /lifecycle/review/{submission_id}`

Retrieve the full review for a submission.

**Response** `200 OK`

```json
{
  "review_id": "rev-...",
  "submission_id": "sub-...",
  "score": 72,
  "readiness_percent": 72,
  "status": "borderline",
  "failure_reasons": ["Missing: authentication module", "Missing: test coverage"],
  "improvement_hints": ["Improve: authentication module", "Enhance architectural modularity"],
  "analysis": {
    "technical_quality": 75,
    "clarity": 80,
    "discipline_signals": 60
  },
  "reviewed_at": "2026-03-09T14:30:00",
  "feature_coverage": 0.65,
  "architecture_score": 14.0,
  "code_quality_score": 6.5,
  "completeness_score": 16.0,
  "missing_features": ["authentication", "test coverage", "caching"],
  "requirement_match": 0.65,
  "evaluation_summary": "Evaluation complete. Score: 72. Implemented 4/7 expected features. Requirement alignment is MODERATE. Implementation follows requirements but has some missing features or architectural gaps.",
  "documentation_score": 0.0,
  "documentation_alignment": "moderate",
  "analysis_pdf": null
}
```

**Scoring field reference:**

| Field | Range | Description |
|-------|-------|-------------|
| `score` | 0–100 | Total weighted score |
| `requirement_match` | 0.0–1.0 | Ratio of requirements satisfied |
| `architecture_score` | 0–20 | Architecture quality contribution |
| `completeness_score` | 0–20 | File completeness contribution |
| `code_quality_score` | 0–10 | README/doc density contribution |
| `documentation_score` | 0–10 | PDF documentation contribution |
| `documentation_alignment` | `high`/`moderate`/`low` | Alignment label based on req_match_ratio |

---

### `GET /lifecycle/next/{submission_id}`

Get the next recommended task after a review.

**Response** `200 OK`

```json
{
  "next_task_id": "next-...",
  "review_id": "rev-...",
  "task_type": "advancement",
  "title": "Add Rate Limiting and API Security",
  "objective": "Implement rate limiting middleware and JWT validation",
  "focus_area": "Security",
  "difficulty": "intermediate",
  "reason": "Strong score in architecture (72). Next step: harden security layer.",
  "assigned_at": "2026-03-09T14:30:05"
}
```

---

### `GET /lifecycle/history`

Get all submissions for the current session, sorted oldest-first.

**Response** `200 OK`

```json
[
  {
    "submission_id": "sub-...",
    "task_title": "Build FastAPI Review System",
    "submitted_by": "Developer",
    "submitted_at": "2026-03-09T14:00:00",
    "score": 72,
    "status": "borderline",
    "has_pdf": false
  }
]
```

---

## TTS Endpoints

### `GET /tts/speak`

Generate speech audio from text using Vaani TTS.

**Query Parameters:**

| Param | Default | Description |
|-------|---------|-------------|
| `text` | required | Text to speak (URL-encoded) |
| `lang` | `en` | Language code (`en`, `ar`, `fr`, `hi`, etc.) |
| `tone` | `neutral` | Tone (`neutral`, `educational`, `excited`) |
| `translate` | `true` | Translate text to target language (requires `GROQ_API_KEY`) |

**Response** `200 OK`  
`Content-Type: audio/mpeg` (MP3 from gTTS) or `audio/wav` (pyttsx3 fallback)

**Example:**

```
GET /api/v1/tts/speak?text=Score+is+72+out+of+100&lang=en&tone=neutral
```

---

### `GET /tts/prosody`

Get prosody hints for a given language and tone (for Vaani RL-TTS integration).

**Query Parameters:** `text`, `lang`, `tone`

**Response** `200 OK`

```json
{
  "pitch": 0.6,
  "speed": 1.0,
  "emphasis": 0.4,
  "pause_duration": 0.2,
  "prosody_hint": "educational",
  "language": "ar",
  "tone": "educational",
  "rtl": true,
  "text_length": 5,
  "word_count": 5
}
```

---

## Error Responses

All errors return JSON in this format:

```json
{ "detail": "Error message here" }
```

| Status | Cause |
|--------|-------|
| `400` | Invalid PDF file type |
| `404` | Submission / review / next task not found |
| `422` | Pydantic validation failure (field too short, etc.) |
| `500` | Internal evaluation error or TTS failure |

**Validation errors** also return the legacy schema for backward compatibility:

```json
{
  "score": 0,
  "status": "fail",
  "failure_reasons": ["Validation Failure", "task_title: ensure this value has at least 5 characters"],
  "improvement_hints": ["Ensure all fields meet length requirements (Title: 5-100, Desc: 10-2000, Name: 2-50)."]
}
```
