"""
Sri Satya Assignment Authority - CANONICAL EVALUATION ENGINE
FINAL CONVERGENCE: Assignment-based evaluation dominance over signal-based scoring
"""
from typing import Dict, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger("assignment_authority")

class AssignmentAuthority:
    """
    Sri Satya's Assignment Engine - AUTHORITATIVE evaluation logic
    
    HIERARCHY ENFORCEMENT:
    1. Assignment Engine (THIS) = PRIMARY AUTHORITY
    2. Signal Evaluation = SUPPORTING ONLY
    3. Validation Layer = FINAL WRAPPER
    
    NO signal-based scoring can override assignment decisions
    """
    
    def __init__(self):
        self.authority_level = "CANONICAL"
        self.override_permissions = ["signal_scoring", "evaluation_engine"]
    
    def evaluate_assignment_readiness(
        self, 
        task_title: str, 
        task_description: str,
        supporting_signals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        PRIMARY EVALUATION AUTHORITY - Assignment-based scoring
        
        Args:
            task_title: Task title for context
            task_description: Task description for requirements
            supporting_signals: Supporting signals from signal collector
            
        Returns:
            AUTHORITATIVE assignment-based evaluation result
        """
        logger.info(f"[ASSIGNMENT AUTHORITY] PRIMARY EVALUATION: {task_title[:50]}...")
        
        # Extract evidence from supporting signals
        expected_vs_delivered = supporting_signals.get("expected_vs_delivered_evidence", {})
        missing_features = supporting_signals.get("missing_features", [])
        failure_indicators = supporting_signals.get("failure_indicators", [])
        
        # STEP 1: Assignment Readiness Analysis (PRIMARY AUTHORITY)
        readiness_score = self._calculate_assignment_score(
            expected_vs_delivered, missing_features, failure_indicators, supporting_signals
        )
        
        # STEP 2: Assignment Classification (AUTHORITATIVE)
        assignment_status = self._classify_assignment_readiness(readiness_score)
        
        # STEP 3: Pass/Borderline/Fail Determination (CANONICAL)
        evaluation_status = self._determine_evaluation_status(readiness_score)
        
        # STEP 4: Next Assignment Decision (EVIDENCE-DRIVEN)
        next_assignment = self._determine_next_assignment(
            readiness_score, assignment_status, missing_features, failure_indicators
        )
        
        # STEP 5: Authority Result (CANNOT BE OVERRIDDEN)
        authority_result = {
            "authority_level": "PRIMARY_CANONICAL",
            "score": readiness_score,
            "readiness_percent": readiness_score,
            "status": evaluation_status,
            "assignment_status": assignment_status,
            "next_assignment": next_assignment,
            "authority_override": True,
            "evaluation_basis": "assignment_authority",
            "evidence_driven": True,
            "evaluated_at": datetime.now().isoformat(),
            "authority_signature": "sri_satya_assignment_engine",
            
            # Evidence used in evaluation
            "evidence_summary": {
                "expected_features": expected_vs_delivered.get("expected_count", 0),
                "delivered_features": expected_vs_delivered.get("delivered_count", 0),
                "missing_features_count": len(missing_features),
                "failure_indicators_count": len(failure_indicators),
                "delivery_ratio": expected_vs_delivered.get("delivery_ratio", 0.0)
            },
            
            # Supporting signals reference (not used for scoring)
            "supporting_signals_reference": {
                "repository_available": supporting_signals.get("repository_available", False),
                "feature_match_ratio": supporting_signals.get("feature_match_ratio", 0.0),
                "signal_authority": supporting_signals.get("signal_authority", "unknown")
            }
        }
        
        logger.info(f"[ASSIGNMENT AUTHORITY] PRIMARY RESULT: {evaluation_status} (score: {readiness_score})")
        return authority_result
    
    def _calculate_assignment_score(
        self, 
        expected_vs_delivered: Dict[str, Any],
        missing_features: list,
        failure_indicators: list,
        supporting_signals: Dict[str, Any]
    ) -> int:
        """
        Calculate PRIMARY assignment score based on EVIDENCE
        
        Returns:
            Assignment score (0-100) - AUTHORITATIVE
        """
        score = 100  # Start with perfect assignment readiness
        
        # EVIDENCE 1: Expected vs Delivered Gap (PRIMARY FACTOR)
        delivery_ratio = expected_vs_delivered.get('delivery_ratio', 0.0)
        expected_count = expected_vs_delivered.get('expected_count', 0)
        delivered_count = expected_vs_delivered.get('delivered_count', 0)
        
        if expected_count > 0:
            # Major penalty for delivery gaps
            delivery_gap_penalty = int((1 - delivery_ratio) * 50)  # Up to 50 points
            score -= delivery_gap_penalty
            logger.info(f"[ASSIGNMENT AUTHORITY] Delivery gap penalty: {delivery_gap_penalty} (ratio: {delivery_ratio:.2f})")
        
        # EVIDENCE 2: Missing Features Impact (CRITICAL FACTOR)
        if missing_features:
            critical_missing = len([f for f in missing_features if 'critical' in str(f).lower()])
            major_missing = len([f for f in missing_features if 'major' in str(f).lower()])
            minor_missing = len(missing_features) - critical_missing - major_missing
            
            # Progressive penalties
            score -= critical_missing * 20  # 20 points per critical missing
            score -= major_missing * 15     # 15 points per major missing
            score -= minor_missing * 5      # 5 points per minor missing
            
            logger.info(f"[ASSIGNMENT AUTHORITY] Missing features penalty: Critical={critical_missing}, Major={major_missing}, Minor={minor_missing}")
        
        # EVIDENCE 3: Failure Indicators Impact (BLOCKING FACTORS)
        for indicator in failure_indicators:
            if 'repository_not_found' in indicator:
                score -= 25  # Major penalty for missing implementation
            elif 'repository_error' in indicator:
                score -= 15  # Penalty for access issues
            elif 'low_feature_match_ratio' in indicator:
                score -= 20  # Penalty for poor implementation match
            elif 'insufficient_implementation_scope' in indicator:
                score -= 15  # Penalty for incomplete scope
            else:
                score -= 5   # General failure indicator penalty
        
        # EVIDENCE 4: Repository Quality Signals (SUPPORTING FACTOR)
        if supporting_signals.get("repository_available"):
            # Bonus for having implementation
            score += 5
            
            # Quality indicators
            arch_signals = supporting_signals.get("architecture_signals", {})
            if arch_signals.get('has_layers'):
                score += 3
            if arch_signals.get('modular'):
                score += 2
        
        # Ensure score bounds
        final_score = max(0, min(100, score))
        logger.info(f"[ASSIGNMENT AUTHORITY] Final assignment score: {final_score}")
        return final_score
    
    def _determine_evaluation_status(self, readiness_score: int) -> str:
        """
        CANONICAL determination of pass/borderline/fail status
        
        Args:
            readiness_score: Assignment readiness score
            
        Returns:
            Evaluation status (pass/borderline/fail)
        """
        if readiness_score >= 80:
            return "pass"
        elif readiness_score >= 50:
            return "borderline"
        else:
            return "fail"
    
    def _classify_assignment_readiness(self, readiness_score: int) -> str:
        """
        AUTHORITATIVE classification - cannot be overridden by signals
        
        Args:
            readiness_score: Assignment readiness score
            
        Returns:
            Assignment status classification
        """
        if readiness_score >= 80:
            return "READY_FOR_ADVANCEMENT"
        elif readiness_score >= 50:
            return "NEEDS_REINFORCEMENT"
        else:
            return "REQUIRES_CORRECTION"
    
    def _determine_next_assignment(
        self, 
        readiness_score: int, 
        assignment_status: str,
        missing_features: list,
        failure_indicators: list
    ) -> Dict[str, Any]:
        """
        EVIDENCE-DRIVEN next assignment determination
        
        Args:
            readiness_score: Current assignment readiness
            assignment_status: Assignment classification
            missing_features: Specific missing features (STRUCTURED INPUT)
            failure_indicators: Specific failure points (STRUCTURED INPUT)
            
        Returns:
            Next assignment specification based on EVIDENCE
        """
        logger.info(f"[ASSIGNMENT AUTHORITY] Determining next assignment based on evidence...")
        
        if assignment_status == "READY_FOR_ADVANCEMENT":
            return {
                "assignment_type": "advancement",
                "focus_area": "next_level_challenges",
                "difficulty": "progressive",
                "reason": f"Assignment readiness score {readiness_score} indicates readiness for advancement",
                "evidence_basis": "high_delivery_ratio_and_complete_features"
            }
        
        elif assignment_status == "NEEDS_REINFORCEMENT":
            # STRUCTURED EVIDENCE ANALYSIS for reinforcement focus
            focus_area = "general_improvement"
            specific_targets = []
            
            # Analyze missing features for specific focus
            if missing_features:
                critical_missing = [f for f in missing_features if 'critical' in str(f).lower()]
                major_missing = [f for f in missing_features if 'major' in str(f).lower()]
                
                if critical_missing:
                    focus_area = "critical_feature_implementation"
                    specific_targets = critical_missing[:2]  # Top 2 critical
                elif major_missing:
                    focus_area = "major_feature_completion"
                    specific_targets = major_missing[:3]  # Top 3 major
                else:
                    focus_area = "feature_refinement"
                    specific_targets = missing_features[:3]  # Top 3 any
            
            # Analyze failure indicators for additional focus
            failure_focus = []
            for indicator in failure_indicators:
                if 'repository_not_found' in indicator:
                    failure_focus.append("implementation_creation")
                elif 'low_feature_match_ratio' in indicator:
                    failure_focus.append("requirement_alignment")
                elif 'insufficient_implementation_scope' in indicator:
                    failure_focus.append("scope_expansion")
            
            if failure_focus:
                focus_area = f"{focus_area}_with_{failure_focus[0]}"
            
            return {
                "assignment_type": "reinforcement",
                "focus_area": focus_area,
                "difficulty": "targeted",
                "reason": f"Score {readiness_score} requires reinforcement in {focus_area}",
                "specific_targets": specific_targets,
                "failure_focus": failure_focus,
                "evidence_basis": f"missing_features_count_{len(missing_features)}_failure_indicators_{len(failure_indicators)}"
            }
        
        else:  # REQUIRES_CORRECTION
            # STRUCTURED EVIDENCE ANALYSIS for correction focus
            primary_issue = "fundamental_gaps"
            correction_targets = []
            
            # Analyze failure indicators for primary correction focus
            repository_issues = [f for f in failure_indicators if 'repository' in f]
            implementation_issues = [f for f in failure_indicators if 'implementation' in f or 'scope' in f]
            match_issues = [f for f in failure_indicators if 'match' in f or 'ratio' in f]
            
            if repository_issues:
                primary_issue = "implementation_missing"
                correction_targets = repository_issues
            elif implementation_issues:
                primary_issue = "implementation_insufficient"
                correction_targets = implementation_issues
            elif match_issues:
                primary_issue = "requirement_mismatch"
                correction_targets = match_issues
            elif missing_features:
                primary_issue = "feature_gaps"
                correction_targets = missing_features[:2]  # Top 2 missing
            
            return {
                "assignment_type": "correction",
                "focus_area": primary_issue,
                "difficulty": "foundational",
                "reason": f"Score {readiness_score} requires correction of {primary_issue}",
                "correction_targets": correction_targets,
                "primary_issue_category": "repository" if repository_issues else "implementation" if implementation_issues else "requirements",
                "evidence_basis": f"failure_indicators_{len(failure_indicators)}_missing_features_{len(missing_features)}"
            }
    
    def override_signal_evaluation(self, signal_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Override signal-based evaluation with assignment authority
        
        Args:
            signal_result: Result from signal-based evaluation
            
        Returns:
            Authority-corrected evaluation result
        """
        logger.warning("[ASSIGNMENT AUTHORITY] Overriding signal-based evaluation")
        
        # Extract evidence from signal result for assignment evaluation
        expected_vs_delivered = {
            'expected_count': len(signal_result.get('missing_features', [])) + signal_result.get('score', 0) // 10,
            'delivered_count': signal_result.get('score', 0) // 10
        }
        
        missing_features = signal_result.get('missing_features', [])
        failure_reasons = signal_result.get('failure_reasons', [])
        
        # Get authoritative assignment evaluation
        authority_result = self.evaluate_assignment_readiness(
            task_title=signal_result.get('title', 'Unknown Task'),
            task_description=signal_result.get('description', ''),
            expected_vs_delivered=expected_vs_delivered,
            missing_features=missing_features,
            failure_reasons=failure_reasons
        )
        
        # Override signal result with assignment authority
        corrected_result = signal_result.copy()
        corrected_result.update({
            "score": authority_result["assignment_score"],
            "status": authority_result["assignment_status"].lower().replace('_', ''),
            "readiness_percent": authority_result["assignment_readiness"],
            "authority_override": True,
            "evaluation_basis": "assignment_authority",
            "original_signal_score": signal_result.get('score', 0),
            "authority_correction": f"Assignment authority corrected from {signal_result.get('score', 0)} to {authority_result['assignment_score']}"
        })
        
        return corrected_result

# Global assignment authority instance
assignment_authority = AssignmentAuthority()