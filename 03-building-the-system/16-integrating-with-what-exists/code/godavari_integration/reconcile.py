"""The nightly reconciliation: the report the core-system owner reads with his coffee, and trusts.

Why he can trust it:
  * It reads his system, not our memory. Every write in our journal is looked up live in the core, and our
    call log is compared, operation by operation, with the access log he exports for our account.
  * Every count ties out, and every exception is a file number with its evidence, not a percentage.
  * It is deterministic: the same inputs give the same report, and re-running it for a date replaces that
    date's line in the history instead of adding one.
  * It says what it could not check, and how fresh each source was.
  * It carries the job's version, the mapping's version and fingerprint, and the SQL it ran.

It writes nothing anywhere except our own report and history files.
"""

from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any

from .clock import in_write_freeze, IST
from .corespec import CODE_TABLES, WRITE_OPERATIONS
from .journal import CONFIRMED, DEFERRED, DUPLICATE_IN_CORE, EXISTS_NOT_OURS, FAILED, PENDING, UNKNOWN, Journal
from .reporting import ReportingReader
from .sftp_batch import PickupReport
from .soap.errors import CoreError
from .soap.port import CallLog, CorePort
from .standin.core import AccessLogEntry
from .tracker import Migration
from .translate import Mapping

JOB_VERSION = "reconcile 0.6.0"
COMPARED_FIELDS = ("PROD_CD", "BRANCH_CD", "LOAN_AMT", "TENOR_MM", "MNTH_INC", "CUST_FLG_3", "KYC_STAT", "DLR_CD")
CORE_EXPECTED_FOR_TRACKER = {
    "keyed": {"K", "B", "Q", "A", "R"}, "docs_checked": {"K", "B", "Q", "A", "R"}, "verified": {"K", "B", "A"},
    "in_credit_batch": {"B", "A", "R"}, "memo_written": {"B", "A", "R"}, "query_with_senior": {"K", "Q", "B"},
}


@dataclass
class Section:
    title: str
    ok: bool
    lines: list[str] = field(default_factory=list)
    table: list[list[str]] = field(default_factory=list)


@dataclass
class Reconciliation:
    run_date: date
    sections: list[Section]
    sql: list[tuple[str, str, int]]
    header: list[str]

    @property
    def clean(self) -> bool:
        return all(s.ok for s in self.sections)


def _writes(journal: Journal, port: CorePort) -> tuple[Section, Section]:
    rows = journal.all()
    by_state = Counter(r.state for r in rows)
    writes = Section("1. Our writes to the sandbox, checked against the core", True)
    writes.lines.append("journal: " + ", ".join(f"{s.lower()} {by_state[s]}" for s in
                        (CONFIRMED, EXISTS_NOT_OURS, DEFERRED, PENDING, UNKNOWN, DUPLICATE_IN_CORE, FAILED) if by_state[s]))
    drift = Section("2. Fields changed in the core after our write", True)
    dupes, wrong_ref, missing = [], [], []
    for r in rows:
        if r.state not in (CONFIRMED, EXISTS_NOT_OURS, DUPLICATE_IN_CORE):
            continue
        try:
            apps = [s for s in port.get_by_file_number(r.file_no) if not s.is_shell]
        except CoreError as exc:
            writes.lines.append(f"{r.file_no}: lookup failed ({exc}); not checked tonight")
            writes.ok = False
            continue
        if len(apps) > 1:
            dupes.append(f"{r.file_no}: {len(apps)} applications ({', '.join(a.appl_id for a in apps)})")
            continue
        if not apps:
            missing.append(f"{r.file_no}: journal says {r.state} {r.appl_id}, the core has no application")
            continue
        app = apps[0]
        if r.state == CONFIRMED and app.ext_ref != r.key:
            wrong_ref.append(f"{r.file_no}: EXT_REF is {app.ext_ref or 'empty'}, expected our key {r.key}")
        if r.state == CONFIRMED:
            detail = port.get_application(app.appl_id)
            for f in COMPARED_FIELDS:
                sent, now = r.business.get(f, ""), detail.get(f, "")
                if sent and now and sent != now:
                    drift.table.append([r.file_no, app.appl_id, f, sent, now, detail.get("LST_UPD_TS", "")])
    checked = sum(1 for r in rows if r.state in (CONFIRMED, EXISTS_NOT_OURS))
    writes.lines.append(f"looked up live: {checked} files; exactly one application each: {checked - len(dupes) - len(missing)}")
    writes.lines.append(f"duplicates: {len(dupes)}" + ("" if not dupes else " -> " + "; ".join(dupes)))
    writes.lines.append(f"journal says written, core disagrees: {len(missing) + len(wrong_ref)}")
    writes.lines += missing + wrong_ref
    for r in rows:
        if r.state == EXISTS_NOT_OURS:
            writes.lines.append(f"{r.file_no}: already keyed by someone else ({r.appl_id}, no Kaagaz EXT_REF); "
                                "we did not create a second one")
        if r.state in (UNKNOWN, FAILED, DUPLICATE_IN_CORE, PENDING, DEFERRED):
            writes.lines.append(f"{r.file_no}: {r.state.lower()}: {r.note}")
    writes.ok = not dupes and not missing and not wrong_ref and by_state[UNKNOWN] == 0 and by_state[DUPLICATE_IN_CORE] == 0
    if not drift.table:
        drift.lines.append("none")
    else:
        drift.lines.append("expected when a branch user edits on the core screen; listed so nobody is surprised")
    return writes, drift


