import pytest
import subprocess
import time
import sys
import requests
from tests.config import BASE_URL, PORT, SERVER_START_TIMEOUT_S, HTTP_TIMEOUT_S, PROCESS_STOP_TIMEOUT_S
from tests.support.api_client import APIClient


@pytest.fixture(scope="function")
def sut_server():
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(PORT)],
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
            r = requests.get(f"{BASE_URL}/health", timeout=min(HTTP_TIMEOUT_S, 0.5))
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


@pytest.fixture
def api_client():
    return APIClient(base_url=BASE_URL, timeout=HTTP_TIMEOUT_S)