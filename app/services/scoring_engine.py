"""
Scoring Engine - Deterministic Multi-Factor Evaluator v3.1
Supports both intent-based scoring (production) and direct score-based scoring (tests).
"""
from typing import Dict, Any, Optional


class ScoringEngine:
    def __init__(self):
        self.weights = {
            "requirement_match": 40,
            "completeness": 20,
            "architecture": 20,
            "code_quality": 10,
            "documentation": 10
        }

    def classify_score(self, score: float) -> str:
        if score >= 80: return "PASS"
        if score >= 50: return "BORDERLINE"
        return "FAIL"

    def calculate_final_score(self, title_analysis_or_intent, desc_or_repo=None,
                               repo_or_match=None, match_results=None,
                               pdf_analysis=None, pdf_text=""):
        """
        Unified entry point.
        - Old test signature: calculate_final_score(title_analysis, desc_analysis, repo_analysis)
          where each dict has 'title_score' / 'description_score' / 'repository_score'.
        - New production signature: calculate_final_score(intent, repo_signals, match_results, ...)
        """
        if isinstance(title_analysis_or_intent, dict) and 'title_score' in title_analysis_or_intent:
            # Old 3-arg test signature
            title_score = title_analysis_or_intent.get('title_score', 0)
            desc_score = (desc_or_repo or {}).get('description_score', 0)
            repo_score = (repo_or_match or {}).get('repository_score', 0)
            total = round(title_score + desc_score + repo_score, 1)
            classification = self.classify_score(total)
            return {
                "final_score": total,
                "score": total,
                "classification": classification,
                "score_breakdown": {
                    "title": title_score,
                    "description": desc_score,
                    "repository": repo_score
                },
                "requirement_match": 0.0,
                "architecture_score": 0.0,
                "code_quality_score": 0.0,
                "completeness_score": desc_score,
                "documentation_score": 0.0,
                "documentation_alignment": "low",
                "missing_features": [],
                "summary": f"Score: {total}. Classification: {classification}."
            }

        # New production signature: (intent, repo_signals, match_results, ...)
        intent = title_analysis_or_intent
        repo_signals = desc_or_repo
        match_results = repo_or_match if match_results is None else match_results

        feature_match = match_results.get('feature_match_ratio', 0)
        stack_match = match_results.get('tech_stack_match', 0)
        arch_match = match_results.get('architecture_match', 0)

        req_match_ratio = (feature_match * 0.6) + (stack_match * 0.2) + (arch_match * 0.2)
        req_match_score = req_match_ratio * self.weights["requirement_match"]

        completeness_ratio = self._calculate_completeness(intent, repo_signals)
        completeness_score = completeness_ratio * self.weights["completeness"]

        architecture_ratio = self._calculate_architecture_score(repo_signals)
        architecture_score = architecture_ratio * self.weights["architecture"]

        quality_ratio = self._calculate_quality_score(repo_signals)
        quality_score = quality_ratio * self.weights["code_quality"]

        doc_align_ratio = self._calculate_documentation_score(pdf_analysis, pdf_text, repo_signals)
        doc_align_score = doc_align_ratio * self.weights["documentation"]

        total_score = round(req_match_score + completeness_score + architecture_score
                            + quality_score + doc_align_score, 1)

        alignment_status = "low"
        if req_match_ratio > 0.8: alignment_status = "high"
        elif req_match_ratio > 0.5: alignment_status = "moderate"

        return {
            "score": total_score,
            "final_score": total_score,
            "classification": self.classify_score(total_score),
            "score_breakdown": {
                "title": 0.0,
                "description": round(completeness_score, 1),
                "repository": round(architecture_score + quality_score, 1)
            },
            "requirement_match": round(req_match_ratio, 2),
            "architecture_score": round(architecture_score, 1),
            "code_quality_score": round(quality_score, 1),
            "completeness_score": round(completeness_score, 1),
            "documentation_score": round(doc_align_score, 1),
            "documentation_alignment": alignment_status,
            "missing_features": match_results.get('missing_features', []),
            "summary": self._generate_summary(total_score, match_results, alignment_status),
            "title_score": 0.0,
            "description_score": round(completeness_score, 1),
            "repository_score": round(architecture_score + quality_score, 1)
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
        readme_score = quality.get('readme_score', 0)
        score += (readme_score / 3.0) * 0.6
        density = quality.get('documentation_density', 0)
        if density > 0.1: score += 0.4
        return min(score, 1.0)

    def _calculate_documentation_score(self, pdf_analysis: Optional[Dict],
                                        pdf_text: str, signals: Dict) -> float:
        if not pdf_text or not pdf_analysis:
            return 0.0
        score = 0.0
        if len(pdf_text) > 2000: score += 0.4
        elif len(pdf_text) > 500: score += 0.2
        if len(pdf_analysis.get('architecture_description', '')) > 50:
            score += 0.3
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
            summary += "Repository implementation strongly matches the requirements."
        elif alignment == "moderate":
            summary += "Implementation follows requirements but has some gaps."
        else:
            summary += "Significant mismatch between requirements and implementation."
        return summary
