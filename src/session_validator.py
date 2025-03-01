"""
Session validator for PowerLearn LMS Bot.
Validates session state and performs health checks.
"""

import logging
import time
from typing import Dict, Any

from playwright.sync_api import Page

logger = logging.getLogger(__name__)


class SessionValidator:
    """Validates the session state for the PowerLearn LMS Bot."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the session validator.

        Args:
            config: LMS configuration
        """
        self.lms_config = config.get('lms', {})
        self.last_health_check = 0
        self.health_check_interval = 60  # seconds

    def is_logged_in(self, page: Page) -> bool:
        """
        Check if the user is logged in.

        Args:
            page: Playwright page object

        Returns:
            True if logged in, False otherwise
        """
        # Get indicators of successful login
        indicators = self.lms_config.get('logged_in_indicators', [])

        if not indicators:
            logger.warning("No logged in indicators configured, defaulting to URL check")
            # Check if we're on the dashboard URL
            dashboard_url = self.lms_config.get('dashboard_url', '')
            return dashboard_url in page.url

        # Check for presence of indicators
        for selector in indicators:
            try:
                # Check if element exists without waiting
                exists = page.query_selector(selector) is not None
                if exists:
                    return True
            except:
                continue

        return False

    def perform_health_check(self, page: Page) -> Dict[str, Any]:
        """
        Perform a health check on the current session.

        Args:
            page: Playwright page object

        Returns:
            Dictionary with health check results
        """
        current_time = time.time()

        # Skip if we've done a health check recently
        if current_time - self.last_health_check < self.health_check_interval:
            return {"status": "skipped", "reason": "Too soon since last check"}

        self.last_health_check = current_time

        health_status = {
            "timestamp": current_time,
            "url": page.url,
            "title": page.title(),
            "is_logged_in": self.is_logged_in(page),
            "status": "unknown"
        }

        try:
            # Check page responsiveness
            page.evaluate("() => window.performance.timing.domComplete")
            health_status["responsive"] = True

            # Check if any error messages are visible on the page
            error_indicators = [
                ".error-message",
                ".alert-danger",
                "#error-container",
                "[role='alert']"
            ]

            errors_found = []
            for selector in error_indicators:
                elements = page.query_selector_all(selector)
                for element in elements:
                    text = element.text_content()
                    if text and text.strip():
                        errors_found.append(text.strip())

            health_status["errors"] = errors_found

            # Determine overall status
            if health_status["is_logged_in"] and health_status["responsive"] and not errors_found:
                health_status["status"] = "healthy"
            elif not health_status["is_logged_in"]:
                health_status["status"] = "logged_out"
            elif errors_found:
                health_status["status"] = "error"
            else:
                health_status["status"] = "degraded"

        except Exception as e:
            logger.warning(f"Error during health check: {e}")
            health_status["status"] = "error"
            health_status["error"] = str(e)
            health_status["responsive"] = False

        logger.info(f"Health check: {health_status['status']}")
        return health_status

    @staticmethod
    def needs_recovery(health_status: Dict[str, Any]) -> bool:
        """
        Determine if the session needs recovery based on health check results.

        Args:
            health_status: Health check results

        Returns:
            True if session needs recovery, False otherwise
        """
        # Session needs recovery if:
        # 1. Status is error or degraded
        # 2. Not logged in when we should be
        # 3. Page is not responsive

        if health_status["status"] in ["error", "degraded"]:
            return True

        if not health_status["is_logged_in"]:
            return True

        if health_status.get("responsive") is False:
            return True

        return False