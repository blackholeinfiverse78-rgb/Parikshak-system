"""
Product Core v1 Extension - Next Task Generator
Deterministic rule-based task assignment engine.

Version: 1.0.0
Rules: Explicit, versionable, stored in code
"""
from datetime import datetime
from typing import Dict, Any
from enum import Enum


class TaskType(str, Enum):
    """Explicit task type classification"""
    CORRECTION = "correction"
    REINFORCEMENT = "reinforcement"
    ADVANCEMENT = "advancement"


class NextTaskGenerator:
    """
    Deterministic rule engine for next task assignment.
    No AI, no randomness, pure rule-based logic.
    """
    
    # Explicit thresholds (versionable)
    FAIL_THRESHOLD = 50
    PASS_THRESHOLD = 80
    
    # Explicit task rules (versionable)
    TASK_RULES = {
        TaskType.CORRECTION: {
            "title": "Task Definition Fundamentals",
            "objective": "Learn to write clear, structured task descriptions with explicit objectives, requirements, and constraints",
            "focus_area": "Requirements Engineering",
            "difficulty": "beginner",
            "reason": "Score below fail threshold - needs foundational correction"
        },
        TaskType.REINFORCEMENT: {
            "title": "Intermediate Task Structuring",
            "objective": "Build well-defined tasks with technical specifications and clear acceptance criteria",
            "focus_area": "Technical Documentation",
            "difficulty": "intermediate",
            "reason": "Score in borderline range - needs reinforcement practice"
        },
        TaskType.ADVANCEMENT: {
            "title": "Advanced System Design Task",
            "objective": "Design complex systems with comprehensive requirements, architecture, and implementation plans",
            "focus_area": "System Architecture",
            "difficulty": "advanced",
            "reason": "Score above pass threshold - ready for advancement"
        }
    }
    
    @classmethod
    def generate(cls, score: int, previous_submission_id: str) -> Dict[str, Any]:
        """
        Generate next task based on deterministic rules.
        
        Rules:
        - score < FAIL_THRESHOLD (50) → CORRECTION task
        - FAIL_THRESHOLD <= score < PASS_THRESHOLD (50-79) → REINFORCEMENT task
        - score >= PASS_THRESHOLD (80+) → ADVANCEMENT task
        
        Args:
            score: Review score (0-100)
            previous_submission_id: Link to previous submission
            
        Returns:
            Task assignment with type, reason, and timestamp
        """
        # Determine task type (deterministic)
        if score < cls.FAIL_THRESHOLD:
            task_type = TaskType.CORRECTION
        elif score < cls.PASS_THRESHOLD:
            task_type = TaskType.REINFORCEMENT
        else:
            task_type = TaskType.ADVANCEMENT
        
        # Get task definition from rules
        task_def = cls.TASK_RULES[task_type]
        
        # Build assignment
        return {
            "task_type": task_type.value,
            "previous_submission_id": previous_submission_id,
            "title": task_def["title"],
            "objective": task_def["objective"],
            "focus_area": task_def["focus_area"],
            "difficulty": task_def["difficulty"],
            "reason": task_def["reason"],
            "assigned_timestamp": datetime.now()
        }
    
    @classmethod
    def get_thresholds(cls) -> Dict[str, int]:
        """Return current threshold configuration"""
        return {
            "fail_threshold": cls.FAIL_THRESHOLD,
            "pass_threshold": cls.PASS_THRESHOLD
        }
    
    @classmethod
    def get_rules_version(cls) -> str:
        """Return rules version for tracking"""
        return "1.0.0"
