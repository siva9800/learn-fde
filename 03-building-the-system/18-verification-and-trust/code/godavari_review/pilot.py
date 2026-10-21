"""A synthetic pilot week (Monday 7 to Friday 11 December 2026): files, the queue, and a log of what analysts did.

The files are new two-wheeler files from the two pilot branches, drawn from Day 7's generator with a new seed and
built by Day 11's synthesiser (both imported). Six analysts: three in Hyderabad (H1 to H3) on Kukatpally files, three
in Vijayawada (V1 to V3) on Guntur files. Their behaviour is simulated, and two patterns are planted on purpose so the
detector can be checked against them: H3 is fast and accurate; V2 rubber-stamps on Friday afternoon, after Thursday's
batch failed at six and reran at nine and two days of files landed at once (Day 6, BATCH_6PM).

The log is what the review screen would record: every field shown, the band, the seconds on it, the action, and every
approval. The truth (what is on the paper) is used only to simulate whether an analyst catches an error and to check
the detector afterwards; those columns are prefixed "sim_" and the detector strips them before it reads anything.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field, replace
from datetime import date, datetime, timedelta
from typing import Any

from .bands import Band, CellBands
from .evidence import FieldEvidence, rows_for
from .queue import ReviewItem, build_item
from evals import candidates
from evals.day11 import RULESETS
from evals.golden import GoldenFile
from evals.labels import paper_label
from evals.normalise import norm_equal
from intake.catalogue import LoanBundle
from intake.day7_inputs import load_day7_module
from intake.pipeline import FileResult, process
from intake.synth import build_file

PILOT_SEED = 18
PILOT_ID_BASE = 61000            # GF-61xxx: December files; the golden set is GF-4xxxx, Day 7's sample GF-25xxx
WEEK = [date(2026, 12, 7) + timedelta(days=i) for i in range(5)]
BRANCH_TEAM = {"Kukatpally": ("H1", "H2", "H3"), "Guntur": ("V1", "V2", "V3")}
FILES_PER_BRANCH_PER_DAY = 6
LATE_BATCH_DAY = date(2026, 12, 10)        # Thursday: the batch fails at six and reruns at nine


@dataclass(frozen=True)
class Profile:
    review_seconds: float       # median seconds on a review-band field
    catch: float                # chance of catching a wrong value in the review band
    forced_seconds: float       # median seconds on the look-first field
    catch_forced: float
    assess_minutes: float       # assessment and memo per file (Day 9: about 3 hours; not the intake part)


NORMAL = Profile(12.0, 0.90, 15.0, 0.95, 170.0)
PROFILES: dict[str, Profile] = {
    "H1": Profile(11.0, 0.92, 14.0, 0.96, 165.0),
    "H2": Profile(13.0, 0.90, 16.0, 0.95, 175.0),
    "H3": Profile(2.6, 0.90, 4.5, 0.95, 140.0),           # fast and accurate: must not be flagged for speed alone
    "V1": Profile(12.0, 0.92, 15.0, 0.96, 170.0),
    "V2": NORMAL,
    "V3": Profile(14.0, 0.90, 17.0, 0.95, 180.0),
}
STAMPING = Profile(1.1, 0.10, 1.3, 0.20, 6.0)            # V2, Friday after 14:00


@dataclass
class PilotFile:
    bundle: LoanBundle
    result: FileResult
    rows: list[FieldEvidence]
    item: ReviewItem
    analyst: str
    arrived: datetime


@dataclass
class Week:
    files: list[PilotFile]
    log: list[dict[str, Any]] = field(default_factory=list)


def pilot_rows() -> list[Any]:
    """Two-wheeler files from Kukatpally and Guntur in a new synthetic month, re-numbered GF-61xxx."""
    day7 = load_day7_module()
    month = day7.make_loan_files(2400, random.Random(PILOT_SEED))
    rows = [f for f in month if f.product == "two-wheeler" and f.branch in BRANCH_TEAM]
    return [replace(f, file_id=f"GF-{PILOT_ID_BASE + i:05d}") for i, f in enumerate(rows)]


def arrivals() -> list[datetime]:
    """When each day's files appear in the queue. Thursday's batch arrives with Friday's."""
    out: list[datetime] = []
    for d in WEEK:
        when = d + timedelta(days=1) if d == LATE_BATCH_DAY else d
        out.extend([datetime(when.year, when.month, when.day, 2, 0)] * FILES_PER_BRANCH_PER_DAY)
    return out


