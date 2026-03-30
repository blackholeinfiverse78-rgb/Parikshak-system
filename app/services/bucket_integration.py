"""
Bucket Integration Service - Evaluation Logging
Logs every evaluation with score, decision, signals, next task, and trace_id
No evaluation should be silent
"""
import json
import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import logging
from dataclasses import dataclass, asdict

logger = logging.getLogger("bucket_integration")

@dataclass
class EvaluationLog:
    """Structured evaluation log entry"""
    trace_id: str
    timestamp: str
    score: int
    decision: str
    status: str
    task_type: str
    confidence: float
    
    # Core data
    task_title: str
    task_description: str
    submitted_by: str
    repository_url: Optional[str]
    
    # Evaluation results
    evaluation_summary: str
    failure_reasons: list
    improvement_hints: list
    missing_features: list
    
    # Quality metrics
    quality_rubric: Dict[str, Any]
    pac_detection: Dict[str, Any]
    decision_criteria: Dict[str, Any]
    
    # Supporting signals
    signals: Dict[str, Any]
    
    # Next task
    next_task: Dict[str, Any]
    
    # Metadata
    evaluation_time_ms: int
    canonical_authority: bool
    validation_applied: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

class BucketIntegrationService:
    """
    Bucket integration for comprehensive evaluation logging
    Ensures no evaluation is silent - all are logged with full context
    """
    
    def __init__(self, bucket_path: str = "storage/bucket_logs"):
        self.bucket_path = bucket_path
        self.ensure_bucket_exists()
        
    def ensure_bucket_exists(self):
        """Ensure bucket directory exists"""
        os.makedirs(self.bucket_path, exist_ok=True)
        
        # Create index file if it doesn't exist
        index_file = os.path.join(self.bucket_path, "evaluation_index.jsonl")
        if not os.path.exists(index_file):
            with open(index_file, 'w') as f:
                f.write("")  # Create empty file
    
    def log_evaluation(
        self,
        evaluation_result: Dict[str, Any],
        supporting_signals: Dict[str, Any],
        decision_result: Dict[str, Any],
        next_task_result: Dict[str, Any],
        task_data: Dict[str, Any],
        trace_id: Optional[str] = None
    ) -> str:
        """
        Log complete evaluation to bucket
        
        Args:
            evaluation_result: Core evaluation results
            supporting_signals: Supporting signals data
            decision_result: Production decision results
            next_task_result: Next task assignment
            task_data: Original task submission data
            trace_id: Optional trace ID (generated if not provided)
            
        Returns:
            trace_id for the logged evaluation
        """
        if not trace_id:
            trace_id = str(uuid.uuid4())
        
        timestamp = datetime.now().isoformat()
        
        # Create structured log entry
        log_entry = EvaluationLog(
            trace_id=trace_id,
            timestamp=timestamp,
            score=decision_result.get("score", evaluation_result.get("score", 0)),
            decision=decision_result.get("decision", "unknown"),
            status=evaluation_result.get("status", "unknown"),
            task_type=decision_result.get("task_type", "correction"),
            confidence=decision_result.get("confidence", 0.0),
            
            # Core data
            task_title=task_data.get("task_title", ""),
            task_description=task_data.get("task_description", "")[:500] + "..." if len(task_data.get("task_description", "")) > 500 else task_data.get("task_description", ""),
            submitted_by=task_data.get("submitted_by", "unknown"),
            repository_url=task_data.get("github_repo_link"),
            
            # Evaluation results
            evaluation_summary=evaluation_result.get("evaluation_summary", ""),
            failure_reasons=evaluation_result.get("failure_reasons", []),
            improvement_hints=evaluation_result.get("improvement_hints", []),
            missing_features=evaluation_result.get("missing_features", []),
            
            # Quality metrics
            quality_rubric=decision_result.get("quality_rubric", {}),
            pac_detection=decision_result.get("pac_detection", {}),
            decision_criteria=decision_result.get("decision_criteria", {}),
            
            # Supporting signals (summarized)
            signals=self._summarize_signals(supporting_signals),
            
            # Next task
            next_task={
                "task_id": next_task_result.get("next_task_id", ""),
                "task_type": next_task_result.get("task_type", ""),
                "title": next_task_result.get("title", ""),
                "difficulty": next_task_result.get("difficulty", ""),
                "reason": next_task_result.get("reason", "")
            },
            
            # Metadata
            evaluation_time_ms=evaluation_result.get("meta", {}).get("evaluation_time_ms", 0),
            canonical_authority=evaluation_result.get("canonical_authority", False),
            validation_applied=bool(evaluation_result.get("validation_metadata"))
        )
        
        # Write to bucket
        self._write_to_bucket(log_entry)
        
        # Update index
        self._update_index(log_entry)
        
        logger.info(f"[BUCKET] Logged evaluation: trace_id={trace_id}, score={log_entry.score}, decision={log_entry.decision}")
        return trace_id
    
    def _summarize_signals(self, supporting_signals: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize supporting signals for bucket storage"""
        return {
            "repository_available": supporting_signals.get("repository_available", False),
            "feature_match_ratio": supporting_signals.get("feature_match_ratio", 0.0),
            "expected_features_count": len(supporting_signals.get("expected_features", [])),
            "implemented_features_count": len(supporting_signals.get("implemented_features", [])),
            "missing_features_count": len(supporting_signals.get("missing_features", [])),
            "failure_indicators_count": len(supporting_signals.get("failure_indicators", [])),
            "delivery_ratio": supporting_signals.get("expected_vs_delivered_evidence", {}).get("delivery_ratio", 0.0),
            "title_signals_present": bool(supporting_signals.get("title_signals")),
            "description_signals_present": bool(supporting_signals.get("description_signals")),
            "repository_signals_present": bool(supporting_signals.get("repository_signals"))
        }
    
    def _write_to_bucket(self, log_entry: EvaluationLog):
        """Write log entry to bucket file"""
        # Create daily log file
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(self.bucket_path, f"evaluations_{date_str}.jsonl")
        
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                json.dump(log_entry.to_dict(), f, ensure_ascii=False)
                f.write('\n')
        except Exception as e:
            logger.error(f"[BUCKET] Failed to write log entry: {e}")
            # Fallback to error log file
            error_file = os.path.join(self.bucket_path, "bucket_errors.log")
            with open(error_file, 'a') as f:
                f.write(f"{datetime.now().isoformat()}: Failed to log {log_entry.trace_id}: {str(e)}\n")
    
    def _update_index(self, log_entry: EvaluationLog):
        """Update evaluation index with summary"""
        index_file = os.path.join(self.bucket_path, "evaluation_index.jsonl")
        
        index_entry = {
            "trace_id": log_entry.trace_id,
            "timestamp": log_entry.timestamp,
            "score": log_entry.score,
            "decision": log_entry.decision,
            "status": log_entry.status,
            "task_type": log_entry.task_type,
            "confidence": log_entry.confidence,
            "task_title": log_entry.task_title[:100] + "..." if len(log_entry.task_title) > 100 else log_entry.task_title,
            "submitted_by": log_entry.submitted_by,
            "has_repository": bool(log_entry.repository_url),
            "quality_grade": log_entry.quality_rubric.get("quality_grade", "D"),
            "pac_score": log_entry.pac_detection.get("pac_score", 0)
        }
        
        try:
            with open(index_file, 'a', encoding='utf-8') as f:
                json.dump(index_entry, f, ensure_ascii=False)
                f.write('\n')
        except Exception as e:
            logger.error(f"[BUCKET] Failed to update index: {e}")
    
    def get_evaluation_logs(self, limit: int = 100) -> list:
        """Retrieve recent evaluation logs from index"""
        index_file = os.path.join(self.bucket_path, "evaluation_index.jsonl")
        
        if not os.path.exists(index_file):
            return []
        
        logs = []
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Get last N lines
                for line in lines[-limit:]:
                    if line.strip():
                        logs.append(json.loads(line))
        except Exception as e:
            logger.error(f"[BUCKET] Failed to read logs: {e}")
        
        return logs
    
    def get_evaluation_by_trace_id(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve specific evaluation by trace_id"""
        # Search through daily log files (last 7 days)
        for days_back in range(7):
            date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            date = date.replace(day=date.day - days_back)
            date_str = date.strftime("%Y-%m-%d")
            log_file = os.path.join(self.bucket_path, f"evaluations_{date_str}.jsonl")
            
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.strip():
                                log_entry = json.loads(line)
                                if log_entry.get("trace_id") == trace_id:
                                    return log_entry
                except Exception as e:
                    logger.error(f"[BUCKET] Error searching {log_file}: {e}")
        
        return None
    
    def get_bucket_stats(self) -> Dict[str, Any]:
        """Get bucket statistics"""
        stats = {
            "total_evaluations": 0,
            "decisions": {"approve": 0, "conditional": 0, "reject": 0},
            "avg_score": 0,
            "avg_confidence": 0,
            "quality_grades": {"A": 0, "B": 0, "C": 0, "D": 0}
        }
        
        logs = self.get_evaluation_logs(1000)  # Last 1000 evaluations
        
        if not logs:
            return stats
        
        stats["total_evaluations"] = len(logs)
        
        total_score = 0
        total_confidence = 0
        
        for log in logs:
            # Decision counts
            decision = log.get("decision", "reject")
            if decision in stats["decisions"]:
                stats["decisions"][decision] += 1
            
            # Score average
            total_score += log.get("score", 0)
            
            # Confidence average
            total_confidence += log.get("confidence", 0)
            
            # Quality grade counts
            quality_grade = log.get("quality_grade", "D")
            if quality_grade in stats["quality_grades"]:
                stats["quality_grades"][quality_grade] += 1
        
        if len(logs) > 0:
            stats["avg_score"] = round(total_score / len(logs), 1)
            stats["avg_confidence"] = round(total_confidence / len(logs), 3)
        
        return stats

# Global bucket integration service
bucket_integration = BucketIntegrationService()