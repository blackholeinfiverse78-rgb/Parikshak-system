"""
Parikshak Task Selection Engine — Phase 2
Deterministic next-task selection from Niyantran task graph.

BOUNDARY RULES:
  - NO task generation — only selection from existing graph
  - Input:  score (0–10), decision (APPROVED/REJECTED), difficulty
  - Output: next_task_id, selection_reason, source=niyantran_task_graph
  - Same input ALWAYS produces same output (deterministic)
  - Task graph is loaded from Niyantran — never mutated here
"""
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger("task_selection_engine")

# ── Static Niyantran task graph ───────────────────────────────────────────
# In production this is loaded from Niyantran's task graph API.
# Locally it is a static registry — no generation, no mutation.
#
# Structure:
#   key   = (decision_band, difficulty_band)
#   value = list of task_ids in priority order (first match wins)
#
# decision_band : "approved" | "rejected_borderline" | "rejected_fail"
# difficulty_band: "beginner" | "intermediate" | "advanced"

NIYANTRAN_TASK_GRAPH: Dict[tuple, list] = {
    # APPROVED paths — advancement
    ("approved", "beginner"):      ["NT-ADV-B-001", "NT-ADV-B-002", "NT-ADV-B-003"],
    ("approved", "intermediate"):  ["NT-ADV-I-001", "NT-ADV-I-002", "NT-ADV-I-003"],
    ("approved", "advanced"):      ["NT-ADV-A-001", "NT-ADV-A-002", "NT-ADV-A-003"],

    # REJECTED borderline (score 4–5.9) — reinforcement
    ("rejected_borderline", "beginner"):     ["NT-REI-B-001", "NT-REI-B-002"],
    ("rejected_borderline", "intermediate"): ["NT-REI-I-001", "NT-REI-I-002"],
    ("rejected_borderline", "advanced"):     ["NT-REI-A-001", "NT-REI-A-002"],

    # REJECTED fail (score < 4) — correction
    ("rejected_fail", "beginner"):     ["NT-COR-B-001", "NT-COR-B-002"],
    ("rejected_fail", "intermediate"): ["NT-COR-I-001", "NT-COR-I-002"],
    ("rejected_fail", "advanced"):     ["NT-COR-A-001", "NT-COR-A-002"],
}

# Task metadata registry — what each task_id represents
TASK_METADATA: Dict[str, Dict[str, str]] = {
    "NT-ADV-B-001": {"title": "Intermediate API Design Challenge",       "type": "advancement",   "difficulty": "intermediate"},
    "NT-ADV-B-002": {"title": "Service Layer Architecture Task",         "type": "advancement",   "difficulty": "intermediate"},
    "NT-ADV-B-003": {"title": "Database Schema Design Challenge",        "type": "advancement",   "difficulty": "intermediate"},
    "NT-ADV-I-001": {"title": "Advanced Microservices Implementation",   "type": "advancement",   "difficulty": "advanced"},
    "NT-ADV-I-002": {"title": "System Integration Challenge",            "type": "advancement",   "difficulty": "advanced"},
    "NT-ADV-I-003": {"title": "Performance Optimisation Task",           "type": "advancement",   "difficulty": "advanced"},
    "NT-ADV-A-001": {"title": "Distributed Systems Design",              "type": "advancement",   "difficulty": "advanced"},
    "NT-ADV-A-002": {"title": "Production Deployment Architecture",      "type": "advancement",   "difficulty": "advanced"},
    "NT-ADV-A-003": {"title": "Security Hardening Challenge",            "type": "advancement",   "difficulty": "advanced"},
    "NT-REI-B-001": {"title": "REST API Reinforcement Task",             "type": "reinforcement", "difficulty": "beginner"},
    "NT-REI-B-002": {"title": "Authentication Flow Reinforcement",       "type": "reinforcement", "difficulty": "beginner"},
    "NT-REI-I-001": {"title": "Architecture Pattern Reinforcement",      "type": "reinforcement", "difficulty": "intermediate"},
    "NT-REI-I-002": {"title": "Testing Coverage Reinforcement",          "type": "reinforcement", "difficulty": "intermediate"},
    "NT-REI-A-001": {"title": "Advanced Architecture Reinforcement",     "type": "reinforcement", "difficulty": "advanced"},
    "NT-REI-A-002": {"title": "System Design Reinforcement",             "type": "reinforcement", "difficulty": "advanced"},
    "NT-COR-B-001": {"title": "Foundational Implementation Correction",  "type": "correction",    "difficulty": "beginner"},
    "NT-COR-B-002": {"title": "Repository Structure Correction",         "type": "correction",    "difficulty": "beginner"},
    "NT-COR-I-001": {"title": "Feature Delivery Correction",             "type": "correction",    "difficulty": "intermediate"},
    "NT-COR-I-002": {"title": "Requirement Alignment Correction",        "type": "correction",    "difficulty": "intermediate"},
    "NT-COR-A-001": {"title": "Architecture Compliance Correction",      "type": "correction",    "difficulty": "advanced"},
    "NT-COR-A-002": {"title": "Proof of Work Correction",                "type": "correction",    "difficulty": "advanced"},
}


