"""
Product Core v1 - Determinism Verification
Comprehensive test to verify zero variance in orchestration.
"""
import pytest
from datetime import datetime
from app.services.product_orchestrator import ProductOrchestrator
from app.services.review_engine import ReviewEngine
from app.models.schemas import Task
from app.models.persistent_storage import product_storage


def test_determinism_100_iterations():
    """
    Run 100 iterations with identical input.
    Verify zero variance in scores, status, and next task.
    """
    orchestrator = ProductOrchestrator(review_engine=ReviewEngine())
    
    task = Task(
        task_id="task-det-100",
        task_title="Determinism Verification Task with Specific Requirements",
        task_description="""
        Objective: Verify absolute determinism across 100 iterations.
        Requirement: Same input must yield identical output every time.
        Constraint: Zero randomness, zero variance allowed.
        Technical Stack: FastAPI, PostgreSQL, Redis, Docker.
        """,
        submitted_by="QA Engineer",
        timestamp=datetime(2026, 2, 5, 10, 0, 0)  # Fixed timestamp
    )
    
    results = []
    for i in range(100):
        product_storage.clear_all()
        result = orchestrator.process_submission(task)
        results.append(result)
    
    # Verify all scores are identical
    scores = [r["review"]["score"] for r in results]
    assert len(set(scores)) == 1, f"Score variance detected: {set(scores)}"
    
    # Verify all statuses are identical
    statuses = [r["review"]["status"] for r in results]
    assert len(set(statuses)) == 1, f"Status variance detected: {set(statuses)}"
    
    # Verify all readiness percentages are identical
    readiness = [r["review"]["readiness_percent"] for r in results]
    assert len(set(readiness)) == 1, f"Readiness variance detected: {set(readiness)}"
    
    # Verify all next task titles are identical
    next_titles = [r["next_task"]["title"] for r in results]
    assert len(set(next_titles)) == 1, f"Next task title variance detected: {set(next_titles)}"
    
    # Verify all next task difficulties are identical
    difficulties = [r["next_task"]["difficulty"] for r in results]
    assert len(set(difficulties)) == 1, f"Difficulty variance detected: {set(difficulties)}"
    
    print(f"\nDeterminism verified across 100 iterations")
    print(f"  Score: {scores[0]}")
    print(f"  Status: {statuses[0]}")
    print(f"  Next Task: {next_titles[0]} ({difficulties[0]})")


def test_determinism_multiple_tasks():
    """
    Test determinism with multiple different tasks.
    Each task should produce consistent results.
    """
    orchestrator = ProductOrchestrator(review_engine=ReviewEngine())
    
    tasks = [
        Task(
            task_id="task-multi-1",
            task_title="Short Task",
            task_description="Objective: Test short description.",
            submitted_by="User1",
            timestamp=datetime.now()
        ),
        Task(
            task_id="task-multi-2",
            task_title="Medium Length Task with More Details",
            task_description="""
            Objective: Test medium length description with more content.
            Requirement: Include multiple sentences and structure.
            Constraint: Maintain clarity and purpose.
            """,
            submitted_by="User2",
            timestamp=datetime.now()
        ),
        Task(
            task_id="task-multi-3",
            task_title="Comprehensive Task with Full Technical Specification",
            task_description="""
            Objective: Test comprehensive description with full technical details.
            Requirement: Include all necessary technical specifications and requirements.
            Constraint: Must be production-ready and follow best practices.
            
            Technical Stack:
            - API Gateway for routing
            - Database with schema validation
            - Security layer with authentication
            - Caching for performance
            - Async processing for scalability
            - Frontend integration
            - Documentation and tests
            """,
            submitted_by="User3",
            timestamp=datetime.now()
        )
    ]
    
    for task in tasks:
        # Run each task 10 times
        task_results = []
        for i in range(10):
            product_storage.clear_all()
            result = orchestrator.process_submission(task)
            task_results.append(result)
        
        # Verify consistency for this task
        scores = [r["review"]["score"] for r in task_results]
        assert len(set(scores)) == 1, f"Task {task.task_id} has score variance"
        
        statuses = [r["review"]["status"] for r in task_results]
        assert len(set(statuses)) == 1, f"Task {task.task_id} has status variance"
        
        print(f"[OK] Task {task.task_id}: Score={scores[0]}, Status={statuses[0]}")


def test_storage_determinism():
    """
    Verify storage operations are deterministic.
    Same submission should create identical storage records.
    """
    orchestrator = ProductOrchestrator(review_engine=ReviewEngine())
    
    task = Task(
        task_id="task-storage-det",
        task_title="Storage Determinism Test",
        task_description="Objective: Verify storage operations are deterministic.",
        submitted_by="Tester",
        timestamp=datetime(2026, 2, 5, 12, 0, 0)
    )
    
    # Run twice and compare storage
    product_storage.clear_all()
    result1 = orchestrator.process_submission(task)
    submission1 = product_storage.get_submission(result1["submission_id"])
    review1 = product_storage.get_review(result1["review_id"])
    
    product_storage.clear_all()
    result2 = orchestrator.process_submission(task)
    submission2 = product_storage.get_submission(result2["submission_id"])
    review2 = product_storage.get_review(result2["review_id"])
    
    # Compare stored data (excluding IDs which are unique)
    assert submission1.task_title == submission2.task_title
    assert submission1.task_description == submission2.task_description
    assert submission1.submitted_by == submission2.submitted_by
    assert submission1.status == submission2.status
    
    assert review1.score == review2.score
    assert review1.readiness_percent == review2.readiness_percent
    assert review1.status == review2.status
    assert review1.failure_reasons == review2.failure_reasons
    assert review1.analysis == review2.analysis
    
    print("[OK] Storage operations are deterministic")


def test_evaluation_time_determinism():
    """
    Verify evaluation time is deterministic (fixed at 120ms).
    """
    orchestrator = ProductOrchestrator(review_engine=ReviewEngine())
    
    task = Task(
        task_id="task-time-det",
        task_title="Evaluation Time Test",
        task_description="Objective: Verify evaluation time is deterministic.",
        submitted_by="Tester",
        timestamp=datetime.now()
    )
    
    eval_times = []
    for i in range(20):
        product_storage.clear_all()
        result = orchestrator.process_submission(task)
        review = product_storage.get_review(result["review_id"])
        eval_times.append(review.evaluation_time_ms)
    
    # All evaluation times should be identical (120ms fixed)
    assert len(set(eval_times)) == 1, f"Evaluation time variance: {set(eval_times)}"
    assert eval_times[0] == 120, f"Expected 120ms, got {eval_times[0]}ms"
    
    print(f"[OK] Evaluation time is deterministic: {eval_times[0]}ms")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
