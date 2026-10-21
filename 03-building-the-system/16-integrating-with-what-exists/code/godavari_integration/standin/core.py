"""A stand-in for Godavari's 2009 core lending system: the behaviour the owner described, nothing kinder.

What it does, because the real one does (Day 6, transcript 06):
  * CreateApplication always creates. Call it twice for one file and there are two applications.
  * GetApplicationByFileNumber exists and nobody uses it. It returns the file's shell (registered by the
    02:00 job) until an application exists, then every application for that file number.
  * Nothing writes between 17:30 and the end of the 18:00 batch (20:00; 23:00 in the last three days of a
    month). Reads are fine.
  * A rate limit nobody documented: more than RATE_LIMIT calls in one second from one account gets
    "CL-E099 SERVICE BUSY". Found in week 3 from the fault text, not from any document.
  * Faults are SOAP 1.1 faults whose faultstring starts with a code (CL-E023 ...).
  * environment="sandbox" is the quarterly masked copy, last refreshed in July: it does not enforce the
    August release's dealer-code rule, and its credit-check results come from three-month-old rules.
  * A stall can be planted on one create: the commit happens and the reply is late ("commit_then_stall"),
    or the reply is late and the commit happens after the caller gave up ("stall_then_commit"). The first
    reproduces DUPLICATE_ON_RETRY; the second is why "look up, then retry at once" is not enough.

Business time comes from an injectable clock; the rate limit and stalls use real time.
"""

from __future__ import annotations

import threading
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import date, datetime

from ..clock import IST, BusinessClock, in_write_freeze
from ..corespec import (CODE_TABLES, CREATE_APPLICATION_FIELDS, DETAIL_FIELDS, FAULTS, FIELD_BY_NAME,
                        FIELD_CODE_TABLE, PRODUCTION_CONDITIONAL_MANDATORY, SUMMARY_FIELDS, WRITE_OPERATIONS)

RATE_LIMIT = 5                 # calls per account in any one-second window (undocumented)
SANDBOX_REFRESHED = date(2026, 7, 15)


class CoreFaultError(Exception):
    def __init__(self, code: str, field: str = "", extra: str = "") -> None:
        self.code, self.field = code, field
        side, _retryable, text = FAULTS[code]
        self.side = side
        self.faultstring = f"{code} {text}" + (f": {field}" if field else "") + (f" {extra}" if extra else "")
        super().__init__(self.faultstring)


@dataclass
class Stall:
    mode: str                  # "commit_then_stall" or "stall_then_commit"
    seconds: float
    remaining: int = 1         # how many creates for this file stall


@dataclass
class Record:
    appl_id: str
    fields: dict[str, str]
    appl_stat: str
    crt_ts: str
    lst_upd_ts: str
    kyc_hist: list[tuple[str, str, str]] = field(default_factory=list)   # (ts, status, user)


@dataclass(frozen=True)
class AccessLogEntry:
    """The core's own access log, which the owner can export. Ours must agree with it."""

    at: str
    account: str
    operation: str
    subject: str
    outcome: str


def _ts(at: datetime) -> str:
    return at.astimezone(IST).strftime("%Y%m%d%H%M%S")