class TaskSelectionEngine:
    """
    Deterministic task selector.
    Reads from NIYANTRAN_TASK_GRAPH — never generates tasks.
    Same (score, decision, difficulty) always returns same next_task_id.
    """

    SOURCE = "niyantran_task_graph"

    def select_next_task(
        self,
        score_10: float,
        decision: str,
        current_difficulty: str = "beginner"
    ) -> Dict[str, Any]:
        """
        Select next task deterministically.

        Args:
            score_10:           Evaluation score 0–10
            decision:           "APPROVED" or "REJECTED"
            current_difficulty: Current task difficulty level

        Returns:
            {next_task_id, title, task_type, difficulty, selection_reason, source}
        """
        decision_band    = self._map_decision_band(score_10, decision)
        difficulty_band  = self._normalise_difficulty(current_difficulty)
        selection_key    = (decision_band, difficulty_band)

        task_ids = NIYANTRAN_TASK_GRAPH.get(selection_key)

        if not task_ids:
            # Fallback: use beginner correction — always exists
            fallback_key = ("rejected_fail", "beginner")
            task_ids = NIYANTRAN_TASK_GRAPH[fallback_key]
            selection_reason = (
                f"Fallback selection — no graph entry for "
                f"({decision_band}, {difficulty_band})"
            )
        else:
            selection_reason = (
                f"score={score_10:.1f}/10 → {decision_band} | "
                f"difficulty={difficulty_band} | "
                f"graph_key={selection_key}"
            )

        # Always take first task in list (deterministic — no randomness)
        next_task_id = task_ids[0]
        metadata     = TASK_METADATA.get(next_task_id, {})

        logger.info(
            f"[TASK SELECTION] key={selection_key} → {next_task_id} "
            f"({metadata.get('type', 'unknown')})"
        )

        return {
            "next_task_id":      next_task_id,
            "title":             metadata.get("title", "Task Assignment"),
            "task_type":         metadata.get("type", "correction"),
            "difficulty":        metadata.get("difficulty", "beginner"),
            "selection_reason":  selection_reason,
            "source":            self.SOURCE,
            "decision_band":     decision_band,
            "difficulty_band":   difficulty_band,
        }

    def get_task_metadata(self, task_id: str) -> Optional[Dict[str, str]]:
        """Return metadata for a task_id from the graph. None if not found."""
        return TASK_METADATA.get(task_id)

    def validate_task_id(self, task_id: str) -> bool:
        """Check if a task_id exists in the Niyantran task graph."""
        return task_id in TASK_METADATA

    # ── Private helpers ───────────────────────────────────────────────────

    def _map_decision_band(self, score_10: float, decision: str) -> str:
        """Map score + decision to a deterministic decision band."""
        if decision == "APPROVED":
            return "approved"
        # REJECTED — split by score
        if score_10 >= 4.0:
            return "rejected_borderline"
        return "rejected_fail"

    def _normalise_difficulty(self, difficulty: str) -> str:
        """Normalise difficulty string to known band."""
        d = difficulty.lower().strip()
        if d in ("advanced", "expert"):
            return "advanced"
        if d in ("intermediate", "targeted", "reinforcement"):
            return "intermediate"
        return "beginner"  # default — foundational, beginner, correction, unknown


# Global instance
task_selection_engine = TaskSelectionEngine()
