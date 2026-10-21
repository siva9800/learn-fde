"""The port: what the rest of the system may ask the core, whichever client sits underneath.

Two clients implement it: one generated from the WSDL with zeep, one that builds envelopes by hand for the
day the WSDL will not load. Both return plain dataclasses and raise the four errors in errors.py, so the
writer, the reconciliation and the tests never see zeep objects or XML.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Protocol

from ..clock import BusinessClock


@dataclass(frozen=True)
class ApplicationSummary:
    appl_id: str            # "" for a shell
    file_no: str
    branch_cd: str
    appl_stat: str
    ext_ref: str = ""
    crt_ts: str = ""

    @property
    def is_shell(self) -> bool:
        return not self.appl_id and self.appl_stat == "S"


class CorePort(Protocol):
    name: str

    def get_by_file_number(self, file_no: str) -> list[ApplicationSummary]: ...
    def create_application(self, fields: dict[str, str]) -> str: ...
    def get_application(self, appl_id: str) -> dict[str, str]: ...
    def update_kyc_status(self, appl_id: str, status: str, user: str, reason: str = "") -> int: ...


@dataclass(frozen=True)
class CallRecord:
    at: str                 # business time, YYYYMMDDHHMISS
    client: str
    operation: str
    subject: str
    outcome: str            # OK, a fault code, UNAVAILABLE, NOT_SENT, AMBIGUOUS
    ms: int


@dataclass
class CallLog:
    """Our log of every call. The owner's condition: 'every one logged'. It must match his access log."""

    records: list[CallRecord] = field(default_factory=list)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def add(self, record: CallRecord) -> None:
        with self._lock:
            self.records.append(record)


class RateLimiter:
    """A client-side token bucket, set well under the limit the core enforces but never documented."""

    def __init__(self, per_second: float, burst: int = 1) -> None:
        self.interval = 1.0 / per_second
        self.burst = burst
        self._tokens = float(burst)
        self._last = time.monotonic()
        self._lock = threading.Lock()

    def acquire(self) -> None:
        while True:
            with self._lock:
                now = time.monotonic()
                self._tokens = min(self.burst, self._tokens + (now - self._last) / self.interval)
                self._last = now
                if self._tokens >= 1:
                    self._tokens -= 1
                    return
                wait = (1 - self._tokens) * self.interval
            time.sleep(wait)


def subject_of(kwargs: dict) -> str:
    app = kwargs.get("Application")
    if isinstance(app, dict):
        return str(app.get("FILE_NO", ""))
    return str(kwargs.get("FILE_NO") or kwargs.get("APPL_ID") or "")


def stamp(clock: BusinessClock | None) -> str:
    return clock.now().strftime("%Y%m%d%H%M%S") if clock else ""
