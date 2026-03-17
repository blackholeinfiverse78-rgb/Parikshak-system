"""
Shraddha's Aware Engine v2 Validator - Enhanced Output Validation
Implements strict scoring contract compliance with deterministic engineering
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, ValidationError
from datetime import datetime, timedelta
import logging
import json

logger = logging.getLogger("aware_engine_validator")

class ScoringContract(BaseModel):
    """Scoring contract specification for Aware Engine v2"""
    accuracy_weight: float = 0.40  # 40% weighting
    completeness_weight: float = 0.40  # 40% weighting  
    quality_weight: float = 0.20  # 20% weighting
    
    # Score thresholds
    fail_threshold: int = 50
    pass_threshold: int = 80
    
    # Timeline discipline penalties
    timeline_penalty_per_day: float = 5.0
    max_timeline_penalty: float = 20.0

class ValidationResult(BaseModel):
    is_valid: bool
    contract_compliant: bool
    errors: List[str] = []
    warnings: List[str] = []
    scoring_breakdown: Optional[Dict[str, Any]] = None
    sanitized_output: Optional[Dict[str, Any]] = None
    determinism_verified: bool = False

class AwareEngineValidator:
    """
    Shraddha's Aware Engine v2 Validator
    
    Implements:
    - Strict scoring contract compliance (40% Accuracy, 40% Completeness, 20% Quality)
    - Deterministic engineering principles
    - Timeline discipline penalties
    - Deliverables matching validation
    - Schema validation enforcement
    """
    
    def __init__(self):
        self.scoring_contract = ScoringContract()
        
        # Required output schema - STRICT CONTRACT
        self.required_fields = {
            "score": int,
            "readiness_percent": int,
            "status": str,
            "failure_reasons": list,
            "improvement_hints": list,
            "analysis": dict,
            "meta": dict,
            
            # Aware Engine v2 specific fields
            "accuracy_score": float,
            "completeness_score": float,
            "quality_score": float,
            "timeline_penalty": float,
            "deliverables_matched": int,
            "deliverables_total": int,
            
            # Existing fields maintained for compatibility
            "feature_coverage": float,
            "architecture_score": float,
            "code_quality_score": float,
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
            "mode": str,
            "contract_version": str,
            "determinism_hash": str
        }
        
        self.valid_status_values = ["pass", "borderline", "fail"]
        self.valid_mode_values = ["rule", "ml", "hybrid", "aware-v2"]
    
    def validate_with_scoring_contract(self, output: Dict[str, Any], assignment_data: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Validate output against Aware Engine v2 scoring contract.
        
        Args:
            output: Raw output dictionary to validate
            assignment_data: Optional assignment data for deliverables matching
            
        Returns:
            ValidationResult with contract compliance status
        """
        logger.info("Starting Aware Engine v2 validation with scoring contract")
        
        errors = []
        warnings = []
        sanitized = {}
        
        # Step 1: Basic field validation
        basic_validation = self._validate_basic_fields(output)
        errors.extend(basic_validation["errors"])
        sanitized.update(basic_validation["sanitized"])
        
        # Step 2: Scoring contract validation
        contract_validation = self._validate_scoring_contract(sanitized, assignment_data)
        errors.extend(contract_validation["errors"])
        warnings.extend(contract_validation["warnings"])
        
        # Step 3: Determinism verification
        determinism_result = self._verify_determinism(sanitized)
        if not determinism_result["is_deterministic"]:
            warnings.append("Determinism verification failed - output may not be reproducible")
        
        # Step 4: Timeline discipline validation
        timeline_validation = self._validate_timeline_discipline(sanitized, assignment_data)
        warnings.extend(timeline_validation["warnings"])
        
        # Step 5: Deliverables matching validation
        deliverables_validation = self._validate_deliverables_matching(sanitized, assignment_data)
        errors.extend(deliverables_validation["errors"])
        warnings.extend(deliverables_validation["warnings"])
        
        is_valid = len(errors) == 0
        contract_compliant = is_valid and len(warnings) == 0
        
        logger.info(f"Aware Engine v2 validation complete - Valid: {is_valid}, Contract Compliant: {contract_compliant}")
        
        return ValidationResult(
            is_valid=is_valid,
            contract_compliant=contract_compliant,
            errors=errors,
            warnings=warnings,
            scoring_breakdown=contract_validation.get("breakdown"),
            sanitized_output=sanitized if is_valid else None,
            determinism_verified=determinism_result["is_deterministic"]
        )
    
    def _validate_basic_fields(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """Validate basic required fields"""
        errors = []
        sanitized = {}
        
        # Check required fields
        for field, expected_type in self.required_fields.items():
            if field not in output:
                # Provide defaults for Aware Engine v2 specific fields
                if field in ["accuracy_score", "completeness_score", "quality_score"]:
                    sanitized[field] = 0.0
                elif field == "timeline_penalty":
                    sanitized[field] = 0.0
                elif field in ["deliverables_matched", "deliverables_total"]:
                    sanitized[field] = 0
                elif field in self.required_fields:
                    errors.append(f"Missing required field: {field}")
            else:
                try:
                    sanitized[field] = self._sanitize_field(field, output[field], expected_type)
                except Exception as e:
                    errors.append(f"Field '{field}' validation failed: {str(e)}")
        
        # Validate nested objects
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
        
        return {"errors": errors, "sanitized": sanitized}
    
    def _validate_scoring_contract(self, output: Dict[str, Any], assignment_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate against Aware Engine v2 scoring contract"""
        errors = []
        warnings = []
        
        # Extract scoring components
        accuracy_score = output.get("accuracy_score", 0.0)
        completeness_score = output.get("completeness_score", 0.0)
        quality_score = output.get("quality_score", 0.0)
        timeline_penalty = output.get("timeline_penalty", 0.0)
        
        # Validate scoring weights
        if not (0 <= accuracy_score <= 100):
            errors.append(f"Accuracy score out of range: {accuracy_score}")
        if not (0 <= completeness_score <= 100):
            errors.append(f"Completeness score out of range: {completeness_score}")
        if not (0 <= quality_score <= 100):
            errors.append(f"Quality score out of range: {quality_score}")
        
        # Calculate weighted score according to contract
        weighted_accuracy = accuracy_score * self.scoring_contract.accuracy_weight
        weighted_completeness = completeness_score * self.scoring_contract.completeness_weight
        weighted_quality = quality_score * self.scoring_contract.quality_weight
        
        calculated_score = weighted_accuracy + weighted_completeness + weighted_quality - timeline_penalty
        calculated_score = max(0, min(100, calculated_score))  # Clamp to 0-100
        
        # Verify score matches calculation
        reported_score = output.get("score", 0)
        if abs(calculated_score - reported_score) > 1:  # Allow 1 point tolerance for rounding
            warnings.append(f"Score mismatch: calculated {calculated_score:.1f}, reported {reported_score}")
        
        # Validate status alignment with score
        status = output.get("status", "fail")
        expected_status = self._calculate_status_from_score(calculated_score)
        if status != expected_status:
            warnings.append(f"Status mismatch: score {calculated_score} should be '{expected_status}', got '{status}'")
        
        breakdown = {
            "accuracy_component": weighted_accuracy,
            "completeness_component": weighted_completeness,
            "quality_component": weighted_quality,
            "timeline_penalty": timeline_penalty,
            "calculated_total": calculated_score,
            "reported_total": reported_score,
            "contract_compliant": abs(calculated_score - reported_score) <= 1
        }
        
        return {"errors": errors, "warnings": warnings, "breakdown": breakdown}
    
    def _validate_timeline_discipline(self, output: Dict[str, Any], assignment_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate timeline discipline penalties"""
        warnings = []
        
        if not assignment_data:
            return {"warnings": warnings}
        
        timeline_penalty = output.get("timeline_penalty", 0.0)
        
        # Check if penalty is within valid range
        if timeline_penalty > self.scoring_contract.max_timeline_penalty:
            warnings.append(f"Timeline penalty exceeds maximum: {timeline_penalty} > {self.scoring_contract.max_timeline_penalty}")
        
        # Validate penalty calculation if deadline information is available
        if "deadline" in assignment_data and "submission_date" in assignment_data:
            try:
                deadline = datetime.fromisoformat(assignment_data["deadline"])
                submission_date = datetime.fromisoformat(assignment_data["submission_date"])
                
                if submission_date > deadline:
                    days_late = (submission_date - deadline).days
                    expected_penalty = min(
                        days_late * self.scoring_contract.timeline_penalty_per_day,
                        self.scoring_contract.max_timeline_penalty
                    )
                    
                    if abs(timeline_penalty - expected_penalty) > 0.1:
                        warnings.append(f"Timeline penalty calculation mismatch: expected {expected_penalty}, got {timeline_penalty}")
            except (ValueError, KeyError) as e:
                warnings.append(f"Timeline validation failed: {str(e)}")
        
        return {"warnings": warnings}
    
    def _validate_deliverables_matching(self, output: Dict[str, Any], assignment_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate deliverables matching for completeness scoring"""
        errors = []
        warnings = []
        
        deliverables_matched = output.get("deliverables_matched", 0)
        deliverables_total = output.get("deliverables_total", 0)
        
        # Basic validation
        if deliverables_matched > deliverables_total:
            errors.append(f"Deliverables matched ({deliverables_matched}) cannot exceed total ({deliverables_total})")
        
        if deliverables_total > 0:
            match_ratio = deliverables_matched / deliverables_total
            completeness_score = output.get("completeness_score", 0.0)
            
            # Validate completeness score aligns with deliverables matching
            expected_completeness = match_ratio * 100
            if abs(completeness_score - expected_completeness) > 10:  # Allow 10% tolerance
                warnings.append(f"Completeness score ({completeness_score}) doesn't align with deliverables ratio ({expected_completeness:.1f})")
        
        return {"errors": errors, "warnings": warnings}
    
    def _verify_determinism(self, output: Dict[str, Any]) -> Dict[str, bool]:
        """Verify deterministic output characteristics"""
        
        # Check for determinism hash in meta
        meta = output.get("meta", {})
        determinism_hash = meta.get("determinism_hash", "")
        
        # Basic determinism checks
        is_deterministic = True
        
        # Check for random elements that would break determinism
        if "random" in str(output).lower():
            is_deterministic = False
        
        # Check for timestamp-based randomness (evaluation_time_ms should be the only time-based field)
        time_based_fields = [k for k in output.keys() if "time" in k.lower() and k != "evaluation_time_ms"]
        if time_based_fields:
            is_deterministic = False
        
        return {"is_deterministic": is_deterministic}
    
    def _calculate_status_from_score(self, score: float) -> str:
        """Calculate status from score according to contract thresholds"""
        if score >= self.scoring_contract.pass_threshold:
            return "pass"
        elif score >= self.scoring_contract.fail_threshold:
            return "borderline"
        else:
            return "fail"
    
    def _sanitize_field(self, field_name: str, value: Any, expected_type: type) -> Any:
        """Sanitize and convert field to expected type"""
        if expected_type == int:
            if isinstance(value, (int, float)):
                return int(value)
            elif isinstance(value, str) and value.replace('.', '').replace('-', '').isdigit():
                return int(float(value))
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
        """Validate meta nested object with Aware Engine v2 requirements"""
        errors = []
        sanitized = {}
        
        if not isinstance(meta, dict):
            return {"errors": ["Meta must be a dictionary"], "sanitized": {}}
        
        # Add Aware Engine v2 specific meta fields if missing
        if "contract_version" not in meta:
            sanitized["contract_version"] = "aware-v2"
        if "determinism_hash" not in meta:
            sanitized["determinism_hash"] = self._generate_determinism_hash(meta)
        
        for field, expected_type in self.meta_required_fields.items():
            if field not in meta and field not in sanitized:
                if field == "contract_version":
                    sanitized[field] = "aware-v2"
                elif field == "determinism_hash":
                    sanitized[field] = "auto-generated"
                else:
                    errors.append(f"Missing meta field: {field}")
            else:
                try:
                    value = meta.get(field, sanitized.get(field))
                    sanitized[field] = self._sanitize_field(field, value, expected_type)
                except Exception as e:
                    errors.append(f"Meta field '{field}' validation failed: {str(e)}")
        
        return {"errors": errors, "sanitized": sanitized}
    
    def _generate_determinism_hash(self, meta: Dict[str, Any]) -> str:
        """Generate a determinism hash for verification"""
        import hashlib
        
        # Create hash based on evaluation parameters (excluding time)
        hash_data = {
            "mode": meta.get("mode", "unknown"),
            "contract_version": "aware-v2"
        }
        
        hash_string = json.dumps(hash_data, sort_keys=True)
        return hashlib.md5(hash_string.encode()).hexdigest()[:8]
    
    def enforce_scoring_contract(self, output: Dict[str, Any], assignment_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Enforce Aware Engine v2 scoring contract by recalculating scores.
        Use this to ensure contract compliance when validation fails.
        """
        logger.warning("Enforcing Aware Engine v2 scoring contract - recalculating scores")
        
        # Extract or default scoring components
        accuracy_score = output.get("accuracy_score", 50.0)
        completeness_score = output.get("completeness_score", 50.0)
        quality_score = output.get("quality_score", 50.0)
        timeline_penalty = output.get("timeline_penalty", 0.0)
        
        # Apply scoring contract formula
        weighted_accuracy = accuracy_score * self.scoring_contract.accuracy_weight
        weighted_completeness = completeness_score * self.scoring_contract.completeness_weight
        weighted_quality = quality_score * self.scoring_contract.quality_weight
        
        final_score = weighted_accuracy + weighted_completeness + weighted_quality - timeline_penalty
        final_score = max(0, min(100, int(final_score)))
        
        # Update output with contract-compliant values
        enforced_output = output.copy()
        enforced_output.update({
            "score": final_score,
            "readiness_percent": final_score,
            "status": self._calculate_status_from_score(final_score),
            "accuracy_score": accuracy_score,
            "completeness_score": completeness_score,
            "quality_score": quality_score,
            "timeline_penalty": timeline_penalty,
            "meta": {
                **output.get("meta", {}),
                "contract_version": "aware-v2",
                "mode": "aware-v2",
                "determinism_hash": self._generate_determinism_hash(output.get("meta", {}))
            }
        })
        
        return enforced_output