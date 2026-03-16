import sys
import types

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


@pytest.mark.unit
def test_api_client_get_retries_on_503_then_returns_200(monkeypatch):
    calls = []
    statuses = []

    def mock_get(url, **kwargs):
        calls.append((url, kwargs))

        status = 503 if len(calls) == 1 else 200
        statuses.append(status)

        class FakeResponse:
            pass

        resp = FakeResponse()
        resp.status_code = status
        return resp

    client = APIClient(base_url="http://example", timeout=HTTP_TIMEOUT_S)
    monkeypatch.setattr(requests, "get", mock_get)

    res = client.get("/health", retries=1, backoff_s=0)

    assert len(calls) == 2
    assert calls[0][0] == "http://example/health"
    assert calls[0][1]["timeout"] == HTTP_TIMEOUT_S
    assert calls[1][1]["timeout"] == HTTP_TIMEOUT_S
    assert res.status_code == 200
    assert statuses == [503, 200]


@pytest.mark.unit
def test_api_client_get_returns_503_after_retries_exhausted(monkeypatch):
    calls = []
    statuses = []

    def mock_get(url, **kwargs):
        calls.append((url, kwargs))

        status = 503
        statuses.append(status)

        class FakeResponse:
            pass

        resp = FakeResponse()
        resp.status_code = status
        return resp

    client = APIClient(base_url="http://example", timeout=HTTP_TIMEOUT_S)
    monkeypatch.setattr(requests, "get", mock_get)

    res = client.get("/health", retries=1, backoff_s=0)

    assert len(calls) == 2
    assert calls[0][0] == "http://example/health"
    assert calls[0][1]["timeout"] == HTTP_TIMEOUT_S
    assert calls[1][1]["timeout"] == HTTP_TIMEOUT_S
    assert res.status_code == 503
    assert statuses == [503, 503]


@pytest.mark.unit
def test_retry_on_status_false(monkeypatch):
    calls = []

    def mock_get(url, **kwargs):
        calls.append((url, kwargs))

        resp = types.SimpleNamespace(status_code=503)
        return resp

    client = APIClient(base_url="http://example", timeout=HTTP_TIMEOUT_S)
    monkeypatch.setattr(requests, "get", mock_get)

    res = client.get("/health", retries=1, backoff_s=0, retry_on_status=False)

    assert len(calls) == 1
    assert calls[0][0] == "http://example/health"
    assert res.status_code == 503


@pytest.mark.unit
def test_no_sleep_when_backoff_s_is_zero(monkeypatch):
    calls = []
    sleep_calls = []

    def fake_sleep(seconds):
        sleep_calls.append(seconds)

    def mock_get(url, **kwargs):
        calls.append((url, kwargs))

        status = 503 if len(calls) == 1 else 200

        resp = types.SimpleNamespace(status_code=status)
        return resp

    client = APIClient(base_url="http://example", timeout=HTTP_TIMEOUT_S)
    monkeypatch.setattr(requests, "get", mock_get)
    api_module = sys.modules[APIClient.__module__]
    monkeypatch.setattr(api_module.time, "sleep", fake_sleep)

    res = client.get("/health", retries=1, backoff_s=0)

    assert len(calls) == 2
    assert calls[0][0] == "http://example/health"
    assert calls[0][1]["timeout"] == HTTP_TIMEOUT_S
    assert calls[1][1]["timeout"] == HTTP_TIMEOUT_S
    assert res.status_code == 200
    assert sleep_calls == []
