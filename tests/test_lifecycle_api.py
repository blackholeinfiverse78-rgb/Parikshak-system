"""
Product Core v1 - Lifecycle API Tests
Tests for stable API contracts and response consistency.
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime

from app.main import app
from app.models.persistent_storage import product_storage

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_storage():
    """Clear storage before each test"""
    product_storage.clear_all()
    yield
    product_storage.clear_all()


def test_submit_task_stable_contract():
    """Test POST /lifecycle/submit returns stable contract"""
    response = client.post("/api/v1/lifecycle/submit", json={
        "task_title": "Test API Submission",
        "task_description": "Objective: Test API contract stability.",
        "submitted_by": "API Tester"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify stable contract
    assert "submission_id" in data
    assert "review_summary" in data
    assert "next_task_summary" in data
    
    # Verify review_summary structure
    assert "score" in data["review_summary"]
    assert "status" in data["review_summary"]
    assert "readiness_percent" in data["review_summary"]
    
    # Verify next_task_summary structure
    assert "task_id" in data["next_task_summary"]
    assert "task_type" in data["next_task_summary"]
    assert "title" in data["next_task_summary"]
    assert "difficulty" in data["next_task_summary"]


def test_submit_task_with_previous():
    """Test submission with previous_task_id"""
    response = client.post("/api/v1/lifecycle/submit", json={
        "task_title": "Test Lifecycle Tracking",
        "task_description": "Objective: Verify previous task tracking.",
        "submitted_by": "Tester",
        "previous_task_id": "prev-123"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "submission_id" in data


def test_get_history_deterministic_sorting():
    """Test GET /lifecycle/history returns deterministically sorted list"""
    # Submit multiple tasks
    for i in range(3):
        client.post("/api/v1/lifecycle/submit", json={
            "task_title": f"Task {i}",
            "task_description": f"Objective: Test task {i}.",
            "submitted_by": "Tester"
        })
    
    response = client.get("/api/v1/lifecycle/history")
    assert response.status_code == 200
    
    history = response.json()
    assert len(history) == 3
    
    # Verify deterministic sorting (by submitted_at)
    timestamps = [item["submitted_at"] for item in history]
    assert timestamps == sorted(timestamps)
    
    # Verify structure
    for item in history:
        assert "submission_id" in item
        assert "task_title" in item
        assert "submitted_by" in item
        assert "submitted_at" in item
        assert "score" in item
        assert "status" in item


def test_get_review_stable_contract():
    """Test GET /lifecycle/review/{id} returns stable contract"""
    # Submit task
    submit_response = client.post("/api/v1/lifecycle/submit", json={
        "task_title": "Test Review Retrieval",
        "task_description": "Objective: Test review API.",
        "submitted_by": "Tester"
    })
    submission_id = submit_response.json()["submission_id"]
    
    # Get review
    response = client.get(f"/api/v1/lifecycle/review/{submission_id}")
    assert response.status_code == 200
    
    data = response.json()
    
    # Verify stable contract
    required_fields = [
        "review_id", "submission_id", "score", "readiness_percent",
        "status", "failure_reasons", "improvement_hints", "analysis", "reviewed_at"
    ]
    for field in required_fields:
        assert field in data


def test_get_next_task_stable_contract():
    """Test GET /lifecycle/next/{id} returns stable contract"""
    # Submit task
    submit_response = client.post("/api/v1/lifecycle/submit", json={
        "task_title": "Test Next Task Retrieval",
        "task_description": "Objective: Test next task API.",
        "submitted_by": "Tester"
    })
    submission_id = submit_response.json()["submission_id"]
    
    # Get next task
    response = client.get(f"/api/v1/lifecycle/next/{submission_id}")
    assert response.status_code == 200
    
    data = response.json()
    
    # Verify stable contract
    required_fields = [
        "next_task_id", "review_id", "task_type", "title",
        "objective", "focus_area", "difficulty", "reason", "assigned_at"
    ]
    for field in required_fields:
        assert field in data


def test_review_not_found():
    """Test 404 for non-existent review"""
    response = client.get("/api/v1/lifecycle/review/nonexistent")
    assert response.status_code == 404


def test_next_task_not_found():
    """Test 404 for non-existent next task"""
    response = client.get("/api/v1/lifecycle/next/nonexistent")
    assert response.status_code == 404


def test_no_response_drift():
    """Test identical submissions produce identical responses"""
    request_data = {
        "task_title": "Determinism Test Task",
        "task_description": "Objective: Verify no response drift.",
        "submitted_by": "QA"
    }
    
    responses = []
    for i in range(3):
        product_storage.clear_all()
        response = client.post("/api/v1/lifecycle/submit", json=request_data)
        responses.append(response.json())
    
    # Verify scores are identical
    scores = [r["review_summary"]["score"] for r in responses]
    assert len(set(scores)) == 1
    
    # Verify statuses are identical
    statuses = [r["review_summary"]["status"] for r in responses]
    assert len(set(statuses)) == 1
    
    # Verify task types are identical
    task_types = [r["next_task_summary"]["task_type"] for r in responses]
    assert len(set(task_types)) == 1


def test_no_silent_failures():
    """Test API returns proper errors, not silent failures"""
    # Invalid request (missing required field)
    response = client.post("/api/v1/lifecycle/submit", json={
        "task_title": "Test",
        # Missing task_description
        "submitted_by": "Tester"
    })
    
    # Should return 422 (validation error), not 200 with empty response
    assert response.status_code == 422


def test_field_ordering_stable():
    """Test response field ordering is stable"""
    response1 = client.post("/api/v1/lifecycle/submit", json={
        "task_title": "Field Order Test 1",
        "task_description": "Objective: Test field ordering.",
        "submitted_by": "Tester"
    })
    
    product_storage.clear_all()
    
    response2 = client.post("/api/v1/lifecycle/submit", json={
        "task_title": "Field Order Test 2",
        "task_description": "Objective: Test field ordering.",
        "submitted_by": "Tester"
    })
    
    # Field order should be identical (Pydantic guarantees this)
    keys1 = list(response1.json().keys())
    keys2 = list(response2.json().keys())
    assert keys1 == keys2
