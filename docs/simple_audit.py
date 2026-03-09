"""
Determinism and Stability Audit - Product Core v1
Simple version without Unicode characters
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.product_orchestrator import ProductOrchestrator
from app.services.review_engine import ReviewEngine
from app.models.schemas import Task
from app.models.persistent_storage import product_storage
from datetime import datetime
import time

def run_audit():
    print("=" * 60)
    print("DETERMINISM AND STABILITY AUDIT - PRODUCT CORE v1")
    print("=" * 60)
    
    orchestrator = ProductOrchestrator(review_engine=ReviewEngine())
    
    # TEST 1: Sequential Load Test
    print("\nTEST 1 - SEQUENTIAL LOAD TEST (50 submissions)")
    print("-" * 50)
    
    product_storage.clear_all()
    crashes = 0
    
    try:
        for i in range(50):
            task = Task(
                task_id=f"load-test-{i:03d}",
                task_title=f"Load Test Task {i+1:02d}",
                task_description=f"Load test iteration {i+1} with technical requirements",
                submitted_by=f"LoadTester{i+1:02d}",
                timestamp=datetime.now()
            )
            
            result = orchestrator.process_submission(task)
            
            if (i + 1) % 10 == 0:
                print(f"  Completed {i+1}/50 submissions")
        
        total_submissions = len(product_storage.submissions)
        total_reviews = len(product_storage.reviews)
        total_next_tasks = len(product_storage.next_tasks)
        
        print(f"Results: {total_submissions} submissions, {total_reviews} reviews, {total_next_tasks} next tasks")
        
        stability_pass = (crashes == 0 and total_submissions == 50)
        print(f"STABILITY TEST: {'PASS' if stability_pass else 'FAIL'}")
        
    except Exception as e:
        print(f"STABILITY TEST: FAIL - {str(e)}")
        stability_pass = False
    
    # TEST 2: Determinism Test
    print("\nTEST 2 - DETERMINISM TEST (5 identical submissions)")
    print("-" * 50)
    
    base_task = Task(
        task_id="determinism-test",
        task_title="Determinism Test Task with Technical Requirements",
        task_description="""
        Objective: Test deterministic behavior
        Requirements: FastAPI, PostgreSQL, Redis
        Technical Stack: Docker, JWT, async processing
        """,
        submitted_by="DeterminismTester",
        timestamp=datetime(2026, 2, 5, 14, 30, 0)
    )
    
    results = []
    
    try:
        for i in range(5):
            product_storage.clear_all()
            result = orchestrator.process_submission(base_task)
            results.append({
                'score': result['review']['score'],
                'status': result['review']['status'],
                'next_task_type': result['next_task']['task_type']
            })
            print(f"  Iteration {i+1}: Score={result['review']['score']}, Status={result['review']['status']}")
        
        # Check determinism
        first_result = results[0]
        determinism_violations = 0
        
        for i, result in enumerate(results[1:], 2):
            if result['score'] != first_result['score']:
                determinism_violations += 1
                print(f"  Score variance detected in iteration {i}")
            if result['status'] != first_result['status']:
                determinism_violations += 1
                print(f"  Status variance detected in iteration {i}")
            if result['next_task_type'] != first_result['next_task_type']:
                determinism_violations += 1
                print(f"  Next task variance detected in iteration {i}")
        
        determinism_pass = (determinism_violations == 0)
        print(f"DETERMINISM TEST: {'PASS' if determinism_pass else 'FAIL'}")
        
    except Exception as e:
        print(f"DETERMINISM TEST: FAIL - {str(e)}")
        determinism_pass = False
    
    # TEST 3: Storage Consistency
    print("\nTEST 3 - STORAGE CONSISTENCY TEST")
    print("-" * 50)
    
    try:
        # Create test data
        product_storage.clear_all()
        for i in range(10):
            task = Task(
                task_id=f"storage-test-{i}",
                task_title=f"Storage Test {i+1}",
                task_description=f"Testing storage consistency {i+1}",
                submitted_by=f"StorageTester{i+1}",
                timestamp=datetime.now()
            )
            orchestrator.process_submission(task)
        
        # Verify storage integrity
        all_submissions = list(product_storage.submissions.values())
        missing_reviews = 0
        missing_next_tasks = 0
        
        for submission in all_submissions:
            review = product_storage.get_review_by_submission(submission.submission_id)
            next_task = product_storage.get_next_task_by_submission(submission.submission_id)
            
            if not review:
                missing_reviews += 1
            if not next_task:
                missing_next_tasks += 1
        
        print(f"  Total submissions: {len(all_submissions)}")
        print(f"  Missing reviews: {missing_reviews}")
        print(f"  Missing next tasks: {missing_next_tasks}")
        
        storage_pass = (missing_reviews == 0 and missing_next_tasks == 0)
        print(f"STORAGE CONSISTENCY TEST: {'PASS' if storage_pass else 'FAIL'}")
        
    except Exception as e:
        print(f"STORAGE CONSISTENCY TEST: FAIL - {str(e)}")
        storage_pass = False
    
    # Final Results
    print("\n" + "=" * 60)
    print("AUDIT RESULTS SUMMARY")
    print("=" * 60)
    print(f"Stability Status: {'PASS' if stability_pass else 'FAIL'}")
    print(f"Determinism Status: {'PASS' if determinism_pass else 'FAIL'}")
    print(f"Storage Integrity: {'PASS' if storage_pass else 'FAIL'}")
    
    overall_pass = stability_pass and determinism_pass and storage_pass
    print(f"Overall Status: {'PASS' if overall_pass else 'FAIL'}")
    
    return {
        'stability': stability_pass,
        'determinism': determinism_pass,
        'storage': storage_pass,
        'overall': overall_pass
    }

if __name__ == "__main__":
    results = run_audit()