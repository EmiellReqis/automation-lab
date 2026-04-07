from typing import Any

import pytest
import requests

from tests.config import HTTP_TIMEOUT_S
from tests.helpers.fake_session import FakeResponse, RequestCall

OMIT = object()


def _assert_calls(
    calls: list[RequestCall],
    expected_url: str,
    expected_timeout: float,
    expected_count: int,
    expected_kwargs: dict[str, Any] | None = None,
    expected_method: str = "GET",
) -> None:
    assert len(calls) == expected_count, (
        f"call count mismatch: expected {expected_count}, got {len(calls)}; calls={calls}"
    )
    for idx, call in enumerate(calls):
        assert expected_method == call.method, (
            f"call[{idx}] method mismatch: expected {expected_method}, got {call.method}"
        )
        assert call.url == expected_url, (
            f"call[{idx}] url mismatch: expected {expected_url}, got {call.url}"
        )
        assert "timeout" in call.kwargs, (
            f"call[{idx}] missing expected kwarg 'timeout'; "
            f"available keys: {sorted(call.kwargs.keys())}"
        )
        actual_timeout = call.kwargs["timeout"]
        assert actual_timeout == expected_timeout, (
            f"call[{idx}] timeout mismatch: expected {expected_timeout}, got {actual_timeout}"
        )
        if expected_kwargs is not None:
            for key, value in expected_kwargs.items():
                assert key in call.kwargs, (
                    f"call[{idx}] missing expected kwarg '{key}'; "
                    f"available keys: {sorted(call.kwargs.keys())}"
                )
                actual_result = call.kwargs[key]
                assert actual_result == value, (
                    f"call[{idx}] {key} mismatch: expected {value}, got {actual_result}"
                )


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
@pytest.mark.parametrize(
    "outcomes, retries, retry_on_exceptions_arg, expected_count, expected_status, expected_exc",
    [
        pytest.param(
            [requests.exceptions.Timeout("simulated timeout"), FakeResponse(200)],
            1,
            OMIT,
            2,
            200,
            None,
            id="timeout_then_200_retries_once",
        ),
        pytest.param(
            [
                requests.exceptions.Timeout("simulated timeout"),
                requests.exceptions.Timeout("simulated timeout"),
            ],
            1,
            OMIT,
            2,
            None,
            requests.exceptions.Timeout,
            id="timeout_exhausted_raises",
        ),
        pytest.param(
            [requests.exceptions.Timeout("simulated timeout")],
            1,
            False,
            1,
            None,
            requests.exceptions.Timeout,
            id="retry_on_exceptions_disabled_raises_no_retry",
        ),
        pytest.param(
            [
                requests.exceptions.Timeout("simulated timeout"),
                requests.exceptions.Timeout("simulated timeout"),
                requests.exceptions.Timeout("simulated timeout"),
            ],
            2,
            True,
            3,
            None,
            requests.exceptions.Timeout,
            id="timeout_retries_exhausted_raises_after_budget",
        ),
    ],
)
def test_api_client_get_exceptions_retry_policy(
    make_client,
    health_url,
    outcomes,
    retries,
    retry_on_exceptions_arg,
    expected_count,
    expected_status,
    expected_exc,
):

    client, fake = make_client(outcomes)
    call_kwargs = {"retries": retries, "backoff_s": 0}
    if retry_on_exceptions_arg is not OMIT:
        call_kwargs["retry_on_exceptions"] = retry_on_exceptions_arg

    if expected_exc is not None:
        with pytest.raises(expected_exc) as excinfo:
            client.get("/health", **call_kwargs)
    else:
        res = client.get("/health", **call_kwargs)

    _assert_calls(
        calls=fake.calls,
        expected_url=health_url,
        expected_timeout=HTTP_TIMEOUT_S,
        expected_count=expected_count,
    )
    if expected_exc is not None:
        assert "simulated timeout" in str(excinfo.value)
    else:
        assert res.status_code == expected_status
