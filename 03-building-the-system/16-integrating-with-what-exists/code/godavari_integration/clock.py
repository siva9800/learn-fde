"""Business time at Godavari: India Standard Time, the 18:00 batch, the write window, the maintenance window.

Two clocks matter and they must never be confused. Business time (this module) decides *whether* a write
is allowed: it is injectable so tests and the night run can say "it is 17:40 on Thursday". Wall-clock
monotonic time (time.monotonic) decides timeouts and rate limits, and is never simulated.
"""

from __future__ import annotations

from calendar import monthrange
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone

IST = timezone(timedelta(hours=5, minutes=30), "IST")      # no daylight saving; no tzdata needed

WRITE_FREEZE_START = time(17, 30)        # "Nothing writes between five thirty and eight in the evening." (T06)
BATCH_END_NORMAL = time(20, 0)           # "Normally by eight."
BATCH_END_MONTH_END = time(23, 0)        # "Month end, eleven."
MONTH_END_DAYS = 3                       # the last three days of a month carry three times the volume (B3)
MAINTENANCE_WEEKDAY = 6                  # Sunday (invented for the stand-in; agreed in the integration contract)
MAINTENANCE_START, MAINTENANCE_END = time(6, 0), time(9, 0)


def is_month_end(day: date) -> bool:
    return day.day > monthrange(day.year, day.month)[1] - MONTH_END_DAYS


def batch_end(day: date) -> time:
    return BATCH_END_MONTH_END if is_month_end(day) else BATCH_END_NORMAL


def in_write_freeze(at: datetime) -> bool:
    """True while the 18:00 credit-check batch owns the core: from 17:30 until the batch is expected to end."""
    t = at.astimezone(IST).time()
    return WRITE_FREEZE_START <= t < batch_end(at.astimezone(IST).date())


def next_write_slot(at: datetime) -> datetime:
    """The first moment a held write may go: the expected end of tonight's batch."""
    local = at.astimezone(IST)
    if not in_write_freeze(local):
        return local
    return datetime.combine(local.date(), batch_end(local.date()), IST)


def in_maintenance(at: datetime) -> bool:
    local = at.astimezone(IST)
    return local.weekday() == MAINTENANCE_WEEKDAY and MAINTENANCE_START <= local.time() < MAINTENANCE_END


@dataclass
class BusinessClock:
    """A settable clock in IST. `now()` is what every window decision reads."""

    current: datetime

    def now(self) -> datetime:
        return self.current

    def set(self, at: datetime) -> None:
        self.current = at.astimezone(IST)

    def advance(self, **delta: float) -> datetime:
        self.current = self.current + timedelta(**delta)
        return self.current


def ist(y: int, m: int, d: int, hh: int = 0, mm: int = 0) -> datetime:
    return datetime(y, m, d, hh, mm, tzinfo=IST)
