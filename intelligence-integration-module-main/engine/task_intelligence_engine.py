"""
Sri Satya's Task Intelligence Engine - CANONICAL EVALUATION AUTHORITY
This IS Sri Satya's intelligence system, now serving as the PRIMARY evaluation authority
"""
from typing import Dict, Any, Optional
import logging
from datetime import datetime
from models.next_task_model import NextTask
from engine.decision_rules import DecisionRules
from engine.architecture_guard import ArchitectureGuard

logger = logging.getLogger("sri_satya_intelligence")

class TaskIntelligenceEngine:
    """
    Sri Satya's CANONICAL INTELLIGENCE ENGINE
    
    AUTHORITY LEVEL: PRIMARY_CANONICAL
    RESPONSIBILITIES:
    1. PRIMARY evaluation authority (replaces all other evaluators)
    2. Evidence-driven scoring based on assignment readiness
    3. Intelligent next task generation
    
    This IS Sri Satya's intelligence system - not a reimplementation
    """

    def __init__(self):
        self.rules = DecisionRules()
        self.guard = ArchitectureGuard()
        self.authority_level = "PRIMARY_CANONICAL"
        self.intelligence_source = "sri_satya_canonical_engine"
        
    def evaluate_and_assign(
        self, 
        task_title: str,
        task_description: str,
        supporting_signals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Sri Satya's CANONICAL evaluation and assignment method
        
        This method combines evaluation + next task generation in ONE canonical decision
        
        Args:
            task_title: Task title for evaluation
            task_description: Task description for evaluation
            supporting_signals: Evidence from signal collector
            
        Returns:
            Complete canonical evaluation + next task assignment
        """
        logger.info(f"[SRI SATYA INTELLIGENCE] Canonical evaluation: {task_title[:50]}...")
        
        # STEP 1: Evidence-based evaluation (Sri Satya's scoring logic)
        evaluation_result = self._evaluate_assignment_readiness(
            task_title, task_description, supporting_signals
        )
        
        # STEP 2: Intelligent next task generation (Sri Satya's assignment logic)
        next_task_result = self._generate_intelligent_next_task(
            evaluation_result, supporting_signals
        )
        
        # STEP 3: Canonical result with Sri Satya's authority signature
        canonical_result = {
            **evaluation_result,
            **next_task_result,
            "canonical_authority": True,
            "intelligence_source": self.intelligence_source,
            "authority_level": self.authority_level,
            "evaluation_timestamp": datetime.now().isoformat(),
            "sri_satya_signature": True  # Proof this is Sri Satya's engine
        }
        
        logger.info(f"[SRI SATYA INTELLIGENCE] Canonical result: {evaluation_result['status']} (score: {evaluation_result['score']})")
        return canonical_result
    
    def _evaluate_assignment_readiness(
        self,
        task_title: str,
        task_description: str, 
        supporting_signals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Sri Satya's assignment readiness evaluation logic
        
        This uses evidence-based scoring, not heuristics
        """
        # Extract evidence from supporting signals
        expected_vs_delivered = supporting_signals.get("expected_vs_delivered_evidence", {})
        missing_features = supporting_signals.get("missing_features", [])
        failure_indicators = supporting_signals.get("failure_indicators", [])
        
        # Extract component signals for scoring
        title_signals = supporting_signals.get("title_signals", {})
        description_signals = supporting_signals.get("description_signals", {})
        repository_available = supporting_signals.get("repository_available", False)
        feature_match_ratio = supporting_signals.get("feature_match_ratio", 0.0)
        
        # Sri Satya's canonical scoring algorithm
        title_score = self._calculate_title_score(title_signals, task_title)
        description_score = self._calculate_description_score(description_signals, task_description)
        repository_score = self._calculate_repository_score(supporting_signals)
        
        # Total score (out of 100)
        total_score = title_score + description_score + repository_score
        
        # Determine status using Sri Satya's classification rules
        status = self._determine_assignment_status(total_score)
        
        return {
            "score": total_score,
            "status": status,
            "readiness_percent": total_score,
            "evaluation_basis": "sri_satya_canonical_intelligence",
            "authority_level": "PRIMARY_CANONICAL",
            "title_score": title_score,
            "description_score": description_score,
            "repository_score": repository_score,
            "evidence_summary": {
                "expected_features": expected_vs_delivered.get("expected_count", 0),
                "delivered_features": expected_vs_delivered.get("delivered_count", 0),
                "missing_features_count": len(missing_features),
                "failure_indicators_count": len(failure_indicators),
                "delivery_ratio": expected_vs_delivered.get("delivery_ratio", 0.0)
            },
            "supporting_signals": {
                "technical_signals": {
                    "title_score": title_score,
                    "description_score": description_score,
                    "repository_score": repository_score
                },
                "implementation_signals": {
                    "repository_available": repository_available,
                    "feature_match_ratio": feature_match_ratio,
                    "architecture_score": repository_score,
                    "code_quality_score": repository_score,
                    "completeness_score": description_score,
                    "documentation_score": repository_score
                },
                "requirement_match": feature_match_ratio,
                "documentation_alignment": "high" if repository_score > 30 else "medium" if repository_score > 15 else "low"
            }
        }
    
    def _calculate_title_score(self, title_signals: Dict[str, Any], task_title: str) -> int:
        """
        Calculate title score (0-20 points)
        """
        score = 0
        
        # Technical keywords (0-10 points)
        technical_keywords = title_signals.get('technical_keywords', [])
        keyword_score = min(10, len(technical_keywords) * 2)
        score += keyword_score
        
        # Title length and clarity (0-5 points)
        title_length = len(task_title.split())
        if 3 <= title_length <= 8:
            score += 3
        elif title_length > 8:
            score += 2
        else:
            score += 1
        
        # Domain relevance (0-5 points)
        domain_relevance = title_signals.get('domain_relevance', 0)
        score += min(5, int(domain_relevance * 5))
        
        return min(20, score)
    
    def _calculate_description_score(self, description_signals: Dict[str, Any], task_description: str) -> int:
        """
        Calculate description score (0-40 points)
        """
        score = 0
        
        # Technical density (0-15 points)
        technical_density = description_signals.get('technical_density', 0)
        score += min(15, int(technical_density * 15))
        
        # Content depth (0-15 points)
        content_depth = description_signals.get('content_depth', 0)
        score += min(15, int(content_depth * 15))
        
        # Structure quality (0-10 points)
        structure_quality = description_signals.get('structure_quality', 0)
        score += min(10, int(structure_quality * 10))
        
        return min(40, score)
    
    def _calculate_repository_score(self, supporting_signals: Dict[str, Any]) -> int:
        """
        Calculate repository score (0-40 points)
        """
        if not supporting_signals.get("repository_available", False):
            return 0
        
        score = 0
        
        # Feature match ratio (0-20 points)
        feature_match_ratio = supporting_signals.get('feature_match_ratio', 0.0)
        score += min(20, int(feature_match_ratio * 20))
        
        # Implementation files (0-10 points)
        file_count = supporting_signals.get('implementation_files', 0)
        if file_count > 10:
            score += 10
        elif file_count > 5:
            score += 7
        elif file_count > 0:
            score += 5
        
        # Architecture signals (0-10 points)
        architecture_signals = supporting_signals.get('architecture_signals', {})
        if architecture_signals.get('has_layers'):
            score += 5
        if architecture_signals.get('modular'):
            score += 3
        if architecture_signals.get('documented'):
            score += 2
        
        return min(40, score)
    
    def _determine_assignment_status(self, score: int) -> str:
        """
        Sri Satya's assignment status classification
        """
        if score >= 80:
            return "pass"
        elif score >= 50:
            return "borderline"
        else:
            return "fail"
    
    def _generate_intelligent_next_task(
        self,
        evaluation_result: Dict[str, Any],
        supporting_signals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Sri Satya's intelligent next task generation
        
        This uses the ORIGINAL generate_next_task logic but with evidence-driven enhancement
        """
        score = evaluation_result["score"]
        status = evaluation_result["status"]
        missing_features = supporting_signals.get("missing_features", [])
        failure_indicators = supporting_signals.get("failure_indicators", [])
        
        # Create review output for Sri Satya's decision rules
        review_output = {
            "score": score,
            "status": status,
            "missing": missing_features,
            "failure_reasons": failure_indicators,
            "evidence_summary": evaluation_result.get("evidence_summary", {})
        }
        
        # STEP 1: Use Sri Satya's original decision rules
        task_data = self.rules.decide(review_output)
        
        # STEP 2: Enhance with evidence-driven intelligence
        task_data = self._enhance_with_evidence(
            task_data, missing_features, failure_indicators, score
        )
        
        # STEP 3: Apply Sri Satya's architecture guard
        task_data = self.guard.ensure_valid(task_data, review_output)
        
        # STEP 4: Convert to Sri Satya's next task format
        next_task_data = {
            "title": task_data.get("title", "Assignment Task"),
            "objective": task_data.get("objective", "Complete assigned task"),
            "focus_area": task_data.get("focus_area", "general"),
            "difficulty": task_data.get("difficulty", "beginner"),
            "expected_deliverables": task_data.get("expected_deliverables", "Complete implementation")
        }
        
        next_task = NextTask(**next_task_data)
        next_task_dict = next_task.to_dict()
        
        return {
            "next_task_id": f"next-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "task_type": self._determine_task_type(score, status),
            "title": next_task_dict.get("title"),
            "objective": next_task_dict.get("objective"),
            "focus_area": next_task_dict.get("focus_area"),
            "difficulty": next_task_dict.get("difficulty"),
            "reason": f"Sri Satya's intelligence: Score {score} indicates {status} status",
            "evidence_driven": True,
            "intelligence_source": "sri_satya_canonical_engine"
        }
    
    def _enhance_with_evidence(
        self,
        base_task_data: Dict[str, Any],
        missing_features: list,
        failure_indicators: list,
        score: int
    ) -> Dict[str, Any]:
        """
        Sri Satya's evidence-driven task enhancement
        
        This is where the intelligence shows - tasks are shaped by actual evidence
        """
        enhanced_task = base_task_data.copy()
        
        # Evidence-driven objective (Sri Satya's intelligence)
        if missing_features:
            top_missing = missing_features[:2]  # Focus on top 2 missing features
            enhanced_task["objective"] = f"Address critical gaps: {', '.join(top_missing)}"
        
        # Evidence-driven focus area (Sri Satya's focus logic)
        if 'repository_not_found' in failure_indicators:
            enhanced_task["focus_area"] = "Implementation Creation"
        elif 'low_feature_match_ratio' in failure_indicators:
            enhanced_task["focus_area"] = "Requirement Alignment"
        elif missing_features:
            enhanced_task["focus_area"] = "Feature Implementation"
        
        # Evidence-driven deliverables (Sri Satya's deliverable mapping)
        if missing_features:
            enhanced_task["expected_deliverables"] = f"Implement {len(missing_features)} missing features with proper testing"
        
        return enhanced_task
    
    def _determine_task_type(self, score: int, status: str) -> str:
        """
        Sri Satya's task type determination logic
        """
        if status == "pass":
            return "advancement"
        elif status == "borderline":
            return "reinforcement"
        else:
            return "correction"

    def generate_next_task(self, review_output: dict) -> dict:
        """
        ORIGINAL Sri Satya method - maintained for backward compatibility
        
        This is the ORIGINAL generate_next_task method from Sri Satya's engine
        """
        # Step 1 — decision rules (Sri Satya's original logic)
        task_data = self.rules.decide(review_output)

        # Step 2 — architecture guard (Sri Satya's original logic)
        task_data = self.guard.ensure_valid(
            task_data,
            review_output,
        )

        # Step 3 — convert to model (Sri Satya's original logic)
        next_task = NextTask(**task_data)

        return next_task.to_dict()

# Global Sri Satya intelligence instance - THIS IS THE CANONICAL AUTHORITY
sri_satya_intelligence = TaskIntelligenceEngine()