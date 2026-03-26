"""
Shraddha Validation Layer - FINAL AUTHORITATIVE GATE
FINAL CONVERGENCE: All outputs must pass through this validation layer
"""
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
from pydantic import BaseModel, ValidationError

logger = logging.getLogger("shraddha_validation")

class ValidationGate:
    """
    Shraddha's Final Validation Layer - AUTHORITATIVE OUTPUT GATE
    
    HIERARCHY POSITION: FINAL WRAPPER
    - All evaluation results pass through this layer
    - Ensures strict contract compliance
    - Provides final quality assurance
    - Can reject outputs that don't meet standards
    """
    
    def __init__(self):
        self.gate_level = "FINAL_AUTHORITATIVE"
        self.validation_standards = {
            "required_fields": [
                "submission_id", "score", "status", "readiness_percent",
                "next_task_id", "task_type", "title", "difficulty"
            ],
            "score_bounds": {"min": 0, "max": 100},
            "status_values": ["pass", "borderline", "fail", "readyforadvancement", "needsreinforcement", "requirescorrection"],
            "task_types": ["advancement", "reinforcement", "correction"],
            "difficulties": ["beginner", "intermediate", "advanced", "foundational", "targeted", "progressive"]
        }
    
    def validate_final_output(
        self, 
        evaluation_result: Dict[str, Any],
        source: str = "unknown"
    ) -> Dict[str, Any]:
        """
        FINAL VALIDATION GATE - All outputs must pass through here
        
        Args:
            evaluation_result: Result from evaluation pipeline
            source: Source of the evaluation (assignment_authority, signal_evaluation, etc.)
            
        Returns:
            Validated and potentially corrected output
            
        Raises:
            ValidationError: If output cannot be corrected to meet standards
        """
        logger.info(f"[SHRADDHA VALIDATION] Final gate validation from source: {source}")
        
        # STEP 1: Structure Validation
        structure_result = self._validate_structure(evaluation_result)
        if not structure_result["valid"]:
            logger.error(f"[SHRADDHA VALIDATION] Structure validation failed: {structure_result['errors']}")
            return self._create_emergency_response(evaluation_result, structure_result["errors"])
        
        # STEP 2: Contract Compliance Validation
        contract_result = self._validate_contract_compliance(evaluation_result)
        if not contract_result["valid"]:
            logger.warning(f"[SHRADDHA VALIDATION] Contract compliance issues: {contract_result['warnings']}")
            evaluation_result = self._apply_contract_corrections(evaluation_result, contract_result["corrections"])
        
        # STEP 3: Business Logic Validation
        business_result = self._validate_business_logic(evaluation_result)
        if not business_result["valid"]:
            logger.warning(f"[SHRADDHA VALIDATION] Business logic issues: {business_result['warnings']}")
            evaluation_result = self._apply_business_corrections(evaluation_result, business_result["corrections"])
        
        # STEP 4: Final Quality Assurance
        qa_result = self._final_quality_assurance(evaluation_result)
        
        # STEP 5: Add Validation Metadata
        validated_result = self._add_validation_metadata(qa_result, source)
        
        logger.info(f"[SHRADDHA VALIDATION] Final validation complete - Status: {validated_result.get('status')}")
        return validated_result
    
    def _validate_structure(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate basic structure and required fields
        
        Returns:
            Validation result with errors if any
        """
        errors = []
        
        # Check required top-level fields
        for field in self.validation_standards["required_fields"]:
            if field not in result:
                errors.append(f"Missing required field: {field}")
        
        # Check nested structures
        if "review_summary" in result:
            review_summary = result["review_summary"]
            for field in ["score", "status", "readiness_percent"]:
                if field not in review_summary:
                    errors.append(f"Missing required field in review_summary: {field}")
        
        if "next_task_summary" in result:
            next_task = result["next_task_summary"]
            for field in ["task_id", "task_type", "title", "difficulty"]:
                if field not in next_task:
                    errors.append(f"Missing required field in next_task_summary: {field}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _validate_contract_compliance(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate contract compliance (types, bounds, enums) - RESPECT CANONICAL AUTHORITY
        
        Returns:
            Validation result with corrections needed
        """
        warnings = []
        corrections = {}
        
        # CRITICAL: Check if this is from canonical authority (Sri Satya)
        is_canonical = "canonical_authority" in result or "evaluation_basis" in result
        
        # Validate score bounds - PRESERVE canonical scores
        score = result.get("score") or result.get("review_summary", {}).get("score", 0)
        if not isinstance(score, (int, float)) or score < 0 or score > 100:
            if not is_canonical:
                warnings.append(f"Score {score} out of bounds [0-100]")
                corrections["score"] = max(0, min(100, int(score) if isinstance(score, (int, float)) else 0))
            else:
                logger.info(f"[SHRADDHA VALIDATION] Preserving canonical score {score} despite bounds check")
        
        # Validate status enum - DERIVE from canonical score if available
        status = result.get("status") or result.get("review_summary", {}).get("status", "fail")
        if status.lower().replace('_', '') not in self.validation_standards["status_values"]:
            if is_canonical and isinstance(score, (int, float)):
                # Derive status from canonical score
                derived_status = self._score_to_status(int(score))
                warnings.append(f"Invalid status: {status}, deriving from canonical score: {derived_status}")
                corrections["status"] = derived_status
            else:
                warnings.append(f"Invalid status: {status}")
                corrections["status"] = "fail"  # Default to fail for invalid status
        
        # Validate task_type enum
        task_type = result.get("task_type") or result.get("next_task_summary", {}).get("task_type", "correction")
        if task_type not in self.validation_standards["task_types"]:
            warnings.append(f"Invalid task_type: {task_type}")
            corrections["task_type"] = "correction"  # Default to correction
        
        # Validate difficulty enum
        difficulty = result.get("difficulty") or result.get("next_task_summary", {}).get("difficulty", "beginner")
        if difficulty not in self.validation_standards["difficulties"]:
            warnings.append(f"Invalid difficulty: {difficulty}")
            corrections["difficulty"] = "beginner"  # Default to beginner
        
        return {
            "valid": len(warnings) == 0,
            "warnings": warnings,
            "corrections": corrections
        }
    
    def _validate_business_logic(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate business logic consistency - RESPECT CANONICAL AUTHORITY
        
        Returns:
            Validation result with business corrections
        """
        warnings = []
        corrections = {}
        
        # CRITICAL: Check if this is from canonical authority
        is_canonical = "canonical_authority" in result or "evaluation_basis" in result
        
        score = result.get("score") or result.get("review_summary", {}).get("score", 0)
        status = result.get("status") or result.get("review_summary", {}).get("status", "fail")
        task_type = result.get("task_type") or result.get("next_task_summary", {}).get("task_type", "correction")
        
        # Business Rule 1: Score-Status Alignment - DERIVE from canonical score
        if is_canonical and isinstance(score, (int, float)):
            expected_status = self._score_to_status(int(score))
            if status.lower().replace('_', '') != expected_status:
                warnings.append(f"Deriving status from canonical score {score}: {expected_status}")
                corrections["status"] = expected_status
        else:
            expected_status = self._score_to_status(score)
            if status.lower().replace('_', '') != expected_status:
                warnings.append(f"Score {score} inconsistent with status {status}, expected {expected_status}")
                corrections["status"] = expected_status
        
        # Business Rule 2: Status-TaskType Alignment
        final_status = corrections.get("status", status)
        expected_task_type = self._status_to_task_type(final_status)
        if task_type != expected_task_type:
            warnings.append(f"Status {final_status} inconsistent with task_type {task_type}, expected {expected_task_type}")
            corrections["task_type"] = expected_task_type
        
        # Business Rule 3: Readiness Percent Alignment - PRESERVE canonical score
        readiness = result.get("readiness_percent") or result.get("review_summary", {}).get("readiness_percent", score)
        if is_canonical:
            # For canonical results, readiness should match score exactly
            if readiness != score:
                warnings.append(f"Aligning readiness percent with canonical score: {score}")
                corrections["readiness_percent"] = score
        else:
            if abs(readiness - score) > 5:  # Allow 5 point variance for non-canonical
                warnings.append(f"Readiness percent {readiness} should align with score {score}")
                corrections["readiness_percent"] = score
        
        return {
            "valid": len(warnings) == 0,
            "warnings": warnings,
            "corrections": corrections
        }
    
    def _apply_contract_corrections(self, result: Dict[str, Any], corrections: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply contract compliance corrections - PRESERVE CANONICAL SCORES
        """
        corrected_result = result.copy()
        
        for field, value in corrections.items():
            # CRITICAL: Do NOT override canonical scores from Sri Satya
            if field == "score" and "canonical_authority" in result:
                logger.warning(f"[SHRADDHA VALIDATION] Preserving canonical score {result.get('score')} over correction {value}")
                continue
                
            # Apply to top level
            if field in corrected_result:
                corrected_result[field] = value
            
            # Apply to review_summary - PRESERVE canonical scores
            if "review_summary" in corrected_result and field in ["score", "status", "readiness_percent"]:
                if field == "score" and "canonical_authority" in result:
                    continue  # Preserve canonical score
                corrected_result["review_summary"][field] = value
            
            # Apply to next_task_summary
            if "next_task_summary" in corrected_result and field in ["task_type", "difficulty"]:
                corrected_result["next_task_summary"][field] = value
        
        return corrected_result
    
    def _apply_business_corrections(self, result: Dict[str, Any], corrections: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply business logic corrections
        """
        return self._apply_contract_corrections(result, corrections)  # Same logic
    
    def _final_quality_assurance(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Final quality assurance pass
        """
        qa_result = result.copy()
        
        # Ensure all numeric values are properly typed
        if "score" in qa_result:
            qa_result["score"] = int(qa_result["score"])
        if "readiness_percent" in qa_result:
            qa_result["readiness_percent"] = int(qa_result["readiness_percent"])
        
        # Ensure review_summary structure
        if "review_summary" not in qa_result:
            qa_result["review_summary"] = {
                "score": qa_result.get("score", 0),
                "status": qa_result.get("status", "fail"),
                "readiness_percent": qa_result.get("readiness_percent", qa_result.get("score", 0))
            }
        
        # Ensure next_task_summary structure
        if "next_task_summary" not in qa_result:
            qa_result["next_task_summary"] = {
                "task_id": qa_result.get("next_task_id", "next-unknown"),
                "task_type": qa_result.get("task_type", "correction"),
                "title": qa_result.get("title", "Correction Task"),
                "difficulty": qa_result.get("difficulty", "beginner")
            }
        
        return qa_result
    
    def _add_validation_metadata(self, result: Dict[str, Any], source: str) -> Dict[str, Any]:
        """
        Add validation metadata to final result
        """
        validated_result = result.copy()
        
        validated_result["validation_metadata"] = {
            "validated_by": "shraddha_validation_layer",
            "validation_level": "FINAL_AUTHORITATIVE",
            "validated_at": datetime.now().isoformat(),
            "source_system": source,
            "contract_compliance": "ENFORCED",
            "business_logic_validation": "APPLIED",
            "quality_assurance": "COMPLETE"
        }
        
        return validated_result
    
    def _create_emergency_response(self, original_result: Dict[str, Any], errors: List[str]) -> Dict[str, Any]:
        """
        Create emergency response when validation fails completely
        """
        logger.error(f"[SHRADDHA VALIDATION] Creating emergency response due to: {errors}")
        
        return {
            "submission_id": original_result.get("submission_id", "emergency-response"),
            "review_summary": {
                "score": 0,
                "status": "fail",
                "readiness_percent": 0
            },
            "next_task_summary": {
                "task_id": "emergency-correction",
                "task_type": "correction",
                "title": "System Validation Recovery",
                "difficulty": "foundational"
            },
            "validation_metadata": {
                "emergency_response": True,
                "validation_errors": errors,
                "created_at": datetime.now().isoformat()
            }
        }
    
    def _score_to_status(self, score: int) -> str:
        """Convert score to expected status"""
        if score >= 80:
            return "pass"
        elif score >= 50:
            return "borderline"
        else:
            return "fail"
    
    def _status_to_task_type(self, status: str) -> str:
        """Convert status to expected task type"""
        if status == "pass":
            return "advancement"
        elif status == "borderline":
            return "reinforcement"
        else:
            return "correction"

# Global validation gate instance
validation_gate = ValidationGate()