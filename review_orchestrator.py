"""
Facade for the review orchestrator mapping logic.
"""
try:
    from app.services.product_orchestrator import ProductOrchestrator as ReviewOrchestrator
except ImportError:
    pass
