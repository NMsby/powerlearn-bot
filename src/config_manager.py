"""
Configuration manager for PowerLearn LMS Bot.
Handles loading settings from YAML and environment variables.
"""

import logging
import os
from typing import Dict, Any

import yaml

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages configuration settings for the PowerLearn LMS Bot."""

    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize the configuration manager.

        Args:
            config_path: Path to the YAML configuration file
        """
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.load_config()

    def load_config(self) -> None:
        """Load configuration from YAML file and override with environment variables."""
        try:
            # Load from YAML
            with open(self.config_path, 'r') as file:
                self.config = yaml.safe_load(file)

            logger.info(f"Loaded configuration from {self.config_path}")

            # Override with environment variables
            self._override_with_env()

        except FileNotFoundError:
            logger.error(f"Configuration file not found: {self.config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML configuration: {e}")
            raise

    def _override_with_env(self) -> None:
        """Override configuration with environment variables."""
        # Browser settings
        if os.getenv('HEADLESS_MODE'):
            self.config['browser']['headless'] = os.getenv('HEADLESS_MODE').lower() == 'true'

        # Proxy settings
        if os.getenv('USE_PROXY'):
            self.config['proxy']['enabled'] = os.getenv('USE_PROXY').lower() == 'true'

        if os.getenv('PROXY_URL'):
            self.config['proxy']['url'] = os.getenv('PROXY_URL')

        # Logging settings
        if os.getenv('LOG_LEVEL'):
            self.config['logging']['level'] = os.getenv('LOG_LEVEL')

        # Override session duration if set
        if os.getenv('SESSION_DURATION'):
            try:
                self.config['session']['duration'] = int(os.getenv('SESSION_DURATION'))
            except ValueError:
                logger.warning(f"Invalid SESSION_DURATION value: {os.getenv('SESSION_DURATION')}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.

        Args:
            key: Configuration key in dot notation (e.g., 'browser.headless')
            default: Default value if key is not found

        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def get_all(self) -> Dict[str, Any]:
        """Get the entire configuration."""
        return self.config

    def update(self, key: str, value: Any) -> None:
        """
        Update a configuration value using dot notation.

        Args:
            key: Configuration key in dot notation (e.g., 'browser.headless')
            value: New value
        """
        keys = key.split('.')
        config = self.config

        # Navigate to the nested dictionary
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Update the value
        config[keys[-1]] = value
        logger.debug(f"Updated configuration: {key} = {value}")