"""Day 16 project: one night of Godavari's integration layer, end to end, offline.

    python -X utf8 code/run_integration_night.py

Part A reproduces DUPLICATE_ON_RETRY against the stand-in core: the naive client, Day 11's lookup retried at
once, and the safe writer, each under the two ways a timeout can hide a commit. Part B shows the stale
sandbox. Part C runs the night of Thursday 12 November 2026 (week 3, the run-up to M07): the 02:00 SFTP drop,
Day 11's pipeline on what was picked up, the analysts' approvals, the writes, the trackers, the reporting
copy, and at 06:00 on Friday the reconciliation report for the core-system owner.

Writes data/sources/ (Godavari's side, synthetic), data/kaagaz/ (our side), data/reconciliation-2026-11-13.md,
data/reconciliation-history.csv and data/godavari-integration-night.txt. About a minute: the stand-in stalls,
the quiet period and the client's rate limit are real seconds.
"""

from __future__ import annotations

import shutil
import sys
import time
from collections import Counter
from datetime import date
from pathlib import Path

from godavari_integration import synth_sources as ss
from godavari_integration.approvals import approved_records
from godavari_integration.clock import BusinessClock, ist
from godavari_integration.day11 import Approval, Route
from godavari_integration.in_place import OnDemandApplicant, contains_identifier, mask_pan
from godavari_integration.journal import Journal
from godavari_integration.reconcile import reconcile, render_markdown, update_history
from godavari_integration.reporting import QueryRefused, ReportingReader
from godavari_integration.sftp_batch import LocalFolderSource, PickupLedger, complete_partial, pickup, write_region_drop
from godavari_integration.soap.errors import CoreFault
from godavari_integration.soap.port import CallLog, RateLimiter
from godavari_integration.soap.zeep_client import make_port
from godavari_integration.standin.core import CoreStandIn
from godavari_integration.standin.server import running
from godavari_integration.tracker import migrate, read_workbook
from godavari_integration.translate import Mapping
from godavari_integration.writer import QUIET_PERIOD_S, SafeCoreWriter, lookup_then_retry, naive_push

CHAPTER = Path(__file__).resolve().parent.parent
DATA = CHAPTER / "data"
ACCOUNT, SECRET = "SVC_KAAGAZ_SBX", "sbx-only-not-a-real-secret"
STALLS = {"GF-25040": 1.2, "GF-25122": 1.2}       # the two files whose create reply is late tonight
DEMO_QUIET_S = 2.0                                  # production uses QUIET_PERIOD_S; the demo uses seconds
OUT: list[str] = []


def say(line: str = "") -> None:
    print(line)
    OUT.append(line)


def part_a(records: list[tuple[ss.FileFacts, dict]], mapping: Mapping) -> None:
    say("-- A. DUPLICATE_ON_RETRY, reproduced against the stand-in core --")
    say("   two creates tonight get a late reply (1.2 s against a 0.5 s client timeout):")
    say("   commit_then_stall = the core commits, the reply is lost; stall_then_commit = the core commits after")
    say("   the client gave up. Same ten approved files each time, fresh sandbox each time.")
    say(f"   {'mode':<18} {'client':<26} {'applications':>12} {'files duplicated':>17}")
    appr = Approval("GF-AN-1142", date(2026, 11, 12))
    writable = [(f, r) for f, r in records if _maps(mapping, r)]
    for mode in ("commit_then_stall", "stall_then_commit"):
        for client in ("naive (the 2022 vendor)", "lookup, then retry at once", "safe writer"):
            clock = BusinessClock(ist(2026, 11, 12, 16, 10))
            core = CoreStandIn(clock=clock)
            for f, _ in writable:
                core.register_file(f.file_no, f.branch_cd)
            for fno, secs in STALLS.items():
                core.plant_stall(fno, mode, secs)
            with running(core) as url:
                port = make_port("zeep", url, ACCOUNT, SECRET, timeout=0.5, limiter=RateLimiter(4), clock=clock)
                journal = Journal()
                writer = SafeCoreWriter(port, mapping, journal, clock, quiet_period_s=DEMO_QUIET_S)
                for f, rec in writable:
                    if client.startswith("naive"):
                        naive_push(port, mapping, rec)
                    elif client.startswith("lookup"):
                        lookup_then_retry(port, mapping, rec, f.bundle.branch, f.result.route, appr)
                    else:
                        writer.push(rec, f.bundle.branch, f.result.route, appr)
                if client == "safe writer":
                    time.sleep(DEMO_QUIET_S + 0.2)
                    writer.resolve_unknowns()
                time.sleep(1.3)                 # let any late commit land before counting
            dup = sum(1 for f, _ in writable if len(core.applications_for(f.file_no)) > 1)
            say(f"   {mode:<18} {client:<26} {len(core.records):>12} {dup:>17}")
    say()


