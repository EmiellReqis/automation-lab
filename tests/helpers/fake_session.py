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


class FakeSession:
    """
    A minimal stand-in for `requests.Session` used in unit tests.

    It supports scripted outcomes for consecutive `.get()` calls:
      - a response-like object (e.g. `FakeResponse(status_code=200)`) will be returned
      - an `Exception` instance will be raised

    The session also records all calls in `self.calls` as (url, kwargs),
    so tests can assert request URL, timeout, headers, etc.
    """

    def __init__(self, outcomes: Sequence[Any] | None = None):
        self.outcomes: deque[Any] = deque() if outcomes is None else deque(outcomes)
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def get(self, url: str, **kwargs: Any) -> Any:
        """
         Simulate `requests.Session.get(url, **kwargs)`.

        Behavior:
          1) record the call as (url, kwargs) in `self.calls`
          2) take the next item from `self.outcomes`
          3) if the item is an Exception -> raise it
             otherwise -> return it

        Raises:
          AssertionError: if no outcomes are left (helps detect unexpected extra retries).
        """
        self.calls.append((url, kwargs))

        if not self.outcomes:
            raise AssertionError("FakeSession: no more outcomes configured")

        outcome = self.outcomes.popleft()

        if isinstance(outcome, Exception):
            raise outcome
        return outcome
