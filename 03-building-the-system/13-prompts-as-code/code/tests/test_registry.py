"""Release records, promotion gates, rollback, and the shipped registry file."""

from __future__ import annotations

from pathlib import Path

import pytest

from conftest import make_release
from godavari_prompts.loader import PROMPTS_DIR, version_dir
from godavari_prompts.registry import Registry, RegistryError

EVAL = {"set": "s", "set_sha256": "abc", "n_files": 1, "correct_rate": 1.0, "wrong_rate": 0.0,
        "input_tokens_per_file": {"small": 0, "large": 1},
        "per_field": {"monthly_income": {"n": 12, "correct": 12, "unsure": 0, "wrong": 0}}}


def ready(reg: Registry, version: str, *, root: Path = PROMPTS_DIR, evaluation: dict | None = None) -> str:
    rel = reg.add_release(make_release(version, root))
    reg.record_eval(rel.release_id, evaluation or EVAL)
    reg.approve(rel.release_id, "reviewer.kaagaz")
    reg.compliance_read(rel.release_id, "compliance-head.godavari")
    return rel.release_id


def test_the_author_cannot_approve_their_own_prompt() -> None:
    reg = Registry()
    rel = reg.add_release(make_release("2.1.0"))
    reg.record_eval(rel.release_id, EVAL)
    with pytest.raises(RegistryError, match="cannot approve"):
        reg.approve(rel.release_id, "platform.kaagaz")


def test_no_approval_without_an_eval_score() -> None:
    reg = Registry()
    rel = reg.add_release(make_release("2.0.0"))
    with pytest.raises(RegistryError, match="no eval score"):
        reg.approve(rel.release_id, "reviewer.kaagaz")


def test_a_release_must_pin_a_snapshot_not_an_alias() -> None:
    with pytest.raises(RegistryError, match="not a dated snapshot"):
        Registry().add_release(make_release("2.0.0", models={"small": "fake-small-2026-10",
                                                             "large": "fake-large-latest"}))


def test_pilot_needs_the_compliance_read() -> None:
    reg = Registry()
    rel = reg.add_release(make_release("2.0.0"))
    reg.record_eval(rel.release_id, EVAL)
    reg.approve(rel.release_id, "reviewer.kaagaz")
    with pytest.raises(RegistryError, match="compliance head has not read"):
        reg.promote("pilot", rel.release_id, by="fde.kaagaz", at="t", reason="r")


def test_production_needs_a_pilot_run_first() -> None:
    reg = Registry()
    rid = ready(reg, "2.0.0")
    with pytest.raises(RegistryError, match="never ran in pilot"):
        reg.promote("production", rid, by="fde.kaagaz", at="t", reason="r")
    reg.promote("pilot", rid, by="fde.kaagaz", at="t1", reason="r")
    reg.promote("production", rid, by="fde.kaagaz", at="t2", reason="r")
    assert reg.current("production", "extraction").release_id == rid


def test_the_gate_blocks_a_regression_against_what_is_running() -> None:
    reg = Registry()
    good = ready(reg, "2.0.0")
    reg.promote("pilot", good, by="fde.kaagaz", at="t1", reason="r")
    worse = dict(EVAL, per_field={"monthly_income": {"n": 12, "correct": 10, "unsure": 0, "wrong": 2}})
    bad = ready(reg, "2.1.0", evaluation=worse)
    with pytest.raises(RegistryError, match="monthly_income: correct 12 -> 10"):
        reg.promote("pilot", bad, by="fde.kaagaz", at="t2", reason="r")


def test_rollback_restores_the_previous_release_once() -> None:
    reg = Registry()
    first, second = ready(reg, "2.0.0"), ready(reg, "2.1.0")
    reg.promote("pilot", first, by="fde.kaagaz", at="t1", reason="r")
    reg.promote("pilot", second, by="fde.kaagaz", at="t2", reason="r")
    assert reg.rollback("pilot", "extraction", by="fde.kaagaz", at="t3", reason="alert") == first
    assert reg.current("pilot", "extraction").release_id == first
    with pytest.raises(RegistryError, match="nothing to roll back to"):
        reg.rollback("pilot", "extraction", by="fde.kaagaz", at="t4", reason="again")
    with pytest.raises(RegistryError, match="fix it as a new version"):
        reg.promote("pilot", second, by="platform.kaagaz", at="t5", reason="retry")


def test_a_version_edited_after_release_cannot_be_promoted(prompts_copy: Path) -> None:
    reg = Registry(prompts_root=prompts_copy)
    rid = ready(reg, "2.0.0", root=prompts_copy)
    (version_dir("extraction", "2.0.0", prompts_copy) / "partials" / "_role.j2").write_text("Be helpful.\n",
                                                                                            encoding="utf-8")
    with pytest.raises(RegistryError, match="files changed after release"):
        reg.promote("dev", rid, by="fde.kaagaz", at="t", reason="r")
    assert any("hash mismatch" in p for p in reg.verify())


def test_rollback_needs_the_old_files_on_disk(prompts_copy: Path) -> None:
    reg = Registry(prompts_root=prompts_copy)
    first, second = ready(reg, "2.0.0", root=prompts_copy), ready(reg, "2.1.0", root=prompts_copy)
    reg.promote("pilot", first, by="fde.kaagaz", at="t1", reason="r")
    reg.promote("pilot", second, by="fde.kaagaz", at="t2", reason="r")
    (version_dir("extraction", "2.0.0", prompts_copy) / "extract.system.j2").unlink()   # "cleaned up old versions"
    with pytest.raises(RegistryError, match="cannot be restored"):
        reg.rollback("pilot", "extraction", by="fde.kaagaz", at="t3", reason="alert")


def test_the_shipped_registry_verifies_and_records_the_story() -> None:
    reg = Registry.load()
    assert reg.verify() == []
    assert reg.current("pilot", "extraction").release_id == "extraction@2.0.0+fake-large-2026-10"
    actions = [(e["action"], e["to"]) for e in reg.history if e["env"] == "pilot"]
    assert actions[-1] == ("rollback", "extraction@2.0.0+fake-large-2026-10")
    for rel in reg.releases.values():
        assert rel.eval is not None and rel.approved_by and rel.approved_by != rel.author
