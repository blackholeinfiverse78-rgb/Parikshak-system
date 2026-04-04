"""
Parikshak Determinism Proof — Phase 7
Minimum 5 test cases:
  TC-1: Identical input → identical output (3 runs)
  TC-2: Missing REVIEW_PACKET → HARD REJECT
  TC-3: Partial submission (no repo, thin description)
  TC-4: Full valid submission (all criteria met)
  TC-5: Failure case (repo present but empty, no proof)

Run: python -m pytest tests/test_determinism_proof.py -v
"""
import sys
import os
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.assignment_engine import assignment_engine
from app.services.production_decision_engine import production_decision_engine
from app.services.human_in_loop import human_in_loop
from app.services.task_selection_engine import task_selection_engine
from app.services.review_packet_parser import ReviewPacketParser

# ── Shared signal fixtures ────────────────────────────────────────────────

FULL_VALID_SIGNALS = {
    "repository_available": True,
    "implementation_files": 12,
    "expected_features": ["api", "auth", "database", "service", "model"],
    "implemented_features": ["api", "auth", "database", "service", "model"],
    "missing_features": [],
    "failure_indicators": [],
    "expected_vs_delivered_evidence": {
        "expected_count": 5, "delivered_count": 5,
        "delivery_ratio": 1.0, "missing_count": 0
    },
    "title_signals": {
        "technical_keywords": ["jwt", "api", "docker", "auth", "service"],
        "clarity_indicators": 0.9, "domain_relevance": 0.9
    },
    "description_signals": {
        "word_count": 200, "structure_quality": 0.8,
        "content_depth": 0.9, "technical_density": 0.2
    },
    "repository_signals": {
        "structure": {"total_files": 12},
        "architecture": {"layer_count": 3, "has_layers": True, "modular": True},
        "quality": {"readme_score": 3, "documentation_density": 0.5},
        "components": {
            "tests": ["tests/test_api.py", "tests/test_auth.py"],
            "docs": ["README.md", "docs/architecture.md"],
            "routes": ["api/routes.py"], "services": ["services/auth.py"], "models": []
        }
    },
    "domain": "backend"
}

PARTIAL_SIGNALS = {
    "repository_available": False,
    "implementation_files": 0,
    "expected_features": ["api", "auth"],
    "implemented_features": [],
    "missing_features": ["api", "auth"],
    "failure_indicators": ["repository_not_found"],
    "expected_vs_delivered_evidence": {
        "expected_count": 2, "delivered_count": 0,
        "delivery_ratio": 0.0, "missing_count": 2
    },
    "title_signals": {
        "technical_keywords": ["api"],
        "clarity_indicators": 0.6, "domain_relevance": 0.5
    },
    "description_signals": {
        "word_count": 60, "structure_quality": 0.2,
        "content_depth": 0.3, "technical_density": 0.05
    },
    "repository_signals": {},
    "domain": "backend"
}

FAILURE_SIGNALS = {
    "repository_available": True,
    "implementation_files": 1,
    "expected_features": ["api", "auth", "database"],
    "implemented_features": [],
    "missing_features": ["api", "auth", "database"],
    "failure_indicators": ["low_feature_match_ratio", "insufficient_implementation_scope"],
    "expected_vs_delivered_evidence": {
        "expected_count": 3, "delivered_count": 0,
        "delivery_ratio": 0.0, "missing_count": 3
    },
    "title_signals": {
        "technical_keywords": [],
        "clarity_indicators": 0.3, "domain_relevance": 0.2
    },
    "description_signals": {
        "word_count": 15, "structure_quality": 0.0,
        "content_depth": 0.1, "technical_density": 0.0
    },
    "repository_signals": {
        "structure": {"total_files": 1},
        "architecture": {"layer_count": 0, "has_layers": False, "modular": False},
        "quality": {"readme_score": 0, "documentation_density": 0.0},
        "components": {"tests": [], "docs": [], "routes": [], "services": [], "models": []}
    },
    "domain": "backend"
}

VALID_REVIEW_PACKET = """## ENTRY POINT

File: app/main.py Route: /api/v1/lifecycle/submit endpoint api main route app system

## CORE FLOW

Step 1 pipeline flow engine gate step step step step step step step step step step
step step step step step step step step step step step step step step step step step
step step step step step step step step step step step step step step step step step

## LIVE FLOW

Endpoint POST /api/v1/production/niyantran/submit request response http endpoint
endpoint endpoint endpoint endpoint endpoint endpoint endpoint endpoint endpoint
endpoint endpoint endpoint endpoint endpoint endpoint endpoint endpoint endpoint

## OUTPUT SAMPLE

```json
{"score": 7.2, "decision": "APPROVED", "trace_id": "abc-123-def-456"}
```
"""


