"""
Security module for PowerLearn LMS Bot.
Handles credential management and secure operations.
"""

import logging
import os
from typing import Dict, Optional

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class SecurityManager:
    """Manages credentials and security features for the PowerLearn LMS Bot."""

    def __init__(self, env_path: str = ".env"):
        """
        Initialize the security manager.

        Args:
            env_path: Path to the .env file
        """
        # Load environment variables from .env file
        load_dotenv(env_path)
        self._credentials = None

    @staticmethod
    def get_credentials() -> Dict[str, str]:
        """
        Get LMS credentials from environment variables.

        Returns:
            Dictionary containing username and password

        Raises:
            ValueError: If credentials are not set
        """
        username = os.getenv('POWERLEARN_USERNAME')
        password = os.getenv('POWERLEARN_PASSWORD')

        if not username or not password:
            logger.error("Credentials not found in environment variables")
            raise ValueError("LMS credentials must be set in environment variables")

        return {
            'username': username,
            'password': password
        }

    @staticmethod
    def get_proxy_settings() -> Optional[Dict[str, str]]:
        """
        Get proxy settings from environment variables.

        Returns:
            Dictionary containing proxy settings or None if not configured
        """
        if os.getenv('USE_PROXY', 'false').lower() == 'true' and os.getenv('PROXY_URL'):
            return {
                'server': os.getenv('PROXY_URL')
            }
        return None

    def obscure_sensitive_data(self, text: str) -> str:
        """
        Obscure sensitive data in text (e.g., for logging).

        Args:
            text: Text that might contain sensitive data

        Returns:
            Text with sensitive data obscured
        """
        # Get credentials to obscure
        try:
            creds = self.get_credentials()

            # Replace username and password with asterisks
            if creds['username'] in text:
                text = text.replace(creds['username'], '********')
            if creds['password'] in text:
                text = text.replace(creds['password'], '********')

        except ValueError:
            # If credentials aren't available, we can't obscure them
            pass

        return text