class CoreStandIn:
    def __init__(self, environment: str = "sandbox", clock: BusinessClock | None = None,
                 accounts: dict[str, str] | None = None, rate_limit: int = RATE_LIMIT) -> None:
        if environment not in ("sandbox", "production-like"):
            raise ValueError(environment)
        self.environment = environment
        self.clock = clock or BusinessClock(datetime(2026, 11, 12, 10, 0, tzinfo=IST))
        self.accounts = accounts or {"SVC_KAAGAZ_SBX": "sbx-only-not-a-real-secret"}
        self.rate_limit = rate_limit
        self.shells: dict[str, tuple[str, str]] = {}          # padded FILE_NO -> (BRANCH_CD, registered ts)
        self.records: list[Record] = []
        self.stalls: dict[str, Stall] = {}
        self.access_log: list[AccessLogEntry] = []
        self.maintenance_forced = False
        self._seq = 0
        self._recent: dict[str, deque[float]] = {}
        self._lock = threading.RLock()

    # ---- Godavari's side: the 02:00 job and the July snapshot ---------------------------------------
    def register_file(self, file_no: str, branch_cd: str, at: datetime | None = None) -> None:
        """What the 02:00 job does: a shell with the branch code and the file number, nothing else."""
        with self._lock:
            self.shells[file_no.ljust(12)] = (branch_cd, _ts(at or self.clock.now()))

    def seed_legacy(self, rows: list[dict[str, str]]) -> None:
        """Masked records from the July snapshot (or production history), created by people, not by us."""
        with self._lock:
            for row in rows:
                self._seq += 1
                rec = Record(f"AP{self._seq:010d}", dict(row), row.get("APPL_STAT", "K"), row["CRT_TS"], row["CRT_TS"])
                self.records.append(rec)
                self.shells.setdefault(row["FILE_NO"].ljust(12), (row["BRANCH_CD"], row["CRT_TS"]))

    def plant_stall(self, file_no: str, mode: str, seconds: float, times: int = 1) -> None:
        if mode not in ("commit_then_stall", "stall_then_commit"):
            raise ValueError(mode)
        self.stalls[file_no] = Stall(mode, seconds, times)

    def edit_on_core_screen(self, appl_id: str, field_name: str, value: str) -> None:
        """A branch user changes a field on the green screen after our write (it happens; we report it)."""
        with self._lock:
            rec = self._get(appl_id)
            rec.fields[field_name] = value
            rec.lst_upd_ts = _ts(self.clock.now())

    # ---- what the SOAP layer calls -----------------------------------------------------------------
    def authenticate(self, username: str | None, password: str | None) -> str:
        if not username or self.accounts.get(username) != password:
            raise CoreFaultError("CL-E001")
        return username

    def in_maintenance(self) -> bool:
        from ..clock import in_maintenance
        return self.maintenance_forced or in_maintenance(self.clock.now())

    def handle(self, account: str, operation: str, body: dict) -> dict:
        subject = str(body.get("FILE_NO") or body.get("APPL_ID") or body.get("Application", {}).get("FILE_NO", ""))
        try:
            self._rate_check(account)
            if operation in WRITE_OPERATIONS and in_write_freeze(self.clock.now()):
                raise CoreFaultError("CL-E017")
            result = getattr(self, f"_op_{operation}")(account, body)
        except CoreFaultError as fault:
            self._log(account, operation, subject, fault.code)
            raise
        self._log(account, operation, subject, "OK")
        return result

    # ---- operations ----------------------------------------------------------------------------------
    def _op_GetApplicationByFileNumber(self, account: str, body: dict) -> dict:
        file_no = str(body.get("FILE_NO", ""))
        with self._lock:
            apps = [r for r in self.records if r.fields["FILE_NO"].ljust(12) == file_no.ljust(12)]
            if apps:
                return {"ApplicationSummary": [self._summary(r) for r in apps]}
            shell = self.shells.get(file_no.ljust(12))
            if shell:
                return {"ApplicationSummary": [{"FILE_NO": file_no, "BRANCH_CD": shell[0], "APPL_STAT": "S",
                                                "CRT_TS": shell[1]}]}
            return {"ApplicationSummary": []}

    def _op_CreateApplication(self, account: str, body: dict) -> dict:
        fields = {k: str(v) for k, v in dict(body.get("Application") or {}).items()
                  if k in FIELD_BY_NAME and v not in (None, "")}          # unknown elements: silently ignored
        self._validate(fields)
        stall = self.stalls.get(fields["FILE_NO"])
        if stall and stall.remaining > 0:
            stall.remaining -= 1
            if stall.mode == "stall_then_commit":
                time.sleep(stall.seconds)
                return self._commit(fields, account)
            result = self._commit(fields, account)
            time.sleep(stall.seconds)
            return result
        return self._commit(fields, account)

    def _op_GetApplication(self, account: str, body: dict) -> dict:
        with self._lock:
            rec = self._get(str(body.get("APPL_ID", "")))
            values = {**rec.fields, "APPL_ID": rec.appl_id, "APPL_STAT": rec.appl_stat, "CRT_TS": rec.crt_ts,
                      "LST_UPD_TS": rec.lst_upd_ts,
                      "CR_CHK_RSLT": "S3" if self.environment == "sandbox" else "P1"}
            # in the WSDL's sequence order: strict clients (zeep strict=True) reject anything else
            return {"ApplicationDetail": {k: values[k] for k in DETAIL_FIELDS if values.get(k)}}

    def _op_UpdateKYCStatus(self, account: str, body: dict) -> dict:
        status = str(body.get("KYC_STAT", ""))
        if status not in CODE_TABLES["KYC"]:
            raise CoreFaultError("CL-E031", "KYC_STAT", f"= {status}")
        with self._lock:
            rec = self._get(str(body.get("APPL_ID", "")))
            rec.fields["KYC_STAT"] = status
            now = _ts(self.clock.now())
            rec.kyc_hist.append((now, status, str(body.get("USR_ID", account))))   # appended every time
            rec.lst_upd_ts = now
            return {"APPL_ID": rec.appl_id, "KYC_STAT": status, "HIST_SEQ": len(rec.kyc_hist)}

    # ---- internals -----------------------------------------------------------------------------------
    def _validate(self, fields: dict[str, str]) -> None:
        for spec in CREATE_APPLICATION_FIELDS:
            if spec.mandatory and not fields.get(spec.name, "").strip():
                raise CoreFaultError("CL-E023", spec.name)
        if self.environment == "production-like":
            for name, (other, value) in PRODUCTION_CONDITIONAL_MANDATORY.items():
                if fields.get(other) == value and not fields.get(name):
                    raise CoreFaultError("CL-E023", name)
        for name, value in fields.items():
            spec = FIELD_BY_NAME[name]
            if len(value) > spec.length and spec.kind != "N":
                raise CoreFaultError("CL-E040", name)
            if spec.kind == "D" and not _valid_yyyymmdd(value):
                raise CoreFaultError("CL-E041", name, f"= {value}")
            if spec.kind == "N" and not _valid_number(value, spec.length):
                raise CoreFaultError("CL-E041", name, f"= {value}")
            table = FIELD_CODE_TABLE.get(name)
            if table and value not in CODE_TABLES[table]:
                raise CoreFaultError("CL-E031", name, f"= {value}")
        shell = self.shells.get(fields["FILE_NO"].ljust(12))
        if shell is None or shell[0] != fields["BRANCH_CD"]:
            raise CoreFaultError("CL-E052", fields["FILE_NO"])

    def _commit(self, fields: dict[str, str], account: str) -> dict:
        with self._lock:
            self._seq += 1
            now = _ts(self.clock.now())
            fields = {k: v for k, v in fields.items() if k not in ("ROI_PCT", "EMI_AMT")}
            rec = Record(f"AP{self._seq:010d}", fields, "K", now, now)
            self.records.append(rec)
            return {"APPL_ID": rec.appl_id, "APPL_STAT": "K"}

    def _get(self, appl_id: str) -> Record:
        for rec in self.records:
            if rec.appl_id == appl_id:
                return rec
        raise CoreFaultError("CL-E060", "APPL_ID", f"= {appl_id}")

    def _summary(self, rec: Record) -> dict[str, str]:
        values = {**rec.fields, "APPL_ID": rec.appl_id, "APPL_STAT": rec.appl_stat, "CRT_TS": rec.crt_ts}
        return {k: values[k] for k in SUMMARY_FIELDS if values.get(k)}

    def _rate_check(self, account: str) -> None:
        now = time.monotonic()
        with self._lock:
            window = self._recent.setdefault(account, deque())
            while window and now - window[0] >= 1.0:
                window.popleft()
            if len(window) >= self.rate_limit:
                raise CoreFaultError("CL-E099")
            window.append(now)

    def _log(self, account: str, operation: str, subject: str, outcome: str) -> None:
        with self._lock:
            self.access_log.append(AccessLogEntry(_ts(self.clock.now()), account, operation, subject.strip(), outcome))

    # ---- for tests and the reconciliation's "what is really there" ----------------------------------
    def applications_for(self, file_no: str) -> list[Record]:
        with self._lock:
            return [r for r in self.records if r.fields["FILE_NO"].ljust(12) == file_no.ljust(12)]


def _valid_yyyymmdd(value: str) -> bool:
    if len(value) != 8 or not value.isdigit():
        return False
    try:
        datetime.strptime(value, "%Y%m%d")
    except ValueError:
        return False
    return True


def _valid_number(value: str, digits: int) -> bool:
    whole, _, frac = value.partition(".")
    return whole.isdigit() and len(whole) <= digits and (frac == "" or (frac.isdigit() and len(frac) <= 2))
