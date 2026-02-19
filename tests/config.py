import os

def _parse_port(value: str | None, default: int = 8000) -> int:
    if not value:
        return default
    try:
        port = int(value)
    except ValueError:
        return default

    if not (1<=port<=65535):
        return default

    return port

PORT = _parse_port(os.getenv("PORT", 8000))
BASE_URL = os.getenv("BASE_URL", f"http://127.0.0.1:{PORT}")