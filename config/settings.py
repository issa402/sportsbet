"""
Application settings and configuration management.
Supports environment variables and configuration files.
"""

from typing import Dict, List, Optional
import os


class Settings:
    """Main application settings - simple implementation without pydantic."""

    def __init__(self):
        """Initialize settings from environment variables."""
        # Load .env file if it exists
        self._load_env_file()

        # Application
        self.app_name = os.getenv("APP_NAME", "Sports Betting Consensus System")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO")

        # Database
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./sports_betting.db")

        # API Configuration
        self.api_host = os.getenv("API_HOST", "0.0.0.0")
        self.api_port = int(os.getenv("API_PORT", "8000"))

        # Scraping Configuration
        self.request_timeout = int(os.getenv("REQUEST_TIMEOUT", "30"))
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
        self.retry_backoff_factor = float(os.getenv("RETRY_BACKOFF_FACTOR", "1.0"))
        self.rate_limit_delay = float(os.getenv("RATE_LIMIT_DELAY", "2.0"))
        self.user_agent = os.getenv(
            "USER_AGENT",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )

        # Claude API
        self.claude_api_key = os.getenv("CLAUDE_API_KEY")
        self.claude_model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")

        # Scheduler
        self.scheduler_enabled = os.getenv("SCHEDULER_ENABLED", "true").lower() == "true"
        self.scheduler_interval_hours = int(os.getenv("SCHEDULER_INTERVAL_HOURS", "24"))

        # Sources Configuration
        sources_str = os.getenv("ENABLED_SOURCES", "espn,bleacher_report")
        self.enabled_sources = [s.strip() for s in sources_str.split(",")]

    def _load_env_file(self):
        """Load environment variables from .env file if it exists."""
        env_file = ".env"
        if os.path.exists(env_file):
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key.strip()] = value.strip()
            except Exception:
                pass  # Silently ignore errors reading .env


# Global settings instance
settings = Settings()

