from typing import Any

import pytest
import requests

from tests.config import HTTP_TIMEOUT_S
from tests.helpers.fake_session import FakeResponse

OMIT = object()


def _assert_calls(
    calls: list[tuple[str, dict[str, Any]]],
    expected_url: str,
    expected_timeout: float,
    expected_count: int,
) -> None:
    assert len(calls) == expected_count
    for url, kwargs in calls:
        assert url == expected_url
        assert "timeout" in kwargs
        assert kwargs["timeout"] == expected_timeout


@pytest.mark.unit
def test_api_client_get_retries_on_timeout(make_client, health_url):

    outcomes = [requests.exceptions.Timeout("simulated timeout"), FakeResponse(200)]
    client, fake = make_client(outcomes)
    res = client.get("/health", retries=1, backoff_s=0)

    _assert_calls(
        calls=fake.calls,
        expected_url=health_url,
        expected_timeout=HTTP_TIMEOUT_S,
        expected_count=2,
    )
    assert res.status_code == 200


@pytest.mark.unit
def test_api_client_get_raises_after_retries_exhausted(make_client, health_url):

    outcomes = [
        requests.exceptions.Timeout("simulated timeout"),
        requests.exceptions.Timeout("simulated timeout"),
    ]
    client, fake = make_client(outcomes)

    with pytest.raises(requests.exceptions.Timeout) as excinfo:
        client.get("/health", retries=1, backoff_s=0)

    _assert_calls(
        calls=fake.calls,
        expected_url=health_url,
        expected_timeout=HTTP_TIMEOUT_S,
        expected_count=2,
    )
    assert "simulated timeout" in str(excinfo.value)


@pytest.mark.unit
@pytest.mark.parametrize(
    "outcomes, retries, retry_on_status_arg, expected_count, expected_status",
    [
        pytest.param(
            [FakeResponse(503), FakeResponse(200)],
            1,
            OMIT,
            2,
            200,
            id="503_then_200_retries_once",
        ),
        pytest.param(
            [FakeResponse(503), FakeResponse(503)],
            1,
            OMIT,
            2,
            503,
            id="503_exhausted_returns_503",
        ),
        pytest.param(
            [FakeResponse(503)],
            2,
            False,
            1,
            503,
            id="retry_on_status_disabled_no_retry",
        ),
    ],
)
def test_api_client_get_status_retry_policy(
    make_client, health_url, outcomes, retries, retry_on_status_arg, expected_count, expected_status
):
    client, fake = make_client(outcomes)
    if retry_on_status_arg is OMIT:
        res = client.get("/health", retries=retries, backoff_s=0)
    else:
        res = client.get(
            "/health", retries=retries, backoff_s=0, retry_on_status=retry_on_status_arg
        )

    _assert_calls(
        calls=fake.calls,
        expected_url=health_url,
        expected_timeout=HTTP_TIMEOUT_S,
        expected_count=expected_count,
    )
    assert res.status_code == expected_status


@pytest.mark.unit
def test_no_sleep_when_backoff_s_is_zero(monkeypatch, make_client, health_url):
    sleep_calls = []

    def fake_sleep(seconds):
        sleep_calls.append(seconds)

    monkeypatch.setattr("tests.api_client.time.sleep", fake_sleep)
    outcomes = [FakeResponse(503), FakeResponse(200)]
    client, fake = make_client(outcomes)

    res = client.get("/health", retries=1, backoff_s=0)

    _assert_calls(
        calls=fake.calls,
        expected_url=health_url,
        expected_timeout=HTTP_TIMEOUT_S,
        expected_count=2,
    )
    assert res.status_code == 200
    assert sleep_calls == []


@pytest.mark.unit
def test_retry_on_exceptions_false_does_not_retry_and_raises_timeout(make_client, health_url):

    outcomes = [requests.exceptions.Timeout("simulated timeout")]
    client, fake = make_client(outcomes)

    with pytest.raises(requests.exceptions.Timeout) as excinfo:
        client.get("/health", retries=1, backoff_s=0, retry_on_exceptions=False)

    _assert_calls(
        calls=fake.calls,
        expected_url=health_url,
        expected_timeout=HTTP_TIMEOUT_S,
        expected_count=1,
    )
    assert "simulated timeout" in str(excinfo.value)


@pytest.mark.unit
def test_retry_on_exceptions_true_retries_and_raises_timeout_after_budget(make_client, health_url):

    outcomes = [
        requests.exceptions.Timeout("simulated timeout"),
        requests.exceptions.Timeout("simulated timeout"),
        requests.exceptions.Timeout("simulated timeout"),
    ]
    client, fake = make_client(outcomes)

    with pytest.raises(requests.exceptions.Timeout) as excinfo:
        client.get("/health", retries=2, backoff_s=0, retry_on_exceptions=True)

    _assert_calls(
        calls=fake.calls,
        expected_url=health_url,
        expected_timeout=HTTP_TIMEOUT_S,
        expected_count=3,
    )
    assert "simulated timeout" in str(excinfo.value)
