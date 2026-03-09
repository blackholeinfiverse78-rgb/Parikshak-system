# Product Core v1 - Integration Boundaries

**Version**: 1.2.0  
**Purpose**: Define plug-in points for team integration  
**Status**: Production Ready

---

## Integration Philosophy

The system is designed with **explicit integration boundaries** where team members can enhance functionality without modifying core logic.

### Core Principles
1. **Plug-in Architecture**: New components plug into existing interfaces
2. **Optional Layers**: Enhancements are optional, not required
3. **No Core Changes**: Integration points don't require modifying orchestrator
4. **Determinism Preserved**: All integrations must maintain deterministic behavior

---

## Integration Point 1: Scoring Module (Shraddha Zagade)

### Current Implementation
**File**: `app/services/review_engine.py`  
**Interface**: `ReviewEngineInterface`

```python
class ReviewEngineInterface:
    def evaluate(self, task: dict) -> dict:
        """
        Evaluate task and return review output.
        
        Args:
            task: Task dict with title, description, etc.
            
        Returns:
            dict with score, status, analysis, etc.
        """
        pass
```

### Plug-in Point

**Location**: `ProductOrchestrator.__init__()`

```python
class ProductOrchestrator:
    def __init__(self, review_engine: ReviewEngineInterface):
        self._review_engine = review_engine  # ← Plug-in point
```

### How to Upgrade Scoring Logic

#### Step 1: Create New Scoring Engine
```python
# app/services/advanced_scoring_engine.py
from app.core.interfaces.review_engine_interface import ReviewEngineInterface

class AdvancedScoringEngine(ReviewEngineInterface):
    def evaluate(self, task: dict) -> dict:
        # Your enhanced scoring logic here
        # Must return same contract as ReviewEngine
        
        return {
            "score": calculated_score,
            "readiness_percent": readiness,
            "status": status,
            "failure_reasons": reasons,
            "improvement_hints": hints,
            "analysis": {
                "technical_quality": tq_score,
                "clarity": clarity_score,
                "discipline_signals": ds_score
            },
            "meta": {
                "evaluation_time_ms": time_ms,
                "mode": "advanced"  # ← Indicate new mode
            }
        }
```

#### Step 2: Plug Into Orchestrator
```python
# app/api/lifecycle.py
from app.services.advanced_scoring_engine import AdvancedScoringEngine

# Old: orchestrator = ProductOrchestrator(review_engine=ReviewEngine())
# New:
orchestrator = ProductOrchestrator(review_engine=AdvancedScoringEngine())
```

#### Step 3: No Other Changes Required
- Orchestrator uses same interface
- Storage uses same ReviewRecord structure
- API returns same response contract

### Contract Requirements

**Input Contract**:
```python
task: dict = {
    "task_id": str,
    "task_title": str,
    "task_description": str,
    "submitted_by": str,
    "timestamp": datetime
}
```

**Output Contract** (MUST match):
```python
{
    "score": int (0-100),
    "readiness_percent": int (0-100),
    "status": str ("pass" | "borderline" | "fail"),
    "failure_reasons": list[str],
    "improvement_hints": list[str],
    "analysis": {
        "technical_quality": int (0-100),
        "clarity": int (0-100),
        "discipline_signals": int (0-100)
    },
    "meta": {
        "evaluation_time_ms": int,
        "mode": str
    }
}
```

### Determinism Requirement
- **MUST**: Same input → Same output
- **MUST**: No random number generation
- **MUST**: Reproducible results
- **TEST**: Run `test_deterministic_orchestration()` to verify

### Enhancement Ideas
1. **ML-Based Scoring**: Use trained model for scoring
2. **Multi-Criteria Analysis**: Add more analysis dimensions
3. **Context-Aware Scoring**: Consider user history
4. **Weighted Components**: Adjust PDF/Repo/Desc weights
5. **Custom Rubrics**: Define scoring rubrics per domain

---

## Integration Point 2: AI Evaluator (Sri Satya)

### Current Implementation
**Status**: Not implemented (optional layer)  
**Purpose**: Augment scoring with AI-generated insights

### Plug-in Point

**Location**: After ReviewEngine, before storage

