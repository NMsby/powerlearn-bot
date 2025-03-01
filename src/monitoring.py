"""
Monitoring module for PowerLearn LMS Bot.
Tracks session statistics and updates the status dashboard.
"""

import json
import logging
import os
import time
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class MonitoringManager:
    """Manages monitoring and status dashboard for the PowerLearn LMS Bot."""

    def __init__(self, dashboard_path: str = "dashboard/index.html"):
        """
        Initialize the monitoring manager.

        Args:
            dashboard_path: Path to the dashboard HTML file
        """
        self.dashboard_path = dashboard_path
        self.stats_file = "dashboard/stats.json"
        self.stats = {
            "started_at": time.time(),
            "last_updated": time.time(),
            "total_sessions": 0,
            "successful_logins": 0,
            "failed_logins": 0,
            "successful_logouts": 0,
            "failed_logouts": 0,
            "errors": 0,
            "status": "initializing",
            "current_session": None,
            "last_10_sessions": []
        }

        # Create dashboard directory if it doesn't exist
        os.makedirs(os.path.dirname(dashboard_path), exist_ok=True)

        # Initialize dashboard files
        self._init_dashboard()
        self._save_stats()

    def _init_dashboard(self) -> None:
        """Initialize the dashboard HTML file if it doesn't exist."""
        if os.path.exists(self.dashboard_path):
            return

        with open(self.dashboard_path, 'w') as f:
            f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PowerLearn Bot Status</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            color: #333;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }
        .status-card {
            background-color: #f9f9f9;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .status-indicator {
            display: inline-block;
            width: 15px;
            height: 15px;
            border-radius: 50%;
            margin-right: 10px;
        }
        .status-running { background-color: #2ecc71; }
        .status-error { background-color: #e74c3c; }
        .status-paused { background-color: #f39c12; }
        .status-initializing { background-color: #3498db; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .stat-box {
            background-color: #fff;
            border-radius: 5px;
            padding: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
        }
        .stat-label {
            color: #7f8c8d;
            font-size: 14px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        .success { color: #2ecc71; }
        .error { color: #e74c3c; }
        .refresh-time {
            text-align: right;
            color: #7f8c8d;
            font-size: 12px;
            margin-top: 20px;
        }
        .auto-refresh {
            margin-top: 20px;
            text-align: center;
        }
    </style>
</head>
<body>
    <h1>PowerLearn Bot Status Dashboard</h1>

    <div class="status-card">
        <h2>
            <span id="status-indicator" class="status-indicator"></span>
            Current Status: <span id="current-status">Loading...</span>
        </h2>
        <p>
            Running since: <span id="running-since">Loading...</span><br>
            <span id="current-session-info">No active session</span>
        </p>
    </div>

    <h2>Statistics</h2>
    <div class="stats-grid">
        <div class="stat-box">
            <div class="stat-value" id="total-sessions">0</div>
            <div class="stat-label">Total Sessions</div>
        </div>
        <div class="stat-box">
            <div class="stat-value" id="successful-logins">0</div>
            <div class="stat-label">Successful Logins</div>
        </div>
        <div class="stat-box">
            <div class="stat-value" id="failed-logins">0</div>
            <div class="stat-label">Failed Logins</div>
        </div>
        <div class="stat-box">
            <div class="stat-value" id="successful-logouts">0</div>
            <div class="stat-label">Successful Logouts</div>
        </div>
        <div class="stat-box">
            <div class="stat-value" id="failed-logouts">0</div>
            <div class="stat-label">Failed Logouts</div>
        </div>
        <div class="stat-box">
            <div class="stat-value" id="errors">0</div>
            <div class="stat-label">Errors</div>
        </div>
    </div>

    <h2>Session History</h2>
    <table>
        <thead>
            <tr>
                <th>Start Time</th>
                <th>Duration</th>
                <th>Login Status</th>
                <th>Logout Status</th>
                <th>Activities</th>
                <th>Errors</th>
            </tr>
        </thead>
        <tbody id="session-history">
            <tr>
                <td colspan="6" style="text-align: center;">No sessions yet</td>
            </tr>
        </tbody>
    </table>

    <div class="auto-refresh">
        <label>
            <input type="checkbox" id="auto-refresh" checked> 
            Auto refresh every 5 seconds
        </label>
    </div>

    <div class="refresh-time">
        Last updated: <span id="last-updated">Never</span>
    </div>

    <script>
        function formatDateTime(timestamp) {
            return new Date(timestamp * 1000).toLocaleString();
        }

        function formatDuration(seconds) {
            if (seconds < 60) return Math.round(seconds) + " seconds";
            if (seconds < 3600) return Math.round(seconds / 60) + " minutes";
            return (seconds / 3600).toFixed(1) + " hours";
        }

        function updateDashboard() {
            fetch('stats.json?' + new Date().getTime())
                .then(response => response.json())
                .then(data => {
                    // Update status
                    document.getElementById('current-status').textContent = data.status;
                    document.getElementById('status-indicator').className = 
                        'status-indicator status-' + data.status.toLowerCase();

                    // Update running since
                    document.getElementById('running-since').textContent = 
                        formatDateTime(data.started_at);

                    // Update current session
                    if (data.current_session) {
                        document.getElementById('current-session-info').textContent = 
                            `Current session started at ${formatDateTime(data.current_session.start_time)}`;
                    } else {
                        document.getElementById('current-session-info').textContent = 
                            'No active session';
                    }

                    // Update stats
                    document.getElementById('total-sessions').textContent = data.total_sessions;
                    document.getElementById('successful-logins').textContent = data.successful_logins;
                    document.getElementById('failed-logins').textContent = data.failed_logins;
                    document.getElementById('successful-logouts').textContent = data.successful_logouts;
                    document.getElementById('failed-logouts').textContent = data.failed_logouts;
                    document.getElementById('errors').textContent = data.errors;

                    // Update session history
                    const sessionHistoryTable = document.getElementById('session-history');
                    if (data.last_10_sessions && data.last_10_sessions.length > 0) {
                        sessionHistoryTable.innerHTML = '';
                        data.last_10_sessions.forEach(session => {
                            const row = document.createElement('tr');

                            // Start Time
                            const startTimeCell = document.createElement('td');
                            startTimeCell.textContent = formatDateTime(session.start_time);
                            row.appendChild(startTimeCell);

                            // Duration
                            const durationCell = document.createElement('td');
                            if (session.end_time) {
                                durationCell.textContent = formatDuration(session.end_time - session.start_time);
                            } else {
                                durationCell.textContent = 'In progress';
                            }
                            row.appendChild(durationCell);

                            // Login Status
                            const loginStatusCell = document.createElement('td');
                            loginStatusCell.textContent = session.login_successful ? 'Success' : 'Failed';
                            loginStatusCell.className = session.login_successful ? 'success' : 'error';
                            row.appendChild(loginStatusCell);

                            // Logout Status
                            const logoutStatusCell = document.createElement('td');
                            if (session.end_time) {
                                logoutStatusCell.textContent = session.logout_successful ? 'Success' : 'Failed';
                                logoutStatusCell.className = session.logout_successful ? 'success' : 'error';
                            } else {
                                logoutStatusCell.textContent = 'Pending';
                            }
                            row.appendChild(logoutStatusCell);

                            // Activities
                            const activitiesCell = document.createElement('td');
                            if (session.activities) {
                                activitiesCell.textContent = session.activities.length;
                            } else {
                                activitiesCell.textContent = '0';
                            }
                            row.appendChild(activitiesCell);

                            // Errors
                            const errorsCell = document.createElement('td');
                            if (session.errors && session.errors.length > 0) {
                                errorsCell.textContent = session.errors.length;
                                errorsCell.className = 'error';
                            } else {
                                errorsCell.textContent = '0';
                            }
                            row.appendChild(errorsCell);

                            sessionHistoryTable.appendChild(row);
                        });
                    } else {
                        sessionHistoryTable.innerHTML = '<tr><td colspan="6" style="text-align: center;">No sessions yet</td></tr>';
                    }

                    // Update last updated time
                    document.getElementById('last-updated').textContent = 
                        formatDateTime(data.last_updated);
                })
                .catch(error => {
                    console.error('Error fetching stats:', error);
                });
        }

        // Initial update
        updateDashboard();

        // Auto refresh
        let refreshInterval;

        function startAutoRefresh() {
            refreshInterval = setInterval(updateDashboard, 5000);
        }

        function stopAutoRefresh() {
            clearInterval(refreshInterval);
        }

        document.getElementById('auto-refresh').addEventListener('change', function() {
            if (this.checked) {
                startAutoRefresh();
            } else {
                stopAutoRefresh();
            }
        });

        // Start auto refresh by default
        startAutoRefresh();
    </script>
</body>
</html>""")
        logger.info(f"Created dashboard HTML at {self.dashboard_path}")

    def _save_stats(self) -> None:
        """Save the current stats to the JSON file."""
        with open(self.stats_file, 'w') as f:
            json.dump(self.stats, f)

    def update_status(self, status: str) -> None:
        """
        Update the bot status.

        Args:
            status: New status (running, error, paused, initializing)
        """
        self.stats["status"] = status
        self.stats["last_updated"] = time.time()
        self._save_stats()
        logger.info(f"Bot status updated: {status}")

    def start_session(self) -> Dict[str, Any]:
        """
        Start a new session.

        Returns:
            Session object
        """
        session = {
            "id": self.stats["total_sessions"] + 1,
            "start_time": time.time(),
            "login_successful": False,
            "logout_successful": False,
            "end_time": None,
            "activities": [],
            "errors": []
        }

        self.stats["total_sessions"] += 1
        self.stats["current_session"] = session
        self.stats["last_updated"] = time.time()
        self._save_stats()

        logger.info(f"Started session {session['id']}")
        return session

    def update_session(self, session: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Update the current session.

        Args:
            session: Session to update
            **kwargs: Fields to update

        Returns:
            Updated session
        """
        for key, value in kwargs.items():
            session[key] = value

        self.stats["current_session"] = session
        self.stats["last_updated"] = time.time()
        self._save_stats()

        return session

    def end_session(self, session: Dict[str, Any], success: bool = True) -> None:
        """
        End the current session.

        Args:
            session: Session to end
            success: Whether the session was successful
        """
        session["end_time"] = time.time()

        if session["login_successful"]:
            self.stats["successful_logins"] += 1
        else:
            self.stats["failed_logins"] += 1

        if session["logout_successful"]:
            self.stats["successful_logouts"] += 1
        else:
            self.stats["failed_logouts"] += 1

        # Add to session history (keep last 10)
        self.stats["last_10_sessions"].insert(0, session)
        self.stats["last_10_sessions"] = self.stats["last_10_sessions"][:10]

        # Clear current session
        self.stats["current_session"] = None
        self.stats["last_updated"] = time.time()
        self._save_stats()

        logger.info(f"Ended session {session['id']}")

    def record_error(self, error: str, session_id: Optional[int] = None) -> None:
        """
        Record an error.

        Args:
            error: Error message
            session_id: Session ID to associate with the error
        """
        error_entry = {
            "timestamp": time.time(),
            "message": error,
            "session_id": session_id
        }

        self.stats["errors"] += 1

        # Add to current session if it exists
        if self.stats["current_session"]:
            if "errors" not in self.stats["current_session"]:
                self.stats["current_session"]["errors"] = []
            self.stats["current_session"]["errors"].append(error_entry)

        self.stats["last_updated"] = time.time()
        self._save_stats()

        logger.error(f"Recorded error: {error}")