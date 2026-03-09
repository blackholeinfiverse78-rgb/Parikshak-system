"""
Product Core v1 Extension - Review Orchestrator Service
Branch: product-core-v1
Base: demo-freeze-v1.0

Integrated with NextTaskGenerator for deterministic task assignment.
Flow: submission → review_engine → result → storage → next_task_assignment
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
        Core orchestration method with lifecycle tracking.
        """
        # Step 1: Create submission record
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
            pdf_extracted_text=pdf_extracted_text
        )
        
        # Step 2: Store submission
        product_storage.store_submission(submission)
        logger.info(f"Stored submission: {submission_id}")
        
        # Step 3: Call review engine
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
        
        # Step 4: Store review record (Upgraded with deterministic fields)
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
            analysis_pdf=review_output.analysis_pdf
        )
        product_storage.store_review(review_record)
        logger.info(f"Stored detailed review: {review_id}")
        
        # Step 5: Call NextTaskGenerator
        next_task_assignment = NextTaskGenerator.generate(
            score=review_output.score,
            previous_submission_id=submission_id
        )
        next_task_id = f"next-{uuid.uuid4().hex[:12]}"
        
        # Step 6: Store next task assignment
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
        submission.status = TaskStatus.REVIEWED
        
        # Step 7: Return structured response
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
            }
        }
