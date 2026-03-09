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

logger = logging.getLogger("evaluation_engine")

class EvaluationEngine:
    def __init__(self):
        self.intent_extractor = IntentExtractor()
        self.repository_analyzer = RepositoryAnalyzer()
        self.feature_matcher = FeatureMatcher()
        self.scoring_engine = ScoringEngine()
        self.pdf_analyzer = PDFAnalyzer() # Reusing analyzer for content structure
    
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
        logger.info(f"Step 2: Repo Analysis Complete - Architecture Layers: {repo_signals.get('architecture', {}).get('layer_count', 0)}")
        
        # Step 3: Requirement Matching
        match_results = self.feature_matcher.compute_match(intent, repo_signals)
        logger.info(f"Step 3: Requirement Match Ratio: {match_results['feature_match_ratio']}")
        
        # Step 4: Scoring Engine (Redesigned v3.0)
        # We also need basic PDF analysis for documentation scoring
        pdf_analysis = self.pdf_analyzer.analyze_content(pdf_text)
        
        final_result = self.scoring_engine.calculate_final_score(
            intent=intent,
            repo_signals=repo_signals,
            match_results=match_results,
            pdf_analysis=pdf_analysis,
            pdf_text=pdf_text
        )
        
        # Package Results
        final_result['intent'] = intent
        final_result['pdf_analysis'] = pdf_analysis
        
        logger.info(f"Evaluation Complete - Final Score: {final_result['score']}")
        return final_result