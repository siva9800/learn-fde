"""Writing to a core that has no idempotency keys: three clients, two of them wrong.

  naive_push             what the 2022 vendor did: call CreateApplication, and on any error call it again.
                         A timeout after commit becomes a second application (DUPLICATE_ON_RETRY).
  lookup_then_retry      Day 11's push_to_core (key, lookup before create), retried at once on any error.
                         Correct when the core committed before the timeout; wrong when the commit lands
                         after the caller gave up, because the lookup ran too early.
  SafeCoreWriter         the journal, Day 11's push for the lookup-before-create, and one more rule: an
                         ambiguous write is never retried. It waits out a quiet period longer than the core's
                         own transaction ceiling, then the lookup decides. Plus the write window, the busy
                         fault, the maintenance page, a record keyed by hand, and duplicates already there.

Day 11's push_to_core is imported, not copied: the approval check, the route check, the key from file
number and branch code, and lookup-before-create stay in one place.
"""

from __future__ import annotations

import hashlib
import json
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .clock import BusinessClock, in_write_freeze, next_write_slot
from .day11 import Approval, PushLog, Route, push_to_core
from .journal import (CONFIRMED, DEFERRED, DUPLICATE_IN_CORE, EXISTS_NOT_OURS, FAILED, PENDING, UNKNOWN, Journal)
from .soap.errors import AmbiguousOutcome, CoreError, CoreFault, CoreUnavailable, NotSent, RefusedBeforeSending
from .soap.port import CorePort
from .translate import Mapping, MappingError

CORE_TRANSACTION_CEILING_S = 60.0     # the core's own transaction timeout, confirmed with the owner (week 3)
QUIET_PERIOD_S = 90.0                 # wait longer than the ceiling before a lookup may decide


class FileNotRegistered(CoreError):
    """No shell for this file number: the 02:00 job never saw it. Never create around it."""


class DuplicateInCore(CoreError):
    def __init__(self, file_no: str, appl_ids: list[str]) -> None:
        self.file_no, self.appl_ids = file_no, appl_ids
        super().__init__(f"{file_no} already has {len(appl_ids)} applications: {', '.join(appl_ids)}")


class SoapCoreAdapter:
    """Makes the SOAP port look like Day 11's FakeCoreSandbox, so Day 11's push_to_core drives it."""

    def __init__(self, port: CorePort, mapping: Mapping) -> None:
        self.port, self.mapping = port, mapping
        self.last_ext_ref = ""

    def get_application_by_file_number(self, file_number: str) -> dict[str, str] | None:
        summaries = self.port.get_by_file_number(file_number)
        if not summaries:
            raise FileNotRegistered(f"{file_number}: no shell and no application in the core")
        apps = [s for s in summaries if not s.is_shell]
        if len(apps) > 1:
            raise DuplicateInCore(file_number, [a.appl_id for a in apps])
        if not apps:
            return None
        self.last_ext_ref = apps[0].ext_ref
        return {"record_id": apps[0].appl_id, "ext_ref": apps[0].ext_ref}

    def create_application(self, payload: dict[str, Any]) -> str:
        self.last_ext_ref = str(payload.get("idempotency_key", ""))
        return self.port.create_application(self.mapping.to_core(payload))


def business_subset(mapping: Mapping, core_payload: dict[str, str]) -> dict[str, str]:
    """What the journal may keep: everything except direct identifiers."""
    hidden = mapping.direct_identifier_fields()
    return {k: v for k, v in core_payload.items() if k not in hidden}


def payload_hash(core_payload: dict[str, str]) -> str:
    return hashlib.sha256(json.dumps(core_payload, sort_keys=True).encode()).hexdigest()


# ---- the two wrong clients, kept so the difference can be shown and tested --------------------------------
def naive_push(port: CorePort, mapping: Mapping, record: dict[str, Any], retries: int = 2,
               sleep: Callable[[float], None] = time.sleep) -> list[str]:
    """Create, and on any error create again. Returns the ids it saw succeed (often fewer than it made)."""
    payload = mapping.to_core(record)
    created: list[str] = []
    for _ in range(retries + 1):
        try:
            created.append(port.create_application(payload))
            return created
        except Exception:                    # noqa: BLE001 - this is the bug: every error looks retryable
            sleep(0.3)
    return created


def lookup_then_retry(port: CorePort, mapping: Mapping, record: dict[str, Any], branch: str, route: Route,
                      approval: Approval, retries: int = 2) -> str | None:
    """Day 11's push, retried immediately. Safe for 'committed, reply lost'; not for 'committed late'."""
    adapter, log = SoapCoreAdapter(port, mapping), PushLog()
    for _ in range(retries + 1):
        try:
            return push_to_core(record["file_number"], branch, route, record, approval, adapter, log)
        except CoreFault as fault:
            if fault.code == "CL-E099":
                time.sleep(1.0)
                continue
            raise
        except CoreError:
            continue
    return None


# ---- the writer that does not duplicate -------------------------------------------------------------------
@dataclass(frozen=True)
class WriteOutcome:
    file_no: str
    key: str
    state: str
    appl_id: str | None
    note: str = ""


