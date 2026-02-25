import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

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


@pytest.fixture(scope="session")
def sut_server():
    logs_dir = Path(".pytest-logs")
    logs_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_path = logs_dir / f"sut-{ts}.log"

    log_file = open(log_path, "a", encoding="utf-8", buffering=1)
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        # str(PORT),
        "8001"
    ]
    process = subprocess.Popen(
        cmd,
        stdout=log_file,
        stderr=log_file,
    )

    # ---- wait for server readiness ----
    poll_interval_s = 0.2
    deadline = time.time() + SERVER_START_TIMEOUT_S
    last_err: Exception | None = None

    try:
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
            log_file.flush()
            raise RuntimeError(
                f"SUT did not become ready within {SERVER_START_TIMEOUT_S}s. "
                f"See logs {log_path.resolve()} "
                f"Last error: {last_err!r}"
            )

        yield

    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=PROCESS_STOP_TIMEOUT_S)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()

        log_file.close()
