import subprocess
import sys
import time

import pytest
import requests

from tests.config import (
    BASE_URL,
    HTTP_TIMEOUT_S,
    PORT,
    PROCESS_STOP_TIMEOUT_S,
    SERVER_START_TIMEOUT_S,
)
from tests.support.api_client import APIClient


@pytest.fixture
def api_client():
    return APIClient(base_url=BASE_URL, timeout=HTTP_TIMEOUT_S)


@pytest.fixture(scope="function")
def sut_server():
    cmd = [sys.executable,
           "-m",
           "uvicorn",
           "app.main:app",
           "--host",
           "127.0.0.1",
           "--port",
           str(PORT)]
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # ---- wait for server readiness ----
    poll_interval_s = 0.2
    deadline = time.time() + SERVER_START_TIMEOUT_S
    last_err: Exception | None = None

    while time.time() < deadline:
        try:
            resp = requests.get(f"{BASE_URL}/health", timeout=HTTP_TIMEOUT_S)
            if resp.status_code == 200:
                break
        except requests.exceptions.RequestException as err:
            last_err = err
        time.sleep(poll_interval_s)
    else:
        process.terminate()
        try:
            process.wait(timeout=PROCESS_STOP_TIMEOUT_S)
        except subprocess.TimeoutExpired:
            process.kill()
        raise RuntimeError(
            f"SUT did not become ready within {SERVER_START_TIMEOUT_S}s. "
            f"Last error: {last_err!r}"
        )

    yield

    process.terminate()
    try:
        process.wait(timeout=PROCESS_STOP_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        process.kill()
