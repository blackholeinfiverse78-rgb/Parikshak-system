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
        """
        # Extract evidence from supporting signals
        expected_vs_delivered = supporting_signals.get("expected_vs_delivered_evidence", {})
        missing_features = supporting_signals.get("missing_features", [])
        failure_indicators = supporting_signals.get("failure_indicators", [])
        
        # Calculate canonical score based on evidence
        score = self._calculate_canonical_score(
            expected_vs_delivered, missing_features, failure_indicators, supporting_signals
        )
        
        # Determine status (pass/borderline/fail)
        status = self._determine_status(score)
        
        return {
            "score": score,
            "status": status,
            "readiness_percent": score,
            "evaluation_basis": "canonical_intelligence",
            "authority_level": "PRIMARY",
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
        """
        score = 100  # Start with perfect score
        
        # EVIDENCE 1: Delivery ratio (primary factor)
        delivery_ratio = expected_vs_delivered.get('delivery_ratio', 0.0)
        if delivery_ratio < 1.0:
            delivery_penalty = int((1 - delivery_ratio) * 50)  # Up to 50 points
            score -= delivery_penalty
            logger.info(f"[CANONICAL] Delivery penalty: {delivery_penalty} (ratio: {delivery_ratio:.2f})")
        
        # EVIDENCE 2: Missing features impact
        if missing_features:
            # Progressive penalties based on feature criticality
            critical_count = len([f for f in missing_features if 'critical' in str(f).lower()])
            major_count = len([f for f in missing_features if 'major' in str(f).lower()])
            minor_count = len(missing_features) - critical_count - major_count
            
            score -= critical_count * 20  # 20 points per critical
            score -= major_count * 15     # 15 points per major  
            score -= minor_count * 5      # 5 points per minor
            
            logger.info(f"[CANONICAL] Missing features penalty: Critical={critical_count}, Major={major_count}, Minor={minor_count}")
        
        # EVIDENCE 3: Failure indicators
        for indicator in failure_indicators:
            if 'repository_not_found' in indicator:
                score -= 25  # Major penalty for missing repo
            elif 'repository_error' in indicator:
                score -= 15  # Penalty for repo access issues
            elif 'low_feature_match_ratio' in indicator:
                score -= 20  # Penalty for poor implementation match
            else:
                score -= 10  # General failure penalty
        
        # EVIDENCE 4: Repository quality bonus
        if supporting_signals.get("repository_available"):
            score += 5  # Small bonus for having implementation
        
        # Ensure bounds
        final_score = max(0, min(100, score))
        logger.info(f"[CANONICAL] Final score: {final_score}")
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

# Global canonical intelligence instance
canonical_intelligence = CanonicalIntelligenceEngine()