"""
Tests for the security manager.
"""

import os
import unittest
from unittest.mock import patch
from src.security import SecurityManager


class TestSecurityManager(unittest.TestCase):
    """Test cases for the SecurityManager."""

    @patch.dict(os.environ, {
        'POWERLEARN_USERNAME': 'testuser',
        'POWERLEARN_PASSWORD': 'testpass'
    })
    def test_get_credentials(self):
        """Test getting credentials from environment variables."""
        security_manager = SecurityManager()
        credentials = security_manager.get_credentials()

        self.assertEqual(credentials['username'], 'testuser')
        self.assertEqual(credentials['password'], 'testpass')

    def test_missing_credentials(self):
        """Test behavior when credentials are missing."""
        # Remove environment variables if they exist
        env_vars = {}
        for key in ['POWERLEARN_USERNAME', 'POWERLEARN_PASSWORD']:
            if key in os.environ:
                env_vars[key] = os.environ[key]
                del os.environ[key]

        security_manager = SecurityManager()

        with self.assertRaises(ValueError):
            security_manager.get_credentials()

        # Restore environment variables
        for key, value in env_vars.items():
            os.environ[key] = value

    @patch.dict(os.environ, {
        'USE_PROXY': 'true',
        'PROXY_URL': 'http://test-proxy:8080'
    })
    def test_get_proxy_settings(self):
        """Test getting proxy settings from environment variables."""
        security_manager = SecurityManager()
        proxy_settings = security_manager.get_proxy_settings()

        self.assertIsNotNone(proxy_settings)
        self.assertEqual(proxy_settings['server'], 'http://test-proxy:8080')

    def test_obscure_sensitive_data(self):
        """Test obscuring sensitive data in text."""
        with patch.dict(os.environ, {
            'POWERLEARN_USERNAME': 'testuser',
            'POWERLEARN_PASSWORD': 'testpass'
        }):
            security_manager = SecurityManager()

            # Text containing sensitive data
            text = "Logging in with username testuser and password testpass"

            # Obscure sensitive data
            obscured_text = security_manager.obscure_sensitive_data(text)

            self.assertNotIn('testuser', obscured_text)
            self.assertNotIn('testpass', obscured_text)
            self.assertIn('********', obscured_text)


if __name__ == '__main__':
    unittest.main()