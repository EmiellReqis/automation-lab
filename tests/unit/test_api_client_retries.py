import pytest
import requests

from tests.api_client import APIClient
from tests.config import HTTP_TIMEOUT_S


@pytest.mark.unit
def test_api_client_get_retries_on_timeout(monkeypatch):
    calls = []

    def mock_get(url, **kwargs):
        calls.append((url, kwargs))

        if len(calls) == 1:
            raise requests.exceptions.Timeout("simulated timeout")

        class FakeResponse:
            status_code = 200

        return FakeResponse()

    client = APIClient(base_url="http://example", timeout=HTTP_TIMEOUT_S)
    monkeypatch.setattr(requests, "get", mock_get)
    res = client.get("/health", retries=1, backoff_s=0)

    assert len(calls) == 2
    assert calls[0][0] == "http://example/health"
    assert calls[0][1]["timeout"] == HTTP_TIMEOUT_S
    assert calls[1][1]["timeout"] == HTTP_TIMEOUT_S
    assert res.status_code == 200


@pytest.mark.unit
def test_api_client_get_raises_after_retries_exhausted(monkeypatch):
    calls = []

    def mock_get(url, **kwargs):
        calls.append((url, kwargs))
        raise requests.exceptions.Timeout("simulated timeout")

    client = APIClient(base_url="http://example", timeout=HTTP_TIMEOUT_S)
    monkeypatch.setattr(requests, "get", mock_get)

    with pytest.raises(requests.exceptions.Timeout) as excinfo:
        client.get("/health", retries=1, backoff_s=0)

    assert len(calls) == 2
    assert calls[0][0] == "http://example/health"
    assert calls[0][1]["timeout"] == HTTP_TIMEOUT_S
    assert calls[1][1]["timeout"] == HTTP_TIMEOUT_S
    assert "simulated timeout" in str(excinfo.value)
