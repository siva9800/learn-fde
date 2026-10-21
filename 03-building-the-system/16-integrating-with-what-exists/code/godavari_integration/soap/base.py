"""What both clients share: pacing, logging, and turning transport exceptions into the four outcomes."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import TypeVar

import requests

from ..clock import BusinessClock
from .errors import (AmbiguousOutcome, CoreError, CoreFault, CoreUnavailable, NotSent, RefusedBeforeSending,
                     ResponseUnreadable)
from .port import CallLog, CallRecord, RateLimiter, stamp

T = TypeVar("T")
_NOT_CONNECTED_MARKERS = ("NewConnectionError", "NameResolutionError", "Failed to establish", "getaddrinfo failed",
                          "Connection refused", "actively refused")


def classify_transport_error(exc: requests.exceptions.RequestException) -> CoreError:
    """Sent or not sent? A connect timeout or a refused connection means the core never saw the request.
    A read timeout, or a connection dropped after the request went out, means nobody knows."""
    if isinstance(exc, requests.exceptions.ConnectTimeout):
        return NotSent(f"connect timeout: {exc}")
    if isinstance(exc, requests.exceptions.ReadTimeout):
        return AmbiguousOutcome(f"no reply within the read timeout: {exc}")
    if isinstance(exc, requests.exceptions.ConnectionError):
        text = repr(exc)
        if any(marker in text for marker in _NOT_CONNECTED_MARKERS):
            return NotSent(f"could not connect: {exc}")
        return AmbiguousOutcome(f"connection dropped after sending: {exc}")
    return AmbiguousOutcome(f"transport error after sending: {exc}")


class BaseCoreClient:
    name = "base"

    def __init__(self, *, limiter: RateLimiter | None, log: CallLog | None, clock: BusinessClock | None) -> None:
        self.limiter = limiter
        self.log = log if log is not None else CallLog()
        self.clock = clock

    def _call(self, operation: str, subject: str, fn: Callable[[], T]) -> T:
        if self.limiter:
            self.limiter.acquire()
        started = time.monotonic()
        outcome = "OK"
        try:
            return fn()
        except CoreFault as fault:
            outcome = fault.code
            raise
        except CoreUnavailable:
            outcome = "UNAVAILABLE"
            raise
        except RefusedBeforeSending:
            outcome = "REFUSED_LOCALLY"
            raise
        except ResponseUnreadable:
            outcome = "UNREADABLE"
            raise
        except requests.exceptions.RequestException as exc:
            err = classify_transport_error(exc)
            outcome = "NOT_SENT" if isinstance(err, NotSent) else "AMBIGUOUS"
            raise err from exc
        finally:
            self.log.add(CallRecord(stamp(self.clock), self.name, operation, subject.strip(), outcome,
                                    int((time.monotonic() - started) * 1000)))
