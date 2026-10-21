"""The regression check: what it catches, what it misses, and the few-shot split it depends on."""

from __future__ import annotations

import json

from conftest import make_release
from godavari_prompts import synth
from godavari_prompts.fake_model import FakeProvider
from godavari_prompts.gate import compare_evals
from godavari_prompts.loader import available_versions, load
from godavari_prompts.model_port import Tier
from godavari_prompts.pipeline import run_batch
from godavari_prompts.regress import score


def evaluate(version: str, files: list, provider: FakeProvider, models: dict | None = None) -> dict:
    return score(run_batch(make_release(version, models=models), load("extraction", version), files, provider),
                 files, "set")


def test_the_trim_passes_the_kukatpally_gate_because_the_set_has_no_telugu(provider: FakeProvider) -> None:
    labelled = synth.labelled_set()
    assert not any(f.telugu_income for f in labelled)                 # the gap, stated as a test
    assert compare_evals(evaluate("2.1.0", labelled, provider), evaluate("2.0.0", labelled, provider)) == []


def test_the_same_gate_on_a_telugu_slice_blocks_the_trim(provider: FakeProvider) -> None:
    telugu = [f for f in synth.lab_set() if f.telugu_income]
    problems = compare_evals(evaluate("2.1.0", telugu, provider), evaluate("2.0.0", telugu, provider))
    assert any(p.startswith("monthly_income: wrong 0 ->") for p in problems)


def test_a_new_snapshot_guesses_smudged_digits_and_fails_the_gate(provider: FakeProvider) -> None:
    labelled = synth.labelled_set()
    new = FakeProvider({Tier.SMALL: "fake-small-2026-10", Tier.LARGE: "fake-large-2026-11"})
    drifted = evaluate("2.0.0", labelled, new, models={"small": "fake-small-2026-10", "large": "fake-large-2026-11"})
    pinned = evaluate("2.0.0", labelled, provider)
    assert drifted["correct_rate"] == pinned["correct_rate"]          # accuracy alone would not notice
    assert drifted["wrong_rate"] > pinned["wrong_rate"]
    assert compare_evals(drifted, pinned)


def test_few_shot_examples_come_from_the_training_split_only() -> None:
    eval_ids = set(synth.LABELLED_IDS) | {f.file_id for f in synth.lab_set() + synth.guntur_replay()}
    for version in available_versions("extraction"):
        pv = load("extraction", version)
        for ex in pv.meta.get("examples", []):
            data = json.loads((pv.path / ex["file"]).read_text(encoding="utf-8"))
            assert data["split"] == "train" and data["masked"] is True
            assert data["source_file_id"] not in eval_ids
