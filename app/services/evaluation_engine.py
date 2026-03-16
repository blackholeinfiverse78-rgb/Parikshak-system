"""
Deterministic Evaluation Engine - Upgraded v5.0 (PDF Support)
Orchestrates the upgraded 10-step deterministic evaluation process with PDF insights.
"""
import logging
from typing import Dict, Any, Optional

from .intent_extractor import IntentExtractor
from .repository_analyzer import RepositoryAnalyzer
from .feature_matcher import FeatureMatcher
from .scoring_engine import ScoringEngine
from .pdf_analyzer import PDFAnalyzer
from .title_analyzer import TitleAnalyzer
from .description_analyzer import DescriptionAnalyzer

logger = logging.getLogger("evaluation_engine")

class EvaluationEngine:
    def __init__(self):
        self.intent_extractor = IntentExtractor()
        self.repository_analyzer = RepositoryAnalyzer()
        self.feature_matcher = FeatureMatcher()
        self.scoring_engine = ScoringEngine()
        self.pdf_analyzer = PDFAnalyzer()
        self.title_analyzer = TitleAnalyzer()
        self.description_analyzer = DescriptionAnalyzer()
    
    def evaluate(
        self, 
        task_title: str, 
        task_description: str, 
        repository_url: str = None,
        pdf_text: str = ""
    ) -> Dict[str, Any]:
        """
        Full upgraded evaluation pipeline (v5.1):
        1. Requirement Extraction (Title + Description + PDF)
        2. GitHub Repository Analysis
        3. Requirement Matching (Features + Tech Stack + Architecture)
        4. Multi-factor Scoring
        """
        logger.info(f"Starting requirement-matching evaluation for: {task_title}")
        
        # Step 1: Requirement Extraction (Title + Description + PDF)
        intent = self.intent_extractor.extract(task_title, task_description, pdf_text)
        logger.info(f"Step 1: Extracted {len(intent['expected_features'])} features from requirements.")
        
        # Step 2: GitHub Repository Analysis
        repo_signals = self.repository_analyzer.analyze(repository_url)
        repo_available = repo_signals and not repo_signals.get('error') and repo_signals.get('structure', {}).get('total_files', 0) > 0
        logger.info(f"Step 2: Repo Analysis Complete - Architecture Layers: {repo_signals.get('architecture', {}).get('layer_count', 0) if repo_signals else 0}")

        # Step 3: Requirement Matching
        match_results = self.feature_matcher.compute_match(intent, repo_signals or {})
        logger.info(f"Step 3: Requirement Match Ratio: {match_results['feature_match_ratio']}")

        # Step 4: Scoring
        pdf_analysis = self.pdf_analyzer.analyze_content(pdf_text)

        if repo_available:
            title_result = self.title_analyzer.analyze(task_title, task_description)
            desc_result = self.description_analyzer.analyze(task_description)
            final_result = self.scoring_engine.calculate_final_score(
                intent,
                repo_signals,
                match_results,
                pdf_analysis,
                pdf_text
            )
            final_result['title_score'] = round(title_result['title_score'], 1)
            final_result['description_score'] = round(desc_result['description_score'], 1)
            final_result['repository_score'] = round(
                final_result.get('architecture_score', 0) + final_result.get('code_quality_score', 0), 1
            )
        else:
            logger.warning("Repo unavailable or empty — falling back to title+description scoring.")
            title_result = self.title_analyzer.analyze(task_title, task_description)
            desc_result = self.description_analyzer.analyze(task_description)

            title_score = title_result['title_score']
            desc_score = desc_result['description_score']
            total_score = round(title_score + desc_score, 1)

            alignment_status = "high" if total_score >= 48 else "moderate" if total_score >= 30 else "low"
            final_result = {
                "score": total_score,
                "final_score": total_score,
                "classification": self.scoring_engine.classify_score(total_score),
                "score_breakdown": {
                    "title": round(title_score, 1),
                    "description": round(desc_score, 1),
                    "repository": 0.0
                },
                "signals": {
                    "title": title_result.get('signals', {}),
                    "description": desc_result.get('signals', {})
                },
                "requirement_match": round(desc_result['metrics']['technical_term_ratio'], 2),
                "architecture_score": 0.0,
                "code_quality_score": 0.0,
                "completeness_score": round(desc_score, 1),
                "documentation_score": 0.0,
                "documentation_alignment": alignment_status,
                "title_score": round(title_score, 1),
                "description_score": round(desc_score, 1),
                "repository_score": 0.0,
                "missing_features": match_results.get('missing_features', []),
                "summary": (
                    f"Evaluation complete (no repository). Score: {total_score}. "
                    f"Title scored {title_score:.1f}/20, Description scored {desc_score:.1f}/40. "
                    "Submit a real GitHub repository to unlock full 100-point evaluation."
                )
            }

        # Package Results — add keys expected by tests
        final_result['intent'] = intent
        final_result['pdf_analysis'] = pdf_analysis
        final_result.setdefault('final_score', final_result.get('score', 0))
        final_result.setdefault('classification', self.scoring_engine.classify_score(final_result.get('score', 0)))
        final_result.setdefault('score_breakdown', {'title': 0.0, 'description': final_result.get('completeness_score', 0.0), 'repository': final_result.get('architecture_score', 0.0)})
        final_result.setdefault('signals', {})
        final_result.setdefault('title_score', 0.0)
        final_result.setdefault('description_score', 0.0)
        final_result.setdefault('repository_score', 0.0)

        logger.info(f"Evaluation Complete - Final Score: {final_result['score']}")
        return final_result