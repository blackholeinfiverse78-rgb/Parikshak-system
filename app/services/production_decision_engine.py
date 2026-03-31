"""
Production Decision Engine - Standardized Output with Quality Rubric
Implements P/A/C detection, quality rubric (Q_proof, Q_architecture, Q_code), and ≥6 approval logic
"""
from typing import Dict, Any, List
import logging
from dataclasses import dataclass

logger = logging.getLogger("decision_engine")

@dataclass
class QualityRubric:
    """Quality assessment rubric"""
    Q_proof: float      # Evidence quality (0-3)
    Q_architecture: float  # Architecture quality (0-3) 
    Q_code: float       # Code quality (0-3)
    
    @property
    def total_quality(self) -> float:
        return self.Q_proof + self.Q_architecture + self.Q_code
    
    @property
    def quality_grade(self) -> str:
        total = self.total_quality
        if total >= 8: return "A"
        elif total >= 6: return "B" 
        elif total >= 4: return "C"
        else: return "D"

@dataclass
class EffortScore:
    """Effort and authenticity scoring — separate dimension from outcome"""
    description_depth: float    # 0-3: word count + structure quality
    repo_recency: float         # 0-3: repo available + file count signals
    requirement_coverage: float # 0-3: how many stated requirements have evidence

    @property
    def total_effort(self) -> float:
        return self.description_depth + self.repo_recency + self.requirement_coverage

    @property
    def effort_grade(self) -> str:
        t = self.total_effort
        if t >= 8: return "HIGH"
        elif t >= 5: return "MEDIUM"
        elif t >= 2: return "LOW"
        return "NONE"

    @property
    def authenticity_score(self) -> float:
        """0.0-1.0: penalises zero-effort submissions regardless of outcome"""
        return round(min(self.total_effort / 9.0, 1.0), 3)


@dataclass
class PACDetection:
    """Pass/Approve/Complete detection results"""
    pass_indicators: List[str]
    approve_indicators: List[str] 
    complete_indicators: List[str]
    
    @property
    def pac_score(self) -> int:
        return len(self.pass_indicators) + len(self.approve_indicators) + len(self.complete_indicators)
    
    @property
    def has_pac_signals(self) -> bool:
        return self.pac_score > 0

