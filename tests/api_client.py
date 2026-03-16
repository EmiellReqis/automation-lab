import time

import requests

RETRYABLE_STATUSES = {502, 503, 504}


class APIClient:
    def __init__(self, base_url: str, timeout: float = 2.0):
        self.base_url = base_url
        self.timeout = timeout

    def _url(self, path: str) -> str:
        path = path.strip()
        if path.lower().startswith(("http://", "https://")):
            return path
        return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"

    def get(
        self,
        path: str,
        retries: int = 2,
        backoff_s: float = 0.2,
        retry_on_status: bool = True,
        retry_on_exceptions: bool = True,
        **kwargs,
    ):
        retries = max(0, retries)
        backoff_s = max(0.0, backoff_s)
        kwargs.setdefault("timeout", self.timeout)

        for attempt in range(retries + 1):
            try:
                resp = requests.get(self._url(path), **kwargs)
                if retry_on_status and resp.status_code in RETRYABLE_STATUSES:
                    if attempt == retries:
                        return resp
                    if backoff_s:
                        time.sleep(backoff_s)
                    continue
                return resp
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
                if not retry_on_exceptions:
                    raise
                if attempt == retries:
                    raise
                if backoff_s:
                    time.sleep(backoff_s)
                continue

        raise RuntimeError("APIClient.get: unreachable - loop exhausted without return/raise")
