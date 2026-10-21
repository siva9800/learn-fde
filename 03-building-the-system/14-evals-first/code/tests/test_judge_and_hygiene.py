"""A judge earns its place against people; the golden set never leaks and never leaves unmasked."""

from __future__ import annotations

import json

import pytest

from evals import hygiene
from evals.judge import Note, calibration, judge_v2, label_notes, make_notes


@pytest.fixture(scope="module")
def notes(split):
    test, dev = split
    out = make_notes(dev + test)
    label_notes(out)
    return out


@pytest.fixture(scope="module")
def calib(notes):
    return calibration(notes)


def test_judges_are_calibrated_on_dev_and_reported_on_test(calib) -> None:
    assert calib["notes"]["dev"] > 50 and calib["notes"]["test"] > 150


def test_the_holistic_judge_is_not_trusted(calib) -> None:
    v1 = calib["judge-v1 (holistic)"]
    assert not v1["trusted_in_gate"]
    assert v1["test"]["kappa"] < v1["dev"]["kappa"]           # it looked better on the data it was tuned on
    assert v1["test"]["catches_fails"] < 0.5


def test_the_holistic_judge_prefers_its_own_family(calib) -> None:
    v1 = calib["judge-v1 (holistic)"]["test"]
    assert v1["own_family_pass"] > v1["other_pass"]


def test_the_rubric_judge_is_trusted_and_does_not_beat_people_by_magic(calib) -> None:
    v2 = calib["judge-v2 (rubric)"]
    assert v2["trusted_in_gate"]
    assert v2["test"]["catches_fails"] >= 0.9 and v2["test"]["kappa"] >= 0.8


def test_the_rubric_judge_catches_a_pasted_pan_and_an_invented_document() -> None:
    note = Note("x", "GF-1", "test", "note-writer-b",
                "Dear branch team\n- PAN card (or Form 60): not in the file (rule TW-DOC-03).\n"
                "- Please also send the Form 16 for the last two years.\nApplicant PAN ABCPP1234K for your reference.",
                [("TW-DOC-03", "PAN card (or Form 60): not in the file")])
    ok, reasons = judge_v2(note)
    assert not ok
    assert any("Form 16" in r for r in reasons) and any("pan number" in r for r in reasons)


def test_fewshot_examples_come_from_dev_only(truth) -> None:
    examples = [{"file_id": fid, **rec["fields"]} for fid, rec in truth.items() if rec["split"] == "dev"][:3]
    corpus = {"fewshot.json": json.dumps(examples)}
    assert hygiene.leaks(truth, corpus) == []


def test_a_shared_name_is_a_weak_match_not_a_leak(truth) -> None:
    # Two different synthetic customers can share a name, as real ones do; only identifiers prove a leak.
    name = next(v["fields"]["applicant_name"] for v in truth.values() if v["split"] == "test")
    corpus = {"fixture.txt": f"Applicant name: {name}"}
    assert hygiene.leaks(truth, corpus) == []
    assert hygiene.leaks(truth, corpus, weak=True)


def test_a_golden_file_planted_in_a_prompt_is_found(truth) -> None:
    fid, rec = next((k, v) for k, v in truth.items() if v["split"] == "test" and v["fields"].get("pan"))
    prompt = f"Example:\nPAN: {rec['fields']['pan']}\nExtract the PAN as above."
    found = hygiene.leaks(truth, {"prompts/extraction/2.2.0/examples.j2": prompt})
    assert (fid, rec["fields"]["pan"]) in {(f, v) for _, f, v in found}


def test_the_export_for_the_vendor_carries_no_identifiers(baseline_run) -> None:
    rows = hygiene.export_rows(baseline_run.fields)
    text = json.dumps(rows)
    assert hygiene.pii_hits(text) == []
    for r in rows:
        if r["field"] == "applicant_name":
            assert all(len(part) == 2 and part.endswith(".") for part in r["model_read"].split())


@pytest.mark.parametrize("field_name,value,masked", [
    ("pan", "ABCPP1234K", "AB*******K"),
    ("mobile", "9876543210", "******3210"),
    ("applicant_name", "RAVI TEJA PASUPULETI", "R. T. P."),
    ("address", "12-4, KPHB Colony, Kukatpally, Hyderabad 500072", "[address, PIN 500072]"),
    ("requested_amount", "125000", "125000"),
])
def test_masking_rules(field_name: str, value: str, masked: str) -> None:
    assert hygiene.mask(field_name, value) == masked
