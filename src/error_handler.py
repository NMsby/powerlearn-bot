"""
Error handler for PowerLearn LMS Bot.
Manages error detection, recovery, and backoff strategies.
"""

import logging
import random
import time
from typing import Dict, Any, Callable, TypeVar

logger = logging.getLogger(__name__)

# Define a generic type for functions
T = TypeVar('T')


class ErrorHandler:
    """Handles errors and recovery strategies for the PowerLearn LMS Bot."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the error handler.

        Args:
            config: Session configuration dictionary containing retry settings
        """
        self.max_retries = config.get('max_retries', 3)
        self.backoff_factor = config.get('backoff_factor', 2)
        self.jitter = config.get('jitter', 0.1)  # Random jitter factor

    def with_retry(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """
        Execute a function with retry logic.

        Args:
            func: Function to execute
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function

        Returns:
            Result of the function

        Raises:
            Exception: If all retries fail
        """
        retry_count = 0
        last_exception = None

        while retry_count <= self.max_retries:
            try:
                if retry_count > 0:
                    logger.info(f"Retry attempt {retry_count} of {self.max_retries}")

                return func(*args, **kwargs)

            except Exception as e:
                last_exception = e
                retry_count += 1

                if retry_count > self.max_retries:
                    logger.error(f"Max retries ({self.max_retries}) exceeded. Last error: {e}")
                    break

                # Calculate backoff time with jitter
                backoff_time = self._calculate_backoff_time(retry_count)
                logger.warning(f"Error occurred: {e}. Retrying in {backoff_time:.2f} seconds.")

                # Sleep before retry
                time.sleep(backoff_time)

        # If we get here, all retries failed
        raise last_exception if last_exception else RuntimeError("Function failed with unknown error")

    def _calculate_backoff_time(self, retry_count: int) -> float:
        """
        Calculate exponential backoff time with jitter.

        Args:
            retry_count: Current retry attempt number

        Returns:
            Backoff time in seconds
        """
        # Base backoff time: base * (factor ^ retry_count)
        base_backoff = (self.backoff_factor ** retry_count)

        # Add jitter: random value between -jitter*base and +jitter*base
        jitter_amount = random.uniform(-self.jitter, self.jitter) * base_backoff

        return base_backoff + jitter_amount

    @staticmethod
    def is_recoverable_error(error: Exception) -> bool:
        """
        Check if an error is recoverable.

        Args:
            error: Exception to check

        Returns:
            True if the error is recoverable, False otherwise
        """
        # Network errors are usually recoverable
        if "timeout" in str(error).lower() or "network" in str(error).lower():
            return True

        # Page navigation errors might be recoverable
        if "navigation" in str(error).lower():
            return True

        # Some specific errors might not be recoverable
        non_recoverable = [
            "authentication failed",
            "invalid credentials",
            "account locked",
            "captcha"
        ]

        error_str = str(error).lower()
        for term in non_recoverable:
            if term in error_str:
                return False

        # Default to assuming it's recoverable
        return True