class SafeCoreWriter:
    def __init__(self, port: CorePort, mapping: Mapping, journal: Journal, clock: BusinessClock, *,
                 quiet_period_s: float = QUIET_PERIOD_S, max_attempts: int = 3, backoff_s: float = 2.0,
                 sleep: Callable[[float], None] = time.sleep, wall: Callable[[], float] = time.time) -> None:
        self.port, self.mapping, self.journal, self.clock = port, mapping, journal, clock
        self.quiet_period_s, self.max_attempts, self.backoff_s = quiet_period_s, max_attempts, backoff_s
        self.sleep, self.wall = sleep, wall
        self.adapter = SoapCoreAdapter(port, mapping)
        self.pushlog = PushLog()

    def _at(self) -> str:
        return self.clock.now().strftime("%Y%m%d%H%M%S")

    def _out(self, key: str) -> WriteOutcome:
        row = self.journal.get(key)
        assert row is not None
        return WriteOutcome(row.file_no, key, row.state, row.appl_id, row.note or "")

    def push(self, record: dict[str, Any], branch: str, route: Route, approval: Approval | None) -> WriteOutcome:
        key, file_no = str(record["idempotency_key"]), str(record["file_number"])
        row = self.journal.get(key)
        if row and row.state in (CONFIRMED, EXISTS_NOT_OURS, DUPLICATE_IN_CORE):
            return self._out(key)                              # already settled: no call at all
        if row and row.state == UNKNOWN:
            return self._resolve(row)                          # never create over an unknown
        try:
            core_payload = self.mapping.to_core(record)
        except MappingError as exc:                            # fail closed before the core sees anything
            self.journal.intend(key, file_no, str(record.get("branch_code", "")), "", {}, self.mapping.version, self._at())
            self.journal.set_state(key, FAILED, self._at(), note=f"mapping: {exc}")
            return self._out(key)
        self.journal.intend(key, file_no, core_payload["BRANCH_CD"], payload_hash(core_payload),
                            business_subset(self.mapping, core_payload), self.mapping.version, self._at())
        if in_write_freeze(self.clock.now()):
            slot = next_write_slot(self.clock.now()).strftime("%H:%M")
            self.journal.set_state(key, DEFERRED, self._at(), note=f"write window closed; held until {slot}")
            return self._out(key)
        return self._attempt(key, file_no, branch, route, record, approval)

    def _attempt(self, key: str, file_no: str, branch: str, route: Route, record: dict[str, Any],
                 approval: Approval | None) -> WriteOutcome:
        for attempt in range(1, self.max_attempts + 1):
            self.journal.attempt(key, self._at())
            try:
                appl_id = push_to_core(file_no, branch, route, record, approval, self.adapter, self.pushlog)
            except AmbiguousOutcome as exc:
                self.journal.set_state(key, UNKNOWN, self._at(), note=f"no reply: {type(exc).__name__}; "
                                       f"lookup after {self.quiet_period_s:.0f} s quiet", unknown_since=self.wall())
                return self._out(key)
            except (NotSent, CoreUnavailable) as exc:
                self.journal.set_state(key, PENDING, self._at(), note=f"not sent: {exc}"[:200])
                self.sleep(self.backoff_s * attempt)
                continue
            except CoreFault as fault:
                if fault.code == "CL-E017":
                    self.journal.set_state(key, DEFERRED, self._at(), note="CL-E017: batch still running; held")
                    return self._out(key)
                if fault.retryable:
                    self.journal.set_state(key, PENDING, self._at(), note=f"{fault.code}; backing off")
                    self.sleep(self.backoff_s * attempt)
                    continue
                self.journal.set_state(key, FAILED, self._at(), note=fault.faultstring)
                return self._out(key)
            except DuplicateInCore as dup:
                self.journal.set_state(key, DUPLICATE_IN_CORE, self._at(), note=str(dup))
                return self._out(key)
            except RefusedBeforeSending as exc:
                self.journal.set_state(key, FAILED, self._at(), note=f"refused before sending: {exc}")
                return self._out(key)
            except FileNotRegistered as exc:
                self.journal.set_state(key, FAILED, self._at(), note=str(exc))
                return self._out(key)
            except PermissionError as exc:                    # Day 11: no approval, or a blocked route
                self.journal.set_state(key, FAILED, self._at(), note=str(exc))
                return self._out(key)
            action = self.pushlog.entries[-1]["action"]
            if action == "exists" and self.adapter.last_ext_ref != key:
                self.journal.set_state(key, EXISTS_NOT_OURS, self._at(), appl_id=appl_id,
                                       note="an application was already keyed for this file; not created")
            else:
                self.journal.set_state(key, CONFIRMED, self._at(), appl_id=appl_id,
                                       note="created" if action == "created" else "found by lookup")
            return self._out(key)
        return self._out(key)

    def _resolve(self, row: Any) -> WriteOutcome:
        waited = self.wall() - (row.unknown_since or 0.0)
        if waited < self.quiet_period_s:
            return WriteOutcome(row.file_no, row.key, UNKNOWN, None,
                                f"quiet period: {waited:.1f} of {self.quiet_period_s:.0f} s; not yet")
        try:
            summaries = self.port.get_by_file_number(row.file_no)
        except CoreError as exc:
            return WriteOutcome(row.file_no, row.key, UNKNOWN, None, f"lookup failed: {exc}")
        apps = [s for s in summaries if not s.is_shell]
        ours = [a for a in apps if a.ext_ref == row.key]
        if len(apps) > 1:
            self.journal.set_state(row.key, DUPLICATE_IN_CORE, self._at(),
                                   note=f"{len(apps)} applications after an ambiguous write: " + ", ".join(a.appl_id for a in apps))
        elif ours:
            self.journal.set_state(row.key, CONFIRMED, self._at(), appl_id=ours[0].appl_id,
                                   note="resolved by lookup: the write had happened")
        elif apps:
            self.journal.set_state(row.key, EXISTS_NOT_OURS, self._at(), appl_id=apps[0].appl_id,
                                   note="resolved by lookup: keyed by someone else")
        else:
            self.journal.set_state(row.key, PENDING, self._at(), note="resolved by lookup: the write had not happened")
        return self._out(row.key)

    def resolve_unknowns(self) -> list[WriteOutcome]:
        return [self._resolve(row) for row in self.journal.in_state(UNKNOWN)]
