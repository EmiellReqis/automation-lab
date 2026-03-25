import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest
import requests

from tests.api_client import APIClient
from tests.config import (
    BASE_URL,
    HTTP_TIMEOUT_S,
    PORT,
    PROCESS_STOP_TIMEOUT_S,
    SERVER_START_TIMEOUT_S,
    UNIT_BASE_URL,
)
from tests.helpers.fake_session import FakeSession


@pytest.fixture
def api_client():
    """
    Return an APIClient instance configured with the default BASE_URL and HTTP timeout.

    Useful for tests that talk to the running SUT without needing to construct the client
    in every test.
    """
    return APIClient(base_url=BASE_URL, timeout=HTTP_TIMEOUT_S)


@pytest.fixture(scope="session")
def sut_server():
    """
    Start the System Under Test (SUT) as a Uvicorn process for the whole test session.

    - Launches: `uvicorn app.main:app` on 127.0.0.1:<PORT>
    - Waits for readiness by polling GET <BASE_URL>/health until HTTP 200 or timeout.
    - Streams stdout/stderr to a timestamped log file under `.pytest-logs/sut/`.
    - Yields: BASE_URL once the server is ready.
    - Teardown: terminates the process and force-kills it if it does not stop in time.

    Raises:
        RuntimeError: if the SUT does not become ready within SERVER_START_TIMEOUT_S.
    """
    logs_dir = Path(".pytest-logs/sut")
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
        str(PORT),
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

        yield BASE_URL

    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=PROCESS_STOP_TIMEOUT_S)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()

        log_file.close()


@pytest.fixture
def make_client(unit_base_url: str):
    def _make_client(outcomes: list[Any], **client_overrides):
        """
        Build an APIClient instance backed by a FakeSession with predefined outcomes.

        This is a factory function returned by the `make_client` pytest fixture.
        It helps tests focus on scenarios by avoiding repeated boilerplate for
        FakeSession and APIClient construction.

        Args:
            outcomes: A list of outcomes (e.g., fake responses / exceptions) that the
                FakeSession will return/raise in order on subsequent requests.
            **client_overrides: Keyword overrides for APIClient construction.
                Allowed keys are:
                  - "base_url"
                  - "timeout"
                Any unknown keys will raise ValueError to prevent silent typos.

        Returns:
            tuple[APIClient, FakeSession]: A pair of (client, fake_session) so tests can
            use the client for calls and assert on the fake session behavior.

        Raises:
            ValueError: If `client_overrides` contains keys outside the allowed set.
        """
        defaults = {"base_url": unit_base_url, "timeout": HTTP_TIMEOUT_S}
        params = {**defaults, **client_overrides}
        allowed = set(defaults)
        unknown = set(client_overrides) - allowed
        if unknown:
            raise ValueError(
                f"make_client: unknown client override keys {sorted(unknown)}; "
                f"allowed keys are {sorted(allowed)}."
            )
        fake = FakeSession(outcomes)
        client = APIClient(base_url=params["base_url"], timeout=params["timeout"], session=fake)
        return client, fake

    return _make_client


@pytest.fixture
def unit_base_url() -> str:
    return UNIT_BASE_URL


@pytest.fixture
def health_url(unit_base_url: str) -> str:
    return f"{unit_base_url}/health"
