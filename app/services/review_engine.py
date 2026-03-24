"""
Task Review Engine - Final Convergence Adapter
Bridges the final convergence system with the ReviewOutput schema.
"""
from typing import Optional
from ..models.schemas import Task, ReviewOutput, Analysis, Meta
from ..core.interfaces.review_engine_interface import ReviewEngineInterface
from .final_convergence import final_convergence
from .pdf_analyzer import PDFAnalyzer
import logging
import time

logger = logging.getLogger("review_engine")

class ReviewEngine(ReviewEngineInterface):
    def __init__(self):
        # Use final convergence system instead of evaluation engine
        pass

    def evaluate(self, task: dict) -> dict:
        task_obj = Task(**task)
        result = self.review_task(task_obj)
        return result.model_dump()

    def review_task(self, task: Task) -> ReviewOutput:
        start_time = time.time()

        # Clean description — strip legacy GitHub marker if present
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

        # PDF text
        pdf_text = getattr(task, 'pdf_extracted_text', "") or ""
        if not pdf_text and "--- Extracted PDF Content ---" in description:
            try:
                pdf_text = description.split("--- Extracted PDF Content ---")[1].strip()
            except:
                pass

        # Use final convergence system for evaluation
        convergence_result = final_convergence.process_with_convergence(
            task_title=task.task_title,
            task_description=clean_description,
            repository_url=task.github_repo_link or github_url,
            module_id=getattr(task, 'module_id', 'task-review-agent'),
            schema_version=getattr(task, 'schema_version', 'v1.0'),
            pdf_text=pdf_text
        )

        score = int(convergence_result.get('score', 0))
        status = convergence_result.get('status', 'fail')

        # Analysis — extract from convergence result
        supporting_signals = convergence_result.get('supporting_signals', {})
        title_signals = supporting_signals.get('title_signals', {})
        desc_signals = supporting_signals.get('description_signals', {})
        repo_signals = supporting_signals.get('repository_signals', {})

        # Re-run analyzers to get actual scores for display
        from .title_analyzer import TitleAnalyzer
        from .description_analyzer import DescriptionAnalyzer
        _title_result = TitleAnalyzer().analyze(task.task_title, task.task_description)
        _desc_result = DescriptionAnalyzer().analyze(task.task_description)
        title_score_val = _title_result.get('title_score', 0.0)
        desc_score_val = _desc_result.get('description_score', 0.0)

        # Repository score from repo signals
        repo_available = supporting_signals.get('repository_available', False)
        if repo_available and repo_signals:
            arch = repo_signals.get('architecture', {})
            quality = repo_signals.get('quality', {})
            structure = repo_signals.get('structure', {})
            layer_score = min(arch.get('layer_count', 0) / 5, 1.0)
            readme_score = min(quality.get('readme_score', 0) / 3, 1.0)
            file_score = min(structure.get('total_files', 0) / 30, 1.0)
            repo_score_val = round(40 * (0.4 * layer_score + 0.3 * readme_score + 0.3 * file_score), 1)
        else:
            repo_score_val = 0.0

        analysis = Analysis(
            technical_quality=min(100, int(title_score_val)),
            clarity=min(100, int(desc_score_val)),
            discipline_signals=min(100, int(repo_score_val))
        )

        # Extract data from convergence result
        missing_features = convergence_result.get('missing_features', [])
        failure_reasons = convergence_result.get('failure_reasons', [])
        improvement_hints = convergence_result.get('improvement_hints', [])

        # Ensure failure_reasons is non-empty on fail
        if not failure_reasons and score < 50:
            failure_reasons = ["Insufficient technical content in title and description."]

        meta = Meta(
            evaluation_time_ms=int((time.time() - start_time) * 1000),
            mode="hybrid"  # Final convergence mode
        )

        return ReviewOutput(
            score=score,
            readiness_percent=score,
            status=status,
            failure_reasons=failure_reasons[:3],
            improvement_hints=improvement_hints[:5],
            analysis=analysis,
            meta=meta,
            feature_coverage=convergence_result.get('evidence_summary', {}).get('delivery_ratio', 0.0),
            architecture_score=repo_score_val,
            code_quality_score=repo_score_val,
            completeness_score=desc_score_val,
            missing_features=missing_features,
            requirement_match=convergence_result.get('evidence_summary', {}).get('delivery_ratio', 0.0),
            evaluation_summary=convergence_result.get('evaluation_summary', 'Final convergence evaluation complete'),
            documentation_score=repo_score_val,
            documentation_alignment=supporting_signals.get('documentation_alignment', 'low'),
            analysis_pdf=convergence_result.get('pdf_analysis', {}),
            title_score=title_score_val,
            description_score=desc_score_val,
            repository_score=repo_score_val
        )
