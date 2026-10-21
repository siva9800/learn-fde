"""Rupees per unit of work, read from the trace store: per file, per branch, per night, per stage, per prompt release.

The ceiling is Day 12's: Rs 12 of model calls for every file, not on average. Three alerts sit on it:

  ceiling    any file over Rs 12 (Day 12's budget, "a check in the run")
  spike      a branch's median for one night more than 1.5 times that branch's week-one median (the pilot's own baseline)
  forecast   this week's mean cost per file times 1,400 files a month, against Day 12's measured Rs 8,900 a month

All money is what Day 12's ledger recorded (non-estimated rows); the estimate for calls that timed out is shown beside
it, never added in silently. The trace total and the ledger total are the same number: a test holds them together.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from statistics import median
from typing import Any

from . import paths  # noqa: F401
from .store import TraceStore
from intake.reference import BRANCH_CODES
from run_nightly_batch import COST_BUDGET_INR, pct     # Day 12's ceiling and its percentile, imported

CEILING_INR = COST_BUDGET_INR
SPIKE_RATIO = 1.5
FILES_PER_MONTH = 1_400                     # the paper-and-PDF intake workload (Days 4, 7, 9)
DAY12_MONTHLY_INR = 8_900                   # Day 12's measured night, scaled to 1,400 files (section 07.5)
BRANCH_OF = {code: name for name, code in BRANCH_CODES.items()}


@dataclass(frozen=True)
class FileCost:
    file_id: str
    trace_id: str
    run: str
    branch: str
    night: date
    inr: float
    estimated_inr: float
    pages: int
    pages_to_model: int
    calls: int
    release: str
    page_filter: str


def file_costs(store: TraceStore) -> list[FileCost]:
    out = []
    for r in store.by_name("loan_file"):
        a = r["attrs"]
        out.append(FileCost(a["kaagaz.file.id"], r["trace_id"], a["kaagaz.run"], BRANCH_OF[a["kaagaz.file.branch_code"]],
                            r["start"].date(), a.get("kaagaz.cost.inr", 0.0), a.get("kaagaz.cost.estimated_inr", 0.0),
                            a["kaagaz.file.pages"], a["kaagaz.file.pages_to_model"], a.get("kaagaz.llm.calls", 0),
                            a["kaagaz.prompt.release"], a["kaagaz.page_filter"]))
    return sorted(out, key=lambda c: (c.night, c.branch, c.file_id))


def stats(values: list[float]) -> dict[str, float]:
    if not values:
        return {"n": 0, "p50": 0.0, "p95": 0.0, "max": 0.0, "total": 0.0, "mean": 0.0}
    return {"n": len(values), "p50": median(values), "p95": pct(values, 0.95), "max": max(values),
            "total": sum(values), "mean": sum(values) / len(values)}


def rollup(costs: list[FileCost], key: str) -> dict[Any, dict[str, float]]:
    groups: dict[Any, list[float]] = defaultdict(list)
    for c in costs:
        groups[getattr(c, key) if key != "night_branch" else (c.night, c.branch)].append(c.inr)
    return {k: stats(v) for k, v in sorted(groups.items())}


def by_stage(store: TraceStore, run: str | None = None) -> dict[str, float]:
    runs = {r["trace_id"]: r["attrs"]["kaagaz.run"] for r in store.by_name("loan_file")}
    out: dict[str, float] = defaultdict(float)
    for r in store.rows("kind = 'model_call'"):
        if run is None or runs.get(r["trace_id"]) == run:
            out[r["attrs"]["kaagaz.llm.stage"]] += r["attrs"].get("kaagaz.cost.inr", 0.0)
    return dict(sorted(out.items()))


def pages_line(costs: list[FileCost]) -> dict[tuple[date, str], dict[str, float]]:
    """The line added after week two: pages in the file and pages the model was shown, per branch per night."""
    groups: dict[tuple[date, str], list[FileCost]] = defaultdict(list)
    for c in costs:
        groups[(c.night, c.branch)].append(c)
    return {k: {"pages": median([c.pages for c in v]), "to_model": median([c.pages_to_model for c in v]),
                "files": len(v)} for k, v in sorted(groups.items())}


@dataclass(frozen=True)
class CostAlert:
    rule: str
    night: date
    scope: str
    value: float
    threshold: float
    traces: tuple[str, ...]
    text: str


def cost_alerts(costs: list[FileCost], baseline_run: str = "pilot-week-1") -> list[CostAlert]:
    alerts: list[CostAlert] = []
    base = {b: median([c.inr for c in costs if c.branch == b and c.run == baseline_run])
            for b in {c.branch for c in costs if c.run == baseline_run}}
    for c in costs:
        if c.inr > CEILING_INR:
            alerts.append(CostAlert("ceiling", c.night, c.file_id, round(c.inr, 2), CEILING_INR, (c.trace_id,),
                                    f"{c.file_id} ({c.branch}) cost Rs {c.inr:.2f} in model calls; the ceiling is "
                                    f"Rs {CEILING_INR:.0f} for every file; {c.pages} pages, {c.calls} calls"))
    nights: dict[tuple[date, str], list[FileCost]] = defaultdict(list)
    for c in costs:
        nights[(c.night, c.branch)].append(c)
    for (night, branch), group in sorted(nights.items()):
        m = median([c.inr for c in group])
        if branch in base and m > SPIKE_RATIO * base[branch]:
            worst = tuple(c.trace_id for c in sorted(group, key=lambda c: -c.inr)[:3])
            alerts.append(CostAlert("spike", night, branch, round(m, 2), round(SPIKE_RATIO * base[branch], 2), worst,
                                    f"{branch} median Rs {m:.2f} per file on {night:%a %d %b}, {m / base[branch]:.1f} times "
                                    f"its week-one median of Rs {base[branch]:.2f}; median pages "
                                    f"{median([c.pages for c in group]):.0f}"))
    return sorted(alerts, key=lambda a: (a.night, a.rule != "spike", a.scope))


def forecast(costs: list[FileCost], run: str) -> dict[str, float]:
    week = [c.inr for c in costs if c.run == run]
    mean = sum(week) / len(week)
    return {"mean": mean, "monthly": mean * FILES_PER_MONTH, "day12_monthly": DAY12_MONTHLY_INR,
            "ratio": mean * FILES_PER_MONTH / DAY12_MONTHLY_INR}
