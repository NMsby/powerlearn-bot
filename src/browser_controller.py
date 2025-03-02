"""
Browser controller for PowerLearn LMS Bot.
Manages browser initialization, navigation, and interactions.
"""

import logging
from typing import Dict, Any

from playwright.sync_api import sync_playwright, Error as PlaywrightError

from src.error_handler import ErrorHandler
from src.screenshot_manager import ScreenshotManager
from src.security import SecurityManager

logger = logging.getLogger(__name__)


class BrowserController:
    """Controls browser operations for the PowerLearn LMS Bot."""

    def __init__(self, config: Dict[str, Any], security_manager: SecurityManager,
                 error_handler: ErrorHandler, screenshot_manager: ScreenshotManager):
        """
        Initialize the browser controller.

        Args:
            config: Browser and LMS configuration
            security_manager: Security manager instance
            error_handler: Error handler instance
            screenshot_manager: Screenshot manager instance
        """
        self.config = config
        self.browser_config = config.get('browser', {})
        self.lms_config = config.get('lms', {})
        self.security_manager = security_manager
        self.error_handler = error_handler
        self.screenshot_manager = screenshot_manager

        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.is_logged_in = False

    def initialize(self) -> None:
        """
        Initialize the browser.

        Raises:
            PlaywrightError: If browser initialization fails
        """
        logger.info("Initializing browser...")

        try:
            # Start Playwright
            self.playwright = sync_playwright().start()

            # Select browser type
            browser_type = self.browser_config.get('type', 'chromium')
            browser_module = getattr(self.playwright, browser_type)

            # Set up browser launch options
            launch_options = {
                'headless': self.browser_config.get('headless', True)
            }

            # Add proxy if configured
            proxy_settings = self.security_manager.get_proxy_settings()
            if proxy_settings:
                launch_options['proxy'] = proxy_settings

            # Launch browser
            self.browser = browser_module.launch(**launch_options)

            # Create a browser context
            context_options = {}

            # Set viewport size if configured
            viewport = self.browser_config.get('viewport', {})
            if viewport:
                context_options['viewport'] = {
                    'width': viewport.get('width', 1280),
                    'height': viewport.get('height', 800)
                }

            # Set user agent if configured
            user_agent = self.browser_config.get('user_agent')
            if user_agent:
                context_options['user_agent'] = user_agent

            self.context = self.browser.new_context(**context_options)

            # Set default timeout
            timeout = self.browser_config.get('timeout', 30000)
            self.context.set_default_timeout(timeout)

            # Create a new page
            self.page = self.context.new_page()

            logger.info(f"Browser initialized: {browser_type}")

        except PlaywrightError as e:
            logger.error(f"Failed to initialize browser: {e}")
            self.cleanup()
            raise

    def navigate_to(self, url: str) -> bool:
        """
        Navigate to a URL.

        Args:
            url: URL to navigate to

        Returns:
            True if navigation succeeded, False otherwise
        """
        try:
            logger.info(f"Navigating to: {url}")

            # Use error handler to retry navigation if it fails
            def do_navigate():
                self.page.goto(url)
                return True

            return self.error_handler.with_retry(do_navigate)

        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            self.screenshot_manager.take_screenshot(self.page, "error", f"Navigation failed: {url}")
            return False

    def login(self) -> bool:
        """
        Log in to the LMS.

        Returns:
            True if login succeeded, False otherwise
        """
        try:
            logger.info("Attempting to log in...")

            # Navigate to login page
            login_url = self.lms_config.get('url')
            if not self.navigate_to(login_url):
                logger.error("Failed to navigate to login page")
                return False

            # Get selectors
            selectors = self.lms_config.get('login_selectors', {})
            email_field = selectors.get('email_field')
            password_field = selectors.get('password_field')
            submit_button = selectors.get('submit_button')

            # Get credentials
            credentials = self.security_manager.get_credentials()

            # Fill login form
            logger.debug("Filling login form...")
            self.page.fill(email_field, credentials['email'])
            self.page.fill(password_field, credentials['password'])

            # Take screenshot before submitting (if enabled)
            self.screenshot_manager.take_screenshot(self.page, "login", "Before submit")

            # Submit login form
            self.page.click(submit_button)

            # Wait for navigation to complete
            self.page.wait_for_load_state('networkidle')

            # Verify login success
            login_successful = self._verify_login()

            if login_successful:
                logger.info("Login successful")
                self.is_logged_in = True
                self.screenshot_manager.take_screenshot(self.page, "login", "After successful login")
            else:
                logger.error("Login failed - could not verify successful login")
                self.screenshot_manager.take_screenshot(self.page, "error", "Login verification failed")

            return login_successful

        except Exception as e:
            logger.error(f"Login failed with error: {e}")
            self.screenshot_manager.take_screenshot(self.page, "error", f"Login error: {str(e)}")
            return False

    def _verify_login(self) -> bool:
        """
        Verify that login was successful.

        Returns:
            True if logged in, False otherwise
        """
        # Get indicators of successful login
        indicators = self.lms_config.get('logged_in_indicators', [])

        if not indicators:
            logger.warning("No logged in indicators configured, defaulting to URL check")
            # Check if we're on the dashboard URL
            dashboard_url = self.lms_config.get('dashboard_url', '')
            return dashboard_url in self.page.url

        # Check for presence of indicators
        for selector in indicators:
            try:
                # Wait for the element to be visible
                visible = self.page.wait_for_selector(selector, state='visible', timeout=5000) is not None
                if visible:
                    logger.debug(f"Found login indicator: {selector}")
                    return True
            except:
                continue

        return False

    def logout(self) -> bool:
        """
        Log out from the LMS.

        Returns:
            True if logout succeeded, False otherwise
        """
        if not self.is_logged_in:
            logger.info("Already logged out, no action needed")
            return True

        try:
            logger.info("Attempting to log out...")

            # Get selectors
            selectors = self.lms_config.get('logout_selectors', {})
            menu_button = selectors.get('menu_button')
            logout_link = selectors.get('logout_link')

            # Take screenshot before logout (if enabled)
            self.screenshot_manager.take_screenshot(self.page, "logout", "Before logout")

            # Click menu button if needed
            if menu_button:
                self.page.click(menu_button)
                # Small wait to ensure menu is fully expanded
                self.page.wait_for_timeout(500)

            # Click logout link
            self.page.click(logout_link)

            # Wait for navigation to complete
            self.page.wait_for_load_state('networkidle')

            # Verify logout success
            self.is_logged_in = self._verify_login()

            if not self.is_logged_in:
                logger.info("Logout successful")
                self.screenshot_manager.take_screenshot(self.page, "logout", "After successful logout")
                return True
            else:
                logger.error("Logout failed - still appears to be logged in")
                self.screenshot_manager.take_screenshot(self.page, "error", "Logout verification failed")
                return False

        except Exception as e:
            logger.error(f"Logout failed with error: {e}")
            self.screenshot_manager.take_screenshot(self.page, "error", f"Logout error: {str(e)}")
            return False

    def cleanup(self) -> None:
        """Close browser and clean up resources."""
        logger.info("Cleaning up browser resources...")

        try:
            if self.page:
                self.page.close()
                self.page = None

            if self.context:
                self.context.close()
                self.context = None

            if self.browser:
                self.browser.close()
                self.browser = None

            if self.playwright:
                self.playwright.stop()
                self.playwright = None

            logger.info("Browser resources cleaned up")

        except Exception as e:
            logger.error(f"Error during browser cleanup: {e}")