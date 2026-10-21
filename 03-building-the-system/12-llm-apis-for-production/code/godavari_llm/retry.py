"""Retry policy, backoff with full jitter, and a circuit breaker. Pure logic: no I/O, injected clock."""

from __future__ import annotations

import random
from dataclasses import dataclass
from enum import StrEnum

from .provider import Clock


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 4            # first try plus three retries
    base_delay_s: float = 1.0
    max_delay_s: float = 20.0
    call_deadline_s: float = 90.0    # wall-clock budget for one logical call, retries and waits included


def backoff_delay(policy: RetryPolicy, attempt: int, rng: random.Random, retry_after_s: float | None = None) -> float:
    """Delay before retry number `attempt` (1 for the first retry).

    Full jitter: a uniform draw between 0 and min(cap, base * 2**(attempt - 1)). Without jitter, every
    worker that failed together retries together, and the provider sees the same spike again one second
    later. A server's retry-after is a floor, never something to undercut.
    """
    if attempt < 1:
        raise ValueError("attempt counts retries and starts at 1")
    ceiling = min(policy.max_delay_s, policy.base_delay_s * (2 ** (attempt - 1)))
    delay = rng.uniform(0.0, ceiling)
    if retry_after_s is not None:
        delay = max(delay, retry_after_s)
    return delay


class BreakerState(StrEnum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitOpen(Exception):
    """Raised instead of calling a provider the breaker believes is down. Fail fast; defer the work."""


class CircuitBreaker:
    """Opens after `failure_threshold` consecutive health failures (overload, 5xx, timeout). While open,
    calls fail at once. After `cooldown_s`, one probe is let through (half-open): success closes the
    breaker, failure opens it again. 429s and 400s do not count: they are about our requests, not its health."""

    def __init__(self, clock: Clock, failure_threshold: int = 5, cooldown_s: float = 60.0) -> None:
        self.clock = clock
        self.failure_threshold = failure_threshold
        self.cooldown_s = cooldown_s
        self.state = BreakerState.CLOSED
        self.consecutive_failures = 0
        self.opened_at: float | None = None
        self.transitions: list[tuple[float, BreakerState]] = []

    def _move(self, state: BreakerState) -> None:
        if state != self.state:
            self.state = state
            self.transitions.append((self.clock.now(), state))

    def allow(self) -> bool:
        if self.state == BreakerState.OPEN:
            assert self.opened_at is not None
            if self.clock.now() - self.opened_at >= self.cooldown_s:
                self._move(BreakerState.HALF_OPEN)
                return True
            return False
        return True

    def record_success(self) -> None:
        self.consecutive_failures = 0
        self._move(BreakerState.CLOSED)

    def record_failure(self) -> None:
        self.consecutive_failures += 1
        if self.state == BreakerState.HALF_OPEN or self.consecutive_failures >= self.failure_threshold:
            self.opened_at = self.clock.now()
            self._move(BreakerState.OPEN)
