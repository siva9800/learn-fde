"""The branch rule, fail-closed resolution, transfers, drafts, and the post-filter leak."""

from __future__ import annotations

import json
from datetime import datetime

import pytest

from godavari_retrieval.day11 import BRANCH_AD_GROUP, visible_to
from godavari_retrieval.evaluate import permission_audit
from godavari_retrieval.permissions import POLICY_TYPES, SearchFilter, StaleDirectoryError, may_see
from godavari_retrieval.service import RetrievalService

PRECEDENT_Q = ("similar past files: self-employed kirana shop two-wheeler, bank statement income, "
               "rent agreement with landlord electricity bill")


def _prec(now: datetime) -> SearchFilter:
    return SearchFilter(as_of=now.date(), doc_types=frozenset({"loan_decision"}))


def test_the_filter_agrees_with_day11_for_every_loan_chunk_and_every_user(chunks, day1, now):
    for user in day1.members:
        p = day1.resolve(user, now)
        for c in chunks:
            if c.meta.doc_type == "loan_decision":
                assert may_see(p, c) == visible_to(p.groups, c.meta.branch)


def test_acl_names_document_groups_never_users(chunks, day1):
    users = set(day1.members)
    for c in chunks:
        assert not c.meta.acl & users
        if c.meta.doc_type == "loan_decision":
            assert c.meta.acl == {BRANCH_AD_GROUP[c.meta.branch]}


def test_lakshmi_sees_only_the_vijayawada_region(svc, now):
    for q in ("two-wheeler approved", "gold loan sent back", "kirana shop rent agreement", "Sri Sai Motors"):
        r = svc.search("lakshmi", q, now, k=10, f=_prec(now))
        assert {x.chunk.meta.branch for x in r.results} <= {"Vijayawada-Benz Circle", "Guntur", "Rajahmundry"}


@pytest.mark.parametrize("user", ["svc-kaagaz-retrieval", "someone.not.in.the.snapshot"])
def test_no_groups_means_nothing(svc, now, user):
    r = svc.search(user, "income proof self-employed", now, k=5)
    assert r.results == [] and r.total_matches == 0


def test_a_stale_snapshot_refuses_to_answer(svc):
    with pytest.raises(StaleDirectoryError):
        svc.search("lakshmi", "income proof", datetime(2026, 11, 27, 9, 0))


def test_a_transfer_changes_results_without_reindexing(chunks, day1, day2):
    t = datetime(2026, 11, 26, 10, 0)
    before = RetrievalService(chunks, day1).search("kkp.credit.officer", "two-wheeler approved", t, k=5, f=_prec(t))
    after = RetrievalService(chunks, day2).search("kkp.credit.officer", "two-wheeler approved", t, k=5, f=_prec(t))
    assert {x.chunk.meta.branch for x in before.results} == {"Kukatpally"}
    assert {x.chunk.meta.branch for x in after.results} == {"Guntur"}


def test_drafts_are_for_the_compliance_desk_only(svc, now):
    f = SearchFilter(as_of=now.date(), doc_types=POLICY_TYPES)
    assert "GFL/CO/2026/041" not in svc.search("lakshmi", "video KYC repeat customers draft", now, k=10, f=f).keys()
    assert svc.search("compliance.desk.01", "video KYC repeat customers draft", now, k=3, f=f).keys()[0] == "GFL/CO/2026/041"


def test_permission_audit_finds_no_violations(svc, chunks, day1, now):
    checked, violations = permission_audit(svc, chunks, day1, now, ["lakshmi", "srinivas", "kkp.credit.officer"])
    assert checked > 500 and violations == 0


def test_the_naive_post_filter_leaks_through_log_note_and_count(naive_svc, now):
    r = naive_svc.search("lakshmi", PRECEDENT_Q, now, k=5, f=_prec(now))
    assert "GF-23562" not in r.keys()                                  # the list itself looks clean
    assert any("GF-23562" in ln and "kukatpally" in ln for ln in r.debug_log)
    assert "Sri Sai Motors" in r.note and "Kukatpally" in r.note
    assert r.total_matches > len(r.results)


def test_the_pre_filter_leaks_nothing_anywhere(svc, now):
    r = svc.search("lakshmi", PRECEDENT_Q, now, k=5, f=_prec(now))
    blob = json.dumps([r.keys(), r.note, r.debug_log, r.notices, svc.view_log[-1]])
    assert "GF-23562" not in blob and "Kukatpally" not in blob and "Sri Sai" not in blob
    assert r.keys()[0] == "GF-23417"


def test_a_pan_lookup_never_reveals_a_file_in_another_branch(svc, now):
    hidden = svc.search("lakshmi", "prior applications PAN GJKPM6650R", now, k=5, f=_prec(now))
    assert hidden.results == [] and hidden.total_matches == 0
    assert "no file you can see matches this PAN" in hidden.notices
    assert "GJKPM6650R" not in json.dumps(svc.view_log[-1])
    seen = svc.search("srinivas", "prior applications PAN GJKPM6650R", now, k=5, f=_prec(now))
    assert seen.keys() == ["GF-23911"]