class ProductionDecisionEngine:
    """
    Production-ready decision engine with standardized output
    Implements quality rubric, P/A/C detection, and ≥6 approval logic
    """
    
    # Domain-specific feature keyword sets used by domain router
    DOMAIN_FEATURE_SETS: Dict[str, list] = None

    def __init__(self):
        self.approval_threshold = 6  # ≥6 for approval
        self.pac_keywords = {
            "pass": ["pass", "passed", "passing", "success", "successful", "complete", "completed", "done", "finished", "ready"],
            "approve": ["approve", "approved", "accept", "accepted", "good", "excellent", "satisfactory", "meets"],
            "complete": ["complete", "completed", "finished", "done", "implemented", "delivered", "working", "functional"]
        }
    
    def make_decision(
        self, 
        evaluation_result: Dict[str, Any],
        supporting_signals: Dict[str, Any],
        packet_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Make production decision with standardized output
        
        Returns:
            Standardized decision with quality rubric and P/A/C detection
        """
        logger.info("[DECISION ENGINE] Making production decision")
        
        # Extract core metrics
        score = evaluation_result.get("score", 0)
        status = evaluation_result.get("status", "fail")
        
        # Phase 1: P/A/C Detection
        pac_detection = self._detect_pac_signals(evaluation_result, supporting_signals)
        logger.info(f"[DECISION ENGINE] P/A/C signals detected: {pac_detection.pac_score}")

        # Phase 2: Effort / Authenticity Scoring (separate dimension)
        effort_score = self._assess_effort_score(evaluation_result, supporting_signals)
        logger.info(f"[DECISION ENGINE] Effort grade: {effort_score.effort_grade} (authenticity: {effort_score.authenticity_score:.3f})")

        # Phase 3: Quality Rubric Assessment
        quality_rubric = self._assess_quality_rubric(evaluation_result, supporting_signals)
        logger.info(f"[DECISION ENGINE] Quality grade: {quality_rubric.quality_grade} (total: {quality_rubric.total_quality:.1f}/9)")

        # Phase 4: Final Score Computation with caps
        final_score = self._compute_final_score(score, quality_rubric, pac_detection, effort_score)

        # Phase 5: Decision Logic (≥6 approve)
        decision = self._apply_decision_logic(final_score, quality_rubric, pac_detection, effort_score)

        # Phase 6: Structure standardized output
        standardized_output = self._structure_output(
            final_score, decision, quality_rubric, pac_detection,
            effort_score, evaluation_result, supporting_signals
        )
        
        logger.info(f"[DECISION ENGINE] Final decision: {decision['status']} (score: {final_score})")
        return standardized_output
    
    def _detect_pac_signals(
        self, 
        evaluation_result: Dict[str, Any], 
        supporting_signals: Dict[str, Any]
    ) -> PACDetection:
        """Detect Pass/Approve/Complete signals in evaluation data"""
        
        # Combine all text for analysis
        text_sources = [
            evaluation_result.get("evaluation_summary", ""),
            str(evaluation_result.get("improvement_hints", [])),
            str(supporting_signals.get("title_signals", {})),
            str(supporting_signals.get("description_signals", {}))
        ]
        combined_text = " ".join(text_sources).lower()
        
        pass_indicators = []
        approve_indicators = []
        complete_indicators = []
        
        # Detect keywords
        for keyword in self.pac_keywords["pass"]:
            if keyword in combined_text:
                pass_indicators.append(keyword)
        
        for keyword in self.pac_keywords["approve"]:
            if keyword in combined_text:
                approve_indicators.append(keyword)
                
        for keyword in self.pac_keywords["complete"]:
            if keyword in combined_text:
                complete_indicators.append(keyword)
        
        # Additional signal detection from metrics
        if evaluation_result.get("score", 0) >= 80:
            pass_indicators.append("high_score")
        
        if supporting_signals.get("repository_available", False):
            complete_indicators.append("implementation_present")
        
        delivery_ratio = supporting_signals.get("expected_vs_delivered_evidence", {}).get("delivery_ratio", 0)
        if delivery_ratio >= 0.8:
            complete_indicators.append("high_delivery_ratio")
        
        return PACDetection(
            pass_indicators=list(set(pass_indicators)),
            approve_indicators=list(set(approve_indicators)),
            complete_indicators=list(set(complete_indicators))
        )
    
    def _assess_quality_rubric(
        self, 
        evaluation_result: Dict[str, Any], 
        supporting_signals: Dict[str, Any]
    ) -> QualityRubric:
        """Assess quality using Q_proof, Q_architecture, Q_code rubric"""
        
        # Q_proof: Evidence quality (0-3)
        evidence_summary = evaluation_result.get("evidence_summary", {})
        delivery_ratio = evidence_summary.get("delivery_ratio", 0)
        missing_count = evidence_summary.get("missing_features_count", 0)
        
        if delivery_ratio >= 0.9 and missing_count == 0:
            q_proof = 3.0  # Excellent evidence
        elif delivery_ratio >= 0.7 and missing_count <= 2:
            q_proof = 2.0  # Good evidence
        elif delivery_ratio >= 0.4 and missing_count <= 5:
            q_proof = 1.0  # Basic evidence
        else:
            q_proof = 0.0  # Poor evidence
        
        # Q_architecture: Architecture quality (0-3)
        repo_signals = supporting_signals.get("repository_signals", {})
        architecture_signals = repo_signals.get("architecture", {})
        
        layer_count = architecture_signals.get("layer_count", 0)
        has_layers = architecture_signals.get("has_layers", False)
        is_modular = architecture_signals.get("modular", False)
        
        if layer_count >= 3 and has_layers and is_modular:
            q_architecture = 3.0  # Excellent architecture
        elif layer_count >= 2 and (has_layers or is_modular):
            q_architecture = 2.0  # Good architecture
        elif is_modular or layer_count >= 1:
            q_architecture = 1.0  # Basic architecture
        else:
            q_architecture = 0.0  # Poor architecture
        
        # Q_code: Code quality (0-3)
        quality_signals = repo_signals.get("quality", {})
        readme_score = quality_signals.get("readme_score", 0)
        doc_density = quality_signals.get("documentation_density", 0)
        file_count = repo_signals.get("structure", {}).get("total_files", 0)
        
        if readme_score >= 2 and doc_density >= 0.3 and file_count >= 10:
            q_code = 3.0  # Excellent code quality
        elif readme_score >= 1 and doc_density >= 0.1 and file_count >= 5:
            q_code = 2.0  # Good code quality
        elif readme_score >= 1 or file_count >= 3:
            q_code = 1.0  # Basic code quality
        else:
            q_code = 0.0  # Poor code quality
        
        return QualityRubric(
            Q_proof=q_proof,
            Q_architecture=q_architecture,
            Q_code=q_code
        )
    
    def _assess_effort_score(
        self,
        evaluation_result: Dict[str, Any],
        supporting_signals: Dict[str, Any]
    ) -> EffortScore:
        """Score effort and authenticity as a separate dimension from outcome quality"""

        # description_depth: based on description signal depth
        desc_signals = supporting_signals.get("description_signals", {})
        word_count = desc_signals.get("word_count", 0) if isinstance(desc_signals, dict) else 0
        structure_score = desc_signals.get("structure_quality", 0) if isinstance(desc_signals, dict) else 0
        if word_count >= 150 and structure_score >= 0.5:
            description_depth = 3.0
        elif word_count >= 80 and structure_score >= 0.2:
            description_depth = 2.0
        elif word_count >= 30:
            description_depth = 1.0
        else:
            description_depth = 0.0

        # repo_recency: repo present + meaningful file count
        repo_available = supporting_signals.get("repository_available", False)
        file_count = supporting_signals.get("implementation_files", 0)
        if repo_available and file_count >= 10:
            repo_recency = 3.0
        elif repo_available and file_count >= 5:
            repo_recency = 2.0
        elif repo_available:
            repo_recency = 1.0
        else:
            repo_recency = 0.0

        # requirement_coverage: how many stated requirements have matching evidence
        expected = len(supporting_signals.get("expected_features", []))
        implemented = len(supporting_signals.get("implemented_features", []))
        if expected == 0:
            coverage_ratio = 1.0
        else:
            coverage_ratio = implemented / expected
        if coverage_ratio >= 0.8:
            requirement_coverage = 3.0
        elif coverage_ratio >= 0.5:
            requirement_coverage = 2.0
        elif coverage_ratio >= 0.2:
            requirement_coverage = 1.0
        else:
            requirement_coverage = 0.0

        return EffortScore(
            description_depth=description_depth,
            repo_recency=repo_recency,
            requirement_coverage=requirement_coverage
        )

    def _compute_final_score(
        self,
        base_score: int,
        quality_rubric: QualityRubric,
        pac_detection: PACDetection,
        effort_score: EffortScore
    ) -> int:
        """Compute final score with alignment, authenticity, and proof caps"""

        final_score = base_score

        # Apply quality rubric bonus (max +15 points)
        quality_bonus = min(int(quality_rubric.total_quality * 1.67), 15)
        final_score += quality_bonus

        # Apply P/A/C detection bonus (max +10 points)
        pac_bonus = min(pac_detection.pac_score * 2, 10)
        final_score += pac_bonus

        # Apply effort bonus (max +5 points) — rewards genuine work
        effort_bonus = min(int(effort_score.total_effort * 0.55), 5)
        final_score += effort_bonus

        # Alignment cap: If delivery ratio < 0.5, cap at 60
        evidence_summary = {}
        delivery_ratio = evidence_summary.get("delivery_ratio", 1.0)
        if delivery_ratio < 0.5:
            final_score = min(final_score, 60)
            logger.info(f"[DECISION ENGINE] Alignment cap applied: delivery_ratio={delivery_ratio:.2f}")

        # repo_available needed for effort-based authenticity cap
        repo_available = "implementation_present" in (pac_detection.complete_indicators or [])
        # Authenticity cap: driven by effort score — NONE effort caps at 20, LOW at 40
        if effort_score.effort_grade == "NONE":
            final_score = min(final_score, 20)
            logger.info("[DECISION ENGINE] Authenticity cap: NONE effort → cap 20")
        elif effort_score.effort_grade == "LOW" and not repo_available:
            final_score = min(final_score, 40)
            logger.info("[DECISION ENGINE] Authenticity cap: LOW effort + no repo → cap 40")
        
        # Legacy authenticity cap: If no repository, cap at 40
        if not pac_detection.complete_indicators or "implementation_present" not in pac_detection.complete_indicators:
            final_score = min(final_score, 40)
            logger.info("[DECISION ENGINE] Authenticity cap applied: no implementation")
        
        # Proof cap: If quality grade D, cap at 30
        if quality_rubric.quality_grade == "D":
            final_score = min(final_score, 30)
            logger.info("[DECISION ENGINE] Proof cap applied: quality grade D")
        
        # Ensure bounds
        final_score = max(0, min(100, final_score))
        
        logger.info(f"[DECISION ENGINE] Score computation: base={base_score}, quality_bonus={quality_bonus}, pac_bonus={pac_bonus}, final={final_score}")
        return final_score
    
    def _apply_decision_logic(
        self,
        final_score: int,
        quality_rubric: QualityRubric,
        pac_detection: PACDetection,
        effort_score: EffortScore
    ) -> Dict[str, Any]:
        """Apply ≥6 approval logic and determine final decision"""
        
        # Decision criteria scoring (0-11 scale — effort adds 1 point)
        criteria_scores = {
            "score_threshold": 3 if final_score >= 75 else 2 if final_score >= 60 else 1 if final_score >= 40 else 0,
            "quality_grade": 3 if quality_rubric.quality_grade == "A" else 2 if quality_rubric.quality_grade == "B" else 1 if quality_rubric.quality_grade == "C" else 0,
            "pac_signals": 2 if pac_detection.pac_score >= 5 else 1 if pac_detection.pac_score >= 2 else 0,
            "evidence_strength": 2 if quality_rubric.Q_proof >= 2 else 1 if quality_rubric.Q_proof >= 1 else 0,
            "effort_authenticity": 1 if effort_score.effort_grade in ("HIGH", "MEDIUM") else 0
        }
        
        total_criteria_score = sum(criteria_scores.values())
        
        # ≥6 approval logic
        if total_criteria_score >= 6:
            decision_status = "approve"
            task_type = "advancement"
            confidence = min(0.95, 0.7 + (total_criteria_score - 6) * 0.05)
        elif total_criteria_score >= 4:
            decision_status = "conditional"
            task_type = "reinforcement"
            confidence = 0.6 + (total_criteria_score - 4) * 0.05
        else:
            decision_status = "reject"
            task_type = "correction"
            confidence = 0.4 + total_criteria_score * 0.05
        
        return {
            "status": decision_status,
            "task_type": task_type,
            "confidence": confidence,
            "criteria_scores": criteria_scores,
            "total_criteria_score": total_criteria_score,
            "approval_threshold_met": total_criteria_score >= 6
        }
    
    def _structure_output(
        self,
        final_score: int,
        decision: Dict[str, Any],
        quality_rubric: QualityRubric,
        pac_detection: PACDetection,
        effort_score: EffortScore,
        evaluation_result: Dict[str, Any],
        supporting_signals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Structure standardized output exactly as defined"""

        return {
            # Core decision
            "score": final_score,
            "decision": decision["status"],
            "confidence": decision["confidence"],
            "task_type": decision["task_type"],

            # Quality rubric
            "quality_rubric": {
                "Q_proof": quality_rubric.Q_proof,
                "Q_architecture": quality_rubric.Q_architecture,
                "Q_code": quality_rubric.Q_code,
                "total_quality": quality_rubric.total_quality,
                "quality_grade": quality_rubric.quality_grade
            },

            # Effort / authenticity (separate scored dimension)
            "effort_score": {
                "description_depth": effort_score.description_depth,
                "repo_recency": effort_score.repo_recency,
                "requirement_coverage": effort_score.requirement_coverage,
                "total_effort": effort_score.total_effort,
                "effort_grade": effort_score.effort_grade,
                "authenticity_score": effort_score.authenticity_score
            },

            # P/A/C detection
            "pac_detection": {
                "pass_indicators": pac_detection.pass_indicators,
                "approve_indicators": pac_detection.approve_indicators,
                "complete_indicators": pac_detection.complete_indicators,
                "pac_score": pac_detection.pac_score,
                "has_pac_signals": pac_detection.has_pac_signals
            },

            # Decision criteria
            "decision_criteria": {
                "criteria_scores": decision["criteria_scores"],
                "total_criteria_score": decision["total_criteria_score"],
                "approval_threshold_met": decision["approval_threshold_met"],
                "threshold": self.approval_threshold
            },

            # Metadata
            "decision_metadata": {
                "engine": "production_decision_engine",
                "version": "1.1",
                "standardized_output": True,
                "rubric_applied": True,
                "pac_detected": True,
                "caps_applied": True,
                "effort_scored": True
            }
        }

# Global decision engine instance
production_decision_engine = ProductionDecisionEngine()