"""Shared fixtures: Day 14's golden files chosen once, a fresh engine per test, and helpers to drive a file."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from godavari_workflow.budgets import Budget  # noqa: E402
from godavari_workflow.clock import BusinessClock  # noqa: E402
from godavari_workflow.day14 import load_truth, select  # noqa: E402
from godavari_workflow.engine import Engine, Systems  # noqa: E402
from godavari_workflow.naive import NaiveTools  # noqa: E402
from godavari_workflow.planner import StubPlanner  # noqa: E402
from godavari_workflow.store import Store  # noqa: E402
from godavari_workflow.systems import Faults  # noqa: E402

NOW = datetime(2026, 11, 26, 10, 0)


@pytest.fixture(scope="session")
def golden() -> list[Any]:
    return select()[0]


@pytest.fixture(scope="session")
def truth() -> dict[str, dict[str, Any]]:
    return load_truth()


@pytest.fixture(scope="session")
def files(golden: list[Any]) -> dict[str, Any]:
    """Named golden files: an address-only two-wheeler file, a Guntur send-back, a clean one, a multi-rule one."""
    probe = Systems.open()
    picked: dict[str, Any] = {}
    for gf in golden:
        bundle, _ = gf.build()
        t = NaiveTools(bundle, probe.directory, probe.relay, probe.tracker, probe.core, NOW, NOW.date())
        comp = t.get_completeness_result(bundle.file_id)
        rules = [f["rule_id"] for f in comp["branch_facing"]]
        if "address_only" not in picked and rules and all(r.endswith("DOC-05") for r in rules) \
                and bundle.product == "two-wheeler":
            picked["address_only"] = gf
        if "guntur" not in picked and rules and bundle.branch == "Guntur":
            picked["guntur"] = gf
        if "clean" not in picked and not rules and comp["route"] == "ready_for_approval":
            picked["clean"] = gf
        if "multi" not in picked and len(rules) >= 2:
            picked["multi"] = gf
    assert set(picked) == {"address_only", "guntur", "clean", "multi"}, picked.keys()
    return picked


def make_engine(planner: Any = None, *, budget: Budget | None = None, faults: Faults | None = None,
                folder: Path | None = None, **kw: Any) -> Engine:
    store = Store(folder / "workflow.sqlite") if folder else Store()
    return Engine(store, Systems.open(folder), BusinessClock(NOW), planner or StubPlanner(), budget=budget,
                  faults=faults, **kw)


def to_approval(eng: Engine, gf: Any) -> dict[str, Any]:
    """Receive a golden file and run it to its proposal; return the approval row."""
    bundle, _ = gf.build()
    eng.receive(bundle)
    eng.run_until_rest(bundle.file_id)
    run = eng.store.get(bundle.file_id)
    assert run is not None and run.data.get("approval_id"), f"{bundle.file_id} rests in {run.state if run else None}"
    row = eng.store.approval(run.data["approval_id"])
    assert row is not None
    return row
