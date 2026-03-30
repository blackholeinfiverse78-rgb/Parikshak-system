"""
Human-in-Loop Service - Confidence-based Escalation
Implements confidence calculation and triggers escalation if < 0.98
Provides override capability for human reviewers
"""
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
from dataclasses import dataclass
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
    """Detailed confidence calculation metrics"""
    base_confidence: float
    quality_adjustment: float
    pac_adjustment: float
    evidence_adjustment: float
    consistency_adjustment: float
    final_confidence: float
    
    # Confidence factors
    score_consistency: float
    signal_alignment: float
    decision_clarity: float
    evidence_strength: float
    
    # Flags
    requires_escalation: bool
    escalation_reasons: List[str]

@dataclass
class EscalationCase:
    """Human escalation case"""
    case_id: str
    trace_id: str
    timestamp: str
    reason: EscalationReason
    confidence: float
    
    # Original evaluation
    original_evaluation: Dict[str, Any]
    original_decision: Dict[str, Any]
    
    # Escalation context
    escalation_context: Dict[str, Any]
    
    # Human review
    status: EscalationStatus
    assigned_reviewer: Optional[str] = None
    review_notes: Optional[str] = None
    human_override: Optional[Dict[str, Any]] = None
    resolved_at: Optional[str] = None

class HumanInLoopService:
    """
    Human-in-loop service for confidence-based escalation
    Calculates confidence and manages human review process
    """
    
    def __init__(self, confidence_threshold: float = 0.98):
        self.confidence_threshold = confidence_threshold
        self.escalation_cases = {}  # In production, this would be a database
        
    def calculate_confidence(
        self,
        evaluation_result: Dict[str, Any],
        decision_result: Dict[str, Any],
        supporting_signals: Dict[str, Any]
    ) -> ConfidenceMetrics:
        """
        Calculate detailed confidence metrics
        
        Returns:
            ConfidenceMetrics with detailed breakdown
        """
        logger.info("[HUMAN-IN-LOOP] Calculating confidence metrics")
        
        # Base confidence from decision engine
        base_confidence = decision_result.get("confidence", 0.5)
        
        # Quality-based adjustment
        quality_rubric = decision_result.get("quality_rubric", {})
        quality_grade = quality_rubric.get("quality_grade", "D")
        quality_adjustment = self._calculate_quality_adjustment(quality_grade, quality_rubric)
        
        # P/A/C signal adjustment
        pac_detection = decision_result.get("pac_detection", {})
        pac_adjustment = self._calculate_pac_adjustment(pac_detection)
        
        # Evidence strength adjustment
        evidence_summary = evaluation_result.get("evidence_summary", {})
        evidence_adjustment = self._calculate_evidence_adjustment(evidence_summary)
        
        # Consistency adjustment (score vs signals alignment)
        consistency_adjustment = self._calculate_consistency_adjustment(
            evaluation_result, decision_result, supporting_signals
        )
        
        # Calculate individual confidence factors
        score_consistency = self._calculate_score_consistency(evaluation_result, decision_result)
        signal_alignment = self._calculate_signal_alignment(supporting_signals, decision_result)
        decision_clarity = self._calculate_decision_clarity(decision_result)
        evidence_strength = self._calculate_evidence_strength(evidence_summary)
        
        # Final confidence calculation
        final_confidence = min(1.0, max(0.0, 
            base_confidence + 
            quality_adjustment + 
            pac_adjustment + 
            evidence_adjustment + 
            consistency_adjustment
        ))
        
        # Determine if escalation is required
        requires_escalation = final_confidence < self.confidence_threshold
        escalation_reasons = self._identify_escalation_reasons(
            final_confidence, quality_grade, pac_detection, evidence_summary, 
            score_consistency, signal_alignment
        )
        
        confidence_metrics = ConfidenceMetrics(
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
        
        logger.info(f"[HUMAN-IN-LOOP] Confidence calculated: {final_confidence:.3f} (threshold: {self.confidence_threshold})")
        if requires_escalation:
            logger.warning(f"[HUMAN-IN-LOOP] Escalation required: {', '.join(escalation_reasons)}")
        
        return confidence_metrics
    
    def process_with_human_loop(
        self,
        evaluation_result: Dict[str, Any],
        decision_result: Dict[str, Any],
        supporting_signals: Dict[str, Any],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Process evaluation with human-in-loop logic
        
        Returns:
            Enhanced result with confidence metrics and escalation handling
        """
        # Calculate confidence
        confidence_metrics = self.calculate_confidence(
            evaluation_result, decision_result, supporting_signals
        )
        
        # Check if escalation is required
        if confidence_metrics.requires_escalation:
            escalation_case = self._create_escalation_case(
                evaluation_result, decision_result, supporting_signals, 
                confidence_metrics, trace_id
            )
            
            # In production, this would trigger human reviewer notification
            logger.info(f"[HUMAN-IN-LOOP] Escalation case created: {escalation_case.case_id}")
            
            # Return evaluation with escalation flag
            enhanced_result = {
                **evaluation_result,
                "confidence_metrics": confidence_metrics.__dict__,
                "escalation_required": True,
                "escalation_case_id": escalation_case.case_id,
                "human_review_pending": True
            }
        else:
            # High confidence - proceed normally
            enhanced_result = {
                **evaluation_result,
                "confidence_metrics": confidence_metrics.__dict__,
                "escalation_required": False,
                "human_review_pending": False
            }
        
        return enhanced_result
    
    def apply_human_override(
        self,
        case_id: str,
        reviewer: str,
        override_decision: Dict[str, Any],
        review_notes: str
    ) -> Dict[str, Any]:
        """
        Apply human override to escalated case
        
        Args:
            case_id: Escalation case ID
            reviewer: Human reviewer identifier
            override_decision: Human decision override
            review_notes: Reviewer notes
            
        Returns:
            Updated evaluation result with human override
        """
        if case_id not in self.escalation_cases:
            raise ValueError(f"Escalation case {case_id} not found")
        
        escalation_case = self.escalation_cases[case_id]
        
        # Apply human override
        escalation_case.status = EscalationStatus.OVERRIDDEN
        escalation_case.assigned_reviewer = reviewer
        escalation_case.review_notes = review_notes
        escalation_case.human_override = override_decision
        escalation_case.resolved_at = datetime.now().isoformat()
        
        # Create overridden result
        overridden_result = {
            **escalation_case.original_evaluation,
            **override_decision,
            "human_override_applied": True,
            "human_reviewer": reviewer,
            "human_review_notes": review_notes,
            "original_confidence": escalation_case.confidence,
            "override_confidence": 1.0,  # Human override has maximum confidence
            "escalation_resolved": True
        }
        
        logger.info(f"[HUMAN-IN-LOOP] Human override applied by {reviewer} for case {case_id}")
        return overridden_result
    
    def _calculate_quality_adjustment(self, quality_grade: str, quality_rubric: Dict[str, Any]) -> float:
        """Calculate confidence adjustment based on quality grade"""
        grade_adjustments = {"A": 0.1, "B": 0.05, "C": 0.0, "D": -0.1}
        base_adjustment = grade_adjustments.get(quality_grade, -0.1)
        
        # Additional adjustment based on total quality score
        total_quality = quality_rubric.get("total_quality", 0)
        if total_quality >= 8:
            base_adjustment += 0.05
        elif total_quality <= 2:
            base_adjustment -= 0.05
        
        return base_adjustment
    
    def _calculate_pac_adjustment(self, pac_detection: Dict[str, Any]) -> float:
        """Calculate confidence adjustment based on P/A/C signals"""
        pac_score = pac_detection.get("pac_score", 0)
        
        if pac_score >= 5:
            return 0.08
        elif pac_score >= 3:
            return 0.04
        elif pac_score >= 1:
            return 0.02
        else:
            return -0.05
    
    def _calculate_evidence_adjustment(self, evidence_summary: Dict[str, Any]) -> float:
        """Calculate confidence adjustment based on evidence strength"""
        delivery_ratio = evidence_summary.get("delivery_ratio", 0)
        missing_count = evidence_summary.get("missing_features_count", 0)
        
        if delivery_ratio >= 0.9 and missing_count == 0:
            return 0.1
        elif delivery_ratio >= 0.7 and missing_count <= 2:
            return 0.05
        elif delivery_ratio >= 0.4:
            return 0.0
        else:
            return -0.08
    
    def _calculate_consistency_adjustment(
        self, 
        evaluation_result: Dict[str, Any], 
        decision_result: Dict[str, Any], 
        supporting_signals: Dict[str, Any]
    ) -> float:
        """Calculate confidence adjustment based on internal consistency"""
        
        # Check score vs decision consistency
        score = decision_result.get("score", 0)
        decision = decision_result.get("decision", "reject")
        
        expected_decision = "approve" if score >= 75 else "conditional" if score >= 50 else "reject"
        decision_consistent = (decision == expected_decision)
        
        # Check signal vs score consistency
        repo_available = supporting_signals.get("repository_available", False)
        feature_match_ratio = supporting_signals.get("feature_match_ratio", 0)
        
        signal_score_consistent = True
        if score >= 70 and (not repo_available or feature_match_ratio < 0.5):
            signal_score_consistent = False
        if score <= 30 and repo_available and feature_match_ratio >= 0.8:
            signal_score_consistent = False
        
        adjustment = 0.0
        if decision_consistent and signal_score_consistent:
            adjustment = 0.05
        elif not decision_consistent or not signal_score_consistent:
            adjustment = -0.08
        
        return adjustment
    
    def _calculate_score_consistency(self, evaluation_result: Dict[str, Any], decision_result: Dict[str, Any]) -> float:
        """Calculate score consistency factor"""
        original_score = evaluation_result.get("score", 0)
        final_score = decision_result.get("score", 0)
        
        score_diff = abs(original_score - final_score)
        if score_diff <= 5:
            return 1.0
        elif score_diff <= 15:
            return 0.8
        elif score_diff <= 25:
            return 0.6
        else:
            return 0.4
    
    def _calculate_signal_alignment(self, supporting_signals: Dict[str, Any], decision_result: Dict[str, Any]) -> float:
        """Calculate signal alignment factor"""
        repo_available = supporting_signals.get("repository_available", False)
        feature_match_ratio = supporting_signals.get("feature_match_ratio", 0)
        delivery_ratio = supporting_signals.get("expected_vs_delivered_evidence", {}).get("delivery_ratio", 0)
        
        decision = decision_result.get("decision", "reject")
        
        # Expected alignment
        if decision == "approve":
            expected_alignment = repo_available and feature_match_ratio >= 0.7 and delivery_ratio >= 0.8
        elif decision == "conditional":
            expected_alignment = feature_match_ratio >= 0.4 and delivery_ratio >= 0.5
        else:  # reject
            expected_alignment = feature_match_ratio < 0.6 or delivery_ratio < 0.6
        
        return 1.0 if expected_alignment else 0.3
    
    def _calculate_decision_clarity(self, decision_result: Dict[str, Any]) -> float:
        """Calculate decision clarity factor"""
        criteria_scores = decision_result.get("decision_criteria", {}).get("criteria_scores", {})
        total_criteria = decision_result.get("decision_criteria", {}).get("total_criteria_score", 0)
        
        # Clear decision if criteria are strongly in one direction
        if total_criteria >= 7 or total_criteria <= 2:
            return 1.0
        elif total_criteria >= 5 or total_criteria <= 4:
            return 0.7
        else:
            return 0.4  # Borderline decisions are less clear
    
    def _calculate_evidence_strength(self, evidence_summary: Dict[str, Any]) -> float:
        """Calculate evidence strength factor"""
        expected_count = evidence_summary.get("expected_features", 0)
        delivered_count = evidence_summary.get("delivered_features", 0)
        
        if expected_count == 0:
            return 0.5  # No expectations to measure against
        
        delivery_ratio = delivered_count / expected_count
        if delivery_ratio >= 0.9:
            return 1.0
        elif delivery_ratio >= 0.7:
            return 0.8
        elif delivery_ratio >= 0.5:
            return 0.6
        else:
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
        """Identify specific reasons for escalation"""
        reasons = []
        
        if confidence < self.confidence_threshold:
            reasons.append("low_confidence")
        
        if score_consistency < 0.7:
            reasons.append("score_inconsistency")
        
        if signal_alignment < 0.5:
            reasons.append("signal_misalignment")
        
        if quality_grade == "D" and pac_detection.get("pac_score", 0) >= 3:
            reasons.append("conflicting_quality_signals")
        
        delivery_ratio = evidence_summary.get("delivery_ratio", 1.0)
        if 0.4 <= delivery_ratio <= 0.6:  # Borderline delivery
            reasons.append("borderline_delivery")
        
        return reasons
    
    def _create_escalation_case(
        self,
        evaluation_result: Dict[str, Any],
        decision_result: Dict[str, Any],
        supporting_signals: Dict[str, Any],
        confidence_metrics: ConfidenceMetrics,
        trace_id: str
    ) -> EscalationCase:
        """Create escalation case for human review"""
        
        case_id = f"esc-{datetime.now().strftime('%Y%m%d%H%M%S')}-{trace_id[:8]}"
        
        escalation_case = EscalationCase(
            case_id=case_id,
            trace_id=trace_id,
            timestamp=datetime.now().isoformat(),
            reason=EscalationReason.LOW_CONFIDENCE,
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
            status=EscalationStatus.PENDING
        )
        
        # Store escalation case
        self.escalation_cases[case_id] = escalation_case
        
        return escalation_case
    
    def get_pending_escalations(self) -> List[Dict[str, Any]]:
        """Get all pending escalation cases"""
        pending_cases = []
        
        for case in self.escalation_cases.values():
            if case.status == EscalationStatus.PENDING:
                pending_cases.append({
                    "case_id": case.case_id,
                    "trace_id": case.trace_id,
                    "timestamp": case.timestamp,
                    "confidence": case.confidence,
                    "reasons": case.escalation_context.get("escalation_reasons", []),
                    "task_title": case.original_evaluation.get("task_title", "Unknown"),
                    "score": case.original_decision.get("score", 0),
                    "decision": case.original_decision.get("decision", "unknown")
                })
        
        return pending_cases

# Global human-in-loop service
human_in_loop = HumanInLoopService()