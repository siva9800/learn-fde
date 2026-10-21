"""The sampler, the rubber-stamping detector and the correction record, on the simulated pilot week."""

from __future__ import annotations

import pytest

from godavari_review import corrections as C
from godavari_review import sampler, stamping


def test_the_sample_is_reproducible_key_dependent_and_has_a_floor():
    approved = [(f"GF-{61000 + i}", "Guntur" if i % 2 else "Kukatpally") for i in range(40)]
    a = sampler.sample(approved, "key-1")
    assert a == sampler.sample(approved, "key-1")
    assert {p.file_id for p in a} != {p.file_id for p in sampler.sample(approved, "key-2")}
    small = sampler.sample(approved[:8], "key-1")
    assert all(sum(p.branch == b for p in small) >= 3 for b in ("Guntur", "Kukatpally"))


def test_targeted_files_are_added_not_swapped():
    approved = [(f"GF-{61000 + i}", "Guntur") for i in range(30)]
    base = {p.file_id for p in sampler.sample(approved, "k")}
    extra = next(f for f, _ in approved if f not in base)
    picks = sampler.sample(approved, "k", targeted={extra})
    assert base | {extra} == {p.file_id for p in picks}


def test_how_many_fields_it_takes_to_see_a_one_percent_error():
    assert sampler.fields_to_detect(0.01) == 299


def test_the_detector_flags_the_stamping_session_and_not_the_fast_expert(week):
    verdicts = {(s.analyst, s.day, s.half): s.verdict for s in map(stamping.judge, stamping.sessions(week.log))}
    assert verdicts[("V2", "2026-12-11", "PM")].startswith("suspected")
    assert not any(v.startswith("suspected") for k, v in verdicts.items() if k[0] == "H3")
    assert any(v.startswith("fast") for k, v in verdicts.items() if k[0] == "H3")
    assert sum(v.startswith("suspected") for v in verdicts.values()) == 1


def test_the_detector_never_reads_the_simulations_truth(week):
    flipped = [{**e, "sim_correct_before": not e.get("sim_correct_before", True)} for e in week.log]
    a = [(s.analyst, s.day, s.half, s.verdict) for s in map(stamping.judge, stamping.sessions(week.log))]
    b = [(s.analyst, s.day, s.half, s.verdict) for s in map(stamping.judge, stamping.sessions(flipped))]
    assert a == b
    assert not any(k.startswith("sim_") for e in week.log for k in stamping.visible(e))


def test_a_week_of_override_counts_is_weak_evidence_on_its_own(week):
    rows = stamping.weekly_overrides(week.log, 0.054)
    assert not any(r["low"] for r in rows)          # nobody is "low" after one week, including the stamper


def _corr(**kw) -> C.Correction:
    base = dict(file_id="GF-61000", field="applicant_name", stratum="printed", band="review", model_value="RAVI TEJA",
                analyst_value="RAVI TEJA", reason="format only", analyst="H1", at="2026-12-07T10:00:00",
                confidence=0.9, model="stub", rules_fingerprint="f535", bands_version="v")
    base.update(kw)
    return C.Correction(**base)


def test_a_correction_needs_a_reason_from_the_list():
    with pytest.raises(ValueError):
        _corr(reason="fixed")
    with pytest.raises(ValueError):
        _corr(reason="other")


def test_format_only_is_not_a_model_error_and_content_goes_to_dev_as_a_candidate():
    assert not _corr(analyst_value="Ravi Teja").content_change
    c = _corr(field="on_road_price", model_value="37150", analyst_value="137150", reason="misread character")
    assert c.content_change
    cand = C.to_dev_candidate(c)
    assert cand["split"] == "dev" and "single-labeller" in cand["status"]


def test_every_correction_in_the_log_has_a_reason(week):
    items = {p.item.file_id: p for p in week.files}
    for e in week.log:
        if e["event"] == "field" and e["action"] in ("corrected", "keyed", "not_in_file"):
            row = next(r for r in items[e["file_id"]].rows if r.field == e["field"])
            assert C.reason_for(row.field, e["model_value"], e["new_value"], row.evidence) in C.REASONS
