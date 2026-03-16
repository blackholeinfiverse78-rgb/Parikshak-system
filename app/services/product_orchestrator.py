"""
Product Core v1 Extension - Review Orchestrator Service
Branch: product-core-v1
Base: demo-freeze-v1.0

Integrated with NextTaskGenerator for deterministic task assignment.
Flow: submission → registry_validation → review_engine → result → storage → next_task_assignment
"""
from datetime import datetime
from typing import Dict, Any, Optional
import uuid
import logging

from ..core.interfaces.review_engine_interface import ReviewEngineInterface
from ..models.schemas import Task, ReviewOutput
from ..models.persistent_storage import (
    TaskSubmission,
    ReviewRecord,
    NextTaskRecord,
    TaskStatus,
    product_storage
)
from .next_task_generator import NextTaskGenerator
from .registry_validator import registry_validator, ValidationStatus

logger = logging.getLogger("product_orchestrator")


class ProductOrchestrator:
    """
    Simplified orchestrator for product core.
    Single responsibility: Process submission through review pipeline.
    """
    
    def __init__(self, review_engine: ReviewEngineInterface):
        self._review_engine = review_engine
    
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
        
        # Step 1: Registry Validation (NEW - STRUCTURAL DISCIPLINE ENFORCEMENT)
        logger.info(f"Validating task against Blueprint Registry: module_id={task.module_id}")
        validation_result = registry_validator.validate_complete(
            module_id=task.module_id,
            schema_version=task.schema_version
        )
        
        if validation_result.status == ValidationStatus.INVALID:
            logger.warning(f"Registry validation failed: {validation_result.reason}")
            # Return rejection response without scoring
            return self._create_rejection_response(
                task=task,
                reason=validation_result.reason,
                previous_task_id=previous_task_id
            )
        
        logger.info(f"Registry validation passed for module: {task.module_id}")
        
        # Step 2: Create submission record
        submission_id = f"sub-{uuid.uuid4().hex[:12]}"
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
            # Registry validation fields
            module_id=task.module_id,
            schema_version=task.schema_version,
            registry_validation_status="VALID",
            registry_validation_reason=None
        )
        
        # Step 3: Store submission
        product_storage.store_submission(submission)
        logger.info(f"Stored submission: {submission_id}")
        
        # Step 4: Call review engine (deterministic evaluation)
        try:
            review_result_dict = self._review_engine.evaluate(task.model_dump())
            review_output = ReviewOutput(**review_result_dict)
        except Exception as e:
            logger.error(f"Review engine failed: {e}")
            from ..models.schemas import Analysis, Meta
            review_output = ReviewOutput(
                score=0,
                readiness_percent=0,
                status="fail",
                failure_reasons=["Review engine error"],
                improvement_hints=[],
                analysis=Analysis(technical_quality=0, clarity=0, discipline_signals=0),
                meta=Meta(evaluation_time_ms=0, mode="rule")
            )
        
        # Step 5: Store review record (Upgraded with deterministic fields)
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
            # Upgraded fields
            feature_coverage=review_output.feature_coverage,
            architecture_score=review_output.architecture_score,
            code_quality_score=review_output.code_quality_score,
            completeness_score=review_output.completeness_score,
            missing_features=review_output.missing_features,
            requirement_match=review_output.requirement_match,
            evaluation_summary=review_output.evaluation_summary,
            documentation_score=review_output.documentation_score,
            documentation_alignment=review_output.documentation_alignment,
            analysis_pdf=review_output.analysis_pdf,
            title_score=review_output.title_score,
            description_score=review_output.description_score,
            repository_score=review_output.repository_score
        )
        product_storage.store_review(review_record)
        logger.info(f"Stored detailed review: {review_id}")
        
        # Step 6: Call NextTaskGenerator
        next_task_assignment = NextTaskGenerator.generate(
            score=review_output.score,
            previous_submission_id=submission_id
        )
        next_task_id = f"next-{uuid.uuid4().hex[:12]}"
        
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
        
        # Update submission status
        submission.status = TaskStatus.SUBMITTED

        # Step 8: Return structured response
        return {
            "submission_id": submission_id,
            "review_id": review_id,
            "next_task_id": next_task_id,
            "review": review_output.model_dump(),
            "next_task": {
                "task_id": next_task_id,
                "task_type": next_task_assignment["task_type"],
                "title": next_task_assignment["title"],
                "objective": next_task_assignment["objective"],
                "focus_area": next_task_assignment["focus_area"],
                "difficulty": next_task_assignment["difficulty"],
                "reason": next_task_assignment["reason"]
            },
            "registry_validation": {
                "status": "VALID",
                "module_id": task.module_id,
                "schema_version": task.schema_version
            },
            "lifecycle": {
                "current_status": "submitted",
                "previous_task_id": previous_task_id,
                "review_id": review_id,
                "next_task_id": next_task_id
            }
        }
    
    def _create_rejection_response(
        self, 
        task: Task, 
        reason: str, 
        previous_task_id: str = None
    ) -> Dict[str, Any]:
        """
        Create rejection response for registry validation failures.
        Tasks are rejected before scoring to enforce structural discipline.
        """
        logger.info(f"Creating rejection response: {reason}")
        
        # Create submission record with rejection status
        submission_id = f"sub-{uuid.uuid4().hex[:12]}"
        submission = TaskSubmission(
            submission_id=submission_id,
            task_id=task.task_id,
            task_title=task.task_title,
            task_description=task.task_description,
            submitted_by=task.submitted_by,
            submitted_at=datetime.now(),
            status=TaskStatus.SUBMITTED,
            previous_task_id=previous_task_id
        )
        
        # Store submission for audit trail
        product_storage.store_submission(submission)
        
        # Create rejection review (no scoring performed)
        review_id = f"rev-{uuid.uuid4().hex[:12]}"
        from ..models.schemas import Analysis, Meta
        rejection_review = ReviewRecord(
            review_id=review_id,
            submission_id=submission_id,
            score=0,
            readiness_percent=0,
            status="fail",
            failure_reasons=[f"Registry Validation Failed: {reason}"],
            improvement_hints=[
                "Ensure module_id exists in Blueprint Registry",
                "Verify module is not deprecated", 
                "Check schema_version compatibility"
            ],
            analysis={
                "technical_quality": 0,
                "clarity": 0,
                "discipline_signals": 0
            },
            reviewed_at=datetime.now(),
            evaluation_time_ms=0
        )
        
        product_storage.store_review(rejection_review)
        
        # Generate corrective next task
        next_task_id = f"next-{uuid.uuid4().hex[:12]}"
        next_task_record = NextTaskRecord(
            next_task_id=next_task_id,
            review_id=review_id,
            previous_submission_id=submission_id,
            task_type="correction",
            title="Registry Compliance Task",
            objective="Learn to submit tasks with valid module references",
            focus_area="System Architecture Compliance",
            difficulty="beginner",
            reason="Task rejected due to registry validation failure",
            assigned_at=datetime.now()
        )
        
        product_storage.store_next_task(next_task_record)
        
        # Return rejection response
        return {
            "submission_id": submission_id,
            "review_id": review_id,
            "next_task_id": next_task_id,
            "review": {
                "score": 0,
                "readiness_percent": 0,
                "status": "fail",
                "failure_reasons": [f"Registry Validation Failed: {reason}"],
                "improvement_hints": [
                    "Ensure module_id exists in Blueprint Registry",
                    "Verify module is not deprecated",
                    "Check schema_version compatibility"
                ],
                "analysis": {
                    "technical_quality": 0,
                    "clarity": 0,
                    "discipline_signals": 0
                },
                "meta": {
                    "evaluation_time_ms": 0,
                    "mode": "registry_rejection"
                }
            },
            "next_task": {
                "task_id": next_task_id,
                "task_type": "correction",
                "title": "Registry Compliance Task",
                "objective": "Learn to submit tasks with valid module references",
                "focus_area": "System Architecture Compliance",
                "difficulty": "beginner",
                "reason": "Architectural discipline enforcement"
            },
            "registry_validation": {
                "status": "INVALID",
                "reason": reason,
                "module_id": task.module_id,
                "schema_version": task.schema_version
            }
        }