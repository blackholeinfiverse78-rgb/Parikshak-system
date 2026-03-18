from dataclasses import dataclass


@dataclass
class NextTask:
    title: str
    objective: str
    focus_area: str
    difficulty: str
    expected_deliverables: str

    def to_dict(self):
        return {
            "title": self.title,
            "objective": self.objective,
            "focus_area": self.focus_area,
            "difficulty": self.difficulty,
            "expected_deliverables": self.expected_deliverables,
        }