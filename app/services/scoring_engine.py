"""
Scoring Engine - Deterministic Multi-Factor Evaluator v3.0
Redesigned for Requirement-Implementation Matching.
"""
from typing import Dict, Any, List, Optional

class ScoringEngine:
    def __init__(self):
        # Weight Distribution (Step 4)
        self.weights = {
            "requirement_match": 40,
            "completeness": 20,
            "architecture": 20,
            "code_quality": 10,
            "documentation": 10
        }

    def calculate_final_score(
        self,
        intent: Dict[str, Any],
        repo_signals: Dict[str, Any],
        match_results: Dict[str, Any],
        pdf_analysis: Optional[Dict[str, Any]] = None,
        pdf_text: str = ""
    ) -> Dict[str, Any]:
        """
        Deterministic final score calculation based on Requirement Matching (v3.0).
        """
        # 1. Requirement Match (40 pts)
        feature_match = match_results.get('feature_match_ratio', 0)
        stack_match = match_results.get('tech_stack_match', 0)
        arch_match = match_results.get('architecture_match', 0)
        
        req_match_ratio = (feature_match * 0.6) + (stack_match * 0.2) + (arch_match * 0.2)
        req_match_score = req_match_ratio * self.weights["requirement_match"]
        
        # 2. Repository Completeness (20 pts)
        completeness_ratio = self._calculate_completeness(intent, repo_signals)
        completeness_score = completeness_ratio * self.weights["completeness"]
        
        # 3. Architecture Quality (20 pts)
        architecture_ratio = self._calculate_architecture_score(repo_signals)
        architecture_score = architecture_ratio * self.weights["architecture"]
        
        # 4. Code Quality (10 pts)
        quality_ratio = self._calculate_quality_score(repo_signals)
        quality_score = quality_ratio * self.weights["code_quality"]
        
        # 5. PDF Documentation Alignment (10 pts)
        doc_align_ratio = self._calculate_documentation_score(pdf_analysis, pdf_text, repo_signals)
        doc_align_score = doc_align_ratio * self.weights["documentation"]
        
        # Final Total
        total_score = round(req_match_score + completeness_score + architecture_score + quality_score + doc_align_score, 1)
        
        # Alignment Label
        alignment_status = "low"
        if req_match_ratio > 0.8: alignment_status = "high"
        elif req_match_ratio > 0.5: alignment_status = "moderate"

        return {
            "score": total_score,
            "requirement_match": round(req_match_ratio, 2),
            "architecture_score": round(architecture_score, 1),
            "code_quality_score": round(quality_score, 1),
            "completeness_score": round(completeness_score, 1),
            "documentation_score": round(doc_align_score, 1),
            "documentation_alignment": alignment_status,
            "missing_features": match_results.get('missing_features', []),
            "summary": self._generate_summary(total_score, match_results, alignment_status)
        }

    def _calculate_completeness(self, intent: Dict[str, Any], signals: Optional[Dict[str, Any]]) -> float:
        if not signals: return 0.0
        complexity = intent.get('expected_complexity', 'medium')
        file_count = signals.get('structure', {}).get('total_files', 0)
        thresholds = {"low": 3, "medium": 8, "high": 20}
        target = thresholds.get(complexity, 8)
        return min(file_count / target, 1.0)

    def _calculate_architecture_score(self, signals: Optional[Dict[str, Any]]) -> float:
        if not signals: return 0.0
        arch = signals.get('architecture', {})
        score = 0.0
        if arch.get('has_layers'): score += 0.4
        if arch.get('modular'): score += 0.3
        if arch.get('interface_usage'): score += 0.3
        return min(score, 1.0)

    def _calculate_quality_score(self, signals: Optional[Dict[str, Any]]) -> float:
        if not signals: return 0.0
        quality = signals.get('quality', {})
        score = 0.0
        # README quality
        readme_score = quality.get('readme_score', 0)
        score += (readme_score / 3.0) * 0.6
        # Doc density
        density = quality.get('documentation_density', 0)
        if density > 0.1: score += 0.4
        return min(score, 1.0)

    def _calculate_documentation_score(self, pdf_analysis: Optional[Dict], pdf_text: str, signals: Dict) -> float:
        """
        Evaluate PDF documentation depth and clarity.
        """
        if not pdf_text or not pdf_analysis:
            return 0.0
            
        score = 0.0
        # 1. Depth of explanation
        if len(pdf_text) > 2000: score += 0.4
        elif len(pdf_text) > 500: score += 0.2
        # 2. Architecture description presence
        if len(pdf_analysis.get('architecture_description', '')) > 50:
            score += 0.3
        # 3. Feature listing
        if len(pdf_analysis.get('documented_features', [])) >= 3:
            score += 0.3
        return min(score, 1.0)

    def _generate_summary(self, score: float, match_results: Dict[str, Any], alignment: str) -> str:
        implemented = match_results.get('implemented_count', 0)
        expected = match_results.get('expected_count', 0)
        
        summary = f"Evaluation complete. Score: {score}. "
        summary += f"Implemented {implemented}/{expected} expected features. "
        summary += f"Requirement alignment is {alignment.upper()}. "
        
        if alignment == "high":
            summary += "Repository implementation strongly matches the requirements extracted from the title, description, and PDF."
        elif alignment == "moderate":
            summary += "Implementation follows requirements but has some missing features or architectural gaps."
        else:
            summary += "Significant mismatch between specified requirements and repository implementation."
            
        return summary