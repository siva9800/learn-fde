"""The heart of the chapter: a core with no idempotency keys, and a writer that never makes a second loan."""

from __future__ import annotations

import time

import pytest

from godavari_integration.clock import BusinessClock, ist
from godavari_integration.day11 import Approval
from godavari_integration.journal import (CONFIRMED, DEFERRED, DUPLICATE_IN_CORE, EXISTS_NOT_OURS, FAILED, PENDING,
                                          UNKNOWN, Journal)
from godavari_integration.writer import SafeCoreWriter, lookup_then_retry, naive_push

APPROVAL = Approval("GF-AN-1142", ist(2026, 11, 12).date())
STALL, TIMEOUT, QUIET = 0.6, 0.3, 0.9


def _setup(standin, port_for, writable, mode=None, n=3, **kw):
    core, url = standin(**kw)
    files = writable[:n]
    for f, _ in files:
        core.register_file(f.file_no, f.branch_cd)
    if mode:
        core.plant_stall(files[0][0].file_no, mode, STALL)
    return core, port_for("zeep", url, timeout=TIMEOUT), files


def _settle() -> None:
    time.sleep(STALL + 0.2)                     # let a late commit land before counting


def test_naive_retry_creates_a_duplicate_loan_record(standin, port_for, mapping, writable):
    core, port, files = _setup(standin, port_for, writable, "commit_then_stall")
    for _, rec in files:
        naive_push(port, mapping, rec, sleep=lambda s: None)
    _settle()
    assert len(core.applications_for(files[0][0].file_no)) == 2       # the 2022 weekend, in miniature
    assert len(core.records) == len(files) + 1


def test_lookup_then_retry_survives_a_lost_reply(standin, port_for, mapping, writable):
    core, port, files = _setup(standin, port_for, writable, "commit_then_stall")
    for f, rec in files:
        lookup_then_retry(port, mapping, rec, f.bundle.branch, f.result.route, APPROVAL)
    _settle()
    assert all(len(core.applications_for(f.file_no)) == 1 for f, _ in files)


def test_lookup_then_retry_is_not_enough_when_the_commit_is_late(standin, port_for, mapping, writable):
    core, port, files = _setup(standin, port_for, writable, "stall_then_commit")
    for f, rec in files:
        lookup_then_retry(port, mapping, rec, f.bundle.branch, f.result.route, APPROVAL)
    _settle()
    assert len(core.applications_for(files[0][0].file_no)) == 2       # the lookup ran before the commit


@pytest.mark.parametrize("mode", ["commit_then_stall", "stall_then_commit"])
def test_the_safe_writer_never_duplicates(mode, standin, port_for, mapping, writable, clock):
    core, port, files = _setup(standin, port_for, writable, mode)
    journal = Journal()
    writer = SafeCoreWriter(port, mapping, journal, clock, quiet_period_s=QUIET, sleep=lambda s: None)
    outcomes = [writer.push(rec, f.bundle.branch, f.result.route, APPROVAL) for f, rec in files]
    assert outcomes[0].state == UNKNOWN and all(o.state == CONFIRMED for o in outcomes[1:])
    early = writer.resolve_unknowns()
    assert early[0].state == UNKNOWN and "quiet period" in early[0].note            # never decided early
    time.sleep(QUIET + 0.1)
    [resolved] = writer.resolve_unknowns()
    assert resolved.state == CONFIRMED and "had happened" in resolved.note
    _settle()
    assert all(len(core.applications_for(f.file_no)) == 1 for f, _ in files)
    again = writer.push(files[0][1], files[0][0].bundle.branch, files[0][0].result.route, APPROVAL)
    assert again.state == CONFIRMED and len(core.records) == len(files)             # settled: no call at all


def test_an_unknown_that_did_not_happen_is_created_after_the_quiet_period(standin, port_for, mapping, writable, clock):
    core, port, files = _setup(standin, port_for, writable, n=1)
    f, rec = files[0]
    journal = Journal()
    writer = SafeCoreWriter(port, mapping, journal, clock, quiet_period_s=0.0)
    key = rec["idempotency_key"]
    journal.intend(key, f.file_no, f.branch_cd, "x", {}, mapping.version, "20261112161000")
    journal.set_state(key, UNKNOWN, "20261112161000", note="simulated: request lost before the core", unknown_since=0.0)
    [o] = writer.resolve_unknowns()
    assert o.state == PENDING and "had not happened" in o.note
    assert writer.push(rec, f.bundle.branch, f.result.route, APPROVAL).state == CONFIRMED
    assert len(core.applications_for(f.file_no)) == 1


