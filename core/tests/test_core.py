"""DARKWIN Core Test Suite (Pytest)

Provides automated validation for the central reasoning engine,
caching layer, and vulnerability verification logic.

Author: ARYAN AHIRWAR (VIPHACKER.100)
"""

import pytest
import os
from core.cache_manager import global_cache
from core.vuln_verifier import VulnVerifier
from core.stealth import GhostMode
from core.config_manager import get_config, force_reload
from core.module_loader import get_module, list_modules

def test_cache_manager():
    """Test Redis/In-Memory caching layer."""
    key = "pytest_key"
    value = {"status": "ok", "value": 456}
    global_cache.set(key, value, ttl=5)
    
    cached_val = global_cache.get(key)
    assert cached_val == value
    
    global_cache.delete(key)
    assert global_cache.get(key) is None

def test_stealth_engine():
    """Test GhostMode fingerprinting."""
    ghost = GhostMode()
    headers = ghost.get_headers()
    assert "User-Agent" in headers
    assert "Accept-Language" in headers
    assert len(headers["User-Agent"]) > 10

def test_config_reload():
    """Test configuration hot-reloading."""
    config = get_config()
    assert config is not None
    
    # Reloading shouldn't crash
    new_config = force_reload()
    assert new_config is not None
    assert new_config.app.name == "DARKWIN"

def test_module_loader():
    """Test dynamic module discovery and registry."""
    modules_table = list_modules()
    assert modules_table is not None
    
    # Try loading a known module by path
    try:
        mod = get_module("modules.reconnaissance.subdomain.subfinder_runner")
        assert mod is not None
        assert hasattr(mod, "run")
    except ModuleNotFoundError:
        pytest.skip("Subfinder module not found in this environment")

@pytest.mark.asyncio
async def test_vuln_verifier_async():
    """Test async vulnerability verification."""
    verifier = VulnVerifier()
    # Mocking a verification (without real networking)
    # This just checks if the routing works
    result = await verifier.verify("UNKNOWN_TYPE", "http://example.com", "payload")
    assert result is False # Should fall back to AI which returns false on mock error

def run_tests():
    """CLI entry point to run core tests."""
    import sys
    # Ensure the current directory is in path for imports to work
    if os.getcwd() not in sys.path:
        sys.path.append(os.getcwd())
    
    # Run pytest on this file
    retcode = pytest.main([__file__, "-v", "-p", "no:warnings"])
    sys.exit(retcode)
