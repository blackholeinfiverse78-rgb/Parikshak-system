"""
Parikshak Assignment Engine — SINGLE EVALUATION AUTHORITY
Phase 2: Binary P/A/C detection
Phase 3: Quality rubric (Q_proof, Q_architecture, Q_code, alignment, authenticity, effort) — all binary 0/1
Phase 4: Exact scoring formula on 0–10 scale
  final_score = 0.35*completeness + 0.25*quality + 0.20*alignment + 0.10*authenticity + 0.10*effort
"""
from typing import Dict, Any
import logging
from datetime import datetime
from ..models.next_task_model import NextTask
from .decision_rules import DecisionRules
from .architecture_guard import ArchitectureGuard

logger = logging.getLogger("assignment_engine")


class AssignmentEngine:
    """
    SINGLE EVALUATION AUTHORITY.
    Implements the exact Parikshak Phase 2–4 scoring protocol.
    No heuristics. No parallel paths. Deterministic.
    """

    def __init__(self):
        self.authority_level = "CANONICAL_PRIMARY"
        self.rules = DecisionRules()
        self.guard = ArchitectureGuard()

    # ── Public entry point ────────────────────────────────────────────────

    def evaluate_and_assign(
        self,
        task_title: str,
        task_description: str,
        supporting_signals: Dict[str, Any]
    ) -> Dict[str, Any]:
        logger.info(f"[ASSIGNMENT ENGINE] Evaluating: {task_title[:60]}...")

        # Phase 2: Binary P/A/C detection
        pac = self._detect_pac(supporting_signals)

        # Phase 3: Binary quality rubric
        rubric = self._score_rubric(supporting_signals, pac)

        # Phase 4: Exact formula → score on 0–10
        score_10, score_breakdown = self._compute_score(rubric, supporting_signals)

        # Map 0–10 → 0–100 for downstream compatibility
        score_100 = round(score_10 * 10)
        status = self._determine_status(score_10)

        # Evidence summary for downstream engines
        evd = supporting_signals.get("expected_vs_delivered_evidence", {})
        evidence_summary = {
            "expected_features": evd.get("expected_count", 0),
            "delivered_features": evd.get("delivered_count", 0),
            "missing_features_count": len(supporting_signals.get("missing_features", [])),
            "failure_indicators_count": len(supporting_signals.get("failure_indicators", [])),
            "delivery_ratio": evd.get("delivery_ratio", 0.0)
        }

        # Component scores (kept for downstream/UI compatibility, derived from rubric)
        title_score   = self._title_score_compat(supporting_signals)
        desc_score    = self._desc_score_compat(supporting_signals)
        repo_score    = self._repo_score_compat(supporting_signals)

        # Next task generation
        next_task = self._generate_next_task(score_10, status, supporting_signals)

        result = {
            # Core
            "score": score_100,
            "score_10": round(score_10, 2),
            "status": status,
            "readiness_percent": score_100,

            # Phase 2 — P/A/C
            "pac": pac,

            # Phase 3 — rubric
            "rubric": rubric,

            # Phase 4 — score breakdown
            "score_breakdown": score_breakdown,

            # Component scores (UI compat)
            "title_score": title_score,
            "description_score": desc_score,
            "repository_score": repo_score,

            # Evidence
            "evidence_summary": evidence_summary,

            # Authority markers
            "canonical_authority": True,
            "evaluation_basis": "parikshak_assignment_engine",
            "intelligence_source": "parikshak_canonical_engine",
            "evaluation_timestamp": datetime.now().isoformat(),

            # Next task
            **next_task
        }

        logger.info(
            f"[ASSIGNMENT ENGINE] Result: {status} | score_10={score_10:.2f} | "
            f"P={pac['proof']} A={pac['architecture']} C={pac['code']}"
        )
        return result

    # ── Phase 2: Binary P/A/C ─────────────────────────────────────────────

    def _detect_pac(self, signals: Dict[str, Any]) -> Dict[str, int]:
        """
        P = proof present (logs / output / test results)
        A = architecture present (flow + system design)
        C = code present (repo / implementation references)
        Returns binary {proof: 0/1, architecture: 0/1, code: 0/1}
        """
        repo_signals   = signals.get("repository_signals") or {}
        repo_available = signals.get("repository_available", False)
        desc_signals   = signals.get("description_signals") or {}
        title_signals  = signals.get("title_signals") or {}

        # C — code: repo is accessible and has files
        file_count = repo_signals.get("structure", {}).get("total_files", 0)
        code = 1 if (repo_available and file_count > 0) else 0

        # A — architecture: layered structure OR modular OR architecture keywords in description
        arch = repo_signals.get("architecture", {})
        has_layers = arch.get("has_layers", False) or arch.get("layer_count", 0) >= 2
        arch_keywords = {"architecture", "layer", "service", "module", "component",
                         "design", "flow", "pipeline", "orchestrat"}
        desc_text = str(desc_signals).lower()
        title_text = str(title_signals).lower()
        has_arch_keywords = any(kw in desc_text or kw in title_text for kw in arch_keywords)
        architecture = 1 if (has_layers or (code == 1 and has_arch_keywords)) else 0

        # P — proof: test files OR docs OR README with content
        quality = repo_signals.get("quality", {})
        readme_score = quality.get("readme_score", 0)
        components = repo_signals.get("components", {})
        test_files = components.get("tests", [])
        doc_files  = components.get("docs", [])
        proof = 1 if (readme_score >= 1 or len(test_files) > 0 or len(doc_files) > 0) else 0

        logger.info(f"[ASSIGNMENT ENGINE] P/A/C → proof={proof} architecture={architecture} code={code}")
        return {"proof": proof, "architecture": architecture, "code": code}

    # ── Phase 3: Binary quality rubric ───────────────────────────────────

    def _score_rubric(self, signals: Dict[str, Any], pac: Dict[str, int]) -> Dict[str, int]:
        """
        All criteria are binary (0 or 1). No subjective scoring.
        Returns dict with each criterion and derived dimension scores.
        """
        repo_signals   = signals.get("repository_signals") or {}
        repo_available = signals.get("repository_available", False)
        evd            = signals.get("expected_vs_delivered_evidence", {})
        delivery_ratio = evd.get("delivery_ratio", 0.0)
        missing        = signals.get("missing_features", [])
        desc_signals   = signals.get("description_signals") or {}
        word_count     = desc_signals.get("word_count", 0) if isinstance(desc_signals, dict) else 0
        structure_q    = desc_signals.get("structure_quality", 0) if isinstance(desc_signals, dict) else 0
        quality        = repo_signals.get("quality", {})
        readme_score   = quality.get("readme_score", 0)
        doc_density    = quality.get("documentation_density", 0)
        file_count     = repo_signals.get("structure", {}).get("total_files", 0)
        arch           = repo_signals.get("architecture", {})
        layer_count    = arch.get("layer_count", 0)
        is_modular     = arch.get("modular", False)

        # Q_proof: evidence of working output (binary)
        Q_proof = 1 if (pac["proof"] == 1 and delivery_ratio >= 0.5) else 0

        # Q_architecture: structured design present (binary)
        Q_architecture = 1 if (pac["architecture"] == 1 and (layer_count >= 2 or is_modular)) else 0

        # Q_code: real implementation present (binary)
        Q_code = 1 if (pac["code"] == 1 and file_count >= 3) else 0

        # alignment_score: requirements match implementation (binary)
        alignment_score = 1 if (delivery_ratio >= 0.6 and len(missing) <= 3) else 0

        # authenticity_score: genuine effort — repo + description depth (binary)
        authenticity_score = 1 if (repo_available and word_count >= 50) else 0

        # effort_score: description structured + README present (binary)
        effort_score = 1 if (word_count >= 80 and (readme_score >= 1 or structure_q >= 0.3)) else 0

        rubric = {
            "Q_proof": Q_proof,
            "Q_architecture": Q_architecture,
            "Q_code": Q_code,
            "alignment_score": alignment_score,
            "authenticity_score": authenticity_score,
            "effort_score": effort_score,
            # Derived totals for downstream
            "total_quality_binary": Q_proof + Q_architecture + Q_code,
            "rubric_sum": Q_proof + Q_architecture + Q_code + alignment_score + authenticity_score + effort_score
        }

        logger.info(
            f"[ASSIGNMENT ENGINE] Rubric → Q_proof={Q_proof} Q_arch={Q_architecture} "
            f"Q_code={Q_code} align={alignment_score} auth={authenticity_score} effort={effort_score}"
        )
        return rubric

    # ── Phase 4: Exact scoring formula ───────────────────────────────────

    def _compute_score(
        self,
        rubric: Dict[str, int],
        signals: Dict[str, Any]
    ):
        """
        Exact formula (all dimensions 0–1, result 0–10):
        final_score = 0.35*completeness + 0.25*quality + 0.20*alignment
                    + 0.10*authenticity + 0.10*effort

        Caps applied after formula:
        - No proof (Q_proof=0)       → cap at 4.0
        - No code  (Q_code=0)        → cap at 5.0
        - No alignment               → cap at 6.0
        """
        evd            = signals.get("expected_vs_delivered_evidence", {})
        delivery_ratio = evd.get("delivery_ratio", 0.0)

        # completeness: delivery ratio (0–1)
        completeness = min(delivery_ratio, 1.0)

        # quality: fraction of binary quality criteria met (Q_proof + Q_arch + Q_code) / 3
        quality = rubric["total_quality_binary"] / 3.0

        # alignment: binary → float
        alignment = float(rubric["alignment_score"])

        # authenticity: binary → float
        authenticity = float(rubric["authenticity_score"])

        # effort: binary → float
        effort = float(rubric["effort_score"])

        raw_score = (
            0.35 * completeness +
            0.25 * quality +
            0.20 * alignment +
            0.10 * authenticity +
            0.10 * effort
        ) * 10  # scale to 0–10

        # Apply caps
        capped_score = raw_score
        caps_applied = []

        if rubric["Q_proof"] == 0:
            capped_score = min(capped_score, 4.0)
            caps_applied.append("proof_cap_4.0")

        if rubric["Q_code"] == 0:
            capped_score = min(capped_score, 5.0)
            caps_applied.append("code_cap_5.0")

        if rubric["alignment_score"] == 0:
            capped_score = min(capped_score, 6.0)
            caps_applied.append("alignment_cap_6.0")

        final = round(max(0.0, min(10.0, capped_score)), 2)

        breakdown = {
            "completeness": round(completeness, 3),
            "quality": round(quality, 3),
            "alignment": round(alignment, 3),
            "authenticity": round(authenticity, 3),
            "effort": round(effort, 3),
            "raw_score": round(raw_score, 3),
            "final_score_10": final,
            "caps_applied": caps_applied,
            "formula": "0.35*completeness + 0.25*quality + 0.20*alignment + 0.10*authenticity + 0.10*effort"
        }

        logger.info(
            f"[ASSIGNMENT ENGINE] Score: completeness={completeness:.2f} quality={quality:.2f} "
            f"alignment={alignment:.2f} auth={authenticity:.2f} effort={effort:.2f} "
            f"→ raw={raw_score:.2f} final={final}"
        )
        return final, breakdown

    # ── Status determination ──────────────────────────────────────────────

    def _determine_status(self, score_10: float) -> str:
        """Phase 5 threshold: score ≥ 6 → pass, 4–5.9 → borderline, <4 → fail"""
        if score_10 >= 6.0:
            return "pass"
        elif score_10 >= 4.0:
            return "borderline"
        return "fail"

    # ── Next task generation ──────────────────────────────────────────────

    def _generate_next_task(
        self,
        score_10: float,
        status: str,
        signals: Dict[str, Any]
    ) -> Dict[str, Any]:
        missing    = signals.get("missing_features", [])
        indicators = signals.get("failure_indicators", [])

        review_output = {
            "score": round(score_10 * 10),
            "status": status,
            "missing": missing,
            "failure_reasons": indicators
        }

        task_data = self.rules.decide(review_output)

        if missing:
            task_data["objective"] = f"Address missing: {', '.join(missing[:2])}"
        if "repository_not_found" in str(indicators):
            task_data["focus_area"] = "Implementation Creation"
        elif "low_feature_match_ratio" in str(indicators):
            task_data["focus_area"] = "Requirement Alignment"
        elif missing:
            task_data["focus_area"] = "Feature Implementation"

        task_data = self.guard.ensure_valid(task_data, review_output)

        next_task_obj = NextTask(
            title=task_data.get("title", "Assignment Task"),
            objective=task_data.get("objective", "Complete assigned task"),
            focus_area=task_data.get("focus_area", "general"),
            difficulty=task_data.get("difficulty", "beginner"),
            expected_deliverables=task_data.get("expected_deliverables", "Complete implementation")
        )

        task_type = "advancement" if status == "pass" else "reinforcement" if status == "borderline" else "correction"

        return {
            "next_task_id": f"next-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "task_type": task_type,
            "title": next_task_obj.title,
            "objective": next_task_obj.objective,
            "focus_area": next_task_obj.focus_area,
            "difficulty": next_task_obj.difficulty,
            "reason": f"Score {score_10:.1f}/10 → {status}",
            "evidence_driven": True
        }

    # ── UI-compat component scores (0–20/40/40 scale) ────────────────────

    def _title_score_compat(self, signals: Dict[str, Any]) -> float:
        ts = signals.get("title_signals", {})
        kw = ts.get("technical_keywords", [])
        cl = ts.get("clarity_indicators", 0.7)
        dr = ts.get("domain_relevance", 0.8)
        kw_s = min(len(kw) / 2, 1.0) if kw else 0.5
        return round(max(0, min(20, 20 * (0.4 * kw_s + 0.3 * float(cl) + 0.3 * float(dr)))), 1)

    def _desc_score_compat(self, signals: Dict[str, Any]) -> float:
        ds = signals.get("description_signals", {})
        depth = ds.get("content_depth", 0.5)
        tech  = ds.get("technical_density_normalized") or ds.get("technical_density", 0.1)
        struct = ds.get("structure_quality", 0.5)
        return round(max(0, min(40, 40 * (0.35 * float(depth) + 0.35 * min(float(tech) * 1.5, 1.0) + 0.30 * float(struct)))), 1)

    def _repo_score_compat(self, signals: Dict[str, Any]) -> float:
        if not signals.get("repository_available", False):
            rs = signals.get("repository_signals") or {}
            if rs.get("error") == "network_failure":
                return 15.0
            return 0.0
        rs   = signals.get("repository_signals") or {}
        qs   = rs.get("quality", {})
        arch = rs.get("architecture", {})
        readme = qs.get("readme_score", 0)
        doc_d  = qs.get("documentation_density", 0)
        files  = rs.get("structure", {}).get("total_files", 0)
        layers = arch.get("layer_count", 0)
        cq = min((readme / 3.0 + min(doc_d, 1.0)) / 2, 1.0)
        aq = min(layers / 2.0, 1.0) if layers else (0.6 if arch.get("modular") else 0.4)
        dq = min(doc_d + (readme / 3.0) * 0.5, 1.0)
        fb = min(files / 10, 1.0)
        return round(max(0, min(40, 40 * (0.3 * cq + 0.3 * aq + 0.2 * dq + 0.2 * fb))), 1)


# Global instance
assignment_engine = AssignmentEngine()