def _calls(ours: CallLog, theirs: list[AccessLogEntry], account: str, journal: Journal) -> Section:
    sec = Section("3. Our call log against your access log for " + account, True)
    mine = Counter((c.operation, "OK" if c.outcome == "OK" else c.outcome) for c in ours.records
                   if c.outcome not in ("NOT_SENT", "UNAVAILABLE", "REFUSED_LOCALLY"))
    his = Counter((e.operation, e.outcome) for e in theirs if e.account == account)
    keys = sorted(set(mine) | set(his))
    sec.table.append(["operation", "outcome", "our log", "your log", "difference"])
    for k in keys:
        a, b = mine.get(k, 0), his.get(k, 0)
        # a call we logged as AMBIGUOUS is one the core logged as OK: that is the point of the word
        sec.table.append([k[0], k[1], str(a), str(b), str(a - b)])
    ambiguous = sum(v for (op, out), v in mine.items() if out in ("AMBIGUOUS", "UNREADABLE"))
    ok_creates_his = Counter(e.subject for e in theirs if e.account == account and e.operation == "CreateApplication" and e.outcome == "OK")
    double = [f"{fno} ({n} creates)" for fno, n in ok_creates_his.items() if n > 1]
    total_mine = sum(mine.values())
    total_his = sum(his.values())
    sec.lines.append(f"calls: ours {total_mine}, yours {total_his}; {ambiguous} we logged as no-reply, which your log "
                     "records as OK (the core did the work; we did not hear back)")
    in_window = [e for e in theirs if e.account == account and e.operation in WRITE_OPERATIONS
                 and in_write_freeze(datetime.strptime(e.at, "%Y%m%d%H%M%S").replace(tzinfo=IST))]
    sec.lines.append(f"write calls between 17:30 and the end of the batch: {len(in_window)}")
    sec.lines.append(f"files with more than one successful CreateApplication in your log: {len(double)}"
                     + ("" if not double else " -> " + ", ".join(double)))
    busy = his.get(("GetApplicationByFileNumber", "CL-E099"), 0) + his.get(("CreateApplication", "CL-E099"), 0)
    sec.lines.append(f"CL-E099 busy faults: {busy}")
    unexplained = total_mine - ambiguous - (total_his - ambiguous)
    sec.ok = not in_window and not double and unexplained == 0 and total_mine == total_his
    return sec


def _sftp(reports: list[PickupReport]) -> Section:
    sec = Section("4. The 02:00 SFTP batch", True)
    sec.table.append(["poll", "manifest rows", "picked", "re-scan", "already picked", "partial", "late", "missing", "corrupt"])
    for i, r in enumerate(reports, 1):
        sec.table.append([f"{i}: {r.region} {r.night:%d %b}", str(r.manifest_rows), str(r.count("PICKED")),
                          str(r.count("RESCAN")), str(r.count("ALREADY_PICKED")), str(r.count("PARTIAL")),
                          str(r.count("LATE")), str(r.count("MISSING")), str(r.count("CORRUPT"))])
    last = reports[-1] if reports else None
    if last:
        for item in last.items:
            if item.status in ("PARTIAL", "LATE", "MISSING", "CORRUPT", "RESCAN"):
                sec.lines.append(f"{item.file_no}: {item.status.lower()}: {item.detail}")
        sec.ok = last.count("MISSING") == 0 and last.count("CORRUPT") == 0 and last.count("PARTIAL") == 0
    return sec


def _tracker(migration: Migration, reader: ReportingReader) -> Section:
    sec = Section("5. The analysts' trackers against production (reporting copy)", True)
    rows = reader.query("SELECT r.FILE_NO, a.APPL_STAT FROM FILE_REG r LEFT JOIN APPL_MST a ON a.FILE_NO = r.FILE_NO",
                        purpose="tracker reconciliation: core status per registered file")
    core = {r["FILE_NO"]: (r["APPL_STAT"] or "S") for r in rows}
    sec.lines.append(f"tracker rows read: {migration.rows_read}; queue items: {len(migration.items)}; "
                     f"rows for a person: {len(migration.needs_a_person)}; conflicts: {len(migration.conflicts)}; "
                     f"duplicate rows merged: {len(migration.merged_duplicates)}")
    sec.lines += [f"for a person: {x}" for x in migration.needs_a_person]
    sec.lines += [f"conflict: {x}" for x in migration.conflicts]
    found = 0
    for fno, item in sorted(migration.items.items()):
        status = core.get(fno)
        if status is None:
            sec.table.append([fno, item.state, "not registered", "the core has never seen this file number"])
            found += 1
            continue
        expected = CORE_EXPECTED_FOR_TRACKER.get(item.state)
        if expected and status not in expected:
            sec.table.append([fno, item.state, status, f"tracker says {item.state.replace('_', ' ')}, the core says "
                              f"{_status_word(status)}"])
            found += 1
    if sec.table:
        sec.table.insert(0, ["file", "tracker", "core", "what to check"])
    sec.lines.append(f"tracker and core disagree: {found}")
    sec.ok = True          # disagreements are for the team leads, not a failure of the integration
    return sec


