from registry.task_registry import TASK_REGISTRY


class DecisionRules:

    def decide(self, review_output: dict):

        score = review_output.get("score", 0)
        missing = review_output.get("missing", [])

        # FAIL → correction
        if score < 40 or missing:
            return TASK_REGISTRY["correction"]

        # BORDERLINE → reinforcement
        if 40 <= score < 70:
            return TASK_REGISTRY["reinforcement"]

        # PASS → advance
        return TASK_REGISTRY["advance"]