from ..core.interfaces.review_engine_interface import ReviewEngineInterface
from ..core.interfaces.next_task_interface import NextTaskGeneratorInterface
from ..models.schemas import Task, ReviewOutput, Analysis, Meta, TaskCreate
from ..models.orchestration import OrchestrationResult, V2NextTask
from ..models.task_templates import SYSTEM_FALLBACK_TASK
from .pdf_processor import PDFProcessor
from .repo_analyzer import RepoAnalyzer
import logging
import uuid
from datetime import datetime
import json
from fastapi import UploadFile, HTTPException

logger = logging.getLogger("orchestrator")

class ReviewOrchestrator:
    def __init__(
        self,
        review_engine: ReviewEngineInterface,
        next_task_generator: NextTaskGeneratorInterface,
    ):
        self._review_engine = review_engine
        self._next_task_generator = next_task_generator
        # Using service classes directly as they are static/stateless
        self._pdf_processor = PDFProcessor
        self._repo_analyzer = RepoAnalyzer

    @staticmethod
    def classify_readiness(score: int) -> str:
        """
        Deterministic readiness classification based on score bands.
        """
        if score < 0: score = 0
        elif score > 100: score = 100

        if score >= 80:
            return "PASS"
        elif score >= 50:
            return "BORDERLINE"
        else:
            return "FAIL"

    def orchestrate_review(
        self,
        description: str,
        github_url: str = None,
        pdf_file: UploadFile = None,
        submitted_by: str = "Anonymous"
    ) -> OrchestrationResult:
        """
        Full end-to-end orchestration flow:
        1. Validate Inputs
        2. Extract PDF (Reject if fails)
        3. Analyze Repo (Fallback if fails)
        4. Score (via ReviewEngine)
        5. Classify & Generate Next Task
        """
        logger.info(f"Starting extended orchestration. GitHub: {github_url}, PDF: {pdf_file.filename if pdf_file else 'None'}")
        
        # 1. Input Validation
        try:
            from ..models.schemas import ExtendedReviewRequest
            # If github_url or description is provided, validate them
            if github_url or description:
                # Basic mandatory check
                if github_url and not description:
                    raise ValueError("Description is required when providing a GitHub URL")
                
                # Use schema for validation
                ExtendedReviewRequest(
                    github_url=github_url or "https://github.com/placeholder/repo",
                    description=description or "Placeholder description"
                )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # 2. PDF Extraction (Mandatory if provided)
        extracted_text = ""
        if pdf_file:
            if not pdf_file.filename.lower().endswith(".pdf"):
                raise HTTPException(status_code=400, detail="Only PDF files are allowed")

            try:
                extracted_text = self._pdf_processor.extract_text(pdf_file)
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"PDF Extraction failed: {str(e)}")
                raise HTTPException(status_code=400, detail=f"PDF Processing failed: {str(e)}")

        # 3. GitHub Analysis (Fallback if fails)
        repo_metrics = {}
        if github_url:
            try:
                repo_metrics = self._repo_analyzer.analyze_repo(github_url)
                logger.info(f"Repo Metrics Fetched: Commits={repo_metrics.get('commit_count')}, Files={repo_metrics.get('file_count')}, Tests={repo_metrics.get('has_tests')}")
            except HTTPException as e:
                # 404 remains a rejection/not found, but others might fallback
                if e.status_code == 404:
                    raise
                logger.warning(f"GitHub Analysis failed with {e.status_code} - Falling back to deterministic zero-metrics logic")
            except Exception as e:
                logger.warning(f"GitHub Analysis failed: {str(e)} - Falling back to deterministic zero-metrics logic")
                repo_metrics = {}

        # 4. Construct Combined Payload
        # We follow the ReviewEngine's format: [Desc] \n\n --- [Marker] --- \n [Content]
        final_description = description or ""
        if repo_metrics:
            final_description += f"\n\n--- GitHub Repository Metrics ---\n{json.dumps(repo_metrics, indent=2)}"
        if extracted_text:
            final_description += f"\n\n--- Extracted PDF Content ---\n\n{extracted_text}"

        # 5. Create Task object for ReviewEngine
        task = Task(
            task_id="orch-" + str(uuid.uuid4())[:8],
            task_title=f"Review: {github_url if github_url else 'Document Submission'}",
            task_description=final_description,
            submitted_by=submitted_by,
            timestamp=datetime.now()
        )

        return self.process_submission(task)

    def process_submission(self, task: Task) -> OrchestrationResult:
        """
        Core logic for evaluating a task and generating the next step.
        """
        try:
            # 1. Call ReviewEngine
            review_result_dict = self._review_engine.evaluate(task.model_dump())
            review_output = ReviewOutput(**review_result_dict)
            logger.info(f"Review Logic Result: Score={review_output.score}, Status={review_output.status}")
        except Exception as e:
            logger.error(f"ReviewEngine failed: {str(e)}", exc_info=True)
            review_output = ReviewOutput(
                score=0,
                readiness_percent=0,
                status="fail",
                failure_reasons=["Review process error."],
                analysis=Analysis(technical_quality=0, clarity=0, discipline_signals=0),
                meta=Meta(evaluation_time_ms=0, mode="rule")
            )

        # 2. Interpret readiness
        classification = self.classify_readiness(review_output.score)
        logger.info(f"Readiness Classification: {classification}")

        # 3. Next Task Generation
        try:
            next_task = self._next_task_generator.generate_next_task(review_output, classification)
            logger.info(f"Next Task Generated: Title='{next_task.title}', Difficulty='{next_task.difficulty}'")
        except Exception as e:
            logger.warning(f"NextTaskGenerator failed: {str(e)} - Using system fallback")
            next_task = V2NextTask(
                title=SYSTEM_FALLBACK_TASK.title,
                objective=SYSTEM_FALLBACK_TASK.objective,
                focus_area=SYSTEM_FALLBACK_TASK.focus_area,
                difficulty=SYSTEM_FALLBACK_TASK.difficulty
            )

        review_output.next_task = next_task

        return OrchestrationResult(
            review=review_output,
            readiness_classification=classification,
            next_task=next_task
        )
