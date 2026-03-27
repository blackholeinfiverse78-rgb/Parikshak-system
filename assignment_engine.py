"""
Facade for the assignment engine mapping logic.
"""
import sys
import os

# Ensure the module can be found
sys.path.append(os.path.join(os.path.dirname(__file__), "intelligence-integration-module-main", "engine"))

try:
    from canonical_intelligence_engine import CanonicalIntelligenceEngine as AssignmentEngine
except ImportError:
    pass
