"""Unit tests for core configuration management."""

import unittest

from core.config_manager import load_config


class TestConfigManager(unittest.TestCase):
    """Test the config manager's fallback to default values."""

    def test_load_default_config(self) -> None:
        """Loading a non-existent file should return the default config."""
        config = load_config("non_existent.yaml")
        self.assertEqual(config.app.name, "DARKWIN")
        self.assertEqual(config.app.author, "ARYAN AHIRWAR (VIPHACKER.100)")


if __name__ == "__main__":
    unittest.main()
