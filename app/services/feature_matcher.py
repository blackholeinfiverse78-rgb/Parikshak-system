"""
Feature Matcher - Step 3 of Deterministic Evaluation
Compares task intent with repository implementation to calculate coverage.
"""
from typing import Dict, List, Any

class FeatureMatcher:
    def __init__(self):
        # Mapping intent keywords to file system patterns
        self.feature_file_patterns = {
            'api': ['api', 'route', 'controller', 'endpoint', 'fastapi', 'flask'],
            'database': ['db', 'model', 'schema', 'entity', 'postgres', 'sql', 'mongo'],
            'auth': ['auth', 'login', 'security', 'jwt', 'session', 'token'],
            'review': ['review', 'evaluate', 'score', 'audit'],
            'frontend': ['ui', 'component', 'view', 'react', 'vue', 'style'],
            'docker': ['dockerfile', 'docker-compose', 'container'],
            'test': ['test', 'spec', 'jest', 'pytest', 'unittest'],
            'dashboard': ['dashboard', 'panel', 'home', 'main_view']
        }

    def compute_match(self, intent: Dict[str, Any], signals: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive requirement matching between intent and implementation.
        """
        # 1. Feature Matching (Weight 0.5 of total match score if we were calculating one here)
        expected_features = intent.get('expected_features', [])
        repo_components = signals.get('components', {})
        repo_paths = []
        for k in repo_components:
            if isinstance(repo_components[k], list):
                repo_paths.extend(repo_components[k])
                
        implemented_features = []
        missing_features = []
        
        for feature in expected_features:
            is_found = False
            if any(feature.lower() in p.lower() for p in repo_paths):
                is_found = True
            else:
                synonyms = self.feature_file_patterns.get(feature.lower(), [])
                if any(syn in p.lower() for p in repo_paths for syn in synonyms):
                    is_found = True
            
            if is_found:
                implemented_features.append(feature)
            else:
                missing_features.append(feature)
        
        feature_ratio = len(implemented_features) / len(expected_features) if expected_features else 1.0

        # 2. Tech Stack Matching
        expected_stack = set(intent.get('expected_tech_stack', []))
        detected_langs = set(signals.get('structure', {}).get('languages', {}).keys())
        # Map extensions to names
        ext_map = {'py': 'python', 'js': 'javascript', 'ts': 'typescript', 'go': 'go', 'java': 'java', 'rb': 'ruby'}
        detected_stack = {ext_map.get(ext, ext) for ext in detected_langs}
        
        matched_stack = expected_stack.intersection(detected_stack)
        stack_match_ratio = len(matched_stack) / len(expected_stack) if expected_stack else 1.0

        # 3. Architecture Match
        expected_arch = intent.get('expected_architecture', 'Standard').lower()
        arch_signals = signals.get('architecture', {})
        arch_match_score = 1.0
        
        if expected_arch != 'standard':
            # Basic validation: if they expect layers, do we have them?
            if expected_arch in ['layered', 'mvc', 'clean'] and not arch_signals.get('has_layers'):
                arch_match_score = 0.5
            if expected_arch == 'microservices' and arch_signals.get('layer_count', 0) < 5:
                arch_match_score = 0.6

        return {
            "feature_match_ratio": round(feature_ratio, 2),
            "tech_stack_match": round(stack_match_ratio, 2),
            "architecture_match": round(arch_match_score, 2),
            "implemented_features": implemented_features,
            "missing_features": missing_features,
            "expected_count": len(expected_features),
            "implemented_count": len(implemented_features),
            "matched_stack": list(matched_stack)
        }
