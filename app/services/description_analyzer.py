"""
Description Analyzer - Dynamic Scoring Module
Analyzes description quality based on measurable features
"""
import re
from typing import Dict, List, Any
import logging

logger = logging.getLogger("description_analyzer")

class DescriptionAnalyzer:
    def __init__(self):
        self.technical_terms = {
            'api', 'rest', 'graphql', 'database', 'sql', 'nosql', 'authentication', 'auth',
            'jwt', 'oauth', 'security', 'encryption', 'hash', 'bcrypt', 'microservice',
            'docker', 'kubernetes', 'ci/cd', 'pipeline', 'deployment', 'testing', 'unit',
            'integration', 'frontend', 'backend', 'fullstack', 'react', 'angular', 'vue',
            'node', 'python', 'java', 'golang', 'rust', 'typescript', 'javascript',
            'framework', 'library', 'sdk', 'cli', 'tool', 'system', 'service', 'server',
            'client', 'web', 'mobile', 'ios', 'android', 'cloud', 'aws', 'azure', 'gcp',
            'algorithm', 'optimization', 'performance', 'scalability', 'architecture',
            'design', 'pattern', 'solid', 'dry', 'kiss', 'mvc', 'mvp', 'mvvm'
        }
        
        self.step_indicators = [
            'step', 'phase', 'stage', 'first', 'second', 'third', 'next', 'then',
            'finally', 'objective', 'requirement', 'constraint', 'goal', 'target'
        ]
    
    def analyze(self, description: str) -> Dict[str, Any]:
        """Analyze description and return dynamic metrics"""
        words = re.findall(r'\b\w+\b', description.lower())
        sentences = re.split(r'[.!?]+', description)
        
        word_count = len(words)
        sentence_count = len([s for s in sentences if s.strip()])
        
        # Calculate metrics
        technical_term_ratio = self._calculate_technical_ratio(words)
        step_indicator_count = self._count_step_indicators(words)
        code_block_count = self._count_code_blocks(description)
        section_headers = self._count_section_headers(description)
        
        # Derived metrics
        depth_score = min(word_count / 300, 1.0)
        structure_score = min((section_headers + step_indicator_count) / 10, 1.0)
        technical_density = technical_term_ratio
        clarity_score = self._calculate_clarity_score(sentence_count, word_count)
        
        # Dynamic description score formula
        description_score = 40 * (
            0.30 * depth_score +
            0.30 * technical_density +
            0.25 * structure_score +
            0.15 * clarity_score
        )
        
        # Clamp between 0 and 40
        description_score = max(0, min(40, description_score))
        
        return {
            'description_score': round(description_score, 1),
            'metrics': {
                'word_count': word_count,
                'sentence_count': sentence_count,
                'technical_term_ratio': round(technical_term_ratio, 3),
                'step_indicator_count': step_indicator_count,
                'code_block_count': code_block_count,
                'section_headers': section_headers,
                'depth_score': round(depth_score, 3),
                'structure_score': round(structure_score, 3),
                'technical_density': round(technical_density, 3),
                'clarity_score': round(clarity_score, 3)
            },
            'signals': {
                'technical_terms_found': self._get_technical_terms(words),
                'step_indicators_found': self._get_step_indicators(words),
                'has_code_blocks': code_block_count > 0,
                'has_structure': section_headers > 0 or step_indicator_count > 0
            }
        }
    
    def _calculate_technical_ratio(self, words: List[str]) -> float:
        """Calculate ratio of technical terms to total words"""
        if not words:
            return 0.0
        technical_count = sum(1 for word in words if word in self.technical_terms)
        return technical_count / len(words)
    
    def _count_step_indicators(self, words: List[str]) -> int:
        """Count step/process indicators in description"""
        return sum(1 for word in words if word in self.step_indicators)
    
    def _count_code_blocks(self, description: str) -> int:
        """Count code blocks (``` or ` patterns)"""
        code_block_pattern = r'```[\s\S]*?```|`[^`]+`'
        return len(re.findall(code_block_pattern, description))
    
    def _count_section_headers(self, description: str) -> int:
        """Count section headers (# patterns or ALL CAPS lines)"""
        lines = description.split('\n')
        header_count = 0
        
        for line in lines:
            line = line.strip()
            # Markdown headers
            if line.startswith('#'):
                header_count += 1
            # ALL CAPS headers (> 5 chars)
            elif line.isupper() and len(line) > 5:
                header_count += 1
        
        return header_count
    
    def _calculate_clarity_score(self, sentence_count: int, word_count: int) -> float:
        """Calculate clarity based on sentence/word ratio"""
        if word_count == 0:
            return 0.0
        
        # Optimal range: 15-25 words per sentence
        avg_words_per_sentence = word_count / max(sentence_count, 1)
        
        if 15 <= avg_words_per_sentence <= 25:
            return 1.0
        elif 10 <= avg_words_per_sentence < 15 or 25 < avg_words_per_sentence <= 35:
            return 0.7
        else:
            return 0.4
    
    def _get_technical_terms(self, words: List[str]) -> List[str]:
        """Get list of technical terms found"""
        return [word for word in words if word in self.technical_terms]
    
    def _get_step_indicators(self, words: List[str]) -> List[str]:
        """Get list of step indicators found"""
        return [word for word in words if word in self.step_indicators]