"""
Facade for the signal engine mapping logic.
"""
try:
    from app.services.signal_collector import SignalCollector as SignalEngine
except ImportError:
    pass
