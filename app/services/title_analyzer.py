"""
Title Analyzer - Dynamic Scoring Module
Analyzes title quality based on measurable signals
"""
import re
from typing import Dict, List, Any
import logging

logger = logging.getLogger("title_analyzer")

class TitleAnalyzer:
    def __init__(self):
        self.technical_keywords = {
            'api', 'rest', 'graphql', 'database', 'sql', 'nosql', 'authentication', 'auth',
            'jwt', 'oauth', 'security', 'encryption', 'hash', 'bcrypt', 'microservice',
            'docker', 'kubernetes', 'ci/cd', 'pipeline', 'deployment', 'testing', 'unit',
            'integration', 'frontend', 'backend', 'fullstack', 'react', 'angular', 'vue',
            'node', 'python', 'java', 'golang', 'rust', 'typescript', 'javascript',
            'framework', 'library', 'sdk', 'cli', 'tool', 'system', 'service', 'server',
            'client', 'web', 'mobile', 'ios', 'android', 'cloud', 'aws', 'azure', 'gcp'
        }
    
    def analyze(self, title: str, description: str) -> Dict[str, Any]:
        """Analyze title and return dynamic metrics"""
        words = title.lower().split()
        word_count = len(words)
        
        # Calculate metrics
        title_word_count_score = min(word_count / 12, 1.0)
        technical_keyword_ratio = self._calculate_technical_ratio(words)
        duplicate_penalty = self._calculate_duplicate_penalty(words)
        alignment_score = self._calculate_alignment_score(title, description)
        
        # Dynamic title score formula
        title_score = 20 * (
            0.35 * title_word_count_score +
            0.35 * technical_keyword_ratio +
            0.20 * alignment_score -
            0.10 * duplicate_penalty
        )
        
        # Clamp between 0 and 20
        title_score = max(0, min(20, title_score))
        
        return {
            'title_score': round(title_score, 1),
            'metrics': {
                'title_word_count': word_count,
                'technical_keyword_ratio': round(technical_keyword_ratio, 3),
                'duplicate_word_ratio': round(duplicate_penalty, 3),
                'alignment_score': round(alignment_score, 3),
                'title_word_count_score': round(title_word_count_score, 3)
            },
            'signals': {
                'technical_terms_found': self._get_technical_terms(words),
                'duplicate_words': self._get_duplicate_words(words),
                'shared_keywords': self._get_shared_keywords(title, description)
            }
        }
    
    def _calculate_technical_ratio(self, words: List[str]) -> float:
        """Calculate ratio of technical terms to total words"""
        if not words:
            return 0.0
        technical_count = sum(1 for word in words if word in self.technical_keywords)
        return technical_count / len(words)
    
    def _calculate_duplicate_penalty(self, words: List[str]) -> float:
        """Calculate penalty for repeated words"""
        if not words:
            return 0.0
        unique_words = set(words)
        repeated_count = len(words) - len(unique_words)
        return repeated_count / len(words)
    
    def _calculate_alignment_score(self, title: str, description: str) -> float:
        """Calculate alignment between title and description keywords"""
        title_words = set(re.findall(r'\b\w+\b', title.lower()))
        desc_words = set(re.findall(r'\b\w+\b', description.lower()))
        
        if not title_words:
            return 0.0
        
        shared_count = len(title_words.intersection(desc_words))
        return min(shared_count / len(title_words), 1.0)
    
    def _get_technical_terms(self, words: List[str]) -> List[str]:
        """Get list of technical terms found in title"""
        return [word for word in words if word in self.technical_keywords]
    
    def _get_duplicate_words(self, words: List[str]) -> List[str]:
        """Get list of duplicate words"""
        seen = set()
        duplicates = []
        for word in words:
            if word in seen and word not in duplicates:
                duplicates.append(word)
            seen.add(word)
        return duplicates
    
    def _get_shared_keywords(self, title: str, description: str) -> List[str]:
        """Get keywords shared between title and description"""
        title_words = set(re.findall(r'\b\w+\b', title.lower()))
        desc_words = set(re.findall(r'\b\w+\b', description.lower()))
        return list(title_words.intersection(desc_words))