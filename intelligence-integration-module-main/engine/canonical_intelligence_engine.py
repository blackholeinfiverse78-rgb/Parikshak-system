"""
Sri Satya's Canonical Intelligence Engine - SINGLE EVALUATION AUTHORITY
FINAL CONVERGENCE: ONE intelligence system for evaluation + next task generation
"""
from typing import Dict, Any, Optional
import logging
from datetime import datetime
from models.next_task_model import NextTask
from engine.decision_rules import DecisionRules
from engine.architecture_guard import ArchitectureGuard

logger = logging.getLogger("canonical_intelligence")

class CanonicalIntelligenceEngine:
    """
    Sri Satya's SINGLE INTELLIGENCE AUTHORITY
    
    RESPONSIBILITIES:
    1. PRIMARY evaluation authority (replaces all other evaluators)
    2. Evidence-driven next task generation
    3. Assignment readiness determination
    
    HIERARCHY ENFORCEMENT:
    - This engine = ONLY evaluation authority
    - Signal collector = supporting evidence only
    - Validation layer = final output wrapper
    """
    
    def __init__(self):
        self.authority_level = "CANONICAL_PRIMARY"
        self.rules = DecisionRules()
        self.guard = ArchitectureGuard()
        
    def evaluate_and_assign(
        self, 
        task_title: str,
        task_description: str,
        supporting_signals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        CANONICAL evaluation and assignment in ONE method
        
        Args:
            task_title: Task title
            task_description: Task description  
            supporting_signals: Evidence from signal collector
            
        Returns:
            Complete evaluation + next task assignment
        """
        logger.info(f"[CANONICAL INTELLIGENCE] Evaluating: {task_title[:50]}...")
        
        # STEP 1: Evidence-based evaluation (PRIMARY AUTHORITY)
        evaluation_result = self._evaluate_assignment_readiness(
            task_title, task_description, supporting_signals
        )
        
        # STEP 2: Evidence-driven next task generation
        next_task_result = self._generate_next_task_from_evidence(
            evaluation_result, supporting_signals
        )
        
        # STEP 3: Combine into canonical result
        canonical_result = {
            **evaluation_result,
            **next_task_result,
            "canonical_authority": True,
            "intelligence_source": "sri_satya_canonical_engine",
            "evaluation_timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"[CANONICAL INTELLIGENCE] Result: {evaluation_result['status']} (score: {evaluation_result['score']})")
        return canonical_result
    
    def _evaluate_assignment_readiness(
        self,
        task_title: str,
        task_description: str, 
        supporting_signals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        PRIMARY evaluation authority - evidence-based scoring
        SINGLE SOURCE OF TRUTH for ALL scores including component scores
        """
        # Extract evidence from supporting signals
        expected_vs_delivered = supporting_signals.get("expected_vs_delivered_evidence", {})
        missing_features = supporting_signals.get("missing_features", [])
        failure_indicators = supporting_signals.get("failure_indicators", [])
        
        # Calculate canonical score based on evidence
        total_score = self._calculate_canonical_score(
            expected_vs_delivered, missing_features, failure_indicators, supporting_signals
        )
        
        # CANONICAL COMPONENT SCORING - SINGLE AUTHORITY
        title_score = self._calculate_title_score_internal(supporting_signals)
        description_score = self._calculate_description_score_internal(supporting_signals)
        repository_score = self._calculate_repository_score_internal(supporting_signals)
        
        # Determine status (pass/borderline/fail)
        status = self._determine_status(total_score)
        
        return {
            "score": total_score,
            "status": status,
            "readiness_percent": total_score,
            "evaluation_basis": "canonical_intelligence",
            "authority_level": "PRIMARY",
            "title_score": title_score,
            "description_score": description_score,
            "repository_score": repository_score,
            "evidence_summary": {
                "expected_features": expected_vs_delivered.get("expected_count", 0),
                "delivered_features": expected_vs_delivered.get("delivered_count", 0),
                "missing_features_count": len(missing_features),
                "failure_indicators_count": len(failure_indicators),
                "delivery_ratio": expected_vs_delivered.get("delivery_ratio", 0.0)
            }
        }
    
    def _calculate_canonical_score(
        self,
        expected_vs_delivered: Dict[str, Any],
        missing_features: list,
        failure_indicators: list,
        supporting_signals: Dict[str, Any]
    ) -> int:
        """
        Canonical scoring algorithm - SINGLE SOURCE OF TRUTH
        Uses component scores as the foundation, then applies evidence adjustments
        """
        # STEP 1: Calculate component scores (foundation)
        title_score = self._calculate_title_score_internal(supporting_signals)
        description_score = self._calculate_description_score_internal(supporting_signals)
        repository_score = self._calculate_repository_score_internal(supporting_signals)
        
        # Base score from components
        base_score = title_score + description_score + repository_score
        
        logger.info(f"[CANONICAL] Component scores: Title={title_score:.1f}, Description={description_score:.1f}, Repository={repository_score:.1f}, Base={base_score:.1f}")
        
        # STEP 2: Apply evidence-based adjustments (not replacements)
        adjusted_score = base_score
        
        # EVIDENCE 1: Delivery ratio adjustment (minor impact)
        delivery_ratio = expected_vs_delivered.get('delivery_ratio', 1.0)
        if delivery_ratio < 0.8:  # Only penalize if significantly low
            delivery_penalty = int((0.8 - delivery_ratio) * 20)  # Up to 16 points
            adjusted_score -= delivery_penalty
            logger.info(f"[CANONICAL] Delivery penalty: {delivery_penalty} (ratio: {delivery_ratio:.2f})")
        
        # EVIDENCE 2: Missing features adjustment (moderate impact)
        if missing_features:
            missing_penalty = min(len(missing_features) * 5, 20)  # Max 20 points
            adjusted_score -= missing_penalty
            logger.info(f"[CANONICAL] Missing features penalty: {missing_penalty} ({len(missing_features)} features)")
        
        # EVIDENCE 3: Failure indicators adjustment - exclude missing_features_count to avoid double-penalty
        non_duplicate_indicators = [
            f for f in failure_indicators
            if not f.startswith("missing_features_count")
        ]
        failure_penalty = min(len(non_duplicate_indicators) * 3, 15)  # Max 15 points
        if failure_penalty > 0:
            adjusted_score -= failure_penalty
            logger.info(f"[CANONICAL] Failure indicators penalty: {failure_penalty} ({len(non_duplicate_indicators)} indicators)")
        
        # Ensure bounds
        final_score = max(0, min(100, int(adjusted_score)))
        logger.info(f"[CANONICAL] Final score: {final_score} (base: {base_score:.1f}, adjusted: {adjusted_score:.1f})")
        return final_score
    
    def _determine_status(self, score: int) -> str:
        """
        Canonical status determination
        """
        if score >= 80:
            return "pass"
        elif score >= 50:
            return "borderline"
        else:
            return "fail"
    
    def _generate_next_task_from_evidence(
        self,
        evaluation_result: Dict[str, Any],
        supporting_signals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evidence-driven next task generation (not template-based)
        """
        score = evaluation_result["score"]
        status = evaluation_result["status"]
        missing_features = supporting_signals.get("missing_features", [])
        failure_indicators = supporting_signals.get("failure_indicators", [])
        
        # Create review output for decision rules
        review_output = {
            "score": score,
            "status": status,
            "missing": missing_features,
            "failure_reasons": failure_indicators
        }
        
        # Use decision rules to get base task data
        task_data = self.rules.decide(review_output)
        
        # Enhance with evidence-driven specifics
        task_data = self._enhance_task_with_evidence(
            task_data, missing_features, failure_indicators, score
        )
        
        # Apply architecture guard
        task_data = self.guard.ensure_valid(task_data, review_output)
        
        # Convert to next task format
        next_task_data = {
            "title": task_data.get("title", "Assignment Task"),
            "objective": task_data.get("objective", "Complete assigned task"),
            "focus_area": task_data.get("focus_area", "general"),
            "difficulty": task_data.get("difficulty", "beginner"),
            "expected_deliverables": task_data.get("expected_deliverables", "Complete implementation")
        }
        
        next_task = NextTask(**next_task_data)
        next_task_dict = next_task.to_dict()
        
        # Add evidence-driven fields
        next_task_dict.update({
            "evidence_driven": True,
            "derived_from_evaluation": True,
            "missing_features": missing_features[:3],  # Top 3 missing
            "failure_reasons": failure_indicators[:2],  # Top 2 failures
            "expected_vs_delivered": supporting_signals.get("expected_vs_delivered_evidence", {})
        })
        
        return {
            "next_task_id": f"next-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "task_type": self._determine_task_type(score, status),
            "title": next_task_dict.get("title"),
            "objective": next_task_dict.get("objective"),
            "focus_area": next_task_dict.get("focus_area"),
            "difficulty": next_task_dict.get("difficulty"),
            "reason": f"Score {score} indicates {status} status",
            "evidence_driven": True
        }
    
    def _enhance_task_with_evidence(
        self,
        base_task_data: Dict[str, Any],
        missing_features: list,
        failure_indicators: list,
        score: int
    ) -> Dict[str, Any]:
        """
        Enhance base task with specific evidence from evaluation
        """
        enhanced_task = base_task_data.copy()
        
        # Evidence-driven objective enhancement
        if missing_features:
            top_missing = missing_features[:2]  # Top 2 missing features
            enhanced_task["objective"] = f"Address missing features: {', '.join(top_missing)}"
        
        # Evidence-driven focus area
        if 'repository_not_found' in failure_indicators:
            enhanced_task["focus_area"] = "Implementation Creation"
        elif 'low_feature_match_ratio' in failure_indicators:
            enhanced_task["focus_area"] = "Requirement Alignment"
        elif missing_features:
            enhanced_task["focus_area"] = "Feature Implementation"
        
        # Evidence-driven reason
        enhanced_task["reason"] = f"Score {score} indicates need for {enhanced_task.get('task_type', 'improvement')}"
        
        return enhanced_task
    
    def _determine_task_type(self, score: int, status: str) -> str:
        """Determine task type based on score and status"""
        if status == "pass":
            return "advancement"
        elif status == "borderline":
            return "reinforcement"
        else:
            return "correction"
    
    def _calculate_title_score_internal(self, supporting_signals: Dict[str, Any]) -> float:
        """
        Internal title scoring for canonical calculation
        """
        title_signals = supporting_signals.get("title_signals", {})
        technical_keywords = title_signals.get("technical_keywords", [])
        clarity_score = title_signals.get("clarity_indicators", 0.7)
        domain_relevance = title_signals.get("domain_relevance", 0.8)
        
        # Canonical scoring algorithm
        tech_keyword_score = min(len(technical_keywords) / 4, 1.0) if technical_keywords else 0.3
        clarity_normalized = clarity_score if isinstance(clarity_score, (int, float)) else 0.7
        domain_normalized = domain_relevance if isinstance(domain_relevance, (int, float)) else 0.8
        
        title_score = 20 * (0.40 * tech_keyword_score + 0.30 * clarity_normalized + 0.30 * domain_normalized)
        logger.info(f"[CANONICAL] Title score: {title_score:.1f} (keywords={len(technical_keywords)}, clarity={clarity_normalized:.2f}, domain={domain_normalized:.2f})")
        return max(0, min(20, title_score))
    
    def _calculate_description_score_internal(self, supporting_signals: Dict[str, Any]) -> float:
        """
        Internal description scoring for canonical calculation
        """
        desc_signals = supporting_signals.get("description_signals", {})
        content_depth = desc_signals.get("content_depth", 0.5)
        # Use pre-normalized technical_density (0-1) directly; avoid double-normalization
        technical_density = desc_signals.get("technical_density_normalized") or desc_signals.get("technical_density", 0.1)
        structure_quality = desc_signals.get("structure_quality", 0.5)
        
        depth_normalized = content_depth if isinstance(content_depth, (int, float)) else 0.5
        tech_normalized = min(float(technical_density), 1.0) if isinstance(technical_density, (int, float)) else 0.1
        structure_normalized = structure_quality if isinstance(structure_quality, (int, float)) else 0.5
        
        description_score = 40 * (
            0.35 * depth_normalized +
            0.35 * tech_normalized +
            0.30 * structure_normalized
        )
        logger.info(f"[CANONICAL] Description score: {description_score:.1f} (depth={depth_normalized:.2f}, tech={tech_normalized:.2f}, structure={structure_normalized:.2f})")
        return max(0, min(40, description_score))
    
    def _calculate_repository_score_internal(self, supporting_signals: Dict[str, Any]) -> float:
        repo_available = supporting_signals.get("repository_available", False)
        repo_signals = supporting_signals.get("repository_signals") or {}
        
        # Network failure: repo URL was provided but API call failed
        # Give a neutral partial score rather than 0
        if not repo_available:
            has_error = bool(repo_signals.get("error"))
            if has_error and repo_signals.get("error") == "network_failure":
                logger.info("[CANONICAL] Repository score: using neutral fallback (network failure)")
                return 15.0  # Neutral partial score - can't penalize for network issues
            logger.info("[CANONICAL] Repository score: 0.0 (not available)")
            return 0.0
        
        quality_signals = supporting_signals.get("quality_signals") or repo_signals.get("quality", {})
        architecture_signals = supporting_signals.get("architecture_signals") or repo_signals.get("architecture", {})
        
        readme_score = quality_signals.get("readme_score", 0)       # 0-3 scale
        doc_density = quality_signals.get("documentation_density", 0)  # 0-1 ratio
        code_quality = min((readme_score / 3.0 + min(doc_density, 1.0)) / 2, 1.0)
        
        layer_count = architecture_signals.get("layer_count", 0)
        architecture_score = min(layer_count / 4.0, 1.0) if layer_count else (0.3 if architecture_signals.get("modular") else 0.1)
        
        documentation_quality = min(doc_density + (readme_score / 3.0) * 0.5, 1.0)
        
        file_count = repo_signals.get("structure", {}).get("total_files", 0)
        file_bonus = min(file_count / 20, 1.0)
        
        repository_score = 40 * (
            0.3 * code_quality +
            0.3 * architecture_score +
            0.2 * documentation_quality +
            0.2 * file_bonus
        )
        logger.info(f"[CANONICAL] Repository score: {repository_score:.1f} (files={file_count}, quality={code_quality:.2f}, arch={architecture_score:.2f}, docs={documentation_quality:.2f})")
        return max(0, min(40, repository_score))

# Global canonical intelligence instance
canonical_intelligence = CanonicalIntelligenceEngine()