"""Shared fixtures. Everything runs offline: the stand-in core listens on 127.0.0.1 only."""

from __future__ import annotations

import sys
from collections.abc import Callable, Iterator
from contextlib import ExitStack
from pathlib import Path
from typing import Any

import pytest

CODE_DIR = Path(__file__).resolve().parent.parent
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from godavari_integration import synth_sources as ss  # noqa: E402
from godavari_integration.approvals import approved_records  # noqa: E402
from godavari_integration.clock import BusinessClock, ist  # noqa: E402
from godavari_integration.soap.port import CallLog, RateLimiter  # noqa: E402
from godavari_integration.soap.zeep_client import make_port  # noqa: E402
from godavari_integration.standin.core import CoreStandIn  # noqa: E402
from godavari_integration.standin.server import running  # noqa: E402
from godavari_integration.translate import Mapping  # noqa: E402

ACCOUNT, SECRET = "SVC_KAAGAZ_SBX", "sbx-only-not-a-real-secret"


@pytest.fixture(scope="session")
def mapping() -> Mapping:
    return Mapping()


@pytest.fixture(scope="session")
def facts() -> dict[str, ss.FileFacts]:
    return ss.hyderabad_files()


@pytest.fixture(scope="session")
def records(facts: dict[str, ss.FileFacts], mapping: Mapping) -> list[tuple[ss.FileFacts, dict[str, Any]]]:
    return approved_records(facts, mapping, ACCOUNT)


@pytest.fixture(scope="session")
def writable(records: list, mapping: Mapping) -> list[tuple[ss.FileFacts, dict[str, Any]]]:
    out = []
    for f, r in records:
        try:
            mapping.to_core(r)
            out.append((f, r))
        except ValueError:
            pass
    return out


@pytest.fixture
def clock() -> BusinessClock:
    return BusinessClock(ist(2026, 11, 12, 16, 10))


@pytest.fixture
def standin(clock: BusinessClock) -> Iterator[Callable[..., tuple[CoreStandIn, str]]]:
    """Start one or more stand-ins: core, url = standin(environment='sandbox')."""
    with ExitStack() as stack:
        def start(environment: str = "sandbox", rate_limit: int = 50, own_clock: BusinessClock | None = None) -> tuple[CoreStandIn, str]:
            core = CoreStandIn(environment=environment, clock=own_clock or clock, rate_limit=rate_limit)
            url = stack.enter_context(running(core))
            return core, url
        yield start


@pytest.fixture
def port_for(clock: BusinessClock) -> Callable[..., Any]:
    def make(kind: str, url: str, *, timeout: float = 2.0, log: CallLog | None = None, per_second: float | None = None,
             user: str = ACCOUNT, password: str = SECRET) -> Any:
        limiter = RateLimiter(per_second) if per_second else None
        return make_port(kind, url, user, password, timeout=timeout, log=log, limiter=limiter, clock=clock)
    return make
