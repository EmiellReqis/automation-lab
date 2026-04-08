from __future__ import annotations

from collections import deque
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any


@dataclass
class FakeResponse:
    status_code: int
    # (optional for the future)
    # json_data: Any | None = None


@dataclass(frozen=True)
class RequestCall:
    """
    Represents a single HTTP call recorded by FakeSession for assertions and debugging.
    """

    method: str
    url: str
    kwargs: dict[str, Any]


@dataclass(frozen=True)
class ExpectedRequest:
    """
    Represents the expected request for a configured FakeSession outcome.
    """

    method: str
    url: str


@dataclass(frozen=True)
class ConfiguredOutcome:
    expected_request: ExpectedRequest
    outcome: Any


class FakeSession:
    """
    A minimal stand-in for `requests.Session` used in unit tests.

    It supports scripted outcomes for consecutive `.get()` calls:
      - a response-like object will be returned
      - an `Exception` instance will be raised

    The session records every performed request in `self.calls` as `RequestCall`
    objects, so tests can assert HTTP method, URL, and request kwargs.

    If a request is made without a configured outcome, the session fails fast
    with an `AssertionError` that includes request context.
    """

    def __init__(self, outcomes: Sequence[Any] | None = None):
        self.outcomes: deque[Any] = deque() if outcomes is None else deque(outcomes)
        self.calls: list[RequestCall] = []

    def get(self, url: str, **kwargs: Any) -> Any:
        """
        Simulate `requests.Session.get(url, **kwargs)`.

        Records the request in `self.calls`, then consumes the next configured
        outcome from `self.outcomes`.

        Behavior:
          1) store the performed request as `RequestCall(method="GET", url=url, kwargs=kwargs)`
          2) return the next configured outcome
          3) raise the outcome if it is an `Exception`

        Raises:
          AssertionError: if no outcome is configured for the performed request.
        """
        request_call = RequestCall(method="GET", url=url, kwargs=kwargs)
        self.calls.append(request_call)

        if not self.outcomes:
            raise AssertionError(
                f"FakeSession: unexpected request "
                f"{request_call.method} {request_call.url} - no outcome configured"
            )

        outcome = self.outcomes.popleft()

        if isinstance(outcome, ConfiguredOutcome):
            if (
                request_call.method != outcome.expected_request.method
                or request_call.url != outcome.expected_request.url
            ):
                raise AssertionError(
                    f"FakeSession: request mismatch - "
                    f"expected {outcome.expected_request.method} "
                    f"{outcome.expected_request.url}, "
                    f"got {request_call.method} {request_call.url}"
                )
            outcome = outcome.outcome
        if isinstance(outcome, Exception):
            raise outcome
        return outcome
