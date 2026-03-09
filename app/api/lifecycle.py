"""
Product Core v1 - Lifecycle API
Stable API contracts for complete task lifecycle management.
"""
from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from ..services.product_orchestrator import ProductOrchestrator
from ..services.review_engine import ReviewEngine
from ..models.schemas import Task
from ..models.persistent_storage import product_storage
from ..services.pdf_analyzer import PDFAnalyzer

router = APIRouter(prefix="/lifecycle", tags=["lifecycle"])

# Stable request/response models
class TaskSubmitRequest(BaseModel):
    task_title: str = Field(..., min_length=5, max_length=100)
    task_description: str = Field(..., min_length=10, max_length=100000)
    submitted_by: str = Field(..., min_length=2, max_length=50)
    previous_task_id: Optional[str] = None

class ReviewSummary(BaseModel):
    score: int
    status: str
    readiness_percent: int

class NextTaskSummary(BaseModel):
    task_id: str
    task_type: str
    title: str
    difficulty: str

class TaskSubmitResponse(BaseModel):
    submission_id: str
    review_summary: ReviewSummary
    next_task_summary: NextTaskSummary

class SubmissionHistoryItem(BaseModel):
    submission_id: str
    task_title: str
    submitted_by: str
    submitted_at: datetime
    score: int
    status: str
    has_pdf: bool = False

class ReviewDetailResponse(BaseModel):
    review_id: str
    submission_id: str
    score: int
    readiness_percent: int
    status: str
    failure_reasons: List[str]
    improvement_hints: List[str]
    analysis: dict
    reviewed_at: datetime
    feature_coverage: float
    architecture_score: float
    code_quality_score: float
    completeness_score: float
    missing_features: List[str]
    requirement_match: float
    evaluation_summary: str
    documentation_score: float
    documentation_alignment: str
    analysis_pdf: Optional[dict] = None

class NextTaskDetailResponse(BaseModel):
    next_task_id: str
    review_id: str
    task_type: str
    title: str
    objective: str
    focus_area: str
    difficulty: str
    reason: str
    assigned_at: datetime

# Initialize orchestrator
orchestrator = ProductOrchestrator(review_engine=ReviewEngine())
pdf_analyzer = PDFAnalyzer()

@router.post("/submit", response_model=TaskSubmitResponse)
async def submit_task(
    task_title: str = Form(...),
    task_description: str = Form(...),
    submitted_by: str = Form(...),
    github_repo_link: str = Form(...),
    previous_task_id: Optional[str] = Form(None),
    pdf_file: Optional[UploadFile] = File(None)
):
    """
    Submit task for review with optional PDF support.
    """
    try:
        # 1. Handle PDF Processing
        pdf_file_path = None
        pdf_text = ""
        if pdf_file:
            pdf_result = pdf_analyzer.process_upload(pdf_file)
            pdf_file_path = pdf_result["file_path"]
            pdf_text = pdf_result["extracted_text"]

        # 2. Create task object for evaluation
        task = Task(
            task_id=f"task-{datetime.now().timestamp()}",
            task_title=task_title,
            task_description=task_description,
            submitted_by=submitted_by,
            github_repo_link=github_repo_link,
            timestamp=datetime.now(),
            pdf_extracted_text=pdf_text
        )
        
        # 3. Process submission via orchestrator
        result = orchestrator.process_submission(
            task, 
            previous_task_id,
            pdf_file_path=pdf_file_path,
            pdf_extracted_text=pdf_text
        )
        
        # Build response
        return TaskSubmitResponse(
            submission_id=result["submission_id"],
            review_summary=ReviewSummary(
                score=result["review"]["score"],
                status=result["review"]["status"],
                readiness_percent=result["review"]["readiness_percent"]
            ),
            next_task_summary=NextTaskSummary(
                task_id=result["next_task"]["task_id"],
                task_type=result["next_task"]["task_type"],
                title=result["next_task"]["title"],
                difficulty=result["next_task"]["difficulty"]
            )
        )
    except Exception as e:
        logger.error(f"Submission failed: {e}")
        raise HTTPException(status_code=500, detail=f"Submission failed: {str(e)}")

@router.get("/history", response_model=List[SubmissionHistoryItem])
def get_history():
    """
    Get ordered list of all submissions.
    Deterministic sorting: by submitted_at ascending.
    """
    submissions = list(product_storage.submissions.values())
    
    # Sort deterministically by submitted_at
    submissions.sort(key=lambda s: s.submitted_at)
    
    # Build response
    history = []
    for submission in submissions:
        review = product_storage.get_review_by_submission(submission.submission_id)
        history.append(SubmissionHistoryItem(
            submission_id=submission.submission_id,
            task_title=submission.task_title,
            submitted_by=submission.submitted_by,
            submitted_at=submission.submitted_at,
            score=review.score if review else 0,
            status=review.status if review else "unknown",
            has_pdf=bool(submission.pdf_file_path)
        ))
    
    return history

@router.get("/review/{submission_id}", response_model=ReviewDetailResponse)
def get_review(submission_id: str):
    """
    Get stored review output by submission ID.
    Stable contract: Always returns complete review details.
    """
    review = product_storage.get_review_by_submission(submission_id)
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    return ReviewDetailResponse(
        review_id=review.review_id,
        submission_id=review.submission_id,
        score=review.score,
        readiness_percent=review.readiness_percent,
        status=review.status,
        failure_reasons=review.failure_reasons,
        improvement_hints=review.improvement_hints,
        analysis=review.analysis,
        reviewed_at=review.reviewed_at,
        feature_coverage=review.feature_coverage,
        architecture_score=review.architecture_score,
        code_quality_score=review.code_quality_score,
        completeness_score=review.completeness_score,
        missing_features=review.missing_features,
        requirement_match=review.requirement_match,
        evaluation_summary=review.evaluation_summary,
        documentation_score=review.documentation_score,
        documentation_alignment=review.documentation_alignment,
        analysis_pdf=review.analysis_pdf
    )

@router.get("/next/{submission_id}", response_model=NextTaskDetailResponse)
def get_next_task(submission_id: str):
    """
    Get stored next task by submission ID.
    Stable contract: Always returns complete next task details.
    """
    next_task = product_storage.get_next_task_by_submission(submission_id)
    
    if not next_task:
        raise HTTPException(status_code=404, detail="Next task not found")
    
    return NextTaskDetailResponse(
        next_task_id=next_task.next_task_id,
        review_id=next_task.review_id,
        task_type=next_task.task_type,
        title=next_task.title,
        objective=next_task.objective,
        focus_area=next_task.focus_area,
        difficulty=next_task.difficulty,
        reason=next_task.reason,
        assigned_at=next_task.assigned_at
    )
