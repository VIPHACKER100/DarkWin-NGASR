import unittest
from modules.vulnerability_engine.injection.sql.sqli_scanner import run as sqli_scan

class TestVulnSuite(unittest.TestCase):
    def test_sqli_scanner_structure(self):
        # We can't easily run a live scan without a target, so we test the interface
        import asyncio
        config = {"tools": {"sqlmap": "echo"}}
        results = asyncio.run(sqli_scan("http://example.com", "test-scan", config))
        self.assertIsInstance(results, list)

if __name__ == "__main__":
    unittest.main()
