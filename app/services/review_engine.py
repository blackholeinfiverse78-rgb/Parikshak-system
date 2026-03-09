"""
Task Review Engine - Adapter for Deterministic Evaluation v5.0 (PDF Support)
Bridges the upgraded EvaluationEngine with the ReviewOutput schema.
"""
from typing import Optional
from ..models.schemas import Task, ReviewOutput, Analysis, Meta
from ..core.interfaces.review_engine_interface import ReviewEngineInterface
from .evaluation_engine import EvaluationEngine
from .pdf_analyzer import PDFAnalyzer
import logging
import time

logger = logging.getLogger("review_engine")

class ReviewEngine(ReviewEngineInterface):
    def __init__(self):
        self.evaluation_engine = EvaluationEngine()
        
    def evaluate(self, task: dict) -> dict:
        """
        Satisfies ReviewEngineInterface using the upgraded deterministic evaluation.
        """
        task_obj = Task(**task)
        result = self.review_task(task_obj)
        return result.model_dump()

    def review_task(self, task: Task) -> ReviewOutput:
        """
        Executes the full upgraded deterministic evaluation with PDF insights.
        """
        start_time = time.time()
        
        # 1. Clean description & Extract GitHub URL markers if needed
        description = task.task_description
        github_url = None
        clean_description = description
        
        if "--- GitHub Repository Metrics ---" in description:
            try:
                marker = "--- GitHub Repository Metrics ---"
                parts = description.split(marker)
                clean_description = parts[0].strip()
                content = parts[1].strip()
                import json
                if "---" in content:
                    content = content.split("---")[0].strip()
                metrics = json.loads(content)
                github_url = metrics.get('url')
            except Exception as e:
                logger.warning(f"Failed to extract GitHub URL from description: {e}")

        # 2. PDF Extracted Text (Injected by orchestrator)
        pdf_text = getattr(task, 'pdf_extracted_text', "") or ""
        # If not passed as attribute, check if markers existed in description (legacy)
        if not pdf_text and "--- Extracted PDF Content ---" in description:
            try:
                marker = "--- Extracted PDF Content ---"
                pdf_text = description.split(marker)[1].strip()
            except:
                pass

        # 3. Run Upgraded Deterministic Evaluation (v5.1)
        eval_result = self.evaluation_engine.evaluate(
            task_title=task.task_title,
            task_description=clean_description,
            repository_url=task.github_repo_link or github_url,
            pdf_text=pdf_text
        )

        # 4. Map to ReviewOutput Schema
        score = int(eval_result['score'])
        
        # Determine status deterministically
        if score >= 80: status = "pass"
        elif score >= 50: status = "borderline"
        else: status = "fail"
        
        # Analysis signals
        analysis = Analysis(
            technical_quality=int((eval_result['architecture_score'] / 20) * 100) if eval_result['architecture_score'] > 0 else 0,
            clarity=int((eval_result['completeness_score'] / 20) * 100) if eval_result['completeness_score'] > 0 else 0,
            discipline_signals=int((eval_result['documentation_score'] / 10) * 100) if eval_result['documentation_score'] > 0 else 0
        )
        
        # Construct improvement hints
        hints = [f"Improve: {f}" for f in eval_result['missing_features']]
        if score < 75:
            hints.append("Enhance architectural modularity as per Step 4 requirements.")
        if score < 65:
            hints.append("Improve document-to-repo alignment (Check Step 7).")

        meta = Meta(
            evaluation_time_ms=int((time.time() - start_time) * 1000),
            mode="rule"
        )

        return ReviewOutput(
            score=score,
            readiness_percent=score,
            status=status,
            failure_reasons=eval_result['missing_features'][:3],
            improvement_hints=hints[:5],
            analysis=analysis,
            meta=meta,
            # Populate upgraded fields
            feature_coverage=eval_result.get('requirement_match', 0.0),
            architecture_score=eval_result['architecture_score'],
            code_quality_score=eval_result['code_quality_score'],
            completeness_score=eval_result['completeness_score'],
            missing_features=eval_result['missing_features'],
            requirement_match=eval_result.get('requirement_match', 0.0),
            evaluation_summary=eval_result['summary'],
            # NEW fields
            documentation_score=eval_result['documentation_score'],
            documentation_alignment=eval_result['documentation_alignment'],
            analysis_pdf=eval_result.get('pdf_analysis')
        )
