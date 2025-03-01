# PowerLearn LMS Automation Bot

Automated login script for PowerLearn Project Academy LMS. This bot automatically logs in and out at configurable intervals, simulates user activity, and provides comprehensive logging.

## Features

- **Automated Login/Logout**: Configurable intervals for session duration
- **Activity Simulation**: Mimics human-like behavior during logged-in sessions
- **Error Handling**: Robust recovery mechanisms with exponential backoff
- **Screenshot Capture**: Automatically captures screenshots on errors or key events
- **Secure Credential Management**: Keeps credentials secure with environment variables
- **Proxy Support**: Optional proxy configuration for additional security
- **Headless Browser**: Support for visible or headless mode
- **Monitoring Dashboard**: Real-time status monitoring via browser
- **Comprehensive Logging**: Detailed logs with rotation
- **Docker Support**: Easy deployment with Docker

## Prerequisites

- Python 3.8 or higher
- Git
- Docker (optional, for containerized deployment)

## Setup Instructions

### 1. Clone the Repository

``` bash
   git clone https://github.com/yourusername/powerlearn-bot.git
   cd powerlearn-bot
```

### 2. Create a virtual environment: 
``` bash
   python -m venv venv
```

### 3. Activate the virtual environment
   - Windows: 
   ``` bash 
      venv\Scripts\activate
   ```
   - Unix/MacOS: 
   ``` bash
      source venv/bin/activate
   ```

### 4. Install dependencies: 
   ``` bash 
      pip install -r requirements.txt
   ```

### 5. Install Playwright browsers:
``` bash
   python src/main.py --install-browsers
```

### 6. Copy `.env.example` to `.env` and add your credentials
``` bash 
   cp .env.example .env
```

### 7. Edit .env with your credentials and preferences:
``` bash 
   POWERLEARN_USERNAME=your_actual_username/email
   POWERLEARN_PASSWORD=your_actual_password
```

### 8. Configure settings in `config/config.yaml`
- Adjust selectors to match your LMS interface
- Configure activity simulation patterns
- Modify timing and retry settings

### 9. Running the bot: 
- Direct Execution
``` bash
   # Activate the virtual environment if not already activated
   # Then run:
   `python src/main.py`
```

- Docker Deployment
``` bash 
   # Buid and start with Docker Compose
   docker-compose up -d
   
   # View logs
   docker-compose logs -f
```

## Monitoring
The bot includes a monitoring dashboard accessible at dashboard/index.html. Open this file in a web browser to view:
- Current bot status
- Session statistics
- Login/logout success rates
- Error information
- Session history

## Configuration Options
### Browser Settings

- `browser.type`: Browser engine to use (chromium, firefox, webkit)
- `browser.headless`: Run in headless mode without visible UI
- `browser.viewport`: Screen resolution settings
- `browser.timeout`: Page operation timeout in milliseconds

### LMS Settings

- `lms.url`: Login page URL
- `lms.dashboard_url`: Dashboard URL after successful login
- `lms.login_selectors`: CSS selectors for login form elements
- `lms.logged_in_indicators`: Elements that indicate successful login
- `lms.logout_selectors`: Elements for logout operation

### Session Settings

- `session.duration`: Length of login session in seconds
- `session.pause_between`: Wait time between sessions
- `session.max_retries`: Maximum retry attempts
- `session.backoff_factor`: Exponential backoff multiplier

### Activity Simulation

- `activity.enabled`: Enable/disable activity simulation
- `activity.actions`: Configure different types of actions
- `activity.min_actions_per_session`: Minimum actions per session
- `activity.max_actions_per_session`: Maximum actions per session

## Troubleshooting

### Common Issues

1. **Login Failures**:
   - Verify your credentials in the `.env` file
   - Check if the login selectors in `config.yaml` match your LMS

2. **Browser Initialization Errors**:
   - Ensure Playwright browsers are installed
   - Try running with `--install-browsers` option

3. **Unexpected Errors**:
   - Check the logs in the `logs` directory
   - Review screenshots in the `screenshots` directory

### Logs and Debugging

- Log files are located in the `logs` directory
- Error screenshots are saved in the `screenshots` directory
- Adjust log level in `.env` file (DEBUG for more details)

## Security Considerations

- Never commit your `.env` file to version control
- Consider using a proxy for production deployments
- Regularly rotate your LMS password

## License

This project is licensed under the Creative Commons Attribution-NonCommercial-NoDerivs 4.0 International License (CC BY-NC-ND 4.0) - see the LICENSE file for details.

This means:
- You may share the material under the following terms:
  - **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made.
  - **NonCommercial** — You may not use the material for commercial purposes.
  - **NoDerivatives** — If you remix, transform, or build upon the material, you may not distribute the modified material.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.