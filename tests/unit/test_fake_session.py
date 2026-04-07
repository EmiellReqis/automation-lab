from typing import Any

import pytest

from tests.helpers.fake_session import FakeResponse, FakeSession, RequestCall


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