def build_week(bands: dict[tuple[str, str], CellBands], policy: dict[str, Any], bands_version: str,
               mode: str = "prototype") -> Week:
    model = candidates.build("baseline", run_id="pilot-week-1")
    rows_by_branch: dict[str, list[Any]] = {b: [r for r in pilot_rows() if r.branch == b] for b in BRANCH_TEAM}
    files: list[PilotFile] = []
    for branch, team in BRANCH_TEAM.items():
        for k, (row, arrived) in enumerate(zip(rows_by_branch[branch], arrivals())):
            bundle, truth = build_file(row)
            gf = GoldenFile(row.file_id, "pilot", row.product, row.branch, row.channel, row.language_mix, row.pages, row)
            paper = paper_label(gf, bundle, truth).fields
            result = process(bundle, model, RULESETS["two-wheeler"], arrived.date())
            frows = rows_for(bundle, result, "pilot", paper)
            item = build_item(bundle, result, frows, bands, policy, RULESETS["two-wheeler"], arrived, arrived.date(),
                              bands_version, mode)
            files.append(PilotFile(bundle, result, frows, item, team[k % 3], arrived))
    return Week(files)


def _dwell(rng: random.Random, median: float) -> float:
    return round(median * rng.lognormvariate(0.0, 0.35), 1)


def simulate(week: Week, policy: dict[str, Any]) -> Week:
    """Each analyst works their files in arrival order from 10:00, one file at a time: the intake check on screen,
    then assessment, then approval. The log records what the screen would see."""
    s = policy["seconds"]
    by_analyst: dict[str, list[PilotFile]] = {}
    for pf in sorted(week.files, key=lambda p: (p.arrived, p.item.file_id)):
        by_analyst.setdefault(pf.analyst, []).append(pf)
    log: list[dict[str, Any]] = []
    for analyst, todo in sorted(by_analyst.items()):
        rng = random.Random(f"pilot-week-1-{analyst}")
        clock: datetime | None = None
        for pf in todo:
            day_start = datetime(pf.arrived.year, pf.arrived.month, pf.arrived.day, 10, 0)
            if clock is None or clock < day_start:
                clock = day_start
            if clock.hour >= 19 and clock.date() != WEEK[4]:  # carry to the next day; on Friday they stay late
                nxt = clock.date() + timedelta(days=1)
                clock = datetime(nxt.year, nxt.month, nxt.day, 10, 0)
            stamping = analyst == "V2" and clock.date() == WEEK[4] and clock.hour >= 14
            prof = STAMPING if stamping else PROFILES[analyst]
            opened = clock
            log.append({"event": "open", "file_id": pf.item.file_id, "analyst": analyst, "at": opened.isoformat(timespec="seconds")})
            for v in [pf.item.forced, *[f for f in pf.item.fields if not f.forced]]:
                if v is None:
                    continue
                r, band = v.row, v.band
                if v.forced:
                    secs, catch = _dwell(rng, prof.forced_seconds), prof.catch_forced
                elif band == Band.REVIEW:
                    secs, catch = _dwell(rng, prof.review_seconds), prof.catch
                elif band == Band.AUTO:
                    secs, catch = _dwell(rng, s["auto_glance"] if not stamping else 0.4), 0.05
                else:
                    secs, catch = _dwell(rng, s["key_in"] if not stamping else 20.0), 1.0
                action, new_value = "accepted", r.value
                if band == Band.REJECT and r.label is None:
                    action, new_value = "not_in_file", None              # she confirms the document is not there
                elif band == Band.REJECT:
                    action, new_value = "keyed", r.label if rng.random() > 0.01 else r.label + "?"
                elif not r.correct and rng.random() < catch:
                    action, new_value = "corrected", r.label
                    secs += s["review_correct_extra"]
                elif v.forced or band == Band.REVIEW:
                    action = "confirmed"
                    if r.correct and r.value and r.value.isupper() and rng.random() < 0.03:   # a format-only tidy-up
                        action, new_value = "corrected", r.value.title()
                clock += timedelta(seconds=secs)
                log.append({"event": "field", "file_id": pf.item.file_id, "analyst": analyst, "at": clock.isoformat(timespec="seconds"),
                            "field": r.field, "stratum": r.stratum, "band": band.value, "forced": v.forced,
                            "seconds": secs, "action": action, "model_value": r.value, "new_value": new_value,
                            "confidence": r.confidence, "sim_correct_before": r.correct,
                            "sim_correct_after": norm_equal(r.field, new_value, r.label)})
            clock += timedelta(minutes=prof.assess_minutes * rng.uniform(0.85, 1.15))
            log.append({"event": "approve", "file_id": pf.item.file_id, "analyst": analyst, "at": clock.isoformat(timespec="seconds"),
                        "route": pf.item.route})
    week.log = sorted(log, key=lambda e: (e["at"], e["analyst"], e["file_id"]))
    return week
