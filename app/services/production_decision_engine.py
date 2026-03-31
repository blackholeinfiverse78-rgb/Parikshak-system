"""
Parikshak Production Decision Engine — Phase 5
Rules:
  score >= 6.0 → APPROVED
  score <  6.0 → REJECTED
Generates: strengths, failures, root_cause, learning_feedback, next_direction
Also runs: P/A/C enrichment, quality rubric, effort scoring, confidence
"""
from typing import Dict, Any, List
import logging
from dataclasses import dataclass

logger = logging.getLogger("decision_engine")


@dataclass
class QualityRubric:
    Q_proof: float
    Q_architecture: float
    Q_code: float

    @property
    def total_quality(self) -> float:
        return self.Q_proof + self.Q_architecture + self.Q_code

    @property
    def quality_grade(self) -> str:
        t = self.total_quality
        if t >= 8: return "A"
        elif t >= 6: return "B"
        elif t >= 4: return "C"
        return "D"


@dataclass
class EffortScore:
    description_depth: float
    repo_recency: float
    requirement_coverage: float

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
        return round(min(self.total_effort / 9.0, 1.0), 3)


@dataclass
class PACDetection:
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
    Phase 5 Decision Engine.
    Operates on score_10 (0–10 scale from assignment engine).
    score_10 >= 6 → APPROVED, else REJECTED.
    """

    APPROVAL_THRESHOLD = 6.0

    def __init__(self):
        self.pac_keywords = {
            "pass":     ["pass", "passed", "success", "complete", "completed", "done", "finished", "ready"],
            "approve":  ["approve", "approved", "accept", "accepted", "good", "excellent", "satisfactory", "meets"],
            "complete": ["complete", "completed", "finished", "done", "implemented", "delivered", "working", "functional"]
        }

    def make_decision(
        self,
        evaluation_result: Dict[str, Any],
        supporting_signals: Dict[str, Any],
        packet_data: Any = None
    ) -> Dict[str, Any]:
        logger.info("[DECISION ENGINE] Making Phase 5 decision")

        # Use score_10 if available, else derive from score_100
        score_10 = evaluation_result.get("score_10") or round(evaluation_result.get("score", 0) / 10, 2)
        rubric_from_engine = evaluation_result.get("rubric", {})

        # P/A/C enrichment
        pac = self._enrich_pac(evaluation_result, supporting_signals)

        # Quality rubric (continuous, for bonus/confidence)
        quality_rubric = self._assess_quality_rubric(evaluation_result, supporting_signals)

        # Effort scoring
        effort_score = self._assess_effort_score(evaluation_result, supporting_signals)

        # Phase 5 decision — strict threshold on 0–10 scale
        decision, task_type, confidence = self._apply_decision_logic(
            score_10, quality_rubric, pac, effort_score
        )

        # Phase 5 narrative output
        narrative = self._generate_narrative(
            score_10, decision, evaluation_result, supporting_signals,
            rubric_from_engine, quality_rubric, pac
        )

        output = {
            # Core decision (Phase 5)
            "score": score_10,
            "score_100": round(score_10 * 10),
            "decision": decision,
            "confidence": confidence,
            "task_type": task_type,
            "approval_threshold": self.APPROVAL_THRESHOLD,
            "threshold_met": score_10 >= self.APPROVAL_THRESHOLD,

            # Phase 5 narrative
            "strengths":         narrative["strengths"],
            "failures":          narrative["failures"],
            "root_cause":        narrative["root_cause"],
            "learning_feedback": narrative["learning_feedback"],
            "next_direction":    narrative["next_direction"],

            # Quality rubric
            "quality_rubric": {
                "Q_proof":        quality_rubric.Q_proof,
                "Q_architecture": quality_rubric.Q_architecture,
                "Q_code":         quality_rubric.Q_code,
                "total_quality":  quality_rubric.total_quality,
                "quality_grade":  quality_rubric.quality_grade
            },

            # Effort / authenticity
            "effort_score": {
                "description_depth":    effort_score.description_depth,
                "repo_recency":         effort_score.repo_recency,
                "requirement_coverage": effort_score.requirement_coverage,
                "total_effort":         effort_score.total_effort,
                "effort_grade":         effort_score.effort_grade,
                "authenticity_score":   effort_score.authenticity_score
            },

            # P/A/C
            "pac_detection": {
                "pass_indicators":     pac.pass_indicators,
                "approve_indicators":  pac.approve_indicators,
                "complete_indicators": pac.complete_indicators,
                "pac_score":           pac.pac_score,
                "has_pac_signals":     pac.has_pac_signals
            },

            # Decision criteria
            "decision_criteria": {
                "score_10":              score_10,
                "approval_threshold":    self.APPROVAL_THRESHOLD,
                "approval_threshold_met": score_10 >= self.APPROVAL_THRESHOLD,
            },

            # Metadata
            "decision_metadata": {
                "engine":             "parikshak_decision_engine",
                "version":            "2.0",
                "phase":              5,
                "standardized_output": True,
                "rubric_applied":     True,
                "pac_detected":       True,
                "caps_applied":       True,
                "effort_scored":      True
            }
        }

        logger.info(f"[DECISION ENGINE] Decision: {decision} | score_10={score_10} | confidence={confidence:.3f}")
        return output

    # ── Phase 5 decision logic ────────────────────────────────────────────

    def _apply_decision_logic(
        self,
        score_10: float,
        quality_rubric: QualityRubric,
        pac: PACDetection,
        effort_score: EffortScore
    ):
        """score >= 6 → APPROVED, else REJECTED"""
        if score_10 >= self.APPROVAL_THRESHOLD:
            decision  = "APPROVED"
            task_type = "advancement"
            # Confidence increases with margin above threshold
            margin    = score_10 - self.APPROVAL_THRESHOLD
            confidence = min(0.99, 0.80 + margin * 0.04)
        else:
            decision  = "REJECTED"
            task_type = "correction" if score_10 < 4.0 else "reinforcement"
            # Confidence increases as score is clearly below threshold
            gap        = self.APPROVAL_THRESHOLD - score_10
            confidence = min(0.99, 0.70 + gap * 0.04)

        return decision, task_type, round(confidence, 3)

    # ── Phase 5 narrative generation ─────────────────────────────────────

    def _generate_narrative(
        self,
        score_10: float,
        decision: str,
        evaluation_result: Dict[str, Any],
        supporting_signals: Dict[str, Any],
        rubric_from_engine: Dict[str, int],
        quality_rubric: QualityRubric,
        pac: PACDetection
    ) -> Dict[str, Any]:
        """Generate strengths, failures, root_cause, learning_feedback, next_direction"""

        missing    = supporting_signals.get("missing_features", [])
        indicators = supporting_signals.get("failure_indicators", [])
        evd        = supporting_signals.get("expected_vs_delivered_evidence", {})
        delivery   = evd.get("delivery_ratio", 0.0)
        repo_ok    = supporting_signals.get("repository_available", False)
        breakdown  = evaluation_result.get("score_breakdown", {})

        strengths         = []
        failures          = []
        root_cause        = ""
        learning_feedback = []
        next_direction    = ""

        # Strengths
        if rubric_from_engine.get("Q_code", 0) == 1:
            strengths.append("Implementation is present and accessible via repository")
        if rubric_from_engine.get("Q_architecture", 0) == 1:
            strengths.append("Architecture signals detected — layered or modular structure present")
        if rubric_from_engine.get("Q_proof", 0) == 1:
            strengths.append("Proof of work present — README, tests, or documentation found")
        if rubric_from_engine.get("alignment_score", 0) == 1:
            strengths.append("Requirements alignment is strong — delivery ratio above threshold")
        if rubric_from_engine.get("effort_score", 0) == 1:
            strengths.append("Effort is evident — structured description and documentation present")
        if delivery >= 0.8:
            strengths.append(f"High feature delivery ratio: {delivery:.0%}")
        if not strengths:
            strengths.append("Submission received and processed")

        # Failures
        if not repo_ok:
            failures.append("No accessible GitHub repository provided")
        if rubric_from_engine.get("Q_proof", 0) == 0:
            failures.append("No proof of working output — missing README, tests, or logs")
        if rubric_from_engine.get("Q_architecture", 0) == 0:
            failures.append("No architecture signals — flat or unstructured repository")
        if rubric_from_engine.get("Q_code", 0) == 0:
            failures.append("No code present or repository is empty")
        if rubric_from_engine.get("alignment_score", 0) == 0:
            failures.append(f"Low requirement alignment — delivery ratio {delivery:.0%}, {len(missing)} features missing")
        if missing:
            failures.append(f"Missing features: {', '.join(missing[:5])}")
        for ind in indicators[:3]:
            failures.append(f"Signal: {ind}")

        # Root cause
        if not repo_ok:
            root_cause = "No repository submitted — evaluation cannot verify implementation"
        elif rubric_from_engine.get("Q_code", 0) == 0:
            root_cause = "Repository exists but contains no evaluable code files"
        elif rubric_from_engine.get("alignment_score", 0) == 0:
            root_cause = f"Implementation does not cover stated requirements — {len(missing)} features undelivered"
        elif rubric_from_engine.get("Q_proof", 0) == 0:
            root_cause = "Implementation present but no proof of correctness — add tests or documentation"
        elif score_10 >= self.APPROVAL_THRESHOLD:
            root_cause = "All core criteria met — submission approved"
        else:
            root_cause = f"Score {score_10:.1f}/10 below approval threshold of {self.APPROVAL_THRESHOLD}"

        # Learning feedback
        if rubric_from_engine.get("Q_proof", 0) == 0:
            learning_feedback.append("Add a README with setup instructions and sample output")
            learning_feedback.append("Include at least one test file demonstrating working functionality")
        if rubric_from_engine.get("Q_architecture", 0) == 0:
            learning_feedback.append("Organise code into layers: api/, service/, model/ or equivalent")
        if rubric_from_engine.get("alignment_score", 0) == 0:
            learning_feedback.append("Re-read the task requirements and map each requirement to a file/function")
        if missing:
            learning_feedback.append(f"Implement missing features: {', '.join(missing[:3])}")
        if not learning_feedback:
            learning_feedback.append("Maintain current quality and expand test coverage for next task")

        # Next direction
        if decision == "APPROVED":
            next_direction = "Advance to next complexity level — focus on performance, scalability, or new domain"
        elif score_10 >= 4.0:
            next_direction = "Reinforce current task — address missing features and add proof of correctness"
        else:
            next_direction = "Restart with fundamentals — ensure repository, architecture, and proof are all present"

        return {
            "strengths":         strengths,
            "failures":          failures,
            "root_cause":        root_cause,
            "learning_feedback": learning_feedback,
            "next_direction":    next_direction
        }

    # ── P/A/C enrichment (text-based, supplements engine binary) ─────────

    def _enrich_pac(
        self,
        evaluation_result: Dict[str, Any],
        supporting_signals: Dict[str, Any]
    ) -> PACDetection:
        text_sources = [
            evaluation_result.get("evaluation_summary", ""),
            str(evaluation_result.get("improvement_hints", [])),
            str(supporting_signals.get("title_signals", {})),
            str(supporting_signals.get("description_signals", {}))
        ]
        combined = " ".join(text_sources).lower()

        pass_ind     = list({kw for kw in self.pac_keywords["pass"]     if kw in combined})
        approve_ind  = list({kw for kw in self.pac_keywords["approve"]  if kw in combined})
        complete_ind = list({kw for kw in self.pac_keywords["complete"] if kw in combined})

        if evaluation_result.get("score_10", 0) >= 8.0:
            pass_ind.append("high_score")
        if supporting_signals.get("repository_available", False):
            complete_ind.append("implementation_present")
        evd = supporting_signals.get("expected_vs_delivered_evidence", {})
        if evd.get("delivery_ratio", 0) >= 0.8:
            complete_ind.append("high_delivery_ratio")

        return PACDetection(
            pass_indicators=list(set(pass_ind)),
            approve_indicators=list(set(approve_ind)),
            complete_indicators=list(set(complete_ind))
        )

    # ── Quality rubric (continuous, for confidence/grade) ─────────────────

    def _assess_quality_rubric(
        self,
        evaluation_result: Dict[str, Any],
        supporting_signals: Dict[str, Any]
    ) -> QualityRubric:
        evd          = evaluation_result.get("evidence_summary", {})
        delivery     = evd.get("delivery_ratio", 0)
        missing_cnt  = evd.get("missing_features_count", 0)
        repo_signals = supporting_signals.get("repository_signals") or {}
        arch         = repo_signals.get("architecture", {})
        quality      = repo_signals.get("quality", {})

        q_proof = (3.0 if delivery >= 0.9 and missing_cnt == 0
                   else 2.0 if delivery >= 0.7 and missing_cnt <= 2
                   else 1.0 if delivery >= 0.4 and missing_cnt <= 5
                   else 0.0)

        lc = arch.get("layer_count", 0)
        hl = arch.get("has_layers", False)
        mo = arch.get("modular", False)
        q_arch = (3.0 if lc >= 3 and hl and mo
                  else 2.0 if lc >= 2 and (hl or mo)
                  else 1.0 if mo or lc >= 1
                  else 0.0)

        readme = quality.get("readme_score", 0)
        doc_d  = quality.get("documentation_density", 0)
        files  = repo_signals.get("structure", {}).get("total_files", 0)
        q_code = (3.0 if readme >= 2 and doc_d >= 0.3 and files >= 10
                  else 2.0 if readme >= 1 and doc_d >= 0.1 and files >= 5
                  else 1.0 if readme >= 1 or files >= 3
                  else 0.0)

        return QualityRubric(Q_proof=q_proof, Q_architecture=q_arch, Q_code=q_code)

    # ── Effort scoring ────────────────────────────────────────────────────

    def _assess_effort_score(
        self,
        evaluation_result: Dict[str, Any],
        supporting_signals: Dict[str, Any]
    ) -> EffortScore:
        ds         = supporting_signals.get("description_signals") or {}
        wc         = ds.get("word_count", 0) if isinstance(ds, dict) else 0
        sq         = ds.get("structure_quality", 0) if isinstance(ds, dict) else 0
        repo_ok    = supporting_signals.get("repository_available", False)
        file_count = supporting_signals.get("implementation_files", 0)
        expected   = len(supporting_signals.get("expected_features", []))
        implemented = len(supporting_signals.get("implemented_features", []))

        depth = (3.0 if wc >= 150 and sq >= 0.5
                 else 2.0 if wc >= 80 and sq >= 0.2
                 else 1.0 if wc >= 30
                 else 0.0)

        recency = (3.0 if repo_ok and file_count >= 10
                   else 2.0 if repo_ok and file_count >= 5
                   else 1.0 if repo_ok
                   else 0.0)

        cov_ratio = (implemented / expected) if expected > 0 else 1.0
        coverage  = (3.0 if cov_ratio >= 0.8
                     else 2.0 if cov_ratio >= 0.5
                     else 1.0 if cov_ratio >= 0.2
                     else 0.0)

        return EffortScore(
            description_depth=depth,
            repo_recency=recency,
            requirement_coverage=coverage
        )


# Global instance
production_decision_engine = ProductionDecisionEngine()
