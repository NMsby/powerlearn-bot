"""
Screenshot manager for PowerLearn LMS Bot.
Handles taking screenshots, saving them, and managing screenshot files.
"""

import os
import time
from datetime import datetime
from typing import Dict, Any, Optional
import logging
from playwright.sync_api import Page

logger = logging.getLogger(__name__)


class ScreenshotManager:
    """Manages screenshots for the PowerLearn LMS Bot."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the screenshot manager.

        Args:
            config: Screenshot configuration dictionary
        """
        self.config = config
        self.enabled = config.get('enabled', True)
        self.on_error = config.get('on_error', True)
        self.periodic = config.get('periodic', False)
        self.periodic_interval = config.get('periodic_interval', 300)  # seconds
        self.path = config.get('path', 'screenshots/')

        # Create screenshots directory if it doesn't exist
        if self.enabled:
            os.makedirs(self.path, exist_ok=True)
            logger.info(f"Screenshot directory initialized at {self.path}")

    def take_screenshot(self, page: Page, reason: str = "periodic", error: Optional[str] = None) -> Optional[str]:
        """
        Take a screenshot of the current page.

        Args:
            page: Playwright page object
            reason: Reason for taking screenshot (periodic, error, login, logout)
            error: Error message if screenshot is taken due to an error

        Returns:
            Path to the saved screenshot or None if screenshots are disabled
        """
        if not self.enabled:
            return None

        # Skip if it's periodic and periodic screenshots are disabled
        if reason == "periodic" and not self.periodic:
            return None

        # Skip if it's an error and error screenshots are disabled
        if reason == "error" and not self.on_error:
            return None

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{reason}.png"

        if error:
            # Create error-specific filename and make sure it's valid
            error_slug = "".join(c if c.isalnum() else "_" for c in error[:20])
            filename = f"{timestamp}_error_{error_slug}.png"

        filepath = os.path.join(self.path, filename)

        try:
            # Take screenshot
            page.screenshot(path=filepath)
            logger.info(f"Screenshot saved: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return None

    def clean_old_screenshots(self, max_age_days: int = 7, max_files: int = 1000) -> None:
        """
        Clean up old screenshot files.

        Args:
            max_age_days: Maximum age of screenshots to keep in days
            max_files: Maximum number of screenshot files to keep
        """
        if not self.enabled or not os.path.exists(self.path):
            return

        try:
            # Get all screenshot files with their timestamps
            files = []
            for filename in os.listdir(self.path):
                if filename.endswith('.png'):
                    filepath = os.path.join(self.path, filename)
                    files.append((filepath, os.path.getmtime(filepath)))

            # Sort by modification time (oldest first)
            files.sort(key=lambda x: x[1])

            # Delete old files
            now = time.time()
            max_age_seconds = max_age_days * 24 * 60 * 60

            # First, delete files older than max_age_days
            for filepath, mtime in files:
                if now - mtime > max_age_seconds:
                    os.remove(filepath)
                    logger.debug(f"Deleted old screenshot: {filepath}")

            # Then, if we still have too many files, delete the oldest ones
            remaining_files = [(f, m) for f, m in files if os.path.exists(f)]
            if len(remaining_files) > max_files:
                files_to_delete = remaining_files[:(len(remaining_files) - max_files)]
                for filepath, _ in files_to_delete:
                    os.remove(filepath)
                    logger.debug(f"Deleted excess screenshot: {filepath}")

            logger.info(f"Screenshot cleanup complete. Keeping max {max_files} files, max age {max_age_days} days.")

        except Exception as e:
            logger.error(f"Error cleaning up old screenshots: {e}")