from __future__ import annotations

import os
from typing import Any

_TRUE = {"1", "true", "t", "yes", "y", "on"}
_FALSE = {"0", "false", "f", "no", "n", "off"}


def _parse_port(value: str | None, default: int = 8000) -> int:
    if not value:
        return default
    try:
        port = int(value)
    except ValueError:
        return default

    if not (1 <= port <= 65535):
        return default

    return port


def _parse_float(value: str | None, default: float) -> float:
    if not value:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _parse_bool(value: Any, default: bool = False) -> bool:
    """
    Parse boolean-like values from env/config.

    Accepts:
      - bool -> returned as-is
      - None -> default
      - int/float -> bool(value)
      - str -> common truthy/falsey tokens (case/whitespace-insensitive)
    Unknown strings -> default.
    """
    if value is None:
        return default

    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        return bool(value)

    if isinstance(value, str):
        token = value.strip().lower()
        if token in _TRUE:
            return True
        if token in _FALSE:
            return False
        return default

    # last resort: fallback to default rather than surprising truthiness
    return default


PORT = _parse_port(os.getenv("PORT", "8000"))
BASE_URL = os.getenv("BASE_URL", f"http://127.0.0.1:{PORT}")
UNIT_BASE_URL = os.getenv("UNIT_BASE_URL", "http://example")
SERVER_START_TIMEOUT_S = _parse_float(os.getenv("SERVER_START_TIMEOUT_S"), 5.0)
PROCESS_STOP_TIMEOUT_S = _parse_float(os.getenv("PROCESS_STOP_TIMEOUT_S"), 5.0)
HTTP_TIMEOUT_S = _parse_float(os.getenv("HTTP_TIMEOUT_S"), 2.0)
PW_HEADLESS = _parse_bool(os.getenv("PW_HEADLESS"), default=True)
