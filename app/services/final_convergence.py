"""
FINAL CONVERGENCE Orchestrator - Enforces True Hierarchy
Assignment Authority > Signal Support > Validation Gate

This orchestrator ensures:
1. Sri Satya (Assignment) = AUTHORITATIVE
2. Ishan (Signals) = SUPPORTING ONLY
3. Shraddha (Validation) = FINAL WRAPPER
"""
from typing import Dict, Any, Optional
import logging
from datetime import datetime

from .assignment_authority import assignment_authority
from .shraddha_validation import validation_gate
from .signal_collector import signal_collector
from .registry_validator import registry_validator, ValidationStatus

logger = logging.getLogger("final_convergence")

class FinalConvergenceOrchestrator:
    """
    FINAL CONVERGENCE Orchestrator
    
    Enforces the true hierarchy:
    1. Assignment Authority (Sri Satya) = PRIMARY DECISION MAKER
    2. Signal Evaluation (Ishan) = SUPPORTING DATA ONLY
    3. Validation Layer (Shraddha) = FINAL QUALITY GATE
    
    NO parallel logic paths - single unified flow
    """
    
    def __init__(self):
        self.hierarchy_level = "CONVERGENCE_ORCHESTRATOR"
        # NO evaluation engine - only signal collector
        self.convergence_enforced = True
        self.authority_hierarchy = {
            "PRIMARY": "assignment_authority",
            "SUPPORTING": "signal_collector", 
            "FINAL_GATE": "validation_gate"
        }
    
    def process_with_convergence(
        self, 
        task_title: str,
        task_description: str,
        repository_url: Optional[str] = None,
        module_id: str = "task-review-agent",
        schema_version: str = "v1.0",
        pdf_text: str = ""
    ) -> Dict[str, Any]:
        """
        FINAL CONVERGENCE processing with enforced hierarchy
        
        Flow:
        1. Registry Validation (Structural Discipline)
        2. Assignment Authority Evaluation (PRIMARY)
        3. Signal Support (SUPPORTING ONLY)
        4. Validation Gate (FINAL WRAPPER)
        
        Args:
            task_title: Task title
            task_description: Task description
            repository_url: GitHub repository URL
            module_id: Blueprint Registry module ID
            schema_version: Schema version
            pdf_text: PDF content if any
            
        Returns:
            Final converged evaluation result
        """
        logger.info(f"[FINAL CONVERGENCE] Starting convergence processing for: {task_title[:50]}...")
        
        # STEP 1: Registry Validation (Structural Discipline Enforcement)
        logger.info("[FINAL CONVERGENCE] Step 1: Registry Validation")
        registry_result = registry_validator.validate_complete(module_id, schema_version)
        
        if registry_result.status == ValidationStatus.INVALID:
            logger.warning(f"[FINAL CONVERGENCE] Registry validation failed: {registry_result.reason}")
            # Return rejection through validation gate
            rejection_result = {
                "submission_id": f"rejected-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "score": 0,
                "status": "fail",
                "readiness_percent": 0,
                "next_task_id": "registry-correction",
                "task_type": "correction",
                "title": "Registry Compliance Task",
                "difficulty": "foundational",
                "failure_reasons": [f"Registry Validation Failed: {registry_result.reason}"],
                "registry_rejection": True
            }
            return validation_gate.validate_final_output(rejection_result, "registry_rejection")
        
        # STEP 2: Signal Collection (SUPPORTING DATA ONLY)
        logger.info("[FINAL CONVERGENCE] Step 2: Signal Collection (Supporting Data)")
        supporting_signals = signal_collector.collect_supporting_signals(
            task_title=task_title,
            task_description=task_description,
            repository_url=repository_url,
            pdf_text=pdf_text
        )
        
        # STEP 3: Assignment Authority Evaluation (PRIMARY DECISION MAKER)
        logger.info("[FINAL CONVERGENCE] Step 3: Assignment Authority Evaluation (PRIMARY)")
        assignment_result = assignment_authority.evaluate_assignment_readiness(
            task_title=task_title,
            task_description=task_description,
            supporting_signals=supporting_signals
        )
        
        # STEP 4: Validation Gate (FINAL WRAPPER)
        logger.info("[FINAL CONVERGENCE] Step 4: Validation Gate (Final Wrapper)")
        
        # Convert assignment result to API format
        api_format_result = self._convert_assignment_to_api_format(
            assignment_result, supporting_signals
        )
        
        final_result = validation_gate.validate_final_output(
            api_format_result, "assignment_authority"
        )
        
        # STEP 5: Add Convergence Metadata
        converged_result = self._add_convergence_metadata(final_result, supporting_signals)
        
        logger.info(f"[FINAL CONVERGENCE] Convergence complete - Final Status: {converged_result.get('status')}")
        return converged_result
    
    def _convert_assignment_to_api_format(
        self, 
        assignment_result: Dict[str, Any], 
        supporting_signals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Convert Assignment Authority result to API format
        
        Args:
            assignment_result: Result from Assignment Authority
            supporting_signals: Supporting signals for reference
            
        Returns:
            API-formatted result
        """
        # Extract assignment data
        score = assignment_result.get("score", 0)
        status = assignment_result.get("status", "fail")
        next_assignment = assignment_result.get("next_assignment", {})
        
        # Generate IDs
        submission_id = f"sub-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        next_task_id = f"next-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Convert to API format
        api_result = {
            "submission_id": submission_id,
            "score": score,
            "status": status,
            "readiness_percent": assignment_result.get("readiness_percent", score),
            "next_task_id": next_task_id,
            "task_type": next_assignment.get("assignment_type", "correction"),
            "title": self._generate_assignment_title(next_assignment),
            "difficulty": next_assignment.get("difficulty", "beginner"),
            "objective": next_assignment.get("reason", "Complete assignment"),
            "focus_area": next_assignment.get("focus_area", "general"),
            "reason": next_assignment.get("reason", "Assignment determined by authority"),
            
            # Evidence and metadata
            "missing_features": supporting_signals.get("missing_features", []),
            "failure_reasons": [str(f) for f in supporting_signals.get("failure_indicators", [])],
            "expected_vs_delivered": supporting_signals.get("expected_vs_delivered_evidence", {}),
            "evaluation_summary": f"Assignment Authority Evaluation: {status} (Score: {score})",
            "improvement_hints": self._generate_improvement_hints(assignment_result, supporting_signals),
            
            # Authority metadata
            "authority_override": assignment_result.get("authority_override", True),
            "evaluation_basis": assignment_result.get("evaluation_basis", "assignment_authority"),
            "evidence_summary": assignment_result.get("evidence_summary", {}),
            
            # Supporting signals reference
            "supporting_signals": supporting_signals
        }
        
        return api_result
    
    def _generate_improvement_hints(
        self, 
        assignment_result: Dict[str, Any], 
        supporting_signals: Dict[str, Any]
    ) -> list:
        """
        Generate improvement hints based on assignment evaluation
        """
        hints = []
        
        evidence = assignment_result.get("evidence_summary", {})
        missing_count = evidence.get("missing_features_count", 0)
        delivery_ratio = evidence.get("delivery_ratio", 0.0)
        
        if not supporting_signals.get("repository_available"):
            hints.append("Provide valid GitHub repository with implementation")
        
        if missing_count > 0:
            hints.append(f"Implement {missing_count} missing features")
        
        if delivery_ratio < 0.5:
            hints.append("Increase feature delivery ratio - implement more requirements")
        
        failure_indicators = supporting_signals.get("failure_indicators", [])
        if "low_feature_match_ratio" in str(failure_indicators):
            hints.append("Improve implementation to match requirements more closely")
        
        if "insufficient_implementation_scope" in str(failure_indicators):
            hints.append("Expand implementation scope to meet complexity requirements")
        
        return hints if hints else ["Continue with current implementation approach"]
    
    def _generate_assignment_title(self, next_assignment: Dict[str, Any]) -> str:
        """Generate assignment title based on assignment type and focus area"""
        assignment_type = next_assignment.get("assignment_type", "correction")
        focus_area = next_assignment.get("focus_area", "general")
        
        title_templates = {
            "advancement": f"Advanced {focus_area.replace('_', ' ').title()} Challenge",
            "reinforcement": f"{focus_area.replace('_', ' ').title()} Reinforcement",
            "correction": f"{focus_area.replace('_', ' ').title()} Correction Task"
        }
        
        return title_templates.get(assignment_type, "Task Assignment")
    
    def _add_convergence_metadata(self, result: Dict[str, Any], supporting_signals: Dict[str, Any]) -> Dict[str, Any]:
        """Add convergence metadata to final result"""
        converged_result = result.copy()
        
        converged_result["convergence_metadata"] = {
            "orchestrator": "final_convergence",
            "hierarchy_enforced": True,
            "assignment_authority": "PRIMARY",
            "signal_evaluation": "SUPPORTING",
            "validation_layer": "FINAL_WRAPPER",
            "convergence_timestamp": datetime.now().isoformat(),
            "authority_hierarchy": self.authority_hierarchy,
            "signal_authority_level": supporting_signals.get("signal_authority", "unknown"),
            "no_parallel_paths": True
        }
        
        return converged_result

# Global final convergence orchestrator
final_convergence = FinalConvergenceOrchestrator()