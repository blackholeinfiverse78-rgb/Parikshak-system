"""
FINAL CONVERGENCE Product Orchestrator
Enforces Assignment Authority > Signal Support > Validation Gate hierarchy

Flow: submission → registry_validation → FINAL_CONVERGENCE → storage → response
"""
from datetime import datetime
from typing import Dict, Any, Optional
import uuid
import logging

from ..core.interfaces.review_engine_interface import ReviewEngineInterface
from ..models.schemas import Task, ReviewOutputfrom ..models.persistent_storage import (
    TaskSubmission,
    ReviewRecord,
    NextTaskRecord,
    TaskStatus,
    product_storage
)
from .final_convergence import final_convergence
from .registry_validator import registry_validator, ValidationStatus

logger = logging.getLogger("product_orchestrator")


class ProductOrchestrator:
    """
    FINAL CONVERGENCE Product Orchestrator
    Enforces Assignment Authority > Signal Support > Validation Gate hierarchy
    """
    
    def __init__(self, review_engine: ReviewEngineInterface = None):
        # Legacy review engine for backward compatibility only
        self._review_engine = review_engine
        self.convergence_enabled = True
    
    def process_submission(
        self, 
        task: Task, 
        previous_task_id: str = None,
        pdf_file_path: Optional[str] = None,
        pdf_extracted_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Core orchestration method with registry validation and lifecycle tracking.
        
        Flow:
        1. Registry Validation (NEW) - Validate module_id, lifecycle_stage, schema_version
        2. Create submission record
        3. Store submission
        4. Call review engine (only if validation passes)
        5. Store review record
        6. Call NextTaskGenerator
        7. Store next task assignment
        8. Return structured response
        """
        logger.info(f"Processing submission for task: {task.task_title[:50]}...")
        
        # FINAL CONVERGENCE PROCESSING (ENFORCED HIERARCHY)
        logger.info(f"[FINAL CONVERGENCE] Processing task: {task.task_title}")
        logger.info(f"[FINAL CONVERGENCE] Hierarchy: Assignment > Signals > Validation")
        
        # Execute FINAL CONVERGENCE with ENFORCED hierarchy
        convergence_result = final_convergence.process_with_convergence(
            task_title=task.task_title,
            task_description=task.task_description,
            repository_url=getattr(task, 'github_repo_link', None),
            module_id=task.module_id,
            schema_version=task.schema_version,
            pdf_text=pdf_extracted_text or ""
        )
        
        # Check if registry validation failed (handled by convergence)
        if convergence_result.get("registry_rejection"):
            logger.warning(f"Registry validation failed in convergence")
            # Still store the submission and a failed review so /review/{id} doesn't 404
            submission_id = convergence_result.get("submission_id", f"sub-{uuid.uuid4().hex[:12]}")
            submission = TaskSubmission(
                submission_id=submission_id,
                task_id=task.task_id,
                task_title=task.task_title,
                task_description=task.task_description,
                submitted_by=task.submitted_by,
                submitted_at=datetime.now(),
                status=TaskStatus.SUBMITTED,
                previous_task_id=previous_task_id,
                pdf_file_path=pdf_file_path,
                pdf_extracted_text=pdf_extracted_text,
                module_id=task.module_id,
                schema_version=task.schema_version,
                registry_validation_status="INVALID",
                registry_validation_reason=convergence_result.get("failure_reasons", ["Registry validation failed"])[0]
            )
            product_storage.store_submission(submission)

            from ..models.schemas import Analysis, Meta
            review_id = f"rev-{uuid.uuid4().hex[:12]}"
            failure_reasons = convergence_result.get("failure_reasons", ["Registry validation failed"])
            review_record = ReviewRecord(
                review_id=review_id,
                submission_id=submission_id,
                score=0,
                readiness_percent=0,
                status="fail",
                failure_reasons=failure_reasons,
                improvement_hints=["Use a valid module_id and matching schema_version"],
                analysis={"technical_quality": 0, "clarity": 0, "discipline_signals": 0},
                reviewed_at=datetime.now(),
                evaluation_time_ms=0,
                evaluation_summary=f"Registry Rejected: {failure_reasons[0] if failure_reasons else 'Invalid module'}"
            )
            product_storage.store_review(review_record)

            next_task_id = convergence_result.get("next_task_id", f"next-{uuid.uuid4().hex[:12]}")
            next_task_record = NextTaskRecord(
                next_task_id=next_task_id,
                review_id=review_id,
                previous_submission_id=submission_id,
                task_type="correction",
                title="Registry Compliance Task",
                objective="Fix module_id and schema_version to match Blueprint Registry",
                focus_area="Registry Compliance",
                difficulty="beginner",
                reason=failure_reasons[0] if failure_reasons else "Registry validation failed",
                assigned_at=datetime.now()
            )
            product_storage.store_next_task(next_task_record)
            return self._create_convergence_response(convergence_result, task, previous_task_id, review_id, next_task_id)
        
        # Validation layer has already processed the result
        logger.info(f"[FINAL CONVERGENCE] Validation gate passed - Score: {convergence_result.get('score')}")
        
        # Create submission record with convergence data
        submission_id = convergence_result.get("submission_id", f"sub-{uuid.uuid4().hex[:12]}")
        submission = TaskSubmission(
            submission_id=submission_id,
            task_id=task.task_id,
            task_title=task.task_title,
            task_description=task.task_description,
            submitted_by=task.submitted_by,
            submitted_at=datetime.now(),
            status=TaskStatus.SUBMITTED,
            previous_task_id=previous_task_id,
            pdf_file_path=pdf_file_path,
            pdf_extracted_text=pdf_extracted_text,
            # FINAL CONVERGENCE fields
            module_id=task.module_id,
            schema_version=task.schema_version,
            registry_validation_status="VALID",
            registry_validation_reason=None
        )
        
        # Store submission
        product_storage.store_submission(submission)
        logger.info(f"[FINAL CONVERGENCE] Stored submission: {submission_id}")
        
        # Convert convergence result to ReviewOutput format
        from ..models.schemas import Analysis, Meta
        title_score = convergence_result.get("title_score", 0)
        desc_score = convergence_result.get("description_score", 0)
        repo_score = convergence_result.get("repository_score", 0)
        review_output = ReviewOutput(
            score=convergence_result.get("score", 0),
            readiness_percent=convergence_result.get("readiness_percent", 0),
            status=convergence_result.get("status", "fail"),
            failure_reasons=convergence_result.get("failure_reasons", []),
            improvement_hints=convergence_result.get("improvement_hints", []),
            analysis=Analysis(
                technical_quality=min(100, int(title_score * 5)),   # scale /20 → /100
                clarity=min(100, int(desc_score * 2.5)),            # scale /40 → /100
                discipline_signals=min(100, int(repo_score * 2.5))  # scale /40 → /100
            ),
            meta=Meta(evaluation_time_ms=100, mode="hybrid")
        )
        
        supporting_signals = convergence_result.get("supporting_signals", {})
        quality_signals = supporting_signals.get("quality_signals", {})
        architecture_signals = supporting_signals.get("architecture_signals", {})
        feature_match_ratio = supporting_signals.get("feature_match_ratio", 0.0)
        repo_score = convergence_result.get("repository_score", 0.0)
        desc_score = convergence_result.get("description_score", 0.0)

        review_id = f"rev-{uuid.uuid4().hex[:12]}"
        review_record = ReviewRecord(
            review_id=review_id,
            submission_id=submission_id,
            score=review_output.score,
            readiness_percent=review_output.readiness_percent,
            status=review_output.status,
            failure_reasons=review_output.failure_reasons,
            improvement_hints=review_output.improvement_hints,
            analysis={
                "technical_quality": review_output.analysis.technical_quality,
                "clarity": review_output.analysis.clarity,
                "discipline_signals": review_output.analysis.discipline_signals
            },
            reviewed_at=datetime.now(),
            evaluation_time_ms=review_output.meta.evaluation_time_ms,
            feature_coverage=feature_match_ratio,
            architecture_score=min(100.0, repo_score * 2.5),
            code_quality_score=min(100.0, repo_score * 2.5),
            completeness_score=min(100.0, desc_score * 2.5),
            missing_features=convergence_result.get("missing_features", []),
            requirement_match=feature_match_ratio,
            evaluation_summary=convergence_result.get("evaluation_summary", "FINAL CONVERGENCE evaluation complete"),
            documentation_score=min(100.0, repo_score * 2.5),
            documentation_alignment=supporting_signals.get("documentation_alignment", "low"),
            analysis_pdf=convergence_result.get("pdf_analysis", {}),
            title_score=convergence_result.get("title_score", 0),
            description_score=convergence_result.get("description_score", 0),
            repository_score=convergence_result.get("repository_score", 0)
        )
        product_storage.store_review(review_record)
        logger.info(f"[FINAL CONVERGENCE] Stored review: {review_id}")
        
        # Extract next task from convergence result
        next_task_id = convergence_result.get("next_task_id", f"next-{uuid.uuid4().hex[:12]}")
        next_task_assignment = {
            "task_type": convergence_result.get("task_type", "correction"),
            "title": convergence_result.get("title", "Assignment Task"),
            "objective": convergence_result.get("objective", "Complete assigned task"),
            "focus_area": convergence_result.get("focus_area", "general"),
            "difficulty": convergence_result.get("difficulty", "beginner"),
            "reason": convergence_result.get("reason", "Assignment determined by convergence"),
            "assigned_timestamp": datetime.now()
        }
        
        # Step 7: Store next task assignment
        next_task_record = NextTaskRecord(
            next_task_id=next_task_id,
            review_id=review_id,
            previous_submission_id=submission_id,
            task_type=next_task_assignment["task_type"],
            title=next_task_assignment["title"],
            objective=next_task_assignment["objective"],
            focus_area=next_task_assignment["focus_area"],
            difficulty=next_task_assignment["difficulty"],
            reason=next_task_assignment["reason"],
            assigned_at=next_task_assignment["assigned_timestamp"]
        )
        product_storage.store_next_task(next_task_record)
        
        # Update submission status to REVIEWED
        reviewed_submission = TaskSubmission(
            **{**submission.dict(), "status": TaskStatus.REVIEWED}
        )
        product_storage.store_submission(reviewed_submission)

        # Return FINAL CONVERGENCE response
        return self._create_convergence_response(convergence_result, task, previous_task_id, review_id, next_task_id)
    
    def _create_convergence_response(
        self, 
        convergence_result: Dict[str, Any], 
        task: Task, 
        previous_task_id: str = None,
        review_id: str = None,
        next_task_id: str = None
    ) -> Dict[str, Any]:
        """
        Create response from FINAL CONVERGENCE result
        """
        submission_id = convergence_result.get("submission_id")
        review_id = review_id or f"rev-{uuid.uuid4().hex[:12]}"
        next_task_id = next_task_id or convergence_result.get("next_task_id")
        
        return {
            "submission_id": submission_id,
            "review_id": review_id,
            "next_task_id": next_task_id,
            "review": {
                "score": convergence_result.get("score", 0),
                "readiness_percent": convergence_result.get("readiness_percent", 0),
                "status": convergence_result.get("status", "fail"),
                "failure_reasons": convergence_result.get("failure_reasons", []),
                "improvement_hints": convergence_result.get("improvement_hints", []),
                "evaluation_summary": convergence_result.get("evaluation_summary", "FINAL CONVERGENCE evaluation"),
                "missing_features": convergence_result.get("missing_features", []),
                "expected_vs_delivered": convergence_result.get("expected_vs_delivered", {}),
                "analysis": {
                    # CRITICAL FIX: Use canonical scores for response
                    "technical_quality": convergence_result.get("title_score", 0),
                    "clarity": convergence_result.get("description_score", 0),
                    "discipline_signals": convergence_result.get("repository_score", 0)
                },
                "meta": {
                    "evaluation_time_ms": 100,
                    "mode": "final_convergence",
                    "authority_override": convergence_result.get("authority_override", False),
                    "evaluation_basis": convergence_result.get("evaluation_basis", "assignment_authority")
                }
            },
            "next_task": {
                "task_id": next_task_id,
                "task_type": convergence_result.get("task_type", "correction"),
                "title": convergence_result.get("title", "Assignment Task"),
                "objective": convergence_result.get("objective", "Complete assigned task"),
                "focus_area": convergence_result.get("focus_area", "general"),
                "difficulty": convergence_result.get("difficulty", "beginner"),
                "reason": convergence_result.get("reason", "Assignment determined by convergence")
            },
            "registry_validation": {
                "status": "INVALID" if convergence_result.get("registry_rejection") else "VALID",
                "module_id": task.module_id,
                "schema_version": task.schema_version
            },
            "convergence_metadata": convergence_result.get("convergence_metadata", {}),
            "validation_metadata": convergence_result.get("validation_metadata", {}),
            "hierarchy_enforced": True,
            "authority_chain": "Assignment > Signals > Validation"
        }