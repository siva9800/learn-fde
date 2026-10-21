"""The bands: fitted on development only, confirmed on test, failing closed, and priced."""

from __future__ import annotations

import math
from dataclasses import replace

import pytest

from godavari_review import bands as B


def test_the_placeholder_reproduces_day_14s_baseline(test_rows, policy):
    c = B.cost(test_rows, B.placeholder_band, policy)
    assert c["auto_wrong"] == 7                                  # Day 14, section 04.3
    flagged = c["bands"]["review"]["fields"] + c["bands"]["reject"]["fields"]
    assert round(flagged / len(test_rows), 3) == 0.218           # Day 14: 21.8 percent flagged


def test_fit_refuses_test_rows_and_confirm_refuses_dev_rows(dev, test_rows, policy):
    with pytest.raises(ValueError):
        B.fit(test_rows, policy)
    with pytest.raises(ValueError):
        B.confirm(dev, B.fit(dev, policy), policy)


def test_no_threshold_extrapolates_below_what_development_showed_correct(dev, policy):
    for (field, stratum), cb in B.fit(dev, policy).items():
        if cb.accept_at is None:
            continue
        cand = [r for r in B.candidates(dev) if r.cell == (field, stratum) and r.confidence >= cb.accept_at]
        assert len(cand) >= policy["auto_accept"]["min_support_dev"]
        assert all(r.correct for r in cand)
        assert cb.accept_at >= math.floor(min(r.confidence for r in cand) * 100) / 100 - 1e-9


def test_the_tuned_bands_leave_no_confidently_wrong_field_on_test(fitted, test_rows, policy):
    bands, summary = fitted
    c = B.cost(test_rows, lambda r: B.band_for(r, bands), policy)
    assert c["auto_wrong"] == 0
    assert summary["auto_errors_before"] > 0                     # the development fit alone was not enough


def test_the_pooled_number_passes_while_one_field_fails(fitted):
    bands, summary = fitted
    assert summary["upper_before"] < summary["pooled_limit"]     # the average says fine ...
    cb = bands[("on_road_price", "printed")]
    assert cb.status == "withdrawn" and cb.test["auto_errors"] == 6   # ... the on-road price does not
    assert any("Rs I,37,150" in ex for ex in cb.test["examples"])


def test_a_failed_confirmation_removes_automation_and_never_moves_a_threshold(dev, test_rows, policy):
    before = {k: cb.accept_at for k, cb in B.fit(dev, policy).items()}
    bands = B.fit(dev, policy)
    B.confirm(test_rows, bands, policy)
    assert {k: cb.accept_at for k, cb in bands.items()} == before
    assert all(cb.status in ("auto", "withdrawn", "blocked_until_proven", "no_auto_band") for cb in bands.values())


def test_handwritten_telugu_is_never_auto_accepted_until_proved(fitted, test_rows):
    bands, _ = fitted
    hw = [r for r in test_rows if r.stratum == "handwritten_telugu"]
    assert hw and not any(B.band_for(r, bands) == B.Band.AUTO for r in hw)
    assert B.fields_to_prove(0.015) == 253


def test_a_deterministic_finding_always_means_review(fitted, test_rows):
    bands, _ = fitted
    base = next(r for r in test_rows if r.cell == ("mobile", "printed") and B.band_for(r, bands) == B.Band.AUTO)
    assert B.band_for(replace(base, confidence=0.99, det_findings=("ENV-EVIDENCE",)), bands) == B.Band.REVIEW


def test_unknown_cells_fail_closed_and_unsure_is_keyed(fitted, test_rows):
    bands, _ = fitted
    base = test_rows[0]
    assert B.band_for(replace(base, field="co_applicant_income", confidence=0.99, det_findings=()), bands) == B.Band.REVIEW
    assert B.band_for(replace(base, value=None), bands) == B.Band.REJECT


def test_the_bands_cost_more_than_the_placeholder_and_less_than_reviewing_everything(fitted, test_rows, policy):
    bands, _ = fitted
    tuned = B.cost(test_rows, lambda r: B.band_for(r, bands), policy)["hours_per_month"]
    assert B.cost(test_rows, B.placeholder_band, policy)["hours_per_month"] < tuned
    assert tuned < B.cost(test_rows, B.everything_reviewed, policy)["hours_per_month"]
