"""The provider-neutral boundary: one request shape, one response shape, one error vocabulary.

Nothing above this module imports a vendor SDK. An adapter (adapters/anthropic_adapter.py, or the fake in
fake_provider.py) translates these types to and from one vendor's API. Switching providers means writing
one adapter and one price-card row, then re-running the eval set (Day 14); no other file changes.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Protocol


class Tier(StrEnum):
    """Callers ask for a tier, never a model name. The adapter maps the tier to a model it has pinned."""

    SMALL = "small"   # page classification, routing: cheap, fast, low-resolution input
    LARGE = "large"   # field extraction from the hard pages, repairs


@dataclass(frozen=True)
class ModelRequest:
    tier: Tier
    system: str                       # the stable prefix: instructions plus schema description (cacheable)
    user_text: str                    # the variable part: which page, which file
    page_ref: str | None              # the page image the adapter attaches (a storage key, never the bytes)
    json_schema: dict[str, Any] | None
    max_output_tokens: int
    timeout_s: float
    idempotency_key: str
    purpose: str = "first"            # first | bigger_budget | repair: for the ledger and the fake provider
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Usage:
    input_tokens: int = 0             # uncached input
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0
    output_tokens: int = 0

    def __add__(self, other: Usage) -> Usage:
        return Usage(
            self.input_tokens + other.input_tokens,
            self.cache_read_tokens + other.cache_read_tokens,
            self.cache_write_tokens + other.cache_write_tokens,
            self.output_tokens + other.output_tokens,
        )


@dataclass(frozen=True)
class ModelResponse:
    text: str
    usage: Usage
    model: str
    stop_reason: str                  # end | max_tokens | refusal
    latency_s: float
    request_id: str
    ttft_s: float = 0.0


# --- Errors: the only vocabulary the client's retry logic understands ----------------------------------

class ProviderError(Exception):
    retryable = False
    counts_against_health = False     # does this failure say the provider is unwell (for the breaker)?

    def __init__(self, message: str, *, elapsed_s: float = 0.0, request_id: str = "") -> None:
        super().__init__(message)
        self.elapsed_s = elapsed_s
        self.request_id = request_id


class RateLimited(ProviderError):
    """HTTP 429. Our fault (too fast), not the provider's: retry after the server's hint, do not trip the breaker."""

    retryable = True

    def __init__(self, message: str, *, retry_after_s: float | None, **kw: Any) -> None:
        super().__init__(message, **kw)
        self.retry_after_s = retry_after_s


class SpendCapReached(ProviderError):
    """A 429 that is not a rate limit (a monthly cap): retrying cannot help, so it is not retryable."""


class Overloaded(ProviderError):
    """HTTP 529 or 503: the provider is shedding load."""

    retryable = True
    counts_against_health = True


class ServerError(ProviderError):
    """HTTP 500 or a dropped connection."""

    retryable = True
    counts_against_health = True


class ProviderTimeout(ProviderError):
    """We stopped waiting. The provider may still have finished the work and billed it."""

    retryable = True
    counts_against_health = True


class BadRequest(ProviderError):
    """HTTP 400 or 413: the same request will fail the same way. Fix the request, do not retry it."""


# --- The interface every adapter implements ------------------------------------------------------------

class ModelProvider(Protocol):
    name: str

    def model_for(self, tier: Tier) -> str: ...

    def complete(self, request: ModelRequest) -> ModelResponse:
        """One attempt. Raises a ProviderError subclass on failure. Never retries internally."""
        ...


# --- Time, injected so that tests and the simulated night run in milliseconds --------------------------

class Clock(Protocol):
    def now(self) -> float: ...

    def sleep(self, seconds: float) -> None: ...


class SystemClock:
    def now(self) -> float:
        return time.monotonic()

    def sleep(self, seconds: float) -> None:
        time.sleep(seconds)


class VirtualClock:
    """Seconds since 02:00:00 on the night of the batch. Sleeping advances it; nothing really waits."""

    def __init__(self, t: float = 0.0) -> None:
        self.t = t

    def now(self) -> float:
        return self.t

    def sleep(self, seconds: float) -> None:
        self.t += max(0.0, seconds)

    def set(self, t: float) -> None:
        self.t = t
