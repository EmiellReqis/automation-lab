import subprocess
import time
import pytest
import requests
import sys
from tests.config import BASE_URL

def start_server():
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

def wait_for_server(timeout_s=5):
    start = time.time()
    while time.time() - start < timeout_s:
        try:
            r = requests.get(f"{BASE_URL}/health", timeout=0.5)
            if r.status_code == 200:
                return True
        except Exception:
            time.sleep(0.2)
    return False

@pytest.mark.smoke
def test_health_endpoint():
    proc = start_server()
    try:
        assert wait_for_server(), "Server did not start in time"
        r = requests.get(f"{BASE_URL}/health")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}
    finally:
        proc.terminate()
        proc.wait(timeout=5)

@pytest.mark.integration
def test_sum_endpoint():
    proc = start_server()
    try:
        assert wait_for_server(), "Server did not start in time"
        r = requests.get(f"{BASE_URL}/sum", params={"a": 2, "b": 3})
        assert r.status_code == 200
        assert r.json()["sum"] == 5
    finally:
        proc.terminate()
        proc.wait(timeout=5)