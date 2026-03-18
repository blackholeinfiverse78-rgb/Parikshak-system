"""
Autonomous Loop Runner - Continuous Cycle Operation
Implements persistent loop: submission → review → next task → ready for next cycle
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import asyncio
import uuid
from enum import Enum

from ..models.schemas import Task, TaskCreate
from ..models.persistent_storage import TaskSubmission, ReviewRecord, NextTaskRecord
from .review_orchestrator import ReviewOrchestrator
from .registry_validator import registry_validator

logger = logging.getLogger("autonomous_loop")

class LoopState(str, Enum):
    WAITING = "waiting"
    PROCESSING = "processing"
    READY_FOR_NEXT = "ready_for_next"
    ERROR = "error"

class BuilderState:
    """Tracks builder progression across cycles"""
    def __init__(self, builder_id: str):
        self.builder_id = builder_id
        self.current_task_id: Optional[str] = None
        self.previous_tasks: list = []
        self.progression_level: str = "beginner"
        self.focus_area: str = "fundamentals"
        self.last_score: int = 0
        self.cycle_count: int = 0
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

class AutonomousLoopRunner:
    """
    Autonomous Loop Runner - Maintains continuous evaluation cycles
    
    Flow:
    1. Wait for submission
    2. Strict registry validation (BLOCKING)
    3. Process evaluation
    4. Generate next task
    5. Update builder state
    6. Ready for next cycle
    """
    
    def __init__(self, orchestrator: ReviewOrchestrator):
        self.orchestrator = orchestrator
        self.builder_states: Dict[str, BuilderState] = {}
        self.loop_state = LoopState.WAITING
        self.current_cycle_id: Optional[str] = None
        self.is_running = False
    
    async def start_autonomous_loop(self):
        """Start the autonomous loop - runs continuously"""
        logger.info("Starting autonomous loop runner")
        self.is_running = True
        
        while self.is_running:
            try:
                await self._process_cycle()
                await asyncio.sleep(1)  # Prevent tight loop
            except Exception as e:
                logger.error(f"Autonomous loop error: {e}")
                self.loop_state = LoopState.ERROR
                await asyncio.sleep(5)  # Error backoff
    
    def stop_autonomous_loop(self):
        """Stop the autonomous loop"""
        logger.info("Stopping autonomous loop runner")
        self.is_running = False
    
    async def _process_cycle(self):
        """Process one complete cycle"""
        
        if self.loop_state == LoopState.WAITING:
            # Check for pending submissions
            pending_submission = self._get_pending_submission()
            if pending_submission:
                self.loop_state = LoopState.PROCESSING
                self.current_cycle_id = str(uuid.uuid4())[:8]
                logger.info(f"Starting cycle {self.current_cycle_id}")
                
                await self._process_submission(pending_submission)
        
        elif self.loop_state == LoopState.PROCESSING:
            # Processing handled in _process_submission
            pass
        
        elif self.loop_state == LoopState.READY_FOR_NEXT:
            # Cycle complete, ready for next
            logger.info(f"Cycle {self.current_cycle_id} complete - ready for next")
            self.loop_state = LoopState.WAITING
            self.current_cycle_id = None
        
        elif self.loop_state == LoopState.ERROR:
            # Error recovery
            logger.warning("Loop in error state - attempting recovery")
            self.loop_state = LoopState.WAITING
    
    async def _process_submission(self, submission: TaskSubmission):
        """Process a single submission through the complete cycle"""
        
        try:
            # Step 1: STRICT Registry Validation (BLOCKING)
            if not self._strict_registry_validation(submission):
                logger.error(f"Registry validation FAILED - rejecting submission {submission.submission_id}")
                self._mark_submission_rejected(submission, "Registry validation failed")
                self.loop_state = LoopState.READY_FOR_NEXT
                return
            
            # Step 2: Get/Create Builder State
            builder_state = self._get_or_create_builder_state(submission.submitted_by)
            
            # Step 3: Create Task with State Context
            task = self._create_task_with_context(submission, builder_state)
            
            # Step 4: Process through Orchestrator
            result = self.orchestrator.process_submission(task)
            
            # Step 5: Update Builder State
            self._update_builder_state(builder_state, result, task)
            
            # Step 6: Store Results
            self._store_cycle_results(submission, result, builder_state)
            
            # Step 7: Prepare for Next Cycle
            self.loop_state = LoopState.READY_FOR_NEXT
            
            logger.info(f"Cycle complete - Builder {builder_state.builder_id} progressed to level {builder_state.progression_level}")
            
        except Exception as e:
            logger.error(f"Cycle processing failed: {e}")
            self.loop_state = LoopState.ERROR
    
    def _strict_registry_validation(self, submission: TaskSubmission) -> bool:
        """STRICT registry validation - BLOCKS evaluation if invalid"""
        
        # Validate module_id
        module_validation = registry_validator.validate_module_id(submission.module_id)
        if module_validation.status.value != "VALID":
            logger.error(f"Invalid module_id: {submission.module_id} - {module_validation.reason}")
            return False
        
        # Validate lifecycle stage
        lifecycle_validation = registry_validator.validate_lifecycle_stage(submission.module_id)
        if lifecycle_validation.status.value != "VALID":
            logger.error(f"Invalid lifecycle stage for {submission.module_id} - {lifecycle_validation.reason}")
            return False
        
        # Validate schema version
        schema_validation = registry_validator.validate_schema_version(submission.module_id, submission.schema_version)
        if schema_validation.status.value != "VALID":
            logger.error(f"Schema version mismatch for {submission.module_id} - {schema_validation.reason}")
            return False
        
        logger.info(f"Registry validation PASSED for {submission.module_id}")
        return True
    
    def _get_or_create_builder_state(self, builder_id: str) -> BuilderState:
        """Get existing builder state or create new one"""
        
        if builder_id not in self.builder_states:
            self.builder_states[builder_id] = BuilderState(builder_id)
            logger.info(f"Created new builder state for {builder_id}")
        
        return self.builder_states[builder_id]
    
    def _create_task_with_context(self, submission: TaskSubmission, builder_state: BuilderState) -> Task:
        """Create task with builder state context"""
        
        # Add builder context to task description
        context_description = f"{submission.task_description}\n\n--- Builder Context ---\n"
        context_description += f"Previous Tasks: {len(builder_state.previous_tasks)}\n"
        context_description += f"Current Level: {builder_state.progression_level}\n"
        context_description += f"Focus Area: {builder_state.focus_area}\n"
        context_description += f"Last Score: {builder_state.last_score}\n"
        
        return Task(
            task_id=submission.submission_id,
            task_title=submission.task_title,
            task_description=context_description,
            submitted_by=submission.submitted_by,
            timestamp=submission.submitted_at,
            github_repo_link=submission.github_repo_link,
            module_id=submission.module_id,
            schema_version=submission.schema_version
        )
    
    def _update_builder_state(self, builder_state: BuilderState, result, task: Task):
        """Update builder state based on evaluation result"""
        
        # Update progression based on score
        score = result.review.score
        status = result.review.status
        
        # Track previous task
        builder_state.previous_tasks.append({
            "task_id": task.task_id,
            "title": task.task_title,
            "score": score,
            "status": status,
            "timestamp": datetime.now().isoformat()
        })
        
        # Update progression level
        if score >= 80 and builder_state.progression_level == "beginner":
            builder_state.progression_level = "intermediate"
        elif score >= 80 and builder_state.progression_level == "intermediate":
            builder_state.progression_level = "advanced"
        elif score < 50:
            # Regression - stay at current level but adjust focus
            pass
        
        # Update focus area based on next task
        if hasattr(result.next_task, 'focus_area'):
            builder_state.focus_area = result.next_task.focus_area
        
        # Update tracking
        builder_state.last_score = score
        builder_state.cycle_count += 1
        builder_state.current_task_id = task.task_id
        builder_state.updated_at = datetime.now()
        
        logger.info(f"Builder {builder_state.builder_id} updated: Level={builder_state.progression_level}, Score={score}")
    
    def _get_pending_submission(self) -> Optional[TaskSubmission]:
        """Get next pending submission (mock implementation)"""
        # In real implementation, this would check a queue or database
        # For now, return None to indicate no pending submissions
        return None
    
    def _mark_submission_rejected(self, submission: TaskSubmission, reason: str):
        """Mark submission as rejected due to validation failure"""
        logger.warning(f"Submission {submission.submission_id} rejected: {reason}")
        # In real implementation, update submission status in storage
    
    def _store_cycle_results(self, submission: TaskSubmission, result, builder_state: BuilderState):
        """Store complete cycle results"""
        logger.info(f"Storing cycle results for {submission.submission_id}")
        # In real implementation, persist to storage
    
    def get_builder_state(self, builder_id: str) -> Optional[BuilderState]:
        """Get current builder state"""
        return self.builder_states.get(builder_id)
    
    def get_loop_status(self) -> Dict[str, Any]:
        """Get current loop status"""
        return {
            "is_running": self.is_running,
            "loop_state": self.loop_state.value,
            "current_cycle_id": self.current_cycle_id,
            "active_builders": len(self.builder_states),
            "total_cycles": sum(state.cycle_count for state in self.builder_states.values())
        }

# Global autonomous loop instance
autonomous_loop: Optional[AutonomousLoopRunner] = None

def initialize_autonomous_loop(orchestrator: ReviewOrchestrator) -> AutonomousLoopRunner:
    """Initialize the global autonomous loop"""
    global autonomous_loop
    autonomous_loop = AutonomousLoopRunner(orchestrator)
    return autonomous_loop

def get_autonomous_loop() -> Optional[AutonomousLoopRunner]:
    """Get the global autonomous loop instance"""
    return autonomous_loop