def _maps(mapping: Mapping, rec: dict) -> bool:
    try:
        mapping.to_core(rec)
        return True
    except ValueError:
        return False


def part_b(records: list[tuple[ss.FileFacts, dict]], mapping: Mapping) -> None:
    say("-- B. The stale sandbox: the same create, July's rules against August's --")
    f, rec = next((f, r) for f, r in records if f.bundle.product == "two-wheeler" and _maps(mapping, r))
    payload = mapping.to_core(rec)
    payload.pop("DLR_CD")                      # what mapping 1.2.0 sent: the WSDL says DLR_CD is optional
    for env in ("sandbox", "production-like"):
        core = CoreStandIn(environment=env)
        core.register_file(f.file_no, f.branch_cd)
        with running(core) as url:
            port = make_port("raw", url, ACCOUNT, SECRET, timeout=2.0)
            try:
                appl = port.create_application(payload)
                say(f"   {env:<16} {f.file_no} without DLR_CD -> created {appl}")
            except CoreFault as fault:
                say(f"   {env:<16} {f.file_no} without DLR_CD -> {fault.faultstring}")
    say("   mapping 1.3.0 sends DLR_CD for every two-wheeler file; known drift SBX-01 records why (contracts/)")
    say()


def main() -> int:
    started = time.monotonic()
    say("== Day 16 · integrating with what exists: one night of Godavari's integration, offline ==")
    mapping = Mapping()
    record = mapping.check_signoff()
    problems = mapping.problems()
    ours = sum(1 for fm in mapping.fields.values() if fm.ours)
    say(f"mapping {mapping.version} ({record['status']} by {record['reviewed_by']}, {record['reviewed_on']}): "
        f"{len(mapping.fields)} core fields, {ours} mapped, {len(mapping.fields) - ours} not ours; problems: {len(problems)}")
    for p in problems:
        say(f"   {p}")
    facts = ss.hyderabad_files()
    records = approved_records(facts, mapping, ACCOUNT)
    say(f"input: Day 7's sample through Day 11's pipeline: {len(ss.night_files(facts))} Kukatpally files, "
        f"{len(records)} routed ready or review and approved by the analysts")
    say()
    part_a(records, mapping)
    part_b(records, mapping)

    # ---------------------------------------------------------------------------------------------------
    say("-- C. The night of Thursday 12 November 2026 --")
    for sub in ("sources", "kaagaz"):
        shutil.rmtree(DATA / sub, ignore_errors=True)
    src, ours_dir = DATA / "sources", DATA / "kaagaz"
    ours_dir.mkdir(parents=True)
    clock = BusinessClock(ist(2026, 11, 12, 2, 0))
    sandbox = CoreStandIn(environment="sandbox", clock=clock)
    night = sorted(ss.night_files(facts), key=lambda x: x.file_no)
    drops = {d.file_no: d for d in ss.drop_files(night)}
    late = ss.drop_files([facts["GF-25035"]])
    write_region_drop(src / "sftp", "HYD", ss.NIGHT, list(drops.values()), partial=["GF-25129"], late=late)
    for f in night:
        sandbox.register_file(f.file_no, f.branch_cd, clock.now())
    say(f"02:00 Godavari's job (simulated): {len(night)} files to HYD/20261112 with manifest and .done; "
        f"{len(night)} shells registered")
    source, ledger = LocalFolderSource(src / "sftp"), PickupLedger(ours_dir / "pickup-ledger.sqlite")
    staging = ours_dir / "staging"
    pickups = []
    for at, label in ((ist(2026, 11, 12, 2, 30), "02:30 poll"), (ist(2026, 11, 12, 3, 30), "03:30 poll"),
                      (ist(2026, 11, 12, 4, 10), "04:10 re-run")):
        clock.set(at)
        if label.startswith("03:30"):
            complete_partial(src / "sftp", "HYD", ss.NIGHT, drops["GF-25129"])
        rep = pickup(source, "HYD", ss.NIGHT, staging, ledger)
        pickups.append(rep)
        counts = Counter(i.status for i in rep.items)
        say(f"{label}: " + ", ".join(f"{k.lower()} {v}" for k, v in sorted(counts.items())))
        for i in rep.items:
            if i.status in ("PARTIAL", "LATE"):
                say(f"   {i.file_no}: {i.detail}")
    picked = {i.file_no for r in pickups for i in r.picked()}
    say(f"picked up and staged: {len(picked)} files, each under a temporary name, hash-checked, then renamed")
    say()

    # ---- the day: approvals and writes ----
    owner_keyed = "GF-25010"
    clock.set(ist(2026, 11, 12, 11, 0))
    sandbox.seed_legacy([{"FILE_NO": owner_keyed, "BRANCH_CD": "KKP01", "PROD_CD": "GL", "APPL_STAT": "K",
                          "CRT_TS": "20261112110000", "ENTRY_USR": "GF-IT-0007", "LOAN_AMT": "190000"}])
    say(f"11:00 the owner keys {owner_keyed} by hand in the sandbox, to see what a shell looks like")
    for fno, secs in STALLS.items():
        sandbox.plant_stall(fno, "commit_then_stall" if fno == "GF-25040" else "stall_then_commit", secs)
    journal, calls = Journal(ours_dir / "journal.sqlite"), CallLog()
    with running(sandbox) as url:
        port = make_port("zeep", url, ACCOUNT, SECRET, timeout=0.5, limiter=RateLimiter(4), log=calls, clock=clock)
        writer = SafeCoreWriter(port, mapping, journal, clock, quiet_period_s=DEMO_QUIET_S)
        appr = Approval("GF-AN-1142", date(2026, 11, 12))
        last = "GF-25179"
        clock.set(ist(2026, 11, 12, 16, 10))
        say("16:10 the analysts' approved files go to the writer:")
        for f, rec in records:
            if f.file_no == last or f.file_no not in picked:
                continue
            out = writer.push(rec, f.bundle.branch, f.result.route, appr)
            say(f"   {f.file_no} {out.state.lower():<16} {out.appl_id or '':<13} {out.note[:70]}")
        clock.set(ist(2026, 11, 12, 17, 40))
        f, rec = next((f, r) for f, r in records if f.file_no == last)
        out = writer.push(rec, f.bundle.branch, f.result.route, appr)
        say(f"17:40 {last} approved late: {out.state.lower()}: {out.note}")
        time.sleep(DEMO_QUIET_S + 0.2)
        clock.set(ist(2026, 11, 12, 17, 50))
        say(f"17:50 resolving no-reply writes (quiet period {DEMO_QUIET_S:.0f} s here; {QUIET_PERIOD_S:.0f} s in production):")
        for o in writer.resolve_unknowns():
            say(f"   {o.file_no} {o.state.lower():<16} {o.appl_id or '':<13} {o.note}")
        clock.set(ist(2026, 11, 12, 20, 5))
        out = writer.push(rec, f.bundle.branch, f.result.route, appr)
        say(f"20:05 window open again: {last} {out.state.lower()} {out.appl_id}")
        say()

        # ---- data in place: an analyst opens a file ----
        clock.set(ist(2026, 11, 12, 16, 30))
        reader_pii = OnDemandApplicant(port, mapping, clock)
        shown = reader_pii.view("GF-25001", "GF-AN-1142", "analyst_review")
        reader_pii.view("GF-25001", "GF-AN-1142", "analyst_review")
        say(f"on demand: GF-AN-1142 opens GF-25001; PAN read from the core and shown as {mask_pan(shown['PAN_NO'])} "
            f"in every log; 2 views logged ({sum(v.cache_hit for v in reader_pii.views)} from the 900 s cache)")
        try:
            reader_pii.view("GF-25001", "GF-AN-1142", "model_context")
        except PermissionError as exc:
            say(f"on demand: refused: {exc}")
        say()

        # ---- the trackers and the reporting copy ----
        status = ss.production_status(facts)
        db = ss.build_reporting_db(src / "reporting.sqlite", facts, status)
        trackers = ss.build_trackers(src / "trackers", facts)
        reads = [read_workbook(p) for p in trackers]
        migration = migrate(reads)
        say(f"trackers: {len(trackers)} workbooks, {migration.rows_read} rows -> {len(migration.items)} queue items; "
            f"{len(migration.needs_a_person)} for a person, {len(migration.conflicts)} conflict, "
            f"{len(migration.merged_duplicates)} duplicate row merged")
        for r in reads:
            say(f"   {r.workbook}: header on row {r.header_row}, {len(r.columns)} columns recognised, "
                f"{len(r.rows)} rows" + (f", skipped: {'; '.join(r.skipped)}" if r.skipped else ""))
        reporting = ReportingReader(db)
        for sql in ("SELECT APPL_NM, PAN_NO FROM APPL_MST WHERE FILE_NO = 'GF-25001'",
                    "UPDATE APPL_MST SET APPL_STAT = 'K' WHERE FILE_NO = 'GF-25037'"):
            try:
                reporting.query(sql, purpose="demonstration")
            except QueryRefused as exc:
                say(f"reporting copy refused: {sql.split(' WHERE')[0]} -> {str(exc).split(' (')[0]}")
        reporting.log.entries.clear()

        # ---- Friday 02:00: the next drop ----
        clock.set(ist(2026, 11, 13, 2, 0))
        rescan = ss.drop_files([facts["GF-25040"]])[0]
        rescan = type(rescan)(rescan.file_no, rescan.branch_cd, rescan.content.replace(b"%%EOF", b"%% re-scanned declaration\n%%EOF"), rescan.pages + 1)
        write_region_drop(src / "sftp", "HYD", date(2026, 11, 13), late + [rescan])
        clock.set(ist(2026, 11, 13, 2, 30))
        rep2 = pickup(source, "HYD", date(2026, 11, 13), staging, ledger)
        pickups.append(rep2)
        say("Fri 02:30 poll: " + "; ".join(f"{i.file_no} {i.status.lower()}" + (f" ({i.detail})" if i.detail else "")
                                           for i in rep2.items))
        say()

        # ---- Friday 06:00: reconciliation, as a separate job with its own read-only client ----
        clock.set(ist(2026, 11, 13, 6, 0))
        our_calls = CallLog(list(calls.records))              # the day's calls, frozen before the job reads
        access_log = list(sandbox.access_log)                 # the owner's export, taken at the same moment
        recon_port = make_port("raw", url, ACCOUNT, SECRET, timeout=5.0, limiter=RateLimiter(4), clock=clock)
        rec = reconcile(run_date=date(2026, 11, 13), journal=journal, port=recon_port, our_calls=our_calls,
                        access_log=access_log, account=ACCOUNT, pickups=pickups, migration=migration,
                        reader=reporting, mapping=mapping)
    not_checked = [
        "production writes: there are none yet; live writes start 8 December (M14) if this history is clean",
        "credit-check results in the sandbox: computed on July's rules, so ignored (finding A5)",
        "applications carrying our EXT_REF on files we never journaled: needs a query on the sandbox's own "
        "tables, which only you can run; requested for Monday",
        "the WhatsApp pages (finding A3): they never reach any system this report can read",
    ]
    history = update_history(DATA / "reconciliation-history.csv", rec.run_date, rec.clean,
                             f"{sum(1 for r in journal.all() if r.state == 'CONFIRMED')} confirmed; "
                             f"{len(journal.all())} journaled")
    report = render_markdown(rec, not_checked, history)
    (DATA / "reconciliation-2026-11-13.md").write_text(report, encoding="utf-8", newline="\n")
    dump = journal.dump_text() + "\n" + report + "\n".join(OUT)
    pans = [ff.truth.fields["pan"] for ff in facts.values()]
    names = [ff.truth.fields["applicant_name"] for ff in facts.values()]
    leaked = contains_identifier(dump, pans + names)
    say("06:00 reconciliation for the core-system owner: " + ("CLEAN" if rec.clean else "NOT CLEAN"))
    for s in rec.sections:
        say(f"   {s.title}: {'ok' if s.ok else 'NOT OK'}")
        for line in s.lines[:8]:
            say(f"      {line}")
        if s.table and not s.title.startswith("2."):
            for row in s.table[:8]:
                say("      | " + " | ".join(row))
        elif s.table:
            for row in s.table:
                say(f"      {row[0]} {row[2]}: we sent {row[3]}, core now {row[4]}")
    say(f"customer names or PANs in our journal, our log lines and the report: {len(leaked)}")
    say()
    say(f"wrote data/reconciliation-2026-11-13.md, data/reconciliation-history.csv, data/kaagaz/, data/sources/")
    say(f"elapsed: {time.monotonic() - started:.1f} s")
    (DATA / "godavari-integration-night.txt").write_text("\n".join(OUT) + "\n", encoding="utf-8", newline="\n")
    return 0 if rec.clean and not leaked else 1


if __name__ == "__main__":
    raise SystemExit(main())
