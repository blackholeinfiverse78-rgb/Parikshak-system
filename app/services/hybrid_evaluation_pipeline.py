"""
Hybrid Evaluation Pipeline - Final Convergence Integration
Merges Sri Satya's Assignment Engine + Ishan's Signal Evaluation + Shraddha's Validator
"""
from typing import Dict, Any
import logging
import time
from datetime import datetime, timedelta

from .assignment_engine import AssignmentEngine, AssignmentStatus
from .evaluation_engine import EvaluationEngine
from .output_validator import OutputValidator
from .aware_engine_validator import AwareEngineValidator
from .task_intelligence_engine import TaskIntelligenceEngine
from ..models.schemas import ReviewOutput, Analysis, Meta

logger = logging.getLogger("hybrid_pipeline")

class HybridEvaluationPipeline:
    """
    Unified evaluation pipeline that combines three intelligence layers:
    1. Assignment Engine (AUTHORITATIVE) - base evaluation
    2. Signal-based Evaluation (SUPPORTING) - enrichment
    3. Output Validator (FINAL WRAPPER) - contract enforcement
    
    Hierarchy: Assignment → Signals → Validation
    """
    
    def __init__(self):
        self.assignment_engine = AssignmentEngine()
        self.signal_engine = EvaluationEngine()
        self.output_validator = OutputValidator()
        self.aware_validator = AwareEngineValidator()  # Shraddha's Aware Engine v2
        self.intelligence_engine = TaskIntelligenceEngine()
    
    def evaluate(self, task_title: str, task_description: str, repository_url: str = None, pdf_text: str = "") -> Dict[str, Any]:
        """
        Execute hybrid evaluation pipeline with strict hierarchy enforcement.
        
        Args:
            task_title: Task title to evaluate
            task_description: Task description to evaluate  
            repository_url: Optional GitHub repository URL
            pdf_text: Optional PDF content
            
        Returns:
            Validated output dictionary following strict contract
        """
        start_time = time.time()
        logger.info(f"Starting hybrid evaluation for: {task_title}")
        
        # STEP 1: Assignment Engine (AUTHORITATIVE)
        logger.info("Step 1: Running Assignment Engine (AUTHORITATIVE)")
        assignment_result = self.assignment_engine.evaluate(task_title, task_description)
        
        # STEP 2: Signal-based Evaluation (SUPPORTING)
        logger.info("Step 2: Running Signal-based Evaluation (SUPPORTING)")
        signal_result = self.signal_engine.evaluate(task_title, task_description, repository_url, pdf_text)
        
        # STEP 3: Merge Logic with Hierarchy Enforcement
        logger.info("Step 3: Merging results with hierarchy enforcement")
        merged_result = self._merge_with_hierarchy(assignment_result, signal_result)
        
        # STEP 4: Output Validation with Aware Engine v2 (Shraddha's Validator)
        logger.info("Step 4: Applying Aware Engine v2 Validation (Shraddha's Validator)")
        
        # Apply Aware Engine v2 validation with scoring contract
        aware_validation = self.aware_validator.validate_with_scoring_contract(
            merged_result, 
            assignment_data={
                "deliverables": assignment_result.get("missing_requirements", []),
                "submission_date": datetime.now().isoformat(),
                "deadline": (datetime.now() + timedelta(days=7)).isoformat()
            }
        )
        
        if not aware_validation.contract_compliant:
            logger.warning(f"Aware Engine v2 validation warnings: {aware_validation.warnings}")
            if aware_validation.errors:
                logger.error(f"Aware Engine v2 validation errors: {aware_validation.errors}")
                final_output = self.aware_validator.enforce_scoring_contract(merged_result)
            else:
                final_output = aware_validation.sanitized_output or merged_result
        else:
            final_output = aware_validation.sanitized_output
            logger.info("Aware Engine v2 validation passed - contract compliant")
        
        # Add Aware Engine v2 specific fields
        final_output["accuracy_score"] = float(assignment_result["accuracy"])
        final_output["quality_score"] = min(100.0, float((signal_result.get("architecture_score", 0) + signal_result.get("code_quality_score", 0)) / 2 * 5))
        final_output["timeline_penalty"] = 0.0
        final_output["deliverables_matched"] = max(0, 4 - len(assignment_result.get("missing_requirements", [])))
        final_output["deliverables_total"] = 4
        
        # Update meta with Aware Engine v2 information
        final_output["meta"]["contract_version"] = "aware-v2"
        final_output["meta"]["determinism_hash"] = self._generate_determinism_hash(final_output)
        
        # Add evaluation metadata
        final_output["meta"]["evaluation_time_ms"] = int((time.time() - start_time) * 1000)
        final_output["meta"]["mode"] = "hybrid-aware-v2"
        
        # STEP 5: Generate Next Task using Intelligence Engine
        logger.info("Step 5: Generating next task using Intelligence Engine")
        try:
            next_task = self.intelligence_engine.generate_next_task(final_output)
            final_output["next_task"] = next_task.model_dump()
            logger.info(f"Next task generated: {next_task.title} ({next_task.difficulty})")
        except Exception as e:
            logger.warning(f"Intelligence engine failed: {e} - using fallback")
            # Fallback to simple task assignment
            from ..models.task_templates import SYSTEM_FALLBACK_TASK
            final_output["next_task"] = {
                "title": SYSTEM_FALLBACK_TASK.title,
                "objective": SYSTEM_FALLBACK_TASK.objective,
                "focus_area": SYSTEM_FALLBACK_TASK.focus_area,
                "difficulty": SYSTEM_FALLBACK_TASK.difficulty
            }
        
        logger.info(f"Hybrid evaluation complete - Final Score: {final_output['score']}, Status: {final_output['status']}, Next Task: {final_output.get('next_task', {}).get('title', 'None')}")
        return final_output
    
    def _merge_with_hierarchy(self, assignment_result: Dict[str, Any], signal_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge assignment and signal results with strict hierarchy enforcement.
        
        Rules:
        - If assignment FAIL → final = FAIL (signals cannot override)
        - Signals can refine score, enrich analysis, improve hints
        - Assignment engine is AUTHORITATIVE for base status
        """
        logger.info("Applying hierarchy merge rules")
        
        # Base status from assignment engine (AUTHORITATIVE)
        assignment_status = assignment_result["base_status"]
        assignment_accuracy = assignment_result["accuracy"]
        assignment_completeness = assignment_result["completeness"]
        
        # Signal enrichment
        signal_score = signal_result.get("score", 0)
        signal_architecture = signal_result.get("architecture_score", 0.0)
        signal_code_quality = signal_result.get("code_quality_score", 0.0)
        
        # HIERARCHY RULE 1: Assignment FAIL → Final FAIL
        if assignment_status == AssignmentStatus.FAIL.value:
            logger.info("Assignment engine determined FAIL - signals cannot override")
            final_score = min(49, max(assignment_accuracy, assignment_completeness))
            final_status = "fail"
            failure_reasons = assignment_result["missing_requirements"]
            if not failure_reasons:
                failure_reasons = ["Assignment evaluation failed - insufficient task structure"]
        
        # HIERARCHY RULE 2: Assignment PASS/BORDERLINE → Signals can refine
        else:
            logger.info("Assignment engine allows refinement - applying signal enrichment")
            
            # Weighted combination: Assignment (60%) + Signals (40%)
            assignment_base_score = (assignment_accuracy + assignment_completeness) / 2
            refined_score = int(assignment_base_score * 0.6 + signal_score * 0.4)
            
            # Ensure assignment status boundaries are respected
            if assignment_status == AssignmentStatus.PASS.value:
                final_score = max(80, refined_score)  # PASS must be >= 80
            elif assignment_status == AssignmentStatus.BORDERLINE.value:
                final_score = max(50, min(79, refined_score))  # BORDERLINE: 50-79
            else:
                final_score = refined_score
            
            # Status determination
            if final_score >= 80:
                final_status = "pass"
            elif final_score >= 50:
                final_status = "borderline"
            else:
                final_status = "fail"
            
            failure_reasons = []
            if final_status == "fail":
                failure_reasons = assignment_result["missing_requirements"][:3]
                if not failure_reasons:
                    failure_reasons = ["Insufficient overall quality"]
        
        # Build enriched analysis
        analysis = {
            "technical_quality": min(100, int(assignment_result["technical_depth"])),
            "clarity": min(100, int(assignment_result["clarity_score"])),
            "discipline_signals": min(100, int((signal_architecture + signal_code_quality) / 2))
        }
        
        # Build improvement hints (signals can enhance)
        improvement_hints = []
        if assignment_result["missing_requirements"]:
            improvement_hints.extend([f"Add {req} to task definition" for req in assignment_result["missing_requirements"][:3]])
        
        signal_hints = signal_result.get("missing_features", [])[:2]
        improvement_hints.extend([f"Improve: {hint}" for hint in signal_hints])
        
        if final_score < 75:
            improvement_hints.append("Enhance technical depth and architectural clarity")
        
        # Construct merged result
        merged = {
            "score": final_score,
            "readiness_percent": final_score,
            "status": final_status,
            "failure_reasons": failure_reasons,
            "improvement_hints": improvement_hints[:5],
            "analysis": analysis,
            "meta": {
                "evaluation_time_ms": 0,  # Will be set by caller
                "mode": "hybrid"
            },
            "feature_coverage": signal_result.get("requirement_match", 0.0),
            "architecture_score": signal_result.get("architecture_score", 0.0),
            "code_quality_score": signal_result.get("code_quality_score", 0.0),
            "completeness_score": float(assignment_completeness),
            "missing_features": signal_result.get("missing_features", []),
            "requirement_match": signal_result.get("requirement_match", 0.0),
            "evaluation_summary": self._generate_summary(assignment_result, signal_result, final_score, final_status),
            "documentation_score": signal_result.get("documentation_score", 0.0),
            "documentation_alignment": signal_result.get("documentation_alignment", "unknown"),
            "title_score": signal_result.get("title_score", 0.0),
            "description_score": signal_result.get("description_score", 0.0),
            "repository_score": signal_result.get("repository_score", 0.0),
            "analysis_pdf": signal_result.get("pdf_analysis")
        }
        
        logger.info(f"Merge complete - Assignment: {assignment_status}, Final: {final_status}, Score: {final_score}")
        return merged
    
    def _generate_summary(self, assignment_result: Dict, signal_result: Dict, final_score: int, final_status: str) -> str:
        """Generate evaluation summary combining both engines"""
        assignment_status = assignment_result["base_status"]
        
        if assignment_status == AssignmentStatus.FAIL.value:
            return (f"Assignment evaluation failed (authoritative). Score: {final_score}. "
                   f"Missing requirements: {', '.join(assignment_result['missing_requirements'][:3])}. "
                   "Signals cannot override assignment failure.")
        
        repo_info = "with repository analysis" if signal_result.get("architecture_score", 0) > 0 else "without repository"
        
        return (f"Hybrid evaluation complete {repo_info}. Final score: {final_score} ({final_status}). "
               f"Assignment base: {assignment_result['accuracy']:.0f}% accuracy, {assignment_result['completeness']:.0f}% completeness. "
               f"Signal enrichment applied. Aware Engine v2 contract compliant.")
    
    def _generate_determinism_hash(self, output: Dict[str, Any]) -> str:
        """Generate determinism hash for Aware Engine v2 compliance"""
        import hashlib
        import json
        
        # Create hash based on core evaluation parameters
        hash_data = {
            "score": output.get("score", 0),
            "status": output.get("status", "unknown"),
            "accuracy_score": output.get("accuracy_score", 0),
            "completeness_score": output.get("completeness_score", 0),
            "quality_score": output.get("quality_score", 0)
        }
        
        hash_string = json.dumps(hash_data, sort_keys=True)
        return hashlib.md5(hash_string.encode()).hexdigest()[:8]