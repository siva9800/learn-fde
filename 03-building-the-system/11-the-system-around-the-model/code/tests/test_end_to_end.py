"""The whole batch, end to end. These are the tests that would fail if the split were wrong."""

from __future__ import annotations

import csv
from datetime import date
from functools import cache

from intake import rules_gold, rules_two_wheeler
from intake.catalogue import Doc
from intake.day7_inputs import DAY7_GENERATOR, day7_sample
from intake.model import UNSURE_BELOW, StubModel
from intake.pipeline import FileResult, check_note, process, score
from intake.routing import Route
from intake.ruleset import Action, Finding
from intake.synth import build_batch
from intake.validators import grounding_errors

AS_OF = date(2026, 11, 9)
RULESETS = {"two-wheeler": rules_two_wheeler.RULESET, "gold": rules_gold.RULESET}


@cache
def run() -> tuple[FileResult, ...]:
    model = StubModel()
    return tuple(score(process(b, model, RULESETS[b.product], AS_OF), t) for b, t in build_batch(day7_sample()))


def test_the_sample_is_day7s_sample_not_a_copy() -> None:
    rows = day7_sample()
    csv_path = DAY7_GENERATOR.parent.parent / "data" / "godavari_loan_file_sample.csv"
    with csv_path.open(encoding="utf-8") as fh:
        day7 = list(csv.DictReader(fh))
    assert [r.file_id for r in rows] == [d["file_id"] for d in day7]
    assert [r.product for r in rows] == [d["product"] for d in day7]
    assert [str(r.has_address_proof) for r in rows] == [d["has_address_proof"] for d in day7]


def test_batch_size_and_products() -> None:
    results = run()
    assert len(results) == 130
    assert sum(r.product == "two-wheeler" for r in results) == 81


def test_the_run_is_deterministic() -> None:
    model = StubModel()
    again = [process(b, model, RULESETS[b.product], AS_OF).route for b, _ in build_batch(day7_sample())]
    assert again == [r.route for r in run()]


def test_no_file_with_a_rule_breach_reaches_ready_for_approval() -> None:
    for r in run():
        breaches = {d for d in r.defects if not d.startswith("FIELD_ERROR")}
        assert not (breaches and r.route == Route.READY_FOR_APPROVAL), (r.file_id, breaches)


def test_every_rule_breach_in_the_batch_is_caught() -> None:
    missed = [(r.file_id, d) for r in run() for d in r.missed if not d.startswith("FIELD_ERROR")]
    assert missed == []


def test_the_model_alone_would_have_shipped_more_than_the_system_misses() -> None:
    shipped = sum(len(r.model_alone_shipped) for r in run())
    missed = sum(len(r.missed) for r in run())
    assert shipped > 10 * missed


def test_no_send_back_or_block_without_a_real_problem() -> None:
    assert [fa for r in run() for fa in r.false_alarms] == []


def test_ungrounded_claims_never_reach_a_rule() -> None:
    model = StubModel()
    hallucinated = 0
    for bundle, _ in build_batch(day7_sample()):
        for claim in model.read(bundle).documents:
            if grounding_errors(bundle, claim):
                hallucinated += 1
    env = sum(1 for r in run() for f in r.findings if f.rule_id == "ENV-GROUND")
    assert hallucinated > 0 and env == hallucinated


def test_the_stub_says_unsure_rather_than_returning_a_low_confidence_value() -> None:
    model = StubModel()
    for bundle, _ in build_batch(day7_sample())[:40]:
        for fv in model.read(bundle).fields.values():
            assert fv.value is None or fv.confidence >= UNSURE_BELOW


def test_every_branch_facing_note_cites_every_rule_that_fired() -> None:
    for r in run():
        for f in r.findings:
            if f.action in (Action.SEND_BACK, Action.BLOCK):
                assert f.rule_id in r.note, (r.file_id, f.rule_id)


def test_check_note_appends_a_missing_citation() -> None:
    findings = [Finding("TW-DOC-05", "regulatory", Action.SEND_BACK, "proof of address: not in the file",
                        doc=Doc.PROOF_OF_ADDRESS)]
    fixed, corrected = check_note("Please ask the branch for the address proof.", findings)
    assert corrected and "TW-DOC-05" in fixed
