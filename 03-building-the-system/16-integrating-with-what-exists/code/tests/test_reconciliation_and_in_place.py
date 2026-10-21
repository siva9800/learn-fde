"""The reconciliation the owner trusts, and the data we read in place instead of copying."""

from __future__ import annotations

import pytest

from godavari_integration import synth_sources as ss
from godavari_integration.clock import ist
from godavari_integration.day11 import Approval
from godavari_integration.in_place import OnDemandApplicant, mask_pan, safe_for_log
from godavari_integration.journal import Journal
from godavari_integration.reconcile import reconcile, render_markdown, update_history
from godavari_integration.reporting import ReportingReader
from godavari_integration.soap.port import CallLog
from godavari_integration.tracker import migrate, read_workbook
from godavari_integration.writer import SafeCoreWriter, naive_push

from conftest import ACCOUNT

APPROVAL = Approval("GF-AN-1142", ist(2026, 11, 12).date())


@pytest.fixture(scope="module")
def side_sources(tmp_path_factory, facts):
    root = tmp_path_factory.mktemp("src")
    db = ss.build_reporting_db(root / "reporting.sqlite", facts, ss.production_status(facts))
    migration = migrate([read_workbook(p) for p in ss.build_trackers(root / "trackers", facts)])
    return db, migration


def _night(standin, port_for, mapping, writable, clock, *, naive_one=False):
    core, url = standin()
    files = writable[:4]
    for f, _ in files:
        core.register_file(f.file_no, f.branch_cd)
    calls, journal = CallLog(), Journal()
    port = port_for("zeep", url, log=calls)
    writer = SafeCoreWriter(port, mapping, journal, clock)
    for f, rec in files:
        writer.push(rec, f.bundle.branch, f.result.route, APPROVAL)
    if naive_one:                                # someone runs the old script once
        naive_push(port, mapping, files[0][1])
    return core, url, calls, journal


def _reconcile(core, url, calls, journal, port_for, mapping, side_sources):
    db, migration = side_sources
    frozen, access = CallLog(list(calls.records)), list(core.access_log)
    return reconcile(run_date=ist(2026, 11, 13).date(), journal=journal, port=port_for("raw", url),
                     our_calls=frozen, access_log=access, account=ACCOUNT, pickups=[], migration=migration,
                     reader=ReportingReader(db), mapping=mapping)


def test_a_clean_night_reconciles_clean(standin, port_for, mapping, writable, clock, side_sources):
    core, url, calls, journal = _night(standin, port_for, mapping, writable, clock)
    rec = _reconcile(core, url, calls, journal, port_for, mapping, side_sources)
    assert rec.clean, [(s.title, s.lines) for s in rec.sections if not s.ok]


def test_a_duplicate_is_named_by_file_and_the_night_is_not_clean(standin, port_for, mapping, writable, clock, side_sources):
    core, url, calls, journal = _night(standin, port_for, mapping, writable, clock, naive_one=True)
    rec = _reconcile(core, url, calls, journal, port_for, mapping, side_sources)
    assert not rec.clean
    writes = rec.sections[0]
    fno = writable[0][0].file_no
    assert any(line.startswith("duplicates: 1") and fno in line for line in writes.lines)
    assert any(f"{fno} (2 creates)" in line for line in rec.sections[2].lines)      # from his own access log


def test_a_field_changed_on_the_core_screen_is_listed_not_hidden(standin, port_for, mapping, writable, clock, side_sources):
    core, url, calls, journal = _night(standin, port_for, mapping, writable, clock)
    f = writable[1][0]
    [app] = core.applications_for(f.file_no)
    core.edit_on_core_screen(app.appl_id, "LOAN_AMT", "85000")
    rec = _reconcile(core, url, calls, journal, port_for, mapping, side_sources)
    assert [row[:5] for row in rec.sections[1].table] == [[f.file_no, app.appl_id, "LOAN_AMT",
                                                           journal.get(writable[1][1]["idempotency_key"]).business["LOAN_AMT"], "85000"]]


def test_the_tracker_and_mapping_findings_come_from_the_reporting_copy(standin, port_for, mapping, writable, clock, side_sources):
    core, url, calls, journal = _night(standin, port_for, mapping, writable, clock)
    rec = _reconcile(core, url, calls, journal, port_for, mapping, side_sources)
    tracker, codes = rec.sections[4], rec.sections[5]
    assert {row[0] for row in tracker.table[1:]} == {"GF-25037", "GF-25147"}
    assert any("APPLSTAT H" in line for line in codes.lines)
    assert all("APPL_NM" not in sql for _, sql, _ in rec.sql)


def test_history_is_one_line_per_date_however_often_the_job_runs(tmp_path):
    path = tmp_path / "history.csv"
    for clean in (False, True, True):
        rows = update_history(path, ist(2026, 11, 13).date(), clean, "x")
    assert len(rows) == 1 and rows[0]["clean"] == "yes"


def test_the_report_holds_no_identifiers(standin, port_for, mapping, writable, clock, side_sources):
    core, url, calls, journal = _night(standin, port_for, mapping, writable, clock)
    report = render_markdown(_reconcile(core, url, calls, journal, port_for, mapping, side_sources), [], [])
    for _, rec in writable:
        assert rec["pan"] not in report and rec["applicant_name"] not in report


def test_identifiers_are_read_on_demand_logged_every_time_and_forgotten(standin, port_for, mapping, writable, clock):
    core, url, _, _ = _night(standin, port_for, mapping, writable, clock)
    f, rec = writable[0]
    t = {"now": 0.0}
    reader = OnDemandApplicant(port_for("raw", url), mapping, clock, ttl_s=900, now=lambda: t["now"])
    assert reader.view(f.file_no, "GF-AN-1142", "analyst_review")["PAN_NO"] == rec["pan"]
    reads_before = len(core.access_log)
    reader.view(f.file_no, "GF-AN-1142", "analyst_review")
    assert len(core.access_log) == reads_before and [v.cache_hit for v in reader.views] == [False, True]
    t["now"] = 901.0
    assert reader.purge() == 1 and reader.cached_files() == []
    reader.view(f.file_no, "GF-AN-1142", "analyst_review")
    assert len(core.access_log) > reads_before                     # expired: read from the core again
    with pytest.raises(PermissionError):
        reader.view(f.file_no, "GF-AN-1142", "model_context")
    with pytest.raises(PermissionError):
        reader.view(f.file_no, "", "analyst_review")


def test_logs_get_masks_not_identifiers(mapping, writable):
    _, rec = writable[0]
    core = mapping.to_core(rec)
    safe = safe_for_log(mapping, core)
    assert safe["PAN_NO"] == "PAN " + mask_pan(rec["pan"]) and rec["pan"] not in str(safe)
    assert safe["APPL_NM"] == "<APPL_NM withheld>" and safe["LOAN_AMT"] == core["LOAN_AMT"]