```python
class ProductOrchestrator:
    def __init__(
        self, 
        review_engine: ReviewEngineInterface,
        ai_evaluator: Optional[AIEvaluatorInterface] = None  # ← New parameter
    ):
        self._review_engine = review_engine
        self._ai_evaluator = ai_evaluator  # ← Optional layer
```

### Proposed Interface

```python
# app/core/interfaces/ai_evaluator_interface.py
class AIEvaluatorInterface:
    def augment_review(
        self, 
        task: dict, 
        review_output: dict
    ) -> dict:
        """
        Augment review output with AI insights.
        
        Args:
            task: Original task dict
            review_output: Output from ReviewEngine
            
        Returns:
            Augmented review output (same contract + optional fields)
        """
        pass
```

### Integration Flow

```python
# In ProductOrchestrator.process_submission()

# Step 3: Call review engine
review_output = self._review_engine.evaluate(task.model_dump())

# Step 3.5: Optionally augment with AI (NEW)
if self._ai_evaluator:
    review_output = self._ai_evaluator.augment_review(
        task.model_dump(), 
        review_output
    )

# Step 4: Store review (same as before)
```

### Implementation Example

```python
# app/services/ai_evaluator.py
class AIEvaluator(AIEvaluatorInterface):
    def augment_review(self, task: dict, review_output: dict) -> dict:
        # Generate AI insights
        ai_insights = self._generate_insights(task, review_output)
        
        # Add to improvement_hints (optional field)
        review_output["improvement_hints"].extend(ai_insights)
        
        # Add AI metadata (optional field)
        review_output["ai_metadata"] = {
            "model": "gpt-4",
            "confidence": 0.95,
            "insights_count": len(ai_insights)
        }
        
        return review_output
```

### Contract Requirements

**Input**: 
- task: dict (same as ReviewEngine input)
- review_output: dict (output from ReviewEngine)

**Output**:
- MUST preserve all required fields from review_output
- MAY add optional fields (e.g., ai_metadata, ai_insights)
- MUST NOT modify score, status, or analysis (unless explicitly designed to)

### Determinism Consideration
- **AI is non-deterministic** by nature
- **Solution**: Make AI layer optional and clearly marked
- **Storage**: Store AI metadata separately if needed
- **Testing**: Test with and without AI layer

### Enhancement Ideas
1. **Insight Generation**: Generate specific improvement suggestions
2. **Example Provision**: Provide examples of good task descriptions
3. **Trend Analysis**: Analyze patterns across submissions
4. **Personalized Feedback**: Tailor feedback to user level
5. **Quality Prediction**: Predict likelihood of success

---

## Integration Point 3: Validation Layer (Vinayak Tiwari)

### Current Implementation
**Status**: Pydantic validation only  
**Purpose**: Add runtime verification and custom validation rules

### Plug-in Point

**Location**: Before orchestrator, in API layer

```python
# app/api/lifecycle.py
@router.post("/submit", response_model=TaskSubmitResponse)
def submit_task(
    request: TaskSubmitRequest,
    validator: ValidatorInterface = Depends(get_validator)  # ← Injection point
):
    # Step 1: Custom validation (NEW)
    validation_result = validator.validate_submission(request)
    if not validation_result.is_valid:
        raise HTTPException(422, detail=validation_result.errors)
    
    # Step 2: Process submission (same as before)
    task = Task(...)
    result = orchestrator.process_submission(task)
    return result
```

### Proposed Interface

```python
# app/core/interfaces/validator_interface.py
class ValidationResult(BaseModel):
    is_valid: bool
    errors: List[str]
    warnings: List[str]

class ValidatorInterface:
    def validate_submission(self, request: TaskSubmitRequest) -> ValidationResult:
        """
        Validate submission request with custom rules.
        
        Args:
            request: TaskSubmitRequest from API
            
        Returns:
            ValidationResult with is_valid flag and error messages
        """
        pass
```

### Implementation Example

