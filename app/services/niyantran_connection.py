"""
Niyantran Connection Service - Task Orchestration Interface
Accepts tasks from Niyantran and returns review + next task
Ensures end-to-end flow works seamlessly
"""
from typing import Dict, Any, Optional
import logging
from datetime import datetime
from dataclasses import dataclass

from .final_convergence import final_convergence
from .production_decision_engine import production_decision_engine
from .bucket_integration import bucket_integration

logger = logging.getLogger("niyantran_connection")

@dataclass
class NiyantranTask:
    """Task received from Niyantran"""
    task_id: str
    task_title: str
    task_description: str
    submitted_by: str
    repository_url: Optional[str] = None
    module_id: str = "task-review-agent"
    schema_version: str = "v1.0"
    pdf_text: str = ""
    priority: str = "normal"
    deadline: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NiyantranTask":
        """Create NiyantranTask from dictionary"""
        return cls(
            task_id=data.get("task_id", ""),
            task_title=data.get("task_title", ""),
            task_description=data.get("task_description", ""),
            submitted_by=data.get("submitted_by", "unknown"),
            repository_url=data.get("repository_url"),
            module_id=data.get("module_id", "task-review-agent"),
            schema_version=data.get("schema_version", "v1.0"),
            pdf_text=data.get("pdf_text", ""),
            priority=data.get("priority", "normal"),
            deadline=data.get("deadline")
        )

@dataclass
class NiyantranResponse:
    """Response to Niyantran with review + next task"""
    task_id: str
    trace_id: str
    
    # Review results
    review: Dict[str, Any]
    
    # Next task assignment
    next_task: Dict[str, Any]
    
    # Processing metadata
    processing_time_ms: int
    timestamp: str
    status: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        return {
            "task_id": self.task_id,
            "trace_id": self.trace_id,
            "review": self.review,
            "next_task": self.next_task,
            "processing_metadata": {
                "processing_time_ms": self.processing_time_ms,
                "timestamp": self.timestamp,
                "status": self.status
            }
        }

