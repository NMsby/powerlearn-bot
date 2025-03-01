"""
Main controller for PowerLearn LMS Bot.
Orchestrates the login/logout cycle and manages all components.
"""

import logging
import signal
import time
import traceback

from src.activity_simulator import ActivitySimulator
from src.browser_controller import BrowserController
from src.config_manager import ConfigManager
from src.error_handler import ErrorHandler
from src.logger import Logger
from src.monitoring import MonitoringManager
from src.screenshot_manager import ScreenshotManager
from src.security import SecurityManager
from src.session_validator import SessionValidator


class MainController:
    """Main controller for the PowerLearn LMS Bot."""

    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize the main controller.

        Args:
            config_path: Path to the configuration file
        """
        # Initialize configuration
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.get_all()

        # Initialize logger
        self.logger_manager = Logger(self.config['logging'])
        self.logger = self.logger_manager.get_logger()

        # Set global logger
        logging.getLogger('powerlearn_bot').setLevel(
            getattr(logging, self.config['logging']['level'])
        )

        # Initialize components
        self.security_manager = SecurityManager()
        self.error_handler = ErrorHandler(self.config['session'])
        self.screenshot_manager = ScreenshotManager(self.config['screenshots'])
        self.session_validator = SessionValidator(self.config)
        self.activity_simulator = ActivitySimulator(self.config['activity'])
        self.monitoring = MonitoringManager()

        # Browser controller will be initialized during run
        self.browser_controller = None

        # Runtime variables
        self.running = False
        self.session_count = 0
        self.current_session = None

        # Set up signal handlers
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

        self.logger.info("Main controller initialized")
        self.monitoring.update_status("initializing")

    def _handle_shutdown(self, signum, frame):
        """Handle shutdown signals."""
        self.logger.info(f"Received signal {signum}, shutting down gracefully")
        self.stop()

    def start(self) -> None:
        """Start the bot."""
        self.logger.info("Starting PowerLearn LMS Bot")
        self.running = True
        self.monitoring.update_status("running")

        try:
            self._run_loop()
        except Exception as e:
            self.logger.error(f"Unhandled error in main loop: {e}")
            self.logger.error(traceback.format_exc())
            self.monitoring.update_status("error")
            self.monitoring.record_error(str(e))
            self.stop()

    def stop(self) -> None:
        """Stop the bot."""
        self.logger.info("Stopping PowerLearn LMS Bot")
        self.running = False

        # Clean up resources
        try:
            if self.browser_controller:
                self.browser_controller.cleanup()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

        self.monitoring.update_status("stopped")
        self.logger.info("Bot stopped")

    def _run_loop(self) -> None:
        """Run the main bot loop."""
        while self.running:
            try:
                # Initialize browser if needed
                if not self.browser_controller:
                    self.browser_controller = BrowserController(
                        self.config,
                        self.security_manager,
                        self.error_handler,
                        self.screenshot_manager
                    )
                    self.browser_controller.initialize()

                # Start a new session
                self._run_session()

                # Pause between sessions
                pause_time = self.config['session'].get('pause_between', 300)
                self.logger.info(f"Pausing for {pause_time} seconds before next session")
                self.monitoring.update_status("paused")

                # Implement interruptible sleep
                start_time = time.time()
                while self.running and (time.time() - start_time) < pause_time:
                    time.sleep(1)

                if self.running:
                    self.monitoring.update_status("running")

            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                self.logger.error(traceback.format_exc())
                self.monitoring.record_error(str(e))

                # Try to recover
                self._attempt_recovery()

                # Pause before retry
                time.sleep(30)

    def _run_session(self) -> None:
        """Run a single login/logout session."""
        self.session_count += 1
        self.logger.info(f"Starting session {self.session_count}")

        # Create session in monitoring
        self.current_session = self.monitoring.start_session()
        session_successful = False
        login_successful = False
        logout_successful = False

        try:
            # Attempt login
            login_successful = self.browser_controller.login()
            self.monitoring.update_session(
                self.current_session,
                login_successful=login_successful
            )

            if not login_successful:
                self.logger.error("Login failed, ending session")
                return

            # Get session duration
            session_duration = self.config['session'].get('duration', 900)  # 15 minutes default
            self.logger.info(f"Logged in successfully, session duration: {session_duration} seconds")

            # Simulate activity during the session
            if self.activity_simulator.enabled:
                activity_results = self.activity_simulator.simulate_activity(
                    self.browser_controller.page,
                    session_duration
                )
                self.monitoring.update_session(
                    self.current_session,
                    activities=activity_results.get('actions_performed', [])
                )
            else:
                # Just wait for the session duration
                self.logger.info(f"Activity simulation disabled, waiting for {session_duration} seconds")
                # Implement interruptible sleep
                start_time = time.time()
                while self.running and (time.time() - start_time) < session_duration:
                    time.sleep(1)

                    # Periodically check session health
                    if (time.time() - start_time) % 60 < 1:  # Check roughly every minute
                        health = self.session_validator.perform_health_check(self.browser_controller.page)

                        if self.session_validator.needs_recovery(health):
                            self.logger.warning(f"Session needs recovery: {health['status']}")
                            break

            # Attempt logout if still running
            if self.running:
                logout_successful = self.browser_controller.logout()
                session_successful = login_successful and logout_successful

        except Exception as e:
            self.logger.error(f"Error during session: {e}")
            self.logger.error(traceback.format_exc())
            self.monitoring.record_error(str(e), self.current_session['id'])

            # Screenshot on error
            if self.browser_controller and self.browser_controller.page:
                self.screenshot_manager.take_screenshot(
                    self.browser_controller.page,
                    "error",
                    f"Session error: {str(e)}"
                )

        finally:
            # End session in monitoring
            self.monitoring.update_session(
                self.current_session,
                logout_successful=logout_successful
            )
            self.monitoring.end_session(self.current_session, session_successful)
            self.current_session = None

            self.logger.info(f"Session {self.session_count} ended")

    def _attempt_recovery(self) -> None:
        """Attempt to recover from errors by reinitializing the browser."""
        self.logger.info("Attempting recovery...")
        self.monitoring.update_status("recovering")

        try:
            # Clean up existing browser
            if self.browser_controller:
                self.browser_controller.cleanup()
                self.browser_controller = None

            # Create and initialize a new browser
            self.browser_controller = BrowserController(
                self.config,
                self.security_manager,
                self.error_handler,
                self.screenshot_manager
            )
            self.browser_controller.initialize()

            self.logger.info("Recovery successful")
            self.monitoring.update_status("running")

        except Exception as e:
            self.logger.error(f"Recovery failed: {e}")
            self.monitoring.update_status("error")
            self.monitoring.record_error(f"Recovery attempt failed: {str(e)}")