"""DARKWIN Core Unit Tests

Provides automated validation for the central reasoning engine,
caching layer, and vulnerability verification logic.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import unittest
import asyncio
from core.cache_manager import global_cache
from core.vuln_verifier import VulnVerifier
from core.stealth import GhostMode

class TestDarkWinCore(unittest.TestCase):
    """Test suite for DARKWIN core components."""

    def test_cache_manager(self):
        """Test Redis-based caching layer."""
        key = "test_key"
        value = {"status": "ok", "value": 123}
        global_cache.set(key, value, ttl=10)
        
        cached_val = global_cache.get(key)
        self.assertEqual(cached_val, value)
        
        global_cache.delete(key)
        self.assertIsNone(global_cache.get(key))

    def test_stealth_engine(self):
        """Test GhostMode fingerprinting."""
        ghost = GhostMode()
        headers = ghost.get_headers()
        self.assertIn("User-Agent", headers)
        self.assertIn("Accept-Language", headers)

    def test_vuln_verifier_init(self):
        """Test Verifier initialization."""
        verifier = VulnVerifier()
        self.assertIsNotNone(verifier.ghost)

def run_tests():
    """Execute the test suite."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDarkWinCore)
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == "__main__":
    run_tests()
