"""Tests for vulnerability scanner module interfaces."""

import asyncio
import unittest

from modules.vulnerability_engine.injection.sql.sqli_scanner import run as sqli_scan


class TestVulnSuite(unittest.TestCase):
    """Verify that scanner entry points return the expected type."""

    def test_sqli_scanner_structure(self) -> None:
        """The SQLi scanner should always return a list."""
        config = {"tools": {"sqlmap": "echo"}}
        results = asyncio.run(sqli_scan("http://example.com", "test-scan", config))
        self.assertIsInstance(results, list)


if __name__ == "__main__":
    unittest.main()
