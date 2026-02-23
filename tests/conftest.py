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
    client = APIClient(base_url=BASE_URL, timeout=HTTP_TIMEOUT_S)
    process = subprocess.Popen(
        [sys.executable,
         "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(PORT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # ---- wait for server readiness ----
    poll_interval_s = 0.2
    deadline = time.time() + SERVER_START_TIMEOUT_S
    server_ready = False

    while time.time() < deadline:
        try:
            r = client.get("/health", timeout=min(HTTP_TIMEOUT_S, 0.5))
            if r.status_code == 200:
                server_ready = True
                break
        except requests.RequestException:
            # expected while server is starting
            pass
        time.sleep(poll_interval_s)

    if not server_ready:
        # cleanup before failing
        process.terminate()
        try:
            process.wait(timeout=PROCESS_STOP_TIMEOUT_S)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=PROCESS_STOP_TIMEOUT_S)

        pytest.fail("Server did not start in time")

    try:
        yield process
    finally:
        process.terminate()
        try:
            process.wait(timeout=PROCESS_STOP_TIMEOUT_S)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=PROCESS_STOP_TIMEOUT_S)
