"""The write to the core lending system: deterministic, approved, and safe to repeat.

The real system is a 2009 SOAP API whose CreateApplication has no idempotency (Day 6, finding A5). This
module is the thin, honest version of the integration layer: a fake sandbox that behaves like the real
one (a second create makes a second record), and a push function that refuses anything not approved by a
named analyst, derives a key from file number and branch code, and looks the file up before creating.
Day 16 builds the real client from the WSDL; Day 17 puts it behind the state machine.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import date

from .reference import BRANCH_CODES
from .routing import Route


class FakeCoreSandbox:
    """Behaves like the 2009 system: CreateApplication always creates, even for a file it already has."""

    def __init__(self) -> None:
        self.records: list[dict[str, str]] = []

    def get_application_by_file_number(self, file_number: str) -> dict[str, str] | None:
        return next((r for r in self.records if r["file_number"] == file_number), None)

    def create_application(self, payload: dict[str, str]) -> str:
        record_id = f"CORE-{len(self.records) + 1:06d}"
        self.records.append({**payload, "record_id": record_id})
        return record_id


@dataclass(frozen=True)
class Approval:
    analyst_id: str
    approved_on: date
    sanction_date: date | None = None
    disbursement_date: date | None = None


@dataclass
class PushLog:
    entries: list[dict[str, str]] = field(default_factory=list)


def idempotency_key(file_number: str, branch: str) -> str:
    return hashlib.sha256(f"{file_number}|{BRANCH_CODES[branch]}".encode()).hexdigest()[:20]


def push_to_core(file_number: str, branch: str, route: Route, fields: dict[str, str], approval: Approval | None,
                 sandbox: FakeCoreSandbox, log: PushLog) -> str:
    """Returns the core record id. Raises before writing anything that is not allowed."""
    if approval is None:
        raise PermissionError(f"{file_number}: no analyst approval; nothing is written without one")
    if route in (Route.BLOCKED, Route.SEND_BACK):
        raise PermissionError(f"{file_number}: route is {route}; the file is not complete")
    if approval.sanction_date and approval.disbursement_date and approval.disbursement_date < approval.sanction_date:
        raise ValueError(f"{file_number}: disbursement {approval.disbursement_date} is before sanction "
                         f"{approval.sanction_date}")
    key = idempotency_key(file_number, branch)
    existing = sandbox.get_application_by_file_number(file_number)
    if existing is not None:
        log.entries.append({"file_number": file_number, "key": key, "action": "exists", "record": existing["record_id"]})
        return existing["record_id"]
    payload = {"file_number": file_number, "branch_code": BRANCH_CODES[branch], "idempotency_key": key,
               "approved_by": approval.analyst_id, **fields}
    record_id = sandbox.create_application(payload)
    log.entries.append({"file_number": file_number, "key": key, "action": "created", "record": record_id})
    return record_id
