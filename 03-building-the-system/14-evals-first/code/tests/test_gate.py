"""The regression gate blocks the bad change, lets the unchanged model through, and is not an average."""

from __future__ import annotations

from evals import candidates, gate, harness


def _gate(name: str, split, truth, baseline_rows, run_id: str | None = None):
    run = harness.run(candidates.build(name, run_id), split[0], truth)
    return gate.compare(baseline_rows, harness.field_records(run), harness.summarise(run), gate.load_policy()), run


def test_the_baseline_against_itself_passes(split, truth, baseline_rows) -> None:
    checks, _ = _gate("baseline", split, truth, baseline_rows)
    assert all(c.passed for c in checks)


def test_an_unchanged_model_run_again_passes(split, truth, baseline_rows) -> None:
    for i in range(3):
        checks, _ = _gate("rerun", split, truth, baseline_rows, f"rerun-{i}")
        assert all(c.passed for c in checks), [c for c in checks if not c.passed]


def test_the_trimmed_prompt_is_blocked_on_its_field(split, truth, baseline_rows) -> None:
    checks, _ = _gate("trimmed", split, truth, baseline_rows)
    failed = {(c.rule, c.stratum) for c in checks if not c.passed}
    assert ("regressions", "field=monthly_income") in failed


def test_an_average_only_gate_would_have_merged_it(split, truth, baseline_run) -> None:
    trimmed = harness.summarise(harness.run(candidates.build("trimmed"), split[0], truth))
    base = harness.summarise(baseline_run)
    assert gate.average_only(base, trimmed, gate.load_policy()["average_only_max_drop_points"]).passed


def test_a_different_golden_set_cannot_be_compared(split, truth, baseline_rows) -> None:
    run = harness.run(candidates.build("baseline"), split[0][:-1], truth)
    checks = gate.compare(baseline_rows, harness.field_records(run), harness.summarise(run), gate.load_policy())
    assert len(checks) == 1 and not checks[0].passed and checks[0].rule == "same golden set"


def test_a_completeness_miss_fails_however_good_the_fields_are(split, truth, baseline_rows, baseline_run) -> None:
    summary = harness.summarise(baseline_run)
    summary["overall"] = {**summary["overall"], "completeness_recall": 75 / 76, "completeness_misses": 1}
    checks = gate.compare(baseline_rows, baseline_rows, summary, gate.load_policy())
    assert [c.rule for c in checks if not c.passed] == ["completeness recall"]


def test_the_thresholds_sit_above_the_noise_floor_measured_on_dev(split, truth) -> None:
    _, dev = split
    policy = gate.load_policy()
    base = harness.field_records(harness.run(candidates.build("baseline"), dev, truth))
    for i in range(5):
        rerun = harness.field_records(harness.run(candidates.build("rerun", f"rerun-{i}"), dev, truth))
        floor = gate.noise_floor(base, rerun, policy["strata"])
        assert floor["max_net_regressions"] < policy["min_net_regressions"]
        assert floor["max_net_new_confident_wrong"] <= policy["max_new_confident_wrong"]


def test_a_different_truth_file_version_cannot_be_compared(baseline_rows, baseline_run) -> None:
    summary = harness.summarise(baseline_run)
    old, new = {**summary, "truth_sha256": "v1.0"}, {**summary, "truth_sha256": "v1.1"}
    checks = gate.compare(baseline_rows, baseline_rows, new, gate.load_policy(), old)
    assert len(checks) == 1 and not checks[0].passed and "truth file" in checks[0].detail
