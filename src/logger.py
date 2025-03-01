"""
Logger module for PowerLearn LMS Bot.
Handles log configuration, formatting, and rotation.
"""

import os
import logging
import logging.handlers
from datetime import datetime
from typing import Dict, Any, Optional


class Logger:
    """Configures and manages logging for the PowerLearn LMS Bot."""

    def __init__(self, config: Dict[str, Any], app_name: str = "powerlearn_bot"):
        """
        Initialize the logger.

        Args:
            config: Logging configuration dictionary
            app_name: Name of the application
        """
        self.config = config
        self.app_name = app_name
        self.logger = None
        self._configure_logging()

    def _configure_logging(self) -> None:
        """Configure the logging system based on the provided configuration."""
        # Extract configuration values
        log_level_str = self.config.get('level', 'INFO')
        log_file = self.config.get('file', 'logs/powerlearn_bot.log')
        max_size = self.config.get('max_size', 10485760)  # 10MB default
        backup_count = self.config.get('backup_count', 5)
        log_format = self.config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        # Convert string log level to logging constant
        log_level = getattr(logging, log_level_str.upper(), logging.INFO)

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)

        # Clear any existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Create formatters
        formatter = logging.Formatter(log_format)

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level)
        root_logger.addHandler(console_handler)

        # Create file handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_size,
            backupCount=backup_count
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        root_logger.addHandler(file_handler)

        # Create application logger
        self.logger = logging.getLogger(self.app_name)
        self.logger.info(f"Logging initialized at level {log_level_str}")

    def get_logger(self, name: Optional[str] = None) -> logging.Logger:
        """
        Get a logger instance.

        Args:
            name: Logger name (appended to app_name if provided)

        Returns:
            Logger instance
        """
        if name:
            return logging.getLogger(f"{self.app_name}.{name}")
        return self.logger

    def log_dict(self, level: str, message: str, data: Dict[str, Any]) -> None:
        """
        Log a message with structured data.

        Args:
            level: Log level (debug, info, warning, error, critical)
            message: Log message
            data: Dictionary of data to log
        """
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(f"{message} - {data}")

    @staticmethod
    def create_session_log() -> Dict[str, Any]:
        """
        Create a new session log entry.

        Returns:
            Dictionary with session info
        """
        return {
            "session_id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "start_time": datetime.now().isoformat(),
            "status": "started",
            "events": []
        }

    @staticmethod
    def update_session_log(session_log: Dict[str, Any],
                           status: str, event: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Update a session log with a new event.

        Args:
            session_log: Session log dictionary
            status: New session status
            event: Event description
            details: Event details

        Returns:
            Updated session log
        """
        session_log["status"] = status
        session_log["events"].append({
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "details": details or {}
        })
        return session_log