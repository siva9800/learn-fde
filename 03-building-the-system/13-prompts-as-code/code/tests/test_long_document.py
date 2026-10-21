"""The page-1 versus page-40 failure, reproduced, and the per-page approach recovering."""

from __future__ import annotations

import pytest

from conftest import make_release
from godavari_prompts import synth
from godavari_prompts.fake_model import FakeProvider
from godavari_prompts.loader import load
from godavari_prompts.model_port import Tier
from godavari_prompts.pipeline import ModelMismatch, run_batch
from godavari_prompts.regress import by_page_band, score

LAB = synth.lab_set()


@pytest.fixture(scope="module")
def lab_runs() -> dict[str, list]:
    prov = FakeProvider({Tier.SMALL: "fake-small-2026-10", Tier.LARGE: "fake-large-2026-10"})
    return {v: run_batch(make_release(v), load("extraction", v), LAB, prov) for v in ("1.0.0", "1.1.0", "2.0.0")}


def test_the_synthetic_files_are_what_the_chapter_says() -> None:
    assert all(len(f.pages) == 40 for f in LAB)
    with_co = [f for f in LAB if f.truth["co_applicant_name"] != "none"]
    assert with_co and all(f.pages[37].doc == "co_applicant_kyc" for f in with_co)       # page 38
    assert all("Co-applicant: none" in f.pages[0].text for f in with_co)                  # the form never says so
    assert synth.lab_set()[7].sha256 == LAB[7].sha256                                    # seeded, reproducible


def test_v1_is_perfect_on_the_three_page_samples(provider: FakeProvider) -> None:
    files = synth.three_page_samples()
    ev = score(run_batch(make_release("1.0.0"), load("extraction", "1.0.0"), files, provider), files, "s")
    assert ev["correct_rate"] == 1.0


def test_v1_silently_drops_the_late_co_applicant(lab_runs: dict[str, list]) -> None:
    co = score(lab_runs["1.0.0"], LAB, "lab", only="co_applicant")["per_field"]["co_applicant_name"]
    assert co["correct"] / co["n"] < 0.7
    assert co["unsure"] == 0                       # silent: every miss is a confident "none", not a null
    assert co["wrong"] == co["n"] - co["correct"]


def test_moving_the_request_moves_the_failure(lab_runs: dict[str, list]) -> None:
    bands = [(13, 24), (36, 40)]
    v1 = {b: ok / n for b, n, ok in by_page_band(lab_runs["1.0.0"], LAB, bands)}
    v11 = {b: ok / n for b, n, ok in by_page_band(lab_runs["1.1.0"], LAB, bands)}
    assert v11["pages 36-40"] > v1["pages 36-40"]          # the back recovers
    assert v11["pages 13-24"] < 0.9                        # the middle does not


def test_per_page_extraction_recovers_and_stops_confident_errors(lab_runs: dict[str, list]) -> None:
    ev = score(lab_runs["2.0.0"], LAB, "lab")
    co = score(lab_runs["2.0.0"], LAB, "lab", only="co_applicant")["per_field"]["co_applicant_name"]
    telugu = score(lab_runs["2.0.0"], LAB, "lab", only="telugu_income")["per_field"]["monthly_income"]
    assert co["correct"] == co["n"]
    assert telugu["correct"] == telugu["n"]
    assert ev["wrong_rate"] == 0.0
    assert ev["correct_rate"] > score(lab_runs["1.0.0"], LAB, "lab")["correct_rate"]


def test_without_the_glossary_telugu_income_is_read_as_annual(provider: FakeProvider) -> None:
    files = [f for f in synth.guntur_replay() if f.telugu_income]
    res = run_batch(make_release("2.1.0"), load("extraction", "2.1.0"), files, provider)
    for r, f in zip(res, files):
        assert int(r.fields["monthly_income"]["value"]) == 12 * int(f.truth["monthly_income"])


def test_the_batch_stops_when_the_adapter_alias_has_moved() -> None:
    rel = make_release("2.0.0")
    before = FakeProvider({Tier.SMALL: "fake-small-2026-10", Tier.LARGE: "fake-large-latest"}, today="2026-11-12")
    after = FakeProvider({Tier.SMALL: "fake-small-2026-10", Tier.LARGE: "fake-large-latest"}, today="2026-11-17")
    run_batch(rel, load("extraction", "2.0.0"), LAB[:1], before)               # same snapshot today: runs
    with pytest.raises(ModelMismatch, match="fake-large-2026-11"):
        run_batch(rel, load("extraction", "2.0.0"), LAB[:1], after)
