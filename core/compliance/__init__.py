# Compliance and Legal Enforcement Package
"""DARKWIN Compliance & Legal Module

Handles scanning scope enforcement, PII scrubbing in reports, 
and data retention policies to ensure legal and ethical operations.
"""

from core.compliance.scope_enforcer import ScopeEnforcer
from core.compliance.privacy_scrubber import scrub_pii
from core.compliance.data_retention_manager import enforce_retention

__all__ = ["ScopeEnforcer", "scrub_pii", "enforce_retention"]
