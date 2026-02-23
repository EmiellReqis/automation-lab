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


def _parse_float(value: str | None, default: float) -> float:
    if not value:
        return default
    try:
        return float(value)
    except ValueError:
        return default


PORT = _parse_port(os.getenv("PORT", "8000"))
BASE_URL = os.getenv("BASE_URL", f"http://127.0.0.1:{PORT}")
SERVER_START_TIMEOUT_S = _parse_float(os.getenv("SERVER_START_TIMEOUT_S"), 5.0)
PROCESS_STOP_TIMEOUT_S = _parse_float(os.getenv("PROCESS_STOP_TIMEOUT_S"), 5.0)
HTTP_TIMEOUT_S = _parse_float(os.getenv("HTTP_TIMEOUT_S"), 2.0)
