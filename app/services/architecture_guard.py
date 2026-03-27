class ArchitectureGuard:

    def ensure_valid(self, task_data: dict, review_output: dict):

        track = review_output.get("track")

        if not track:
            return task_data

        # Example rule: keep same track
        task_data["focus_area"] = track

        return task_data