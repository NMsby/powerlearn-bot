"""
Tests for the configuration manager.
"""

import os
import unittest
from unittest.mock import patch
import tempfile
import yaml
from src.config_manager import ConfigManager


class TestConfigManager(unittest.TestCase):
    """Test cases for the ConfigManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_config = {
            'browser': {
                'headless': True,
                'type': 'chromium'
            },
            'session': {
                'duration': 900,
                'pause_between': 300
            }
        }

        # Create temporary config file
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = os.path.join(self.temp_dir.name, 'config.yaml')

        with open(self.config_path, 'w') as f:
            yaml.dump(self.test_config, f)

    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()

    def test_load_config(self):
        """Test loading configuration from file."""
        config_manager = ConfigManager(self.config_path)
        self.assertEqual(config_manager.get('browser.headless'), True)
        self.assertEqual(config_manager.get('browser.type'), 'chromium')
        self.assertEqual(config_manager.get('session.duration'), 900)

    def test_get_default(self):
        """Test getting default values."""
        config_manager = ConfigManager(self.config_path)
        self.assertEqual(config_manager.get('nonexistent.key', 'default'), 'default')

    @patch.dict(os.environ, {'HEADLESS_MODE': 'false'})
    def test_override_with_env(self):
        """Test overriding config with environment variables."""
        config_manager = ConfigManager(self.config_path)
        self.assertEqual(config_manager.get('browser.headless'), False)

    def test_update_config(self):
        """Test updating configuration."""
        config_manager = ConfigManager(self.config_path)
        config_manager.update('browser.headless', False)
        self.assertEqual(config_manager.get('browser.headless'), False)

        # Test creating nested keys
        config_manager.update('new.nested.key', 'value')
        self.assertEqual(config_manager.get('new.nested.key'), 'value')


if __name__ == '__main__':
    unittest.main()