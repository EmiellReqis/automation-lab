import pytest
import requests
from tests.config import BASE_URL

@pytest.mark.smoke
def test_health_endpoint(sut_server):
    r = requests.get(f"{BASE_URL}/health", timeout=1.0)

    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

@pytest.mark.integration
def test_sum_endpoint(sut_server):
    r = requests.get(f"{BASE_URL}/sum",
                     params={"a": 2, "b": 3},
                     timeout=1.0)

    assert r.status_code == 200
    assert r.json()["sum"] == 5
