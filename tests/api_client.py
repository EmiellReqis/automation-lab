import time

import requests


class APIClient:
    def __init__(self, base_url: str, timeout: float = 2.0):
        self.base_url = base_url
        self.timeout = timeout

    def _url(self, path: str) -> str:
        path = path.strip()
        if path.lower().startswith(("http://", "https://")):
            return path
        return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"

    def get(self, path: str, retries: int = 2, backoff_s: float = 0.2, **kwargs):
        retries = max(0, retries)
        kwargs.setdefault("timeout", self.timeout)

        for attempt in range(retries + 1):
            try:
                return requests.get(self._url(path), **kwargs)
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
                if attempt == retries:
                    raise
                time.sleep(backoff_s)
