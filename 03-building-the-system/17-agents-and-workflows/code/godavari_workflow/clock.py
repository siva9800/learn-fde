"""Business time for the workflow: a settable clock in IST (naive datetimes, as Day 15's directory uses) and
the working-hours arithmetic that approval deadlines and resubmission timeouts are measured in.

The working calendar is an assumption for the stand-in, to be agreed with Srinivas and the Vijayawada team
lead before the pilot: Monday to Friday, 09:30 to 17:30, no holidays modelled.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta

DAY_START, DAY_END = time(9, 30), time(17, 30)
WORKDAYS = frozenset({0, 1, 2, 3, 4})          # Monday to Friday
HOURS_PER_DAY = 8.0


@dataclass
class BusinessClock:
    current: datetime

    def now(self) -> datetime:
        return self.current

    def set(self, at: datetime) -> None:
        self.current = at

    def advance(self, **delta: float) -> datetime:
        self.current = self.current + timedelta(**delta)
        return self.current


def _next_open(at: datetime) -> datetime:
    """The first working moment at or after `at`."""
    probe = at
    while True:
        if probe.weekday() in WORKDAYS:
            start = datetime.combine(probe.date(), DAY_START)
            end = datetime.combine(probe.date(), DAY_END)
            if probe < start:
                return start
            if probe < end:
                return probe
        probe = datetime.combine(probe.date() + timedelta(days=1), DAY_START)


def add_working_hours(at: datetime, hours: float) -> datetime:
    """`at` plus `hours` of working time. A proposal made at 16:30 with a four-hour deadline is due at
    12:30 the next working day, not at 20:30 the same evening."""
    remaining = timedelta(hours=hours)
    cursor = _next_open(at)
    while True:
        end_of_day = datetime.combine(cursor.date(), DAY_END)
        if cursor + remaining <= end_of_day:
            return cursor + remaining
        remaining -= end_of_day - cursor
        cursor = _next_open(end_of_day)


def add_working_days(at: datetime, days: int) -> datetime:
    return add_working_hours(at, days * HOURS_PER_DAY)


def stamp(at: datetime) -> str:
    return at.strftime("%Y-%m-%d %H:%M")


def parse(text: str) -> datetime:
    return datetime.strptime(text, "%Y-%m-%d %H:%M")
