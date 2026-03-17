"""
Sri Satya's Assignment Engine - AUTHORITATIVE Base Evaluation
Provides accuracy, completeness, missing requirements, and base status
"""
from typing import Dict, Any, List
from enum import Enum
import logging
import re

logger = logging.getLogger("assignment_engine")

class AssignmentStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    BORDERLINE = "BORDERLINE"

class AssignmentEngine:
    """
    Assignment-based evaluation engine that provides authoritative base evaluation.
    This engine focuses on task structure, requirements clarity, and assignment completeness.
    """
    
    def __init__(self):
        # Core requirements for any valid task assignment
        self.required_elements = [
            "objective",
            "deliverables", 
            "timeline",
            "scope"
        ]
        
        # Technical indicators for quality assessment
        self.technical_keywords = [
            "api", "database", "authentication", "architecture", "framework",
            "implementation", "testing", "deployment", "security", "performance",
            "integration", "system", "module", "component", "service", "endpoint",
            "algorithm", "data structure", "design pattern", "scalability"
        ]
    
    def evaluate(self, task_title: str, task_description: str) -> Dict[str, Any]:
        """
        Perform assignment-based evaluation focusing on task structure and completeness.
        
        Args:
            task_title: Task title to evaluate
            task_description: Task description to evaluate
            
        Returns:
            Dict containing accuracy, completeness, missing_requirements, and base_status
        """
        logger.info(f"Starting assignment evaluation for: {task_title}")
        
        # Step 1: Analyze task structure
        structure_analysis = self._analyze_structure(task_title, task_description)
        
        # Step 2: Check requirement completeness
        completeness_analysis = self._analyze_completeness(task_description)
        
        # Step 3: Assess technical accuracy
        accuracy_analysis = self._analyze_accuracy(task_title, task_description)
        
        # Step 4: Determine base status
        base_status = self._determine_base_status(
            structure_analysis, completeness_analysis, accuracy_analysis
        )
        
        result = {
            "accuracy": accuracy_analysis["score"],
            "completeness": completeness_analysis["score"], 
            "missing_requirements": completeness_analysis["missing_elements"],
            "base_status": base_status.value,
            "structure_quality": structure_analysis["score"],
            "technical_depth": accuracy_analysis["technical_depth"],
            "clarity_score": structure_analysis["clarity"],
            "assignment_details": {
                "structure": structure_analysis,
                "completeness": completeness_analysis,
                "accuracy": accuracy_analysis
            }
        }
        
        logger.info(f"Assignment evaluation complete - Status: {base_status.value}, Accuracy: {result['accuracy']}, Completeness: {result['completeness']}")
        return result
    
    def _analyze_structure(self, title: str, description: str) -> Dict[str, Any]:
        """Analyze task structure and clarity"""
        score = 0
        clarity = 0
        issues = []
        
        # Title analysis (0-25 points)
        if len(title.strip()) >= 10:
            score += 5
        if any(keyword in title.lower() for keyword in self.technical_keywords):
            score += 10
        if "," in title or ":" in title:  # Structured title
            score += 5
        if len(title.split()) >= 4:  # Descriptive title
            score += 5
            
        # Description structure (0-25 points)
        lines = [line.strip() for line in description.split('\n') if line.strip()]
        if len(lines) >= 3:
            score += 10
        if any(line.startswith(('-', '*', '1.', '2.')) for line in lines):
            score += 10  # Has bullet points or numbering
        if len(description.split()) >= 50:
            score += 5  # Sufficient detail
            
        # Clarity assessment
        if "objective" in description.lower() or "goal" in description.lower():
            clarity += 25
        if "requirement" in description.lower() or "deliverable" in description.lower():
            clarity += 25
        if "timeline" in description.lower() or "deadline" in description.lower():
            clarity += 25
        if "scope" in description.lower() or "boundary" in description.lower():
            clarity += 25
            
        return {
            "score": min(50, score),
            "clarity": clarity,
            "issues": issues
        }
    
    def _analyze_completeness(self, description: str) -> Dict[str, Any]:
        """Analyze requirement completeness"""
        score = 0
        missing_elements = []
        found_elements = []
        
        desc_lower = description.lower()
        
        # Check for required elements
        element_checks = {
            "objective": ["objective", "goal", "purpose", "aim"],
            "deliverables": ["deliverable", "output", "result", "produce", "create"],
            "timeline": ["timeline", "deadline", "schedule", "duration", "time"],
            "scope": ["scope", "boundary", "limit", "include", "exclude"]
        }
        
        for element, keywords in element_checks.items():
            if any(keyword in desc_lower for keyword in keywords):
                found_elements.append(element)
                score += 25
            else:
                missing_elements.append(element)
        
        return {
            "score": score,
            "missing_elements": missing_elements,
            "found_elements": found_elements
        }
    
    def _analyze_accuracy(self, title: str, description: str) -> Dict[str, Any]:
        """Analyze technical accuracy and depth"""
        combined_text = f"{title} {description}".lower()
        
        # Technical keyword density
        technical_matches = sum(1 for keyword in self.technical_keywords if keyword in combined_text)
        total_words = len(combined_text.split())
        technical_density = technical_matches / max(total_words, 1) * 100
        
        # Technical depth assessment
        depth_indicators = [
            "architecture", "design pattern", "algorithm", "data structure",
            "scalability", "performance", "security", "integration", "testing"
        ]
        depth_score = sum(10 for indicator in depth_indicators if indicator in combined_text)
        
        # Accuracy score (0-100)
        accuracy_score = min(100, int(technical_density * 10 + depth_score))
        
        return {
            "score": accuracy_score,
            "technical_depth": min(100, depth_score),
            "technical_density": technical_density,
            "technical_matches": technical_matches
        }
    
    def _determine_base_status(self, structure: Dict, completeness: Dict, accuracy: Dict) -> AssignmentStatus:
        """Determine base assignment status - AUTHORITATIVE decision"""
        
        # Critical failure conditions (FAIL)
        if completeness["score"] < 50:  # Missing too many requirements
            return AssignmentStatus.FAIL
            
        if structure["score"] < 25:  # Poor structure
            return AssignmentStatus.FAIL
            
        if accuracy["score"] < 30:  # Insufficient technical content
            return AssignmentStatus.FAIL
        
        # High quality conditions (PASS)
        if (completeness["score"] >= 75 and 
            structure["score"] >= 40 and 
            accuracy["score"] >= 60):
            return AssignmentStatus.PASS
        
        # Everything else is BORDERLINE
        return AssignmentStatus.BORDERLINE