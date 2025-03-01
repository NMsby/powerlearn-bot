"""
Activity simulator for PowerLearn LMS Bot.
Simulates user activities during logged-in sessions.
"""

import logging
import random
import time
from typing import Dict, Any, Optional

from playwright.sync_api import Page

logger = logging.getLogger(__name__)


class ActivitySimulator:
    """Simulates user activities for the PowerLearn LMS Bot."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the activity simulator.

        Args:
            config: Activity configuration
        """
        self.config = config
        self.enabled = config.get('enabled', True)
        self.actions = config.get('actions', [])
        self.min_actions = config.get('min_actions_per_session', 3)
        self.max_actions = config.get('max_actions_per_session', 10)

    def simulate_activity(self, page: Page, duration: int) -> Dict[str, Any]:
        """
        Simulate user activity for the specified duration.

        Args:
            page: Playwright page object
            duration: Maximum duration in seconds

        Returns:
            Dictionary with activity results
        """
        if not self.enabled or not self.actions:
            logger.info("Activity simulation disabled or no actions configured")
            return {"status": "skipped", "reason": "Disabled"}

        logger.info(f"Starting activity simulation (max duration: {duration}s)")

        start_time = time.time()
        end_time = start_time + duration

        activity_log = {
            "start_time": start_time,
            "actions_performed": [],
            "status": "running"
        }

        # Determine number of actions to perform
        num_actions = random.randint(self.min_actions, self.max_actions)

        try:
            for i in range(num_actions):
                # Check if we've exceeded the duration
                if time.time() > end_time:
                    logger.info("Activity simulation stopped: duration exceeded")
                    activity_log["status"] = "completed"
                    activity_log["reason"] = "duration_exceeded"
                    break

                # Select and perform a random action
                action_result = self._perform_random_action(page)

                if action_result:
                    activity_log["actions_performed"].append(action_result)

            # If we completed all planned actions
            if len(activity_log["actions_performed"]) == num_actions:
                activity_log["status"] = "completed"
                activity_log["reason"] = "actions_completed"

        except Exception as e:
            logger.error(f"Error during activity simulation: {e}")
            activity_log["status"] = "error"
            activity_log["error"] = str(e)

        activity_log["end_time"] = time.time()
        activity_log["duration"] = activity_log["end_time"] - activity_log["start_time"]

        logger.info(f"Activity simulation ended: {activity_log['status']}")
        logger.debug(f"Performed {len(activity_log['actions_performed'])} actions")

        return activity_log

    def _perform_random_action(self, page: Page) -> Optional[Dict[str, Any]]:
        """
        Select and perform a random action.

        Args:
            page: Playwright page object

        Returns:
            Dictionary with action results or None if no action was performed
        """
        # Select actions based on probability
        available_actions = []

        for action in self.actions:
            probability = action.get('probability', 1.0)
            if random.random() <= probability:
                available_actions.append(action)

        if not available_actions:
            return None

        # Select a random action
        action = random.choice(available_actions)
        action_type = action.get('type')

        action_log = {
            "type": action_type,
            "timestamp": time.time()
        }

        try:
            if action_type == 'navigate':
                self._perform_navigate_action(page, action, action_log)
            elif action_type == 'scroll':
                self._perform_scroll_action(page, action, action_log)
            elif action_type == 'wait':
                self._perform_wait_action(action, action_log)
            else:
                logger.warning(f"Unknown action type: {action_type}")
                return None

            action_log["status"] = "success"
            return action_log

        except Exception as e:
            logger.error(f"Error performing action {action_type}: {e}")
            action_log["status"] = "error"
            action_log["error"] = str(e)
            return action_log

    @staticmethod
    def _perform_navigate_action(page: Page, action: Dict[str, Any], log: Dict[str, Any]) -> None:
        """
        Perform a navigation action.

        Args:
            page: Playwright page object
            action: Action configuration
            log: Action log to update
        """
        urls = action.get('urls', [])
        if not urls:
            raise ValueError("No URLs specified for navigate action")

        url = random.choice(urls)
        log["url"] = url
        logger.debug(f"Navigating to: {url}")

        page.goto(url)
        page.wait_for_load_state('networkidle')

    @staticmethod
    def _perform_scroll_action(page: Page, action: Dict[str, Any], log: Dict[str, Any]) -> None:
        """
        Perform a scroll action.

        Args:
            page: Playwright page object
            action: Action configuration
            log: Action log to update
        """
        min_distance = action.get('min_distance', 100)
        max_distance = action.get('max_distance', 800)

        distance = random.randint(min_distance, max_distance)
        log["distance"] = distance
        logger.debug(f"Scrolling: {distance}px")

        page.evaluate(f"window.scrollBy(0, {distance})")
        time.sleep(random.uniform(0.5, 2.0))

    @staticmethod
    def _perform_wait_action(action: Dict[str, Any], log: Dict[str, Any]) -> None:
        """
        Perform a wait action.

        Args:
            action: Action configuration
            log: Action log to update
        """
        min_duration = action.get('min_duration', 5)
        max_duration = action.get('max_duration', 30)

        duration = random.uniform(min_duration, max_duration)
        log["duration"] = duration
        logger.debug(f"Waiting: {duration:.2f}s")

        time.sleep(duration)