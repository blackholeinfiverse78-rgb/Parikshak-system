"""
Parikshak Bucket Integration — Phase 6
Every review MUST write a log entry. No exceptions.
Exact schema per spec:
  type, candidate_id, task_id, score, decision,
  review_summary, next_task, trace_id
"""
import json
import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger("bucket_integration")


class BucketIntegrationService:
    """
    Phase 6 — Mandatory evaluation logging.
    Writes to daily JSONL files + maintains a searchable index.
    No evaluation is silent.
    """

    def __init__(self, bucket_path: str = "storage/bucket_logs"):
        self.bucket_path = bucket_path
        os.makedirs(self.bucket_path, exist_ok=True)
        index_file = os.path.join(self.bucket_path, "evaluation_index.jsonl")
        if not os.path.exists(index_file):
            open(index_file, "w").close()

    # ── Public API ────────────────────────────────────────────────────────

    def log_evaluation(
        self,
        evaluation_result: Dict[str, Any],
        supporting_signals: Dict[str, Any],
        decision_result: Dict[str, Any],
        next_task_result: Dict[str, Any],
        task_data: Dict[str, Any],
        trace_id: Optional[str] = None
    ) -> str:
        """
        Write mandatory bucket log entry.
        Returns trace_id.
        """
        if not trace_id:
            trace_id = str(uuid.uuid4())

        entry = self._build_entry(
            evaluation_result, supporting_signals,
            decision_result, next_task_result,
            task_data, trace_id
        )

        self._write(entry)
        self._update_index(entry)

        logger.info(
            f"[BUCKET] Logged: trace_id={trace_id} | "
            f"score={entry['score']} | decision={entry['decision']}"
        )
        return trace_id

    def get_evaluation_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Phase 5 allowed read: evaluation index (same_task_history)."""
        index_file = os.path.join(self.bucket_path, "evaluation_index.jsonl")
        if not os.path.exists(index_file):
            return []
        logs = []
        try:
            with open(index_file, "r", encoding="utf-8") as f:
                for line in f.readlines()[-limit:]:
                    if line.strip():
                        logs.append(json.loads(line))
        except Exception as e:
            logger.error(f"[BUCKET] Failed to read index: {e}")
        return logs

    def get_evaluation_by_trace_id(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Phase 5 allowed read: specific evaluation by trace_id (same_task_history)."""
        for days_back in range(7):
            from datetime import timedelta
            date_str = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
            log_file = os.path.join(self.bucket_path, f"evaluations_{date_str}.jsonl")
            if not os.path.exists(log_file):
                continue
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            entry = json.loads(line)
                            if entry.get("trace_id") == trace_id:
                                return entry
            except Exception as e:
                logger.error(f"[BUCKET] Error reading {log_file}: {e}")
        return None

    def get_escalation_cases(self, candidate_id: str) -> List[Dict[str, Any]]:
        """
        Phase 5 allowed read: escalation_cases for a specific candidate.
        ONLY returns entries where candidate_id matches.
        """
        all_logs = self.get_evaluation_logs(1000)
        return [
            log for log in all_logs
            if log.get("candidate_id") == candidate_id
            and log.get("review_summary", {}).get("requires_human_review", False)
        ]

    def reject_unauthorised_read(self, read_type: str) -> Dict[str, Any]:
        """
        Phase 5: Reject any read not in allowed_reads.
        allowed_reads = [same_task_history, escalation_cases]
        """
        allowed = ["same_task_history", "escalation_cases"]
        logger.error(f"[BUCKET] REJECTED unauthorised read type: {read_type}")
        return {
            "error": "BUCKET_READ_REJECTED",
            "reason": f"Read type '{read_type}' not in allowed_reads: {allowed}",
            "allowed_reads": allowed
        }

    def get_bucket_stats(self) -> Dict[str, Any]:
        stats = {
            "total_evaluations": 0,
            "decisions": {"APPROVED": 0, "REJECTED": 0},
            "avg_score": 0.0,
            "avg_confidence": 0.0,
            "quality_grades": {"A": 0, "B": 0, "C": 0, "D": 0}
        }
        logs = self.get_evaluation_logs(1000)
        if not logs:
            return stats
        stats["total_evaluations"] = len(logs)
        total_score = sum(l.get("score", 0) for l in logs)
        total_conf  = sum(l.get("confidence", 0) for l in logs)
        for log in logs:
            d = log.get("decision", "REJECTED")
            if d in stats["decisions"]:
                stats["decisions"][d] += 1
            g = log.get("quality_grade", "D")
            if g in stats["quality_grades"]:
                stats["quality_grades"][g] += 1
        stats["avg_score"]      = round(total_score / len(logs), 2)
        stats["avg_confidence"] = round(total_conf  / len(logs), 3)
        return stats

    # ── Entry builder — exact Phase 6 schema ─────────────────────────────

    def _build_entry(
        self,
        evaluation_result: Dict[str, Any],
        supporting_signals: Dict[str, Any],
        decision_result: Dict[str, Any],
        next_task_result: Dict[str, Any],
        task_data: Dict[str, Any],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Phase 6 mandatory fields:
          type, candidate_id, task_id, score, decision,
          review_summary, next_task, trace_id
        """
        score    = decision_result.get("score", evaluation_result.get("score_10", 0))
        decision = decision_result.get("decision", "REJECTED")
        confidence = decision_result.get("confidence", 0.0)

        # review_summary — structured block
        review_summary = {
            "score_10":          score,
            "score_100":         round(score * 10) if score <= 10 else score,
            "status":            evaluation_result.get("status", "fail"),
            "decision":          decision,
            "confidence":        confidence,
            "pac": {
                "proof":        evaluation_result.get("pac", {}).get("proof", 0),
                "architecture": evaluation_result.get("pac", {}).get("architecture", 0),
                "code":         evaluation_result.get("pac", {}).get("code", 0)
            },
            "rubric": evaluation_result.get("rubric", {}),
            "score_breakdown":   evaluation_result.get("score_breakdown", {}),
            "strengths":         decision_result.get("strengths", []),
            "failures":          decision_result.get("failures", []),
            "root_cause":        decision_result.get("root_cause", ""),
            "learning_feedback": decision_result.get("learning_feedback", []),
            "quality_rubric":    decision_result.get("quality_rubric", {}),
            "effort_score":      decision_result.get("effort_score", {}),
            "requires_human_review": confidence < 0.98
        }

        # next_task — structured block
        next_task = {
            "task_id":    next_task_result.get("next_task_id", ""),
            "task_type":  next_task_result.get("task_type", "correction"),
            "title":      next_task_result.get("title", ""),
            "difficulty": next_task_result.get("difficulty", "beginner"),
            "objective":  next_task_result.get("objective", ""),
            "focus_area": next_task_result.get("focus_area", ""),
            "reason":     next_task_result.get("reason", ""),
            "next_direction": decision_result.get("next_direction", "")
        }

        desc = task_data.get("task_description", "")

        return {
            # Phase 6 mandatory fields
            "type":           "task_review",
            "candidate_id":   task_data.get("submitted_by", "unknown"),
            "task_id":        task_data.get("task_id", task_data.get("task_title", "unknown")[:40]),
            "score":          score,
            "decision":       decision,
            "review_summary": review_summary,
            "next_task":      next_task,
            "trace_id":       trace_id,

            # Extended fields for traceability
            "timestamp":      datetime.now().isoformat(),
            "task_title":     task_data.get("task_title", ""),
            "task_description": (desc[:500] + "...") if len(desc) > 500 else desc,
            "repository_url": task_data.get("github_repo_link") or task_data.get("repository_url"),
            "domain":         supporting_signals.get("domain", "unknown"),
            "confidence":     confidence,
            "quality_grade":  decision_result.get("quality_rubric", {}).get("quality_grade", "D"),
            "signals_summary": self._summarize_signals(supporting_signals),
            "canonical_authority": evaluation_result.get("canonical_authority", False),
            "validation_applied":  bool(evaluation_result.get("validation_metadata"))
        }

    def _summarize_signals(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "repository_available":      signals.get("repository_available", False),
            "feature_match_ratio":       signals.get("feature_match_ratio", 0.0),
            "expected_features_count":   len(signals.get("expected_features", [])),
            "implemented_features_count": len(signals.get("implemented_features", [])),
            "missing_features_count":    len(signals.get("missing_features", [])),
            "failure_indicators_count":  len(signals.get("failure_indicators", [])),
            "delivery_ratio":            signals.get("expected_vs_delivered_evidence", {}).get("delivery_ratio", 0.0),
            "domain":                    signals.get("domain", "unknown")
        }

    def _write(self, entry: Dict[str, Any]) -> None:
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(self.bucket_path, f"evaluations_{date_str}.jsonl")
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                json.dump(entry, f, ensure_ascii=False)
                f.write("\n")
        except Exception as e:
            logger.error(f"[BUCKET] Write failed: {e}")
            # Fallback — never lose a log
            fallback = os.path.join(self.bucket_path, "bucket_errors.log")
            with open(fallback, "a") as fb:
                fb.write(f"{datetime.now().isoformat()} | {entry.get('trace_id')} | {e}\n")

    def _update_index(self, entry: Dict[str, Any]) -> None:
        index_file = os.path.join(self.bucket_path, "evaluation_index.jsonl")
        index_entry = {
            "trace_id":     entry["trace_id"],
            "timestamp":    entry["timestamp"],
            "type":         entry["type"],
            "candidate_id": entry["candidate_id"],
            "task_id":      entry["task_id"],
            "score":        entry["score"],
            "decision":     entry["decision"],
            "confidence":   entry["confidence"],
            "quality_grade": entry["quality_grade"],
            "domain":       entry["domain"],
            "task_title":   entry["task_title"][:80]
        }
        try:
            with open(index_file, "a", encoding="utf-8") as f:
                json.dump(index_entry, f, ensure_ascii=False)
                f.write("\n")
        except Exception as e:
            logger.error(f"[BUCKET] Index update failed: {e}")


# Global instance
bucket_integration = BucketIntegrationService()