# ── TC-1: Identical input → identical output (3 runs) ────────────────────

def test_tc1_determinism_3_runs():
    """Same signals → same score, status, PAC, rubric across 3 runs."""
    results = [
        assignment_engine.evaluate_and_assign(
            "JWT Authentication REST API with Docker",
            "Build JWT auth REST API with Docker deployment and service layer",
            FULL_VALID_SIGNALS
        )
        for _ in range(3)
    ]

    scores   = [r["score_10"] for r in results]
    statuses = [r["status"]   for r in results]
    pacs     = [str(r["pac"]) for r in results]
    rubrics  = [str(r["rubric"]) for r in results]

    assert len(set(scores))   == 1, f"Scores differ across runs: {scores}"
    assert len(set(statuses)) == 1, f"Statuses differ: {statuses}"
    assert len(set(pacs))     == 1, f"PAC differs: {pacs}"
    assert len(set(rubrics))  == 1, f"Rubric differs: {rubrics}"

    print(f"[TC-1 PASS] 3 runs identical: score={scores[0]} status={statuses[0]} PAC={results[0]['pac']}")


# ── TC-2: Missing REVIEW_PACKET → HARD REJECT ────────────────────────────

def test_tc2_missing_review_packet():
    """Empty directory → HARD REJECT with rejection_type=HARD_GATE_FAILURE."""
    with tempfile.TemporaryDirectory() as empty_dir:
        result = ReviewPacketParser().enforce_packet_requirement(empty_dir)

    assert result["valid"] is False
    assert result["rejection_type"] == "HARD_GATE_FAILURE"
    assert "missing" in result["reason"].lower() or "not found" in result["reason"].lower()

    print(f"[TC-2 PASS] Missing packet rejected: {result['reason']}")


# ── TC-3: Partial submission (no repo, thin description) ─────────────────

def test_tc3_partial_submission():
    """No repo, thin description → REJECTED, score < 6, caps applied."""
    result = assignment_engine.evaluate_and_assign(
        "REST API Service",
        "Build a REST API service with authentication",
        PARTIAL_SIGNALS
    )
    decision = production_decision_engine.make_decision(result, PARTIAL_SIGNALS)

    assert result["score_10"] < 6.0,          f"Expected score < 6, got {result['score_10']}"
    assert result["status"] in ("fail", "borderline")
    assert result["pac"]["code"] == 0,         "No repo → code=0"
    assert decision["decision"] == "REJECTED", f"Expected REJECTED, got {decision['decision']}"
    assert len(result["score_breakdown"]["caps_applied"]) > 0, "Caps must be applied"

    # Task selection must still work deterministically
    sel = task_selection_engine.select_next_task(result["score_10"], "REJECTED", "beginner")
    assert sel["source"] == "niyantran_task_graph"
    assert sel["next_task_id"].startswith("NT-")

    print(f"[TC-3 PASS] Partial: score={result['score_10']} caps={result['score_breakdown']['caps_applied']} next={sel['next_task_id']}")


# ── TC-4: Full valid submission ───────────────────────────────────────────

def test_tc4_full_valid_submission():
    """All criteria met → APPROVED, score ≥ 6, no caps, confidence formula correct."""
    result   = assignment_engine.evaluate_and_assign(
        "JWT Authentication REST API with Docker Deployment",
        "Build production REST API with JWT auth, Docker, service layer, tests",
        FULL_VALID_SIGNALS
    )
    decision = production_decision_engine.make_decision(result, FULL_VALID_SIGNALS)

    assert result["score_10"] >= 6.0,          f"Expected score ≥ 6, got {result['score_10']}"
    assert result["status"] == "pass"
    assert result["pac"]["proof"] == 1
    assert result["pac"]["architecture"] == 1
    assert result["pac"]["code"] == 1
    assert result["rubric"]["rubric_sum"] == 6, f"All 6 rubric criteria must be 1, got {result['rubric']['rubric_sum']}"
    assert decision["decision"] == "APPROVED"
    assert len(result["score_breakdown"]["caps_applied"]) == 0, "No caps on full valid submission"

    # Phase 3: verify confidence formula
    conf = human_in_loop.calculate_confidence(result, decision, FULL_VALID_SIGNALS)
    expected_conf = (1 + 1 + 1 + 1.0) / 4  # all PAC=1, rubric_completeness=1.0
    assert abs(conf.final_confidence - expected_conf) < 0.001, \
        f"Confidence formula wrong: expected {expected_conf}, got {conf.final_confidence}"

    # Task selection → advancement
    sel = task_selection_engine.select_next_task(result["score_10"], "APPROVED", "beginner")
    assert sel["task_type"] == "advancement"
    assert sel["source"] == "niyantran_task_graph"

    print(f"[TC-4 PASS] Full valid: score={result['score_10']} decision={decision['decision']} confidence={conf.final_confidence} next={sel['next_task_id']}")


