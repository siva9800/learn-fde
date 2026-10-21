"""The harness measures Day 11's system as it is, and its numbers mean what the report says they mean."""

from __future__ import annotations

from pathlib import Path

import pytest

from evals import candidates, harness
from evals.day11 import DAY11_CODE
from evals.harness import LabelsChanged, field_status, summarise

CODE = Path(__file__).resolve().parent.parent


@pytest.mark.parametrize("pred,label,flagged,expected", [
    ("125000", "125000", False, "correct"),
    ("Rs 1,25,000", "125000", True, "correct_flagged"),
    ("1250000", "125000", True, "wrong_flagged"),
    ("1250000", "125000", False, "confident_wrong"),
    (None, "125000", True, "wrong_flagged"),          # "unsure" is wrong but honest
    ("125000", None, False, "confident_wrong"),       # a value for something that is not in the file
    (None, None, True, "correct_flagged"),
])
def test_the_four_outcomes(pred, label, flagged, expected) -> None:
    assert field_status("requested_amount", pred, label, flagged) == expected


def test_day11_is_imported_by_path_not_copied() -> None:
    import intake
    assert Path(intake.__file__).resolve().parent == (DAY11_CODE / "intake").resolve()
    assert not (CODE / "intake").exists()
    assert not list(CODE.rglob("rules_two_wheeler.py"))


def test_every_mandatory_field_of_every_golden_file_is_scored(baseline_run, split) -> None:
    test, _ = split
    expected = sum(12 for _ in test)          # Day 11's MANDATORY_FIELDS has twelve per product
    assert len(baseline_run.fields) == expected
    assert len(baseline_run.files) == len(test)


def test_the_run_is_deterministic(split, truth, baseline_run) -> None:
    again = harness.run(candidates.build("baseline"), split[0], truth)
    assert [r.status for r in again.fields] == [r.status for r in baseline_run.fields]


def test_strata_add_up(baseline_run) -> None:
    s = summarise(baseline_run)
    for key in ("product", "branch", "channel", "language", "pilot", "handwritten_telugu", "field"):
        parts = [m for k, m in s["strata"].items() if k.startswith(key + "=")]
        assert sum(m["fields"] for m in parts) == s["overall"]["fields"], key
        assert sum(m["correct"] for m in parts) == s["overall"]["correct"], key


def test_the_signed_rules_miss_no_incomplete_golden_file(baseline_run) -> None:
    s = summarise(baseline_run)
    assert s["overall"]["completeness_recall"] == 1.0
    assert s["overall"]["incomplete_files"] > 50


def test_confidently_wrong_means_wrong_and_unflagged(baseline_run) -> None:
    for r in baseline_run.fields:
        if r.status == "confident_wrong":
            assert not r.flagged and not r.correct


def test_the_harness_refuses_files_whose_pages_changed(split, truth) -> None:
    test, _ = split
    with pytest.raises(LabelsChanged):
        harness.run(candidates.build("baseline"), test[:1], truth, {test[0].file_id: "0" * 64})


def test_exact_match_understates_accuracy_against_a_canonical_truth_file(baseline_run) -> None:
    o = summarise(baseline_run)["overall"]
    assert o["exact_accuracy"] < o["accuracy"]


def test_the_trimmed_prompt_hides_in_the_average_but_not_in_its_field(split, truth, baseline_run) -> None:
    trimmed = summarise(harness.run(candidates.build("trimmed"), split[0], truth))
    base = summarise(baseline_run)
    assert base["overall"]["accuracy"] - trimmed["overall"]["accuracy"] < 0.02
    assert (base["strata"]["field=monthly_income"]["accuracy"]
            - trimmed["strata"]["field=monthly_income"]["accuracy"]) > 0.05
    assert trimmed["overall"]["flagged_rate"] < base["overall"]["flagged_rate"]   # it even looks cheaper
