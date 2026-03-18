from engine.task_intelligence_engine import TaskIntelligenceEngine


class IntelligenceAdapter:

    def __init__(self):
        self.engine = TaskIntelligenceEngine()

    def process(self, review_output: dict):

        next_task = self.engine.generate_next_task(
            review_output
        )

        return next_task