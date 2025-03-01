# PowerLearn LMS Automation Bot

Automated login script for PowerLearn Project Academy LMS. This bot automatically logs in and out at configurable intervals, simulates user activity, and provides comprehensive logging.

## Features
- Automated login/logout at configurable intervals
- User activity simulation
- Error handling with automatic recovery
- Screenshot capture for debugging
- Secure credential management
- Proxy support
- Headless browser support
- Monitoring dashboard

## Setup Instructions
1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and add your credentials
6. Configure settings in `config/config.yaml`
7. Run the bot: `python src/main.py`