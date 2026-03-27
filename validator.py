"""
Facade for the registry validation mapping logic.
"""
try:
    from app.services.registry_validator import RegistryValidator as Validator
except ImportError:
    pass