def _status_word(code: str) -> str:
    return CODE_TABLES["APPLSTAT"].get(code, code).lower()


def _mapping_drift(mapping: Mapping, reader: ReportingReader) -> Section:
    sec = Section("6. Codes in your CODE_MST that the mapping does not know", True)
    rows = reader.query("SELECT CODE_TYP, CODE_VAL, CODE_DESC FROM CODE_MST WHERE ACTIVE_FLG = 'Y'",
                        purpose="mapping drift: active codes")
    known = {t: set(v.values()) for t, v in mapping.codes.items()}
    unknown = [r for r in rows if r["CODE_TYP"] in known and r["CODE_VAL"] not in known[r["CODE_TYP"]]]
    for r in unknown:
        sec.lines.append(f"{r['CODE_TYP']} {r['CODE_VAL']} '{r['CODE_DESC']}': not in mapping {mapping.version}; "
                         "anything reading it fails closed until the owner reviews the meaning")
    if not unknown:
        sec.lines.append("none")
    sec.ok = True          # a finding for the mapping owner; reads fail closed meanwhile
    return sec


def update_history(path: Path, run_date: date, clean: bool, summary: str) -> list[dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    if path.exists():
        with path.open(newline="", encoding="utf-8") as fh:
            rows = {r["date"]: r for r in csv.DictReader(fh)}
    rows[run_date.isoformat()] = {"date": run_date.isoformat(), "clean": "yes" if clean else "no", "summary": summary}
    ordered = [rows[k] for k in sorted(rows)]
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["date", "clean", "summary"], lineterminator="\n")
        w.writeheader()
        w.writerows(ordered)
    return ordered


def reconcile(*, run_date: date, journal: Journal, port: CorePort, our_calls: CallLog, access_log: list[AccessLogEntry],
              account: str, pickups: list[PickupReport], migration: Migration, reader: ReportingReader,
              mapping: Mapping, extra_header: list[str] | None = None) -> Reconciliation:
    writes, drift = _writes(journal, port)
    sections = [writes, drift, _calls(our_calls, access_log, account, journal), _sftp(pickups),
                _tracker(migration, reader), _mapping_drift(mapping, reader)]
    refreshed = reader.last_refresh()
    header = [f"job {JOB_VERSION}; mapping {mapping.version} (fingerprint {mapping.fingerprint()[:12]})",
              f"sources: sandbox core (live lookups, read-only); your access log export; our journal and call log; "
              f"SFTP manifests; three tracker workbooks; reporting copy refreshed {refreshed:%d %b %Y %H:%M}"]
    return Reconciliation(run_date, sections, list(reader.log.entries), header + (extra_header or []))


def render_markdown(rec: Reconciliation, not_checked: list[str], history: list[dict[str, str]]) -> str:
    out = [f"# Integration reconciliation · {rec.run_date:%A %d %B %Y}", "",
           f"**For:** the core-system owner. **Overall:** {'CLEAN' if rec.clean else 'NOT CLEAN'}.", ""]
    out += [f"- {h}" for h in rec.header]
    out.append("")
    for s in rec.sections:
        out += [f"## {s.title} · {'ok' if s.ok else 'NOT OK'}", ""]
        out += [f"- {line}" for line in s.lines]
        if s.table:
            out.append("")
            head, *body = s.table if s.title.startswith(("3.", "4.", "5.")) else (
                [["file", "application", "field", "we sent", "core now", "changed at"]] + s.table)
            out.append("| " + " | ".join(head) + " |")
            out.append("|" + "---|" * len(head))
            out += ["| " + " | ".join(row) + " |" for row in body]
        out.append("")
    clean_run = 0
    for row in reversed(history):
        if row["clean"] != "yes":
            break
        clean_run += 1
    out += ["## 7. The month of logged calls", "",
            f"- consecutive clean nights in the history file: {clean_run} (your condition: a month, before live writes "
            "on 8 December, M14)", ""]
    out += ["## 8. What this report could not check", ""] + [f"- {x}" for x in not_checked] + [""]
    out += ["## Appendix: the queries this job ran on the reporting copy", ""]
    out += [f"- {purpose}: `{sql}` ({n} row{'' if n == 1 else 's'})" for purpose, sql, n in rec.sql]
    return "\n".join(out) + "\n"


__all__ = ["Reconciliation", "reconcile", "render_markdown", "update_history", "Any"]
