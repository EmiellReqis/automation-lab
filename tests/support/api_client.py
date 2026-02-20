import requests


class APIClient:
    def __init__(self, base_url: str, timeout: float = 2.0):
        self.base_url = base_url
        self.timeout = timeout


    def _url(self, path: str) -> str:
        if path.lower().startswith(("http://", "https://")):
            return path
        return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"

    def get(self, path: str, **kwargs):
        kwargs.setdefault("timeout", self.timeout)
        return requests.get(self._url(path), **kwargs)