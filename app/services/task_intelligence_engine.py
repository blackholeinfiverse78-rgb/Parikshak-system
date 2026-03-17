"""
Task Intelligence Engine - Integrated into Hybrid System
Autonomous next task generation based on review output
"""
from typing import Dict, Any, Optional
from ..models.schemas import V2NextTask
from enum import Enum
import logging

logger = logging.getLogger("intelligence_engine")

class TaskType(str, Enum):
    CORRECTION = "correction"
    REINFORCEMENT = "reinforcement" 
    ADVANCEMENT = "advancement"

class TaskIntelligenceEngine:
    """
    Autonomous intelligence layer for next task generation.
    Integrates with the hybrid evaluation pipeline to provide intelligent task progression.
    """
    
    def __init__(self):
        # Task registry with detailed task definitions
        self.task_registry = {
            TaskType.CORRECTION: {
                "title": "Task Definition Fundamentals",
                "objective": "Learn to write clear, structured task descriptions with explicit objectives, requirements, and constraints",
                "focus_area": "Requirements Engineering",
                "difficulty": "beginner"
            },
            TaskType.REINFORCEMENT: {
                "title": "Intermediate Task Structuring", 
                "objective": "Build well-defined tasks with technical specifications and clear acceptance criteria",
                "focus_area": "Technical Documentation",
                "difficulty": "intermediate"
            },
            TaskType.ADVANCEMENT: {
                "title": "Advanced System Design Task",
                "objective": "Design complex systems with comprehensive requirements, architecture, and implementation plans", 
                "focus_area": "System Architecture",
                "difficulty": "advanced"
            }
        }
        
        # Decision thresholds aligned with hybrid pipeline
        self.fail_threshold = 50
        self.pass_threshold = 80
    
    def generate_next_task(self, review_output: Dict[str, Any], builder_context: Optional[Dict[str, Any]] = None) -> V2NextTask:
        """
        Generate next task based on review output AND system state.
        
        Args:
            review_output: Output from hybrid evaluation pipeline
            builder_context: Builder progression state and history
            
        Returns:
            V2NextTask object for next task assignment
        """
        logger.info("Generating next task from intelligence engine with system context")
        
        # Extract key metrics from review output
        score = review_output.get("score", 0)
        status = review_output.get("status", "fail")
        missing_requirements = review_output.get("failure_reasons", [])
        completeness_score = review_output.get("completeness_score", 0)
        
        # Extract builder context
        if builder_context:
            previous_tasks = builder_context.get("previous_tasks", [])
            progression_level = builder_context.get("progression_level", "beginner")
            focus_area = builder_context.get("focus_area", "fundamentals")
            cycle_count = builder_context.get("cycle_count", 0)
        else:
            previous_tasks = []
            progression_level = "beginner"
            focus_area = "fundamentals"
            cycle_count = 0
        
        # Apply system-driven decision rules
        task_type = self._apply_system_driven_rules(
            score, status, missing_requirements, completeness_score,
            previous_tasks, progression_level, focus_area, cycle_count
        )
        
        # Get task definition
        task_data = self.task_registry[task_type]
        
        # Apply system-aware architecture guard
        task_data = self._apply_system_aware_guard(task_data, review_output, builder_context)
        
        # Create V2NextTask object
        next_task = V2NextTask(
            title=task_data["title"],
            objective=task_data["objective"], 
            focus_area=task_data["focus_area"],
            difficulty=task_data["difficulty"]
        )
        
        logger.info(f"Generated system-driven next task: {task_type.value} - {next_task.title} (Level: {progression_level})")
        return next_task
    
    def _apply_system_driven_rules(self, score: int, status: str, missing_requirements: list, 
                                 completeness_score: float, previous_tasks: list, 
                                 progression_level: str, focus_area: str, cycle_count: int) -> TaskType:
        """
        Apply system-driven decision rules that consider builder progression and history.
        
        Rules:
        1. Registry/Module progression takes precedence
        2. Builder history influences difficulty
        3. Focus area consistency maintained
        4. Cycle count affects task complexity
        """
        
        # Rule 1: Critical failures always require correction regardless of history
        if missing_requirements and len(missing_requirements) >= 3:
            logger.info("Decision: CORRECTION (critical missing requirements override system state)")
            return TaskType.CORRECTION
        
        # Rule 2: System-driven progression based on builder level
        if progression_level == "beginner":
            # Beginners need to master fundamentals first
            if score < 60:  # Higher threshold for beginners
                logger.info(f"Decision: CORRECTION (beginner level, score={score})")
                return TaskType.CORRECTION
            elif score < 75:  # Higher threshold for advancement
                logger.info(f"Decision: REINFORCEMENT (beginner level, score={score})")
                return TaskType.REINFORCEMENT
            else:
                logger.info(f"Decision: ADVANCEMENT (beginner ready for intermediate, score={score})")
                return TaskType.ADVANCEMENT
        
        elif progression_level == "intermediate":
            # Intermediate builders have proven basics
            if score < 50:
                logger.info(f"Decision: CORRECTION (intermediate regression, score={score})")
                return TaskType.CORRECTION
            elif score < 80:  # Standard threshold
                logger.info(f"Decision: REINFORCEMENT (intermediate level, score={score})")
                return TaskType.REINFORCEMENT
            else:
                logger.info(f"Decision: ADVANCEMENT (intermediate ready for advanced, score={score})")
                return TaskType.ADVANCEMENT
        
        else:  # Advanced
            # Advanced builders get challenging tasks
            if score < 40:  # Lower threshold - they should know better
                logger.info(f"Decision: CORRECTION (advanced regression, score={score})")
                return TaskType.CORRECTION
            elif score < 85:  # Higher threshold for advancement
                logger.info(f"Decision: REINFORCEMENT (advanced level, score={score})")
                return TaskType.REINFORCEMENT
            else:
                logger.info(f"Decision: ADVANCEMENT (advanced level mastery, score={score})")
                return TaskType.ADVANCEMENT
    
    def _apply_system_aware_guard(self, task_data: Dict[str, Any], review_output: Dict[str, Any], 
                                builder_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Apply system-aware architecture guard that considers builder progression.
        """
        
        if not builder_context:
            return self._apply_architecture_guard(task_data, review_output)
        
        progression_level = builder_context.get("progression_level", "beginner")
        focus_area = builder_context.get("focus_area", "fundamentals")
        previous_tasks = builder_context.get("previous_tasks", [])
        
        # Maintain focus area consistency unless progression warrants change
        if len(previous_tasks) >= 3:  # After 3 tasks, can shift focus
            recent_scores = [task.get("score", 0) for task in previous_tasks[-3:]]
            avg_recent_score = sum(recent_scores) / len(recent_scores)
            
            if avg_recent_score >= 75:  # Consistent good performance
                # Can advance focus area
                if focus_area == "Requirements Engineering" and progression_level != "beginner":
                    task_data["focus_area"] = "Technical Documentation"
                elif focus_area == "Technical Documentation" and progression_level == "advanced":
                    task_data["focus_area"] = "System Architecture"
        
        # Adjust difficulty based on progression level
        if progression_level == "beginner" and task_data["difficulty"] == "advanced":
            task_data["difficulty"] = "intermediate"
            task_data["focus_area"] = "Requirements Engineering"
        elif progression_level == "advanced" and task_data["difficulty"] == "beginner":
            task_data["difficulty"] = "intermediate"  # Don't jump too far
        
        return task_data
    
    def _apply_architecture_guard(self, task_data: Dict[str, Any], review_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Legacy architecture guard method for backward compatibility.
        Simple implementation without recursion.
        """
        # Simple guard - just return task_data with basic adjustments
        repository_score = review_output.get("repository_score", 0)
        score = review_output.get("score", 0)
        
        # Basic adjustments
        if score < 50 and task_data["difficulty"] == "advanced":
            task_data["difficulty"] = "beginner"
            task_data["focus_area"] = "Requirements Engineering"
        elif repository_score > 20 and task_data["difficulty"] == "advanced":
            task_data["focus_area"] = "System Architecture"
        
        return task_data
    
    def get_task_progression_info(self, review_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get information about task progression without generating the actual task.
        Useful for analytics and debugging.
        """
        score = review_output.get("score", 0)
        status = review_output.get("status", "fail")
        missing_requirements = review_output.get("failure_reasons", [])
        completeness_score = review_output.get("completeness_score", 0)
        
        task_type = self._apply_decision_rules(score, status, missing_requirements, completeness_score)
        
        return {
            "recommended_task_type": task_type.value,
            "reasoning": self._get_decision_reasoning(score, status, missing_requirements, completeness_score),
            "difficulty_progression": self._get_difficulty_progression(task_type),
            "focus_area_recommendation": self.task_registry[task_type]["focus_area"]
        }
    
    def _get_decision_reasoning(self, score: int, status: str, missing_requirements: list, completeness_score: float) -> str:
        """Generate human-readable reasoning for task assignment decision"""
        
        if len(missing_requirements) >= 3:
            return f"Critical missing requirements detected: {missing_requirements[:3]}"
        elif completeness_score < 25:
            return f"Assignment completeness too low: {completeness_score}%"
        elif score < self.fail_threshold:
            return f"Score below fail threshold: {score} < {self.fail_threshold}"
        elif score < self.pass_threshold:
            return f"Score in borderline range: {self.fail_threshold} ≤ {score} < {self.pass_threshold}"
        else:
            return f"Score meets advancement criteria: {score} ≥ {self.pass_threshold}"
    
    def _get_difficulty_progression(self, task_type: TaskType) -> str:
        """Get difficulty progression information"""
        
        progression_map = {
            TaskType.CORRECTION: "Foundation building → Beginner level focus",
            TaskType.REINFORCEMENT: "Skill strengthening → Intermediate level practice", 
            TaskType.ADVANCEMENT: "Capability expansion → Advanced level challenges"
        }
        
        return progression_map[task_type]