"""
HTTP client with rate limiting, retries, and error handling.
Provides a robust way to fetch web content with proper backoff strategies.
"""

import time
import random
from typing import Optional, Dict
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from core.logger import logger
from config.settings import settings


class RateLimitedHTTPClient:
    """HTTP client with rate limiting and retry logic."""
    
    def __init__(
        self,
        timeout: int = settings.request_timeout,
        max_retries: int = settings.max_retries,
        backoff_factor: float = settings.retry_backoff_factor,
        rate_limit_delay: float = settings.rate_limit_delay,
    ):
        """
        Initialize the HTTP client.
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
            backoff_factor: Backoff factor for retries
            rate_limit_delay: Delay between requests in seconds
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry strategy."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "HEAD"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set user agent
        session.headers.update({
            'User-Agent': settings.user_agent
        })
        
        return session
    
    def _apply_rate_limit(self):
        """Apply rate limiting between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - elapsed
            # Add random jitter to avoid thundering herd
            sleep_time += random.uniform(0, 0.5)
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
            time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Optional[requests.Response]:
        """
        Make a GET request with rate limiting and error handling.
        
        Args:
            url: URL to fetch
            headers: Additional headers
            **kwargs: Additional arguments to pass to requests.get
            
        Returns:
            Response object or None if request failed
        """
        self._apply_rate_limit()
        
        try:
            logger.debug(f"Fetching: {url}")
            response = self.session.get(
                url,
                timeout=self.timeout,
                headers=headers,
                **kwargs
            )
            response.raise_for_status()
            logger.debug(f"Successfully fetched: {url} (status: {response.status_code})")
            return response
        
        except requests.exceptions.Timeout:
            logger.error(f"Timeout fetching {url}")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error fetching {url}")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error fetching {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {e}")
            return None
    
    def close(self):
        """Close the session."""
        self.session.close()
        logger.debug("HTTP client session closed")