```python
# app/services/custom_validator.py
class CustomValidator(ValidatorInterface):
    def validate_submission(self, request: TaskSubmitRequest) -> ValidationResult:
        errors = []
        warnings = []
        
        # Custom rule 1: Check for profanity
        if self._contains_profanity(request.task_description):
            errors.append("Description contains inappropriate language")
        
        # Custom rule 2: Check for minimum technical keywords
        if self._count_technical_keywords(request.task_description) < 3:
            warnings.append("Consider adding more technical details")
        
        # Custom rule 3: Check for objective statement
        if "objective:" not in request.task_description.lower():
            warnings.append("Consider adding an explicit objective statement")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
```

### Integration Options

#### Option 1: Dependency Injection (Recommended)
```python
def get_validator() -> ValidatorInterface:
    return CustomValidator()

@router.post("/submit")
def submit_task(
    request: TaskSubmitRequest,
    validator: ValidatorInterface = Depends(get_validator)
):
    validation_result = validator.validate_submission(request)
    # ...
```

#### Option 2: Middleware
```python
@app.middleware("http")
async def validation_middleware(request: Request, call_next):
    if request.url.path == "/api/v1/lifecycle/submit":
        # Validate request
        pass
    response = await call_next(request)
    return response
```

### Contract Requirements

**Input**:
- request: TaskSubmitRequest (Pydantic model)

**Output**:
- ValidationResult with is_valid, errors, warnings

### Enhancement Ideas
1. **Content Filtering**: Block inappropriate content
2. **Plagiarism Detection**: Check for copied content
3. **Complexity Analysis**: Ensure minimum complexity
4. **Domain Validation**: Validate domain-specific requirements
5. **Rate Limiting**: Prevent spam submissions
6. **User Quotas**: Enforce submission limits

---

## Integration Testing

### Test New Scoring Engine
```python
def test_custom_scoring_engine():
    custom_engine = CustomScoringEngine()
    orchestrator = ProductOrchestrator(review_engine=custom_engine)
    
    task = Task(...)
    result = orchestrator.process_submission(task)
    
    # Verify contract
    assert "score" in result["review"]
    assert "status" in result["review"]
    # ...
```

### Test AI Evaluator
```python
def test_ai_evaluator_augmentation():
    ai_evaluator = AIEvaluator()
    orchestrator = ProductOrchestrator(
        review_engine=ReviewEngine(),
        ai_evaluator=ai_evaluator
    )
    
    task = Task(...)
    result = orchestrator.process_submission(task)
    
    # Verify AI metadata added
    assert "ai_metadata" in result["review"]
```

### Test Validator
```python
def test_custom_validator():
    validator = CustomValidator()
    request = TaskSubmitRequest(...)
    
    result = validator.validate_submission(request)
    
    assert isinstance(result, ValidationResult)
    assert isinstance(result.is_valid, bool)
```

---

## Deployment Considerations

### Feature Flags
```python
# config.py
ENABLE_AI_EVALUATOR = os.getenv("ENABLE_AI_EVALUATOR", "false") == "true"
ENABLE_CUSTOM_VALIDATOR = os.getenv("ENABLE_CUSTOM_VALIDATOR", "false") == "true"

# app/api/lifecycle.py
if ENABLE_AI_EVALUATOR:
    orchestrator = ProductOrchestrator(
        review_engine=ReviewEngine(),
        ai_evaluator=AIEvaluator()
    )
else:
    orchestrator = ProductOrchestrator(review_engine=ReviewEngine())
```

### Gradual Rollout
1. Deploy with feature flags OFF
2. Enable for 10% of traffic
3. Monitor metrics (latency, errors, scores)
4. Gradually increase to 100%

### Rollback Plan
1. Set feature flag to OFF
2. Restart service
3. System reverts to core behavior

---

## Summary

| Integration Point | Owner | Type | Status | Determinism |
|-------------------|-------|------|--------|-------------|
| Scoring Module | Shraddha Zagade | Required | Implemented | Must maintain |
| AI Evaluator | Sri Satya | Optional | Not implemented | Can be non-deterministic |
| Validation Layer | Vinayak Tiwari | Optional | Not implemented | Must maintain |

---

**Document Status**: COMPLETE  
**Integration Points Defined**: YES  
**Contracts Specified**: YES  
**Examples Provided**: YES