def test_writes_are_held_in_the_window_and_go_after_it(standin, port_for, mapping, writable, clock):
    core, port, files = _setup(standin, port_for, writable, n=1)
    f, rec = files[0]
    writer = SafeCoreWriter(port, mapping, Journal(), clock, sleep=lambda s: None)
    clock.set(ist(2026, 11, 12, 17, 40))
    held = writer.push(rec, f.bundle.branch, f.result.route, APPROVAL)
    assert held.state == DEFERRED and "20:00" in held.note
    assert not [e for e in core.access_log if e.operation == "CreateApplication"]   # not even attempted
    clock.set(ist(2026, 11, 12, 20, 5))
    assert writer.push(rec, f.bundle.branch, f.result.route, APPROVAL).state == CONFIRMED


def test_a_batch_that_overruns_is_a_deferral_not_a_failure(standin, port_for, mapping, writable, clock):
    core_clock = BusinessClock(ist(2026, 11, 12, 18, 0))          # the core is still in its batch
    core, url = standin(own_clock=core_clock)
    f, rec = writable[0]
    core.register_file(f.file_no, f.branch_cd)
    clock.set(ist(2026, 11, 12, 20, 5))                           # our clock says the window is open
    writer = SafeCoreWriter(port_for("raw", url), mapping, Journal(), clock, sleep=lambda s: None)
    out = writer.push(rec, f.bundle.branch, f.result.route, APPROVAL)
    assert out.state == DEFERRED and "CL-E017" in out.note


def test_an_application_keyed_by_someone_else_is_not_overwritten_or_duplicated(standin, port_for, mapping, writable, clock):
    core, port, files = _setup(standin, port_for, writable, n=1)
    f, rec = files[0]
    core.seed_legacy([{"FILE_NO": f.file_no, "BRANCH_CD": f.branch_cd, "APPL_STAT": "K", "CRT_TS": "20261112110000"}])
    out = SafeCoreWriter(port, mapping, Journal(), clock).push(rec, f.bundle.branch, f.result.route, APPROVAL)
    assert out.state == EXISTS_NOT_OURS and len(core.applications_for(f.file_no)) == 1


def test_duplicates_already_in_the_core_stop_the_write_for_a_person(standin, port_for, mapping, writable, clock):
    core, port, files = _setup(standin, port_for, writable, n=1)
    f, rec = files[0]
    for _ in range(2):
        core.seed_legacy([{"FILE_NO": f.file_no, "BRANCH_CD": f.branch_cd, "APPL_STAT": "K", "CRT_TS": "20220611090000"}])
    out = SafeCoreWriter(port, mapping, Journal(), clock).push(rec, f.bundle.branch, f.result.route, APPROVAL)
    assert out.state == DUPLICATE_IN_CORE and len(core.applications_for(f.file_no)) == 2


def test_no_approval_means_no_call(standin, port_for, mapping, writable, clock):
    core, port, files = _setup(standin, port_for, writable, n=1)
    f, rec = files[0]
    out = SafeCoreWriter(port, mapping, Journal(), clock).push(rec, f.bundle.branch, f.result.route, None)
    assert out.state == FAILED and "approval" in out.note
    assert not [e for e in core.access_log if e.operation == "CreateApplication"]


def test_a_mapping_failure_stops_before_the_core_sees_anything(standin, port_for, mapping, records, clock):
    core, url = standin()
    bad = next((f, r) for f, r in records if r["product"] == "two-wheeler" and r.get("income_proof_kind") is None)
    out = SafeCoreWriter(port_for("raw", url), mapping, Journal(), clock).push(bad[1], bad[0].bundle.branch,
                                                                              bad[0].result.route, APPROVAL)
    assert out.state == FAILED and "INC_PRF_CD" in out.note and core.access_log == []


def test_the_journal_holds_no_customer_identifiers(standin, port_for, mapping, writable, clock):
    core, port, files = _setup(standin, port_for, writable, n=3)
    journal = Journal()
    writer = SafeCoreWriter(port, mapping, journal, clock)
    for f, rec in files:
        writer.push(rec, f.bundle.branch, f.result.route, APPROVAL)
    dump = journal.dump_text()
    for f, rec in files:
        assert rec["pan"] not in dump and rec["applicant_name"] not in dump and rec["mobile"] not in dump
        assert rec["idempotency_key"] in dump and str(rec["requested_amount"]) in dump


def test_the_key_is_day11s_and_is_stamped_in_ext_ref(standin, port_for, mapping, writable, clock):
    from godavari_integration.day11 import idempotency_key
    core, port, files = _setup(standin, port_for, writable, n=1)
    f, rec = files[0]
    SafeCoreWriter(port, mapping, Journal(), clock).push(rec, f.bundle.branch, f.result.route, APPROVAL)
    [app] = core.applications_for(f.file_no)
    assert app.fields["EXT_REF"] == idempotency_key(f.file_no, f.bundle.branch) == rec["idempotency_key"]
    assert len(app.fields["EXT_REF"]) == 20 and app.fields["VRFY_USR"] == "GF-AN-1142"
