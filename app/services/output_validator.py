"""
Shraddha's Validator - FINAL WRAPPER for Output Validation
Enforces strict output contract and ensures no missing keys or extra fields
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, ValidationError
import logging

logger = logging.getLogger("output_validator")

class ValidationResult(BaseModel):
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    sanitized_output: Optional[Dict[str, Any]] = None

class OutputValidator:
    """
    Shraddha's output validation service that enforces strict contract compliance.
    Ensures deterministic output format with no missing keys or extra fields.
    """
    
    def __init__(self):
        # Expected output schema - STRICT CONTRACT
        self.required_fields = {
            "score": int,
            "readiness_percent": int, 
            "status": str,
            "failure_reasons": list,
            "improvement_hints": list,
            "analysis": dict,
            "meta": dict,
            "feature_coverage": float,
            "architecture_score": float,
            "code_quality_score": float,
            "completeness_score": float,
            "missing_features": list,
            "requirement_match": float,
            "evaluation_summary": str,
            "documentation_score": float,
            "documentation_alignment": str,
            "title_score": float,
            "description_score": float,
            "repository_score": float
        }
        
        self.analysis_required_fields = {
            "technical_quality": int,
            "clarity": int,
            "discipline_signals": int
        }
        
        self.meta_required_fields = {
            "evaluation_time_ms": int,
            "mode": str
        }
        
        self.valid_status_values = ["pass", "borderline", "fail"]
        self.valid_mode_values = ["rule", "ml", "hybrid"]
        self.valid_alignment_values = ["high", "moderate", "low", "unknown"]
    
    def validate_output(self, output: Dict[str, Any]) -> ValidationResult:
        """
        Validate output against strict contract requirements.
        
        Args:
            output: Raw output dictionary to validate
            
        Returns:
            ValidationResult with validation status and sanitized output
        """
        logger.info("Starting output validation")
        
        errors = []
        warnings = []
        sanitized = {}
        
        # Step 1: Check required fields
        missing_fields = []
        for field, expected_type in self.required_fields.items():
            if field not in output:
                missing_fields.append(field)
            else:
                # Type validation and sanitization
                try:
                    sanitized[field] = self._sanitize_field(field, output[field], expected_type)
                except Exception as e:
                    errors.append(f"Field '{field}' validation failed: {str(e)}")
        
        if missing_fields:
            errors.extend([f"Missing required field: {field}" for field in missing_fields])
        
        # Step 2: Validate nested objects
        if "analysis" in output:
            analysis_validation = self._validate_analysis(output["analysis"])
            if analysis_validation["errors"]:
                errors.extend(analysis_validation["errors"])
            else:
                sanitized["analysis"] = analysis_validation["sanitized"]
        
        if "meta" in output:
            meta_validation = self._validate_meta(output["meta"])
            if meta_validation["errors"]:
                errors.extend(meta_validation["errors"])
            else:
                sanitized["meta"] = meta_validation["sanitized"]
        
        # Step 3: Value range validation
        range_validation = self._validate_ranges(sanitized)
        errors.extend(range_validation["errors"])
        warnings.extend(range_validation["warnings"])
        
        # Step 4: Business logic validation
        logic_validation = self._validate_business_logic(sanitized)
        errors.extend(logic_validation["errors"])
        warnings.extend(logic_validation["warnings"])
        
        is_valid = len(errors) == 0
        
        logger.info(f"Validation complete - Valid: {is_valid}, Errors: {len(errors)}, Warnings: {len(warnings)}")
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            sanitized_output=sanitized if is_valid else None
        )
    
    def _sanitize_field(self, field_name: str, value: Any, expected_type: type) -> Any:
        """Sanitize and convert field to expected type"""
        if expected_type == int:
            if isinstance(value, (int, float)):
                return int(value)
            elif isinstance(value, str) and value.isdigit():
                return int(value)
            else:
                raise ValueError(f"Cannot convert {type(value)} to int")
        
        elif expected_type == float:
            if isinstance(value, (int, float)):
                return float(value)
            elif isinstance(value, str):
                try:
                    return float(value)
                except ValueError:
                    raise ValueError(f"Cannot convert string to float")
            else:
                raise ValueError(f"Cannot convert {type(value)} to float")
        
        elif expected_type == str:
            return str(value) if value is not None else ""
        
        elif expected_type == list:
            if isinstance(value, list):
                return value
            elif value is None:
                return []
            else:
                raise ValueError(f"Expected list, got {type(value)}")
        
        elif expected_type == dict:
            if isinstance(value, dict):
                return value
            elif value is None:
                return {}
            else:
                raise ValueError(f"Expected dict, got {type(value)}")
        
        return value
    
    def _validate_analysis(self, analysis: Any) -> Dict[str, Any]:
        """Validate analysis nested object"""
        errors = []
        sanitized = {}
        
        if not isinstance(analysis, dict):
            return {"errors": ["Analysis must be a dictionary"], "sanitized": {}}
        
        for field, expected_type in self.analysis_required_fields.items():
            if field not in analysis:
                errors.append(f"Missing analysis field: {field}")
            else:
                try:
                    sanitized[field] = self._sanitize_field(field, analysis[field], expected_type)
                except Exception as e:
                    errors.append(f"Analysis field '{field}' validation failed: {str(e)}")
        
        return {"errors": errors, "sanitized": sanitized}
    
    def _validate_meta(self, meta: Any) -> Dict[str, Any]:
        """Validate meta nested object"""
        errors = []
        sanitized = {}
        
        if not isinstance(meta, dict):
            return {"errors": ["Meta must be a dictionary"], "sanitized": {}}
        
        for field, expected_type in self.meta_required_fields.items():
            if field not in meta:
                errors.append(f"Missing meta field: {field}")
            else:
                try:
                    sanitized[field] = self._sanitize_field(field, meta[field], expected_type)
                except Exception as e:
                    errors.append(f"Meta field '{field}' validation failed: {str(e)}")
        
        return {"errors": errors, "sanitized": sanitized}
    
    def _validate_ranges(self, output: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate value ranges and constraints"""
        errors = []
        warnings = []
        
        # Score ranges (0-100)
        score_fields = ["score", "readiness_percent"]
        for field in score_fields:
            if field in output:
                value = output[field]
                if not (0 <= value <= 100):
                    errors.append(f"{field} must be between 0-100, got {value}")
        
        # Analysis ranges (0-100)
        if "analysis" in output:
            for field in ["technical_quality", "clarity", "discipline_signals"]:
                if field in output["analysis"]:
                    value = output["analysis"][field]
                    if not (0 <= value <= 100):
                        errors.append(f"analysis.{field} must be between 0-100, got {value}")
        
        # Status validation
        if "status" in output:
            if output["status"] not in self.valid_status_values:
                errors.append(f"Invalid status: {output['status']}, must be one of {self.valid_status_values}")
        
        # Mode validation
        if "meta" in output and "mode" in output["meta"]:
            if output["meta"]["mode"] not in self.valid_mode_values:
                errors.append(f"Invalid mode: {output['meta']['mode']}, must be one of {self.valid_mode_values}")
        
        # Documentation alignment validation
        if "documentation_alignment" in output:
            if output["documentation_alignment"] not in self.valid_alignment_values:
                warnings.append(f"Unusual documentation_alignment: {output['documentation_alignment']}")
        
        return {"errors": errors, "warnings": warnings}
    
    def _validate_business_logic(self, output: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate business logic consistency"""
        errors = []
        warnings = []
        
        # Score consistency
        if "score" in output and "readiness_percent" in output:
            if output["score"] != output["readiness_percent"]:
                warnings.append("Score and readiness_percent should typically be equal")
        
        # Status-score alignment
        if "score" in output and "status" in output:
            score = output["score"]
            status = output["status"]
            
            if score >= 80 and status != "pass":
                warnings.append(f"Score {score} typically indicates 'pass' status, got '{status}'")
            elif score < 50 and status != "fail":
                warnings.append(f"Score {score} typically indicates 'fail' status, got '{status}'")
            elif 50 <= score < 80 and status != "borderline":
                warnings.append(f"Score {score} typically indicates 'borderline' status, got '{status}'")
        
        # Failure reasons consistency
        if "status" in output and "failure_reasons" in output:
            if output["status"] == "fail" and not output["failure_reasons"]:
                errors.append("Status 'fail' requires non-empty failure_reasons")
        
        return {"errors": errors, "warnings": warnings}
    
    def enforce_contract(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enforce strict contract by filling missing fields with defaults.
        Use this as a last resort to ensure output compliance.
        """
        logger.warning("Enforcing contract with default values - this should not happen in production")
        
        defaults = {
            "score": 0,
            "readiness_percent": 0,
            "status": "fail",
            "failure_reasons": ["Contract enforcement applied"],
            "improvement_hints": [],
            "analysis": {
                "technical_quality": 0,
                "clarity": 0,
                "discipline_signals": 0
            },
            "meta": {
                "evaluation_time_ms": 0,
                "mode": "rule"
            },
            "feature_coverage": 0.0,
            "architecture_score": 0.0,
            "code_quality_score": 0.0,
            "completeness_score": 0.0,
            "missing_features": [],
            "requirement_match": 0.0,
            "evaluation_summary": "Contract enforcement applied",
            "documentation_score": 0.0,
            "documentation_alignment": "unknown",
            "title_score": 0.0,
            "description_score": 0.0,
            "repository_score": 0.0
        }
        
        # Merge with defaults
        enforced = defaults.copy()
        enforced.update(output)
        
        return enforced