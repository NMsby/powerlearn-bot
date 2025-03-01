"""
Main entry point for PowerLearn LMS Bot.
"""

import argparse
import os
import sys

from src.main_controller import MainController


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='PowerLearn LMS Bot')
    parser.add_argument(
        '--config',
        type=str,
        default='config/config.yaml',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--install-browsers',
        action='store_true',
        help='Install Playwright browsers and exit'
    )
    return parser.parse_args()


def install_browsers():
    """Install Playwright browsers."""
    print("Installing Playwright browsers...")
    import subprocess
    subprocess.run(["playwright", "install"])
    print("Browsers installed successfully")


def main():
    """Main entry point."""
    # Parse command line arguments
    args = parse_args()

    # Handle browser installation if requested
    if args.install_browsers:
        install_browsers()
        return

    # Check if config file exists
    if not os.path.exists(args.config):
        print(f"Error: Configuration file not found: {args.config}")
        sys.exit(1)

    # Create and start the main controller
    controller = MainController(args.config)
    controller.start()


if __name__ == "__main__":
    main()