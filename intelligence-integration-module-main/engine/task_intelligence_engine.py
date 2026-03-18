from models.next_task_model import NextTask
from engine.decision_rules import DecisionRules
from engine.architecture_guard import ArchitectureGuard


class TaskIntelligenceEngine:

    def __init__(self):
        self.rules = DecisionRules()
        self.guard = ArchitectureGuard()

    def generate_next_task(self, review_output: dict) -> dict:
        """
        Input:
            review_output from scoring engine

        Output:
            next_task dict compatible with API
        """

        # Step 1 — decision rules
        task_data = self.rules.decide(review_output)

        # Step 2 — architecture guard
        task_data = self.guard.ensure_valid(
            task_data,
            review_output,
        )

        # Step 3 — convert to model
        next_task = NextTask(**task_data)

        return next_task.to_dict()