class NiyantranConnectionService:
    """
    Connection service for Niyantran integration
    Handles task intake, processing, and response generation
    """
    
    def __init__(self):
        self.service_name = "niyantran_connection"
        self.version = "1.0"
        
    def process_niyantran_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process task from Niyantran and return complete response
        
        Args:
            task_data: Task data from Niyantran
            
        Returns:
            Complete response with review + next task
        """
        start_time = datetime.now()
        logger.info(f"[NIYANTRAN] Processing task from Niyantran: {task_data.get('task_title', 'Unknown')[:50]}...")
        
        try:
            # Step 1: Parse Niyantran task
            niyantran_task = NiyantranTask.from_dict(task_data)
            
            # Step 2: Execute full evaluation pipeline
            evaluation_result = self._execute_evaluation_pipeline(niyantran_task)
            
            # Step 3: Make production decision
            decision_result = production_decision_engine.make_decision(
                evaluation_result["evaluation"],
                evaluation_result["supporting_signals"],
                evaluation_result.get("packet_data")
            )
            
            # Step 4: Generate next task
            next_task_result = self._generate_next_task(
                evaluation_result["evaluation"],
                decision_result,
                niyantran_task
            )
            
            # Step 5: Log to bucket
            trace_id = bucket_integration.log_evaluation(
                evaluation_result["evaluation"],
                evaluation_result["supporting_signals"],
                decision_result,
                next_task_result,
                task_data
            )
            
            # Step 6: Create Niyantran response
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            response = NiyantranResponse(
                task_id=niyantran_task.task_id,
                trace_id=trace_id,
                review=self._format_review_for_niyantran(evaluation_result["evaluation"], decision_result),
                next_task=self._format_next_task_for_niyantran(next_task_result, decision_result),
                processing_time_ms=processing_time,
                timestamp=datetime.now().isoformat(),
                status="completed"
            )
            
            logger.info(f"[NIYANTRAN] Task processed successfully: trace_id={trace_id}, decision={decision_result.get('decision')}")
            return response.to_dict()
            
        except Exception as e:
            logger.error(f"[NIYANTRAN] Task processing failed: {e}")
            
            # Create error response
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            error_response = {
                "task_id": task_data.get("task_id", "unknown"),
                "trace_id": f"error-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "review": {
                    "score": 0,
                    "decision": "reject",
                    "status": "fail",
                    "confidence": 0.0,
                    "failure_reasons": [f"Processing error: {str(e)}"],
                    "error": True
                },
                "next_task": {
                    "task_type": "correction",
                    "title": "System Recovery Task",
                    "difficulty": "foundational",
                    "reason": "Processing system encountered an error"
                },
                "processing_metadata": {
                    "processing_time_ms": processing_time,
                    "timestamp": datetime.now().isoformat(),
                    "status": "error"
                }
            }
            
            return error_response
    
    def _execute_evaluation_pipeline(self, niyantran_task: NiyantranTask) -> Dict[str, Any]:
        """Execute the full evaluation pipeline"""
        
        # Use final convergence orchestrator
        convergence_result = final_convergence.process_with_convergence(
            task_title=niyantran_task.task_title,
            task_description=niyantran_task.task_description,
            repository_url=niyantran_task.repository_url,
            module_id=niyantran_task.module_id,
            schema_version=niyantran_task.schema_version,
            pdf_text=niyantran_task.pdf_text
        )
        
        return {
            "evaluation": convergence_result,
            "supporting_signals": convergence_result.get("supporting_signals", {}),
            "packet_data": convergence_result.get("packet_data", {})
        }
    
    def _generate_next_task(
        self, 
        evaluation_result: Dict[str, Any], 
        decision_result: Dict[str, Any],
        niyantran_task: NiyantranTask
    ) -> Dict[str, Any]:
        """Generate next task based on evaluation and decision"""
        
        # Extract next task data from evaluation result
        base_next_task = {
            "next_task_id": evaluation_result.get("next_task_id", f"next-{datetime.now().strftime('%Y%m%d%H%M%S')}"),
            "task_type": decision_result.get("task_type", "correction"),
            "title": evaluation_result.get("title", "Assignment Task"),
            "objective": evaluation_result.get("objective", "Complete assigned task"),
            "focus_area": evaluation_result.get("focus_area", "general"),
            "difficulty": evaluation_result.get("difficulty", "beginner"),
            "reason": evaluation_result.get("reason", "Based on evaluation results")
        }
        
        # Enhance with decision context
        if decision_result.get("decision") == "approve":
            base_next_task["title"] = f"Advanced {base_next_task['focus_area']} Challenge"
            base_next_task["difficulty"] = "advanced"
        elif decision_result.get("decision") == "conditional":
            base_next_task["title"] = f"{base_next_task['focus_area']} Reinforcement Task"
            base_next_task["difficulty"] = "intermediate"
        
        # Add Niyantran-specific fields
        base_next_task.update({
            "assigned_to": niyantran_task.submitted_by,
            "priority": niyantran_task.priority,
            "parent_task_id": niyantran_task.task_id,
            "confidence": decision_result.get("confidence", 0.0),
            "quality_grade": decision_result.get("quality_rubric", {}).get("quality_grade", "D")
        })
        
        return base_next_task
    
    def _format_review_for_niyantran(
        self, 
        evaluation_result: Dict[str, Any], 
        decision_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format review results for Niyantran consumption"""
        
        return {
            # Core results
            "score": decision_result.get("score", evaluation_result.get("score", 0)),
            "decision": decision_result.get("decision", "reject"),
            "status": evaluation_result.get("status", "fail"),
            "confidence": decision_result.get("confidence", 0.0),
            
            # Quality assessment
            "quality_rubric": decision_result.get("quality_rubric", {}),
            "pac_detection": decision_result.get("pac_detection", {}),
            "decision_criteria": decision_result.get("decision_criteria", {}),
            
            # Feedback
            "evaluation_summary": evaluation_result.get("evaluation_summary", ""),
            "failure_reasons": evaluation_result.get("failure_reasons", []),
            "improvement_hints": evaluation_result.get("improvement_hints", []),
            "missing_features": evaluation_result.get("missing_features", []),
            
            # Evidence
            "evidence_summary": evaluation_result.get("evidence_summary", {}),
            "expected_vs_delivered": evaluation_result.get("expected_vs_delivered", {}),
            
            # Component scores
            "component_scores": {
                "title_score": evaluation_result.get("title_score", 0),
                "description_score": evaluation_result.get("description_score", 0),
                "repository_score": evaluation_result.get("repository_score", 0)
            },
            
            # Metadata
            "canonical_authority": evaluation_result.get("canonical_authority", False),
            "evaluation_basis": evaluation_result.get("evaluation_basis", "unknown"),
            "validation_applied": bool(evaluation_result.get("validation_metadata"))
        }
    
    def _format_next_task_for_niyantran(
        self, 
        next_task_result: Dict[str, Any], 
        decision_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format next task for Niyantran consumption"""
        
        return {
            # Task identification
            "task_id": next_task_result.get("next_task_id"),
            "task_type": next_task_result.get("task_type"),
            "parent_task_id": next_task_result.get("parent_task_id"),
            
            # Task details
            "title": next_task_result.get("title"),
            "objective": next_task_result.get("objective"),
            "focus_area": next_task_result.get("focus_area"),
            "difficulty": next_task_result.get("difficulty"),
            "reason": next_task_result.get("reason"),
            
            # Assignment details
            "assigned_to": next_task_result.get("assigned_to"),
            "priority": next_task_result.get("priority", "normal"),
            "confidence": next_task_result.get("confidence"),
            "quality_grade": next_task_result.get("quality_grade"),
            
            # Context
            "derived_from_decision": decision_result.get("decision"),
            "approval_threshold_met": decision_result.get("decision_criteria", {}).get("approval_threshold_met", False),
            "evidence_driven": True
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for Niyantran connection"""
        try:
            # Test bucket connection
            bucket_stats = bucket_integration.get_bucket_stats()
            
            # Test final convergence
            test_result = final_convergence.process_with_convergence(
                task_title="Health Check Test",
                task_description="System health verification test",
                repository_url=None,
                module_id="task-review-agent",
                schema_version="v1.0",
                pdf_text=""
            )
            
            return {
                "status": "healthy",
                "service": self.service_name,
                "version": self.version,
                "timestamp": datetime.now().isoformat(),
                "bucket_stats": bucket_stats,
                "pipeline_test": {
                    "status": "pass" if test_result.get("score") is not None else "fail",
                    "score": test_result.get("score", 0)
                }
            }
            
        except Exception as e:
            logger.error(f"[NIYANTRAN] Health check failed: {e}")
            return {
                "status": "unhealthy",
                "service": self.service_name,
                "version": self.version,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

# Global Niyantran connection service
niyantran_connection = NiyantranConnectionService()