import unittest
from core.config_manager import load_config

class TestConfigManager(unittest.TestCase):
    def test_load_default_config(self):
        config = load_config("non_existent.yaml")
        self.assertEqual(config.app.name, "DARKWIN")
        self.assertEqual(config.app.author, "ARYAN AHIRWAR (VIPHACKER.100)")

if __name__ == "__main__":
    unittest.main()
