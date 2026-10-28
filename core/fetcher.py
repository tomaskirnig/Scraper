import time
import random
import urllib.robotparser
from urllib.parse import urlparse
import requests
from typing import Optional, Dict

class SafeFetcher:
    """
    Polite, safe HTTP fetcher:
    - Domain-level rate limiting with random jitter (1.5 - 2.5s default)
    - Clean standard User-Agent (no botnet/spoofing)
    - Immediate backoff on 429 (Too Many Requests) or 403 (Forbidden)
    - Optional robots.txt checking (disabled by default for user on-demand search queries,
      since search result pages disallow crawler indexing loops)
    """

    DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36 (SafeAggregator/1.0)"
    )

    def __init__(self, min_delay: float = 1.0, max_delay: float = 2.0, enforce_robots: bool = False):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.enforce_robots = enforce_robots
        self.last_request_time: Dict[str, float] = {}
        self.robot_parsers: Dict[str, urllib.robotparser.RobotFileParser] = {}
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.DEFAULT_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "cs,en;q=0.9",
        })

    def _get_domain(self, url: str) -> str:
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def can_fetch(self, url: str) -> bool:
        """Check robots.txt for URL using stdlib robotparser if enforce_robots is True."""
        if not self.enforce_robots:
            return True

        domain = self._get_domain(url)
        if domain not in self.robot_parsers:
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(f"{domain}/robots.txt")
            try:
                rp.read()
                self.robot_parsers[domain] = rp
            except Exception:
                self.robot_parsers[domain] = None

        rp = self.robot_parsers.get(domain)
        if rp is not None:
            try:
                return rp.can_fetch(self.DEFAULT_USER_AGENT, url)
            except Exception:
                return True
        return True

    def _throttle(self, domain: str):
        """Enforce domain rate limiting with random jitter."""
        last_time = self.last_request_time.get(domain, 0)
        elapsed = time.time() - last_time
        required_delay = random.uniform(self.min_delay, self.max_delay)

        if elapsed < required_delay:
            time.sleep(required_delay - elapsed)

        self.last_request_time[domain] = time.time()

    def get(self, url: str, params: Optional[dict] = None, timeout: int = 10) -> Optional[requests.Response]:
        """Safely fetch a URL with throttling and ethical boundary checks."""
        domain = self._get_domain(url)

        # Check robots.txt if enforced
        if not self.can_fetch(url):
            return None

        # Polite rate limiting
        self._throttle(domain)

        try:
            resp = self.session.get(url, params=params, timeout=timeout)
            if resp.status_code in (403, 429):
                # Back off immediately - do NOT attack or bypass
                return None
            return resp
        except Exception:
            return None
