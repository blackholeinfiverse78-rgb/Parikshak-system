"""
Human-in-Loop Service - Confidence-based Escalation
Implements confidence calculation and triggers escalation if < 0.98
Provides override capability for human reviewers
Escalation cases are persisted to disk — survives restarts
"""
from typing import Dict, Any, Optional, List
import logging
import json
import os
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger("human_in_loop")


class EscalationReason(str, Enum):
    LOW_CONFIDENCE = "low_confidence"
    CONFLICTING_SIGNALS = "conflicting_signals"
    EDGE_CASE = "edge_case"
    MANUAL_REVIEW_REQUESTED = "manual_review_requested"
    QUALITY_CONCERN = "quality_concern"


class EscalationStatus(str, Enum):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    RESOLVED = "resolved"
    OVERRIDDEN = "overridden"


@dataclass
class ConfidenceMetrics:
    base_confidence: float
    quality_adjustment: float
    pac_adjustment: float
    evidence_adjustment: float
    consistency_adjustment: float
    final_confidence: float
    score_consistency: float
    signal_alignment: float
    decision_clarity: float
    evidence_strength: float
    requires_escalation: bool
    escalation_reasons: List[str]


@dataclass
class EscalationCase:
    case_id: str
    trace_id: str
    timestamp: str
    reason: str           # plain string — JSON-serialisable
    confidence: float
    original_evaluation: Dict[str, Any]
    original_decision: Dict[str, Any]
    escalation_context: Dict[str, Any]
    status: str           # plain string — JSON-serialisable
    assigned_reviewer: Optional[str] = None
    review_notes: Optional[str] = None
    human_override: Optional[Dict[str, Any]] = None
    resolved_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class HumanInLoopService:
    """
    Human-in-loop service for confidence-based escalation.
    Escalation cases are persisted to disk so restarts do not lose pending reviews.
    """

    def __init__(self, confidence_threshold: float = 0.98,
                 storage_path: str = "storage/escalations"):
        self.confidence_threshold = confidence_threshold
        self.storage_path = storage_path
        os.makedirs(self.storage_path, exist_ok=True)
        self.escalation_cases: Dict[str, EscalationCase] = self._load_all_cases()

    # ── Persistence ──────────────────────────────────────────────────────

    def _case_path(self, case_id: str) -> str:
        return os.path.join(self.storage_path, f"{case_id}.json")

    def _save_case(self, case: EscalationCase) -> None:
        try:
            with open(self._case_path(case.case_id), "w", encoding="utf-8") as f:
                json.dump(case.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"[HUMAN-IN-LOOP] Failed to persist case {case.case_id}: {e}")

    def _load_all_cases(self) -> Dict[str, EscalationCase]:
        cases: Dict[str, EscalationCase] = {}
        if not os.path.isdir(self.storage_path):
            return cases
        for fname in os.listdir(self.storage_path):
            if not fname.endswith(".json"):
                continue
            try:
                with open(os.path.join(self.storage_path, fname), "r", encoding="utf-8") as f:
                    data = json.load(f)
                cases[data["case_id"]] = EscalationCase(**data)
            except Exception as e:
                logger.warning(f"[HUMAN-IN-LOOP] Could not load {fname}: {e}")
        logger.info(f"[HUMAN-IN-LOOP] Loaded {len(cases)} persisted escalation cases")
        return cases

    # ── Confidence calculation ────────────────────────────────────────────

    def calculate_confidence(
        self,
        evaluation_result: Dict[str, Any],
        decision_result: Dict[str, Any],
        supporting_signals: Dict[str, Any]
    ) -> ConfidenceMetrics:
        logger.info("[HUMAN-IN-LOOP] Calculating confidence metrics")

        base_confidence = decision_result.get("confidence", 0.5)

        quality_rubric = decision_result.get("quality_rubric", {})
        quality_grade = quality_rubric.get("quality_grade", "D")
        quality_adjustment = self._calculate_quality_adjustment(quality_grade, quality_rubric)

        pac_detection = decision_result.get("pac_detection", {})
        pac_adjustment = self._calculate_pac_adjustment(pac_detection)

        evidence_summary = evaluation_result.get("evidence_summary", {})
        evidence_adjustment = self._calculate_evidence_adjustment(evidence_summary)

        consistency_adjustment = self._calculate_consistency_adjustment(
            evaluation_result, decision_result, supporting_signals
        )

        score_consistency = self._calculate_score_consistency(evaluation_result, decision_result)
        signal_alignment = self._calculate_signal_alignment(supporting_signals, decision_result)
        decision_clarity = self._calculate_decision_clarity(decision_result)
        evidence_strength = self._calculate_evidence_strength(evidence_summary)

        final_confidence = min(1.0, max(0.0,
            base_confidence + quality_adjustment + pac_adjustment +
            evidence_adjustment + consistency_adjustment
        ))

        requires_escalation = final_confidence < self.confidence_threshold
        escalation_reasons = self._identify_escalation_reasons(
            final_confidence, quality_grade, pac_detection, evidence_summary,
            score_consistency, signal_alignment
        )

        metrics = ConfidenceMetrics(
            base_confidence=base_confidence,
            quality_adjustment=quality_adjustment,
            pac_adjustment=pac_adjustment,
            evidence_adjustment=evidence_adjustment,
            consistency_adjustment=consistency_adjustment,
            final_confidence=final_confidence,
            score_consistency=score_consistency,
            signal_alignment=signal_alignment,
            decision_clarity=decision_clarity,
            evidence_strength=evidence_strength,
            requires_escalation=requires_escalation,
            escalation_reasons=escalation_reasons
        )

        logger.info(f"[HUMAN-IN-LOOP] Confidence: {final_confidence:.3f} (threshold: {self.confidence_threshold})")
        if requires_escalation:
            logger.warning(f"[HUMAN-IN-LOOP] Escalation required: {', '.join(escalation_reasons)}")

        return metrics

    def process_with_human_loop(
        self,
        evaluation_result: Dict[str, Any],
        decision_result: Dict[str, Any],
        supporting_signals: Dict[str, Any],
        trace_id: str
    ) -> Dict[str, Any]:
        confidence_metrics = self.calculate_confidence(
            evaluation_result, decision_result, supporting_signals
        )

        if confidence_metrics.requires_escalation:
            escalation_case = self._create_escalation_case(
                evaluation_result, decision_result, supporting_signals,
                confidence_metrics, trace_id
            )
            logger.info(f"[HUMAN-IN-LOOP] Escalation case created: {escalation_case.case_id}")
            return {
                **evaluation_result,
                "confidence_metrics": confidence_metrics.__dict__,
                "escalation_required": True,
                "escalation_case_id": escalation_case.case_id,
                "human_review_pending": True
            }

        return {
            **evaluation_result,
            "confidence_metrics": confidence_metrics.__dict__,
            "escalation_required": False,
            "human_review_pending": False
        }

    def apply_human_override(
        self,
        case_id: str,
        reviewer: str,
        override_decision: Dict[str, Any],
        review_notes: str
    ) -> Dict[str, Any]:
        if case_id not in self.escalation_cases:
            raise ValueError(f"Escalation case {case_id} not found")

        case = self.escalation_cases[case_id]
        case.status = EscalationStatus.OVERRIDDEN.value
        case.assigned_reviewer = reviewer
        case.review_notes = review_notes
        case.human_override = override_decision
        case.resolved_at = datetime.now().isoformat()
        self._save_case(case)

        logger.info(f"[HUMAN-IN-LOOP] Override applied by {reviewer} for case {case_id}")
        return {
            **case.original_evaluation,
            **override_decision,
            "human_override_applied": True,
            "human_reviewer": reviewer,
            "human_review_notes": review_notes,
            "original_confidence": case.confidence,
            "override_confidence": 1.0,
            "escalation_resolved": True
        }

    def get_pending_escalations(self) -> List[Dict[str, Any]]:
        return [
            {
                "case_id": c.case_id,
                "trace_id": c.trace_id,
                "timestamp": c.timestamp,
                "confidence": c.confidence,
                "reasons": c.escalation_context.get("escalation_reasons", []),
                "task_title": c.original_evaluation.get("task_title", "Unknown"),
                "score": c.original_decision.get("score", 0),
                "decision": c.original_decision.get("decision", "unknown")
            }
            for c in self.escalation_cases.values()
            if c.status == EscalationStatus.PENDING.value
        ]

    # ── Private helpers ───────────────────────────────────────────────────

    def _create_escalation_case(
        self,
        evaluation_result: Dict[str, Any],
        decision_result: Dict[str, Any],
        supporting_signals: Dict[str, Any],
        confidence_metrics: ConfidenceMetrics,
        trace_id: str
    ) -> EscalationCase:
        case_id = f"esc-{datetime.now().strftime('%Y%m%d%H%M%S')}-{trace_id[:8]}"
        case = EscalationCase(
            case_id=case_id,
            trace_id=trace_id,
            timestamp=datetime.now().isoformat(),
            reason=EscalationReason.LOW_CONFIDENCE.value,
            confidence=confidence_metrics.final_confidence,
            original_evaluation=evaluation_result,
            original_decision=decision_result,
            escalation_context={
                "confidence_metrics": confidence_metrics.__dict__,
                "supporting_signals_summary": {
                    "repository_available": supporting_signals.get("repository_available", False),
                    "feature_match_ratio": supporting_signals.get("feature_match_ratio", 0),
                    "delivery_ratio": supporting_signals.get("expected_vs_delivered_evidence", {}).get("delivery_ratio", 0),
                    "quality_grade": decision_result.get("quality_rubric", {}).get("quality_grade", "D")
                },
                "escalation_reasons": confidence_metrics.escalation_reasons
            },
            status=EscalationStatus.PENDING.value
        )
        self.escalation_cases[case_id] = case
        self._save_case(case)
        return case

    def _calculate_quality_adjustment(self, quality_grade: str, quality_rubric: Dict[str, Any]) -> float:
        base = {"A": 0.1, "B": 0.05, "C": 0.0, "D": -0.1}.get(quality_grade, -0.1)
        total = quality_rubric.get("total_quality", 0)
        if total >= 8:
            base += 0.05
        elif total <= 2:
            base -= 0.05
        return base

    def _calculate_pac_adjustment(self, pac_detection: Dict[str, Any]) -> float:
        pac_score = pac_detection.get("pac_score", 0)
        if pac_score >= 5: return 0.08
        elif pac_score >= 3: return 0.04
        elif pac_score >= 1: return 0.02
        return -0.05

    def _calculate_evidence_adjustment(self, evidence_summary: Dict[str, Any]) -> float:
        ratio = evidence_summary.get("delivery_ratio", 0)
        missing = evidence_summary.get("missing_features_count", 0)
        if ratio >= 0.9 and missing == 0: return 0.1
        elif ratio >= 0.7 and missing <= 2: return 0.05
        elif ratio >= 0.4: return 0.0
        return -0.08

    def _calculate_consistency_adjustment(
        self,
        evaluation_result: Dict[str, Any],
        decision_result: Dict[str, Any],
        supporting_signals: Dict[str, Any]
    ) -> float:
        score = decision_result.get("score", 0)
        decision = decision_result.get("decision", "reject")
        expected = "approve" if score >= 75 else "conditional" if score >= 50 else "reject"
        decision_ok = decision == expected

        repo = supporting_signals.get("repository_available", False)
        fmr = supporting_signals.get("feature_match_ratio", 0)
        signal_ok = True
        if score >= 70 and (not repo or fmr < 0.5): signal_ok = False
        if score <= 30 and repo and fmr >= 0.8: signal_ok = False

        if decision_ok and signal_ok: return 0.05
        if not decision_ok or not signal_ok: return -0.08
        return 0.0

    def _calculate_score_consistency(self, evaluation_result: Dict[str, Any], decision_result: Dict[str, Any]) -> float:
        diff = abs(evaluation_result.get("score", 0) - decision_result.get("score", 0))
        if diff <= 5: return 1.0
        elif diff <= 15: return 0.8
        elif diff <= 25: return 0.6
        return 0.4

    def _calculate_signal_alignment(self, supporting_signals: Dict[str, Any], decision_result: Dict[str, Any]) -> float:
        repo = supporting_signals.get("repository_available", False)
        fmr = supporting_signals.get("feature_match_ratio", 0)
        dr = supporting_signals.get("expected_vs_delivered_evidence", {}).get("delivery_ratio", 0)
        decision = decision_result.get("decision", "reject")
        if decision == "approve":
            return 1.0 if (repo and fmr >= 0.7 and dr >= 0.8) else 0.3
        elif decision == "conditional":
            return 1.0 if (fmr >= 0.4 and dr >= 0.5) else 0.3
        return 1.0 if (fmr < 0.6 or dr < 0.6) else 0.3

    def _calculate_decision_clarity(self, decision_result: Dict[str, Any]) -> float:
        total = decision_result.get("decision_criteria", {}).get("total_criteria_score", 0)
        if total >= 7 or total <= 2: return 1.0
        elif total >= 5 or total <= 4: return 0.7
        return 0.4

    def _calculate_evidence_strength(self, evidence_summary: Dict[str, Any]) -> float:
        expected = evidence_summary.get("expected_features", 0)
        delivered = evidence_summary.get("delivered_features", 0)
        if expected == 0: return 0.5
        ratio = delivered / expected
        if ratio >= 0.9: return 1.0
        elif ratio >= 0.7: return 0.8
        elif ratio >= 0.5: return 0.6
        return 0.3

    def _identify_escalation_reasons(
        self,
        confidence: float,
        quality_grade: str,
        pac_detection: Dict[str, Any],
        evidence_summary: Dict[str, Any],
        score_consistency: float,
        signal_alignment: float
    ) -> List[str]:
        reasons = []
        if confidence < self.confidence_threshold: reasons.append("low_confidence")
        if score_consistency < 0.7: reasons.append("score_inconsistency")
        if signal_alignment < 0.5: reasons.append("signal_misalignment")
        if quality_grade == "D" and pac_detection.get("pac_score", 0) >= 3:
            reasons.append("conflicting_quality_signals")
        dr = evidence_summary.get("delivery_ratio", 1.0)
        if 0.4 <= dr <= 0.6: reasons.append("borderline_delivery")
        return reasons


# Global instance
human_in_loop = HumanInLoopService()