# ── TC-5: Failure case (repo present but empty, no proof) ────────────────

def test_tc5_failure_case():
    """Repo present but empty, no proof → REJECTED, proof_cap applied, escalation triggered."""
    result   = assignment_engine.evaluate_and_assign(
        "My App",
        "I built something",
        FAILURE_SIGNALS
    )
    decision = production_decision_engine.make_decision(result, FAILURE_SIGNALS)

    assert result["score_10"] < 6.0
    assert result["pac"]["proof"] == 0,        "No README/tests -> proof=0"
    assert result["pac"]["code"] == 1,         "1 file present -> code=1 (PAC only checks file_count > 0)"
    assert result["rubric"]["Q_code"] == 0,    "Q_code=0 because file_count < 3 threshold"
    assert "proof_cap_4.0" in result["score_breakdown"]["caps_applied"]
    assert decision["decision"] == "REJECTED"
    assert len(decision["failures"]) > 0,      "Must have failure reasons"
    assert decision["root_cause"] != "",       "Must have root cause"

    # Phase 3: confidence formula — proof=0, arch=0, code=1 (1 file>0), rubric_completeness=0/6=0
    # (0 + 0 + 1 + 0) / 4 = 0.25
    conf = human_in_loop.calculate_confidence(result, decision, FAILURE_SIGNALS)
    expected_conf = (0 + 0 + result["pac"]["code"] + 0) / 4.0
    assert abs(conf.final_confidence - expected_conf) < 0.001, \
        f"Expected {expected_conf}, got {conf.final_confidence}"
    assert conf.requires_escalation is True,   "Must escalate — confidence < 0.98"

    # Task selection → correction
    sel = task_selection_engine.select_next_task(result["score_10"], "REJECTED", "beginner")
    assert sel["task_type"] == "correction"

    print(f"[TC-5 PASS] Failure: score={result['score_10']} caps={result['score_breakdown']['caps_applied']} confidence={conf.final_confidence} escalate={conf.requires_escalation}")


# ── TC-6: REVIEW_PACKET parser — parse only, no scoring ──────────────────

def test_tc6_parser_parse_only():
    """Parser must validate+extract only. Must NOT return score or status."""
    with tempfile.TemporaryDirectory() as d:
        with open(os.path.join(d, "REVIEW_PACKET.md"), "w") as f:
            f.write(VALID_REVIEW_PACKET)
        result = ReviewPacketParser().enforce_packet_requirement(d)

    assert result["valid"] is True
    assert "parsed_data" in result
    assert "confidence" in result,          "Must return confidence signal"
    assert "validation_depth" in result,    "Must return validation_depth"
    # Parser must NOT return score or status
    assert "score" not in result,           "Parser must NOT score"
    assert "status" not in result,          "Parser must NOT set status"
    assert "decision" not in result,        "Parser must NOT decide"

    print(f"[TC-6 PASS] Parser: valid={result['valid']} depth={result['validation_depth']} confidence={result['confidence']} no score/status/decision")


# ── TC-7: Task selection determinism ─────────────────────────────────────

def test_tc7_task_selection_determinism():
    """Same (score, decision, difficulty) → same next_task_id across 3 calls."""
    calls = [
        task_selection_engine.select_next_task(7.5, "APPROVED", "beginner")
        for _ in range(3)
    ]
    ids = [c["next_task_id"] for c in calls]
    assert len(set(ids)) == 1, f"Task selection not deterministic: {ids}"
    assert calls[0]["source"] == "niyantran_task_graph"

    print(f"[TC-7 PASS] Task selection deterministic: {ids[0]} × 3")


# ── Runner ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    tests = [
        test_tc1_determinism_3_runs,
        test_tc2_missing_review_packet,
        test_tc3_partial_submission,
        test_tc4_full_valid_submission,
        test_tc5_failure_case,
        test_tc6_parser_parse_only,
        test_tc7_task_selection_determinism,
    ]
    passed = failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"[FAIL] {t.__name__}: {e}")
            failed += 1
    print(f"\n{'='*60}")
    print(f"DETERMINISM PROOF: {passed}/{len(tests)} passed, {failed} failed")
    if failed == 0:
        print("ALL TESTS PASSED — SYSTEM IS DETERMINISTIC")
    print('='*60)
