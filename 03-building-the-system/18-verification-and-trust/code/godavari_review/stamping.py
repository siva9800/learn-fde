"""Signals that someone is approving without looking, from the review screen's own log. No truth is used.

Three signals per analyst per session (morning, before 13:00; afternoon after), and one per week:

  dwell      median seconds on review-band fields below a floor: nobody reads a crop and compares in that time
  forced     median seconds on the look-first field below a floor
  burst      several approvals inside a short window: the assessment between them was skipped too
  overrides  (weekly) corrections in the review band far below what the bands predict, a Poisson tail probability

Speed alone is not a flag: an expert can be fast. A session is "suspected" only when dwell is low and either the
look-first dwell or a burst agrees. The output goes to the team lead as a workload signal and a request for a second
read of those files, not to HR; what is measured, and who sees it, is agreed with the analysts first.
"""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from statistics import median
from typing import Any

DWELL_FLOOR_S = 3.0
FORCED_FLOOR_S = 2.0
BURST_N, BURST_WINDOW = 3, timedelta(minutes=20)
OVERRIDE_P = 0.05


@dataclass
class Session:
    analyst: str
    day: str
    half: str
    files: set[str] = field(default_factory=set)
    review_seconds: list[float] = field(default_factory=list)
    forced_seconds: list[float] = field(default_factory=list)
    approvals: list[datetime] = field(default_factory=list)
    corrections: int = 0
    signals: list[str] = field(default_factory=list)
    verdict: str = "ok"


def visible(event: dict[str, Any]) -> dict[str, Any]:
    """What the detector may read: the log without the simulation's truth columns."""
    return {k: v for k, v in event.items() if not k.startswith("sim_")}


def _half(at: datetime) -> str:
    return "AM" if at.hour < 13 else "PM"


def sessions(log: list[dict[str, Any]]) -> list[Session]:
    out: dict[tuple[str, str, str], Session] = {}
    for raw in log:
        e = visible(raw)
        at = datetime.fromisoformat(e["at"])
        key = (e["analyst"], at.date().isoformat(), _half(at))
        s = out.setdefault(key, Session(*key))
        s.files.add(e["file_id"])
        if e["event"] == "field":
            if e["forced"]:
                s.forced_seconds.append(e["seconds"])
            elif e["band"] == "review":
                s.review_seconds.append(e["seconds"])
            if e["action"] == "corrected" and e["band"] == "review":
                s.corrections += 1
        elif e["event"] == "approve":
            s.approvals.append(at)
    return sorted(out.values(), key=lambda s: (s.day, s.half, s.analyst))


def burst(approvals: list[datetime]) -> bool:
    a = sorted(approvals)
    return any(a[i + BURST_N - 1] - a[i] <= BURST_WINDOW for i in range(len(a) - BURST_N + 1))


def judge(s: Session) -> Session:
    low_dwell = bool(s.review_seconds) and median(s.review_seconds) < DWELL_FLOOR_S
    low_forced = bool(s.forced_seconds) and median(s.forced_seconds) < FORCED_FLOOR_S
    if low_dwell:
        s.signals.append(f"median {median(s.review_seconds):.1f} s on fields to check")
    if low_forced:
        s.signals.append(f"median {median(s.forced_seconds):.1f} s on the look-first field")
    if burst(s.approvals):
        s.signals.append(f"{BURST_N} or more approvals inside {int(BURST_WINDOW.total_seconds() // 60)} minutes")
    if low_dwell and (low_forced or burst(s.approvals)):
        s.verdict = "suspected: second read of these files"
    elif low_dwell:
        s.verdict = "fast: no action (speed alone is not a flag)"
    return s


def poisson_cdf(k: int, lam: float) -> float:
    return sum(math.exp(-lam) * lam ** i / math.factorial(i) for i in range(k + 1))


def weekly_overrides(log: list[dict[str, Any]], expected_wrong_share: float) -> list[dict[str, Any]]:
    """Corrections in the review band against what the bands predict. A low tail probability means the analyst is
    correcting far less than the files need; with a week of data it is weak evidence on its own."""
    per: dict[str, dict[str, float]] = defaultdict(lambda: {"review": 0, "corrections": 0})
    for raw in log:
        e = visible(raw)
        if e["event"] == "field" and e["band"] == "review" and not e["forced"]:
            per[e["analyst"]]["review"] += 1
            per[e["analyst"]]["corrections"] += e["action"] == "corrected"
    rows = []
    for analyst, c in sorted(per.items()):
        lam = c["review"] * expected_wrong_share
        p = poisson_cdf(int(c["corrections"]), lam)
        rows.append({"analyst": analyst, "review_fields": int(c["review"]), "corrections": int(c["corrections"]),
                     "expected": round(lam, 1), "p_this_few": round(p, 3), "low": p < OVERRIDE_P})
    return rows
