from typing import Any

import pytest

from tests.helpers.fake_session import (
    ConfiguredOutcome,
    ExpectedRequest,
    FakeResponse,
    FakeSession,
    RequestCall,
)


@pytest.mark.unit
def test_get_records_request_call() -> None:
    expected_url = "https://example.com/api/users"
    expected_kwargs = {
        "timeout": 5.0,
        "headers": {"Authorization": "Bearer token"},
        "params": {"page": 1},
    }
    outcome = FakeResponse(status_code=200)

    session = FakeSession(outcomes=[outcome])

    result = session.get(expected_url, **expected_kwargs)

    assert result is outcome
    assert len(session.calls) == 1

    call = session.calls[0]
    assert isinstance(call, RequestCall)
    assert call.method == "GET"
    assert call.url == expected_url
    assert call.kwargs == expected_kwargs


@pytest.mark.unit
@pytest.mark.parametrize(
    ("url", "kwargs"),
    [
        (
            "https://example.com/api/users",
            {"timeout": 5.0},
        ),
        (
            "https://example.com/api/orders",
            {"timeout": 2.5, "headers": {"X-Trace-Id": "abc-123"}},
        ),
        (
            "https://example.com/api/search",
            {"timeout": 1.0, "params": {"q": "pytest"}},
        ),
    ],
    ids=[
        "timeout_only",
        "timeout_and_headers",
        "timeout_and_params",
    ],
)
def test_get_fails_fast_with_request_context_when_outcome_is_missing(
    url: str,
    kwargs: dict[str, Any],
) -> None:
    session = FakeSession()

    with pytest.raises(AssertionError) as exc_info:
        session.get(url, **kwargs)

    assert len(session.calls) == 1
    assert session.calls[0].method == "GET"
    assert session.calls[0].url == url
    assert session.calls[0].kwargs == kwargs

    message = str(exc_info.value)
    assert "unexpected request" in message
    assert "GET" in message
    assert url in message
    assert "no outcome configured" in message


@pytest.mark.unit
def test_get_returns_outcome_when_expected_request_matches() -> None:
    expected_method = "GET"
    expected_url = "https://example"

    configured_outcome = ConfiguredOutcome(
        expected_request=ExpectedRequest(method=expected_method, url=expected_url),
        outcome=FakeResponse(status_code=200),
    )
    session = FakeSession(outcomes=[configured_outcome])

    result = session.get(expected_url, timeout=5.0)

    assert result is configured_outcome.outcome
    assert len(session.calls) == 1

    call = session.calls[0]
    assert isinstance(call, RequestCall)
    assert call.method == "GET"
    assert call.url == expected_url
    assert call.kwargs == {"timeout": 5.0}


@pytest.mark.unit
def test_get_fails_fast_when_expected_method_does_not_match() -> None:
    expected_method = "POST"
    expected_url = "https://example"

    configured_outcome = ConfiguredOutcome(
        expected_request=ExpectedRequest(method=expected_method, url=expected_url),
        outcome=FakeResponse(status_code=200),
    )
    session = FakeSession(outcomes=[configured_outcome])

    with pytest.raises(AssertionError) as exc_info:
        session.get(expected_url, timeout=5.0)

    assert len(session.calls) == 1

    message = str(exc_info.value)
    assert "request mismatch" in message
    assert "expected POST" in message
    assert "got GET" in message
    assert expected_url in message


@pytest.mark.unit
def test_get_fails_fast_when_expected_url_does_not_match() -> None:
    expected_method = "GET"
    expected_url = "https://example.com/api/users"
    actual_url = "https://example.com/api/orders"

    configured_outcome = ConfiguredOutcome(
        expected_request=ExpectedRequest(method=expected_method, url=expected_url),
        outcome=FakeResponse(status_code=200),
    )
    session = FakeSession(outcomes=[configured_outcome])

    with pytest.raises(AssertionError) as exc_info:
        session.get(actual_url, timeout=5.0)

    assert len(session.calls) == 1

    message = str(exc_info.value)
    assert "request mismatch" in message
    assert expected_url in message
    assert actual_url in message
    assert "expected GET" in message
    assert "got GET" in message
