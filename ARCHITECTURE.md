## Evaluation Pipeline

assignment_engine → signal_engine → merge_logic → review_orchestrator → validator

## Explicit Engine Functions

- `assignment_engine()`: Authoritative scoring and status determination.
- `signal_engine()`: Supporting repository and quality signals.
- `merge_logic()`: Hierarchical integration of assignment and signals.
- `review_orchestrator()`: Unified pipeline control.
- `validator()`: Strict contract enforcement.

## Guarantees

- **Assignment-first evaluation**: Logic follows strict authoritative rules.
- **Signals cannot override assignment**: Hierarchical merge prevents bypass.
- **Deterministic pipeline**: Same input produces 100% same output.
- **Explicit Signal Bonus**: Supporting signals provide a controlled score enrichment (+5 bonus).
