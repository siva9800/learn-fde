"""Day 18, step 2: the pilot's first week as the review queue would see it.

Run from the chapter folder after tune_thresholds.py (no network, no API key):

    python -X utf8 code/run_pilot_week.py

  1. builds the week's files through Day 11's pipeline and the bands; shows pilot mode refusing unsigned rules
  2. renders Monday's queue (HTML and CSV) and one page per Monday file, with the decision record after the week
  3. simulates six analysts' actions and writes the screen's log
  4. captures every correction with its reason; exports Day 14 development candidates and Day 19 events
  5. runs the rubber-stamping detector on the log (no truth), then checks it against the simulation's truth
  6. draws the spot checks of auto-accepted fields and simulates the blind second read
Writes everything under data/pilot-week-1/.
"""

from __future__ import annotations

import json
import random
import sys
import time
from collections import Counter, defaultdict
from datetime import date
from statistics import median
from typing import Any

from godavari_review import bands as B
from godavari_review import corrections as C
from godavari_review import pilot, render, sampler, stamping
from godavari_review.paths import DATA
from godavari_review.queue import build_item, queue_order
from evals.day11 import RULESETS
from evals.normalise import norm_equal
from intake.ruleset import SignoffError

OUT = DATA / "pilot-week-1"
SAMPLE_KEY = "held-by-the-compliance-head-2026-12"     # in production a secret the analysts' tool cannot read
SECOND_READER = {"Kukatpally": ("the senior analyst", 0.015), "Guntur": ("Lakshmi", 0.0072)}   # Day 14, 03.9


def jsonl(path: Any, rows: list[dict[str, Any]]) -> None:
    render.write(path, "\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in rows))


def main() -> int:
    t0 = time.perf_counter()
    lines: list[str] = []

    def say(line: str = "") -> None:
        print(line)
        lines.append(line)

    policy = B.load_policy()
    if not (DATA / "bands.json").exists():
        print("run code/tune_thresholds.py first")
        return 2
    fitted = B.load(DATA / "bands.json")
    expected_share = json.loads((DATA / "bands.json").read_text(encoding="utf-8"))["summary"]["expected_wrong_share_in_review"]
    version = f"{policy['version']} fitted on Day 14 development, confirmed on test (data/bands.json)"

    say("== Day 18 · pilot week 1: Kukatpally and Guntur, Monday 7 to Friday 11 December 2026 ==")
    week = pilot.build_week(fitted, policy, version)
    say(f"files: {len(week.files)} two-wheeler files ({Counter(p.item.branch for p in week.files)}); "
        f"six analysts; Thursday's batch lands on Friday")
    first = week.files[0]
    try:
        build_item(first.bundle, first.result, first.rows, fitted, policy, RULESETS["two-wheeler"], first.arrived,
                   first.arrived.date(), version, mode="pilot")
        say("pilot mode: rendered (rules are signed)")
    except SignoffError as exc:
        say(f"pilot mode refuses to build a screen: {exc}")
    say(f"prototype mode banner: {first.item.rules_banner}")

    # -- the queue on Monday morning ------------------------------------------------------------------------
    monday = queue_order([p.item for p in week.files if p.arrived.date() == date(2026, 12, 7)])
    links = {i.file_id for i in monday}
    render.write(OUT / "queue-2026-12-07.html", render.render_queue(monday, "Monday 7 December 2026", links))
    render.write(OUT / "queue-2026-12-07.csv", render.queue_csv(monday))
    say()
    say("-- 1. Monday's queue, in order, with the reason each file is there --")
    for k, it in enumerate(monday, start=1):
        say(f"  {k:2}. {it.file_id} {it.branch:10} {render.inr(it.amount):>12}  {it.why}")
    bands_week = Counter(f.band.value for p in week.files for f in p.item.fields)
    forced = Counter(p.item.forced.row.field for p in week.files if p.item.forced)
    say(f"  the week's fields by band: {dict(bands_week)}; look-first field: {dict(forced)}")

    # -- the week, simulated --------------------------------------------------------------------------------
    pilot.simulate(week, policy)
    jsonl(OUT / "action-log.jsonl", [stamping.visible(e) for e in week.log])
    fields_ev = [e for e in week.log if e["event"] == "field"]
    say()
    say("-- 2. what the analysts did --")
    say(f"  {len(fields_ev)} fields shown; actions {dict(Counter(e['action'] for e in fields_ev))}")
    items = {p.item.file_id: p for p in week.files}
    corr: list[C.Correction] = []
    for e in fields_ev:
        if e["action"] not in ("corrected", "keyed", "not_in_file"):
            continue
        pf = items[e["file_id"]]
        row = next(r for r in pf.rows if r.field == e["field"])
        reason = C.reason_for(row.field, e["model_value"], e["new_value"], row.evidence)
        corr.append(C.Correction(e["file_id"], e["field"], e["stratum"], e["band"], e["model_value"], e["new_value"],
                                 reason, e["analyst"], e["at"], e["confidence"], pf.result.output.model_name,
                                 pf.item.rules_fingerprint, version))
    content = [c for c in corr if c.content_change and c.model_value is not None]
    keyed = [c for c in corr if c.model_value is None]          # keyed values and "not in the file" answers
    jsonl(OUT / "corrections.jsonl", [C.to_event(c) for c in corr])
    jsonl(OUT / "dev-candidates.jsonl", [C.to_dev_candidate(c) for c in content + keyed])
    say(f"  corrections captured: {len(corr)} ({dict(Counter(c.reason for c in corr))})")
    say(f"  to Day 14's development split as candidates: {len(content) + len(keyed)} "
        f"({len(content)} content corrections + {len(keyed)} answers where the model was unsure); "
        f"format-only ones go to Day 19 only")
    missed = [e for e in fields_ev if e["sim_correct_before"] and False] or \
             [e for e in fields_ev if not e["sim_correct_after"]]
    say(f"  (simulation truth) wrong values still in approved files: {len(missed)}, by analyst "
        f"{dict(Counter(e['analyst'] for e in missed))}, by band {dict(Counter(e['band'] for e in missed))}")

    # -- rubber-stamping, from the log alone ----------------------------------------------------------------
    sess = [stamping.judge(s) for s in stamping.sessions(week.log)]
    say()
    say("-- 3. rubber-stamping signals (the detector reads the log, never the truth) --")
    say(f"  {'analyst':7} {'day':10} {'half':4} {'files':>5} {'med s check':>11} {'med s first':>11} {'approvals':>9}  verdict")
    for s in sess:
        if s.verdict != "ok" or s.analyst == "V2":
            med_r = f"{median(s.review_seconds):.1f}" if s.review_seconds else "-"
            med_f = f"{median(s.forced_seconds):.1f}" if s.forced_seconds else "-"
            say(f"  {s.analyst:7} {s.day:10} {s.half:4} {len(s.files):5} {med_r:>11} {med_f:>11} {len(s.approvals):9}  "
                f"{s.verdict}{': ' + '; '.join(s.signals) if s.signals else ''}")
    flagged = [s for s in sess if s.verdict.startswith("suspected")]
    say(f"  sessions: {len(sess)}; suspected {len(flagged)}; fast-only {sum(s.verdict.startswith('fast') for s in sess)}")
    say("  weekly override check (corrections in the review band against the bands' expected wrong share "
        f"{expected_share:.1%}):")
    for w in stamping.weekly_overrides(week.log, expected_share):
        say(f"    {w['analyst']}: corrected {w['corrections']} of {w['review_fields']} fields to check, expected "
            f"{w['expected']}, chance of this few {w['p_this_few']:.3f}{'  LOW' if w['low'] else ''}")
    by_session_missed: dict[tuple[str, str, str], int] = defaultdict(int)
    for e in missed:
        at = e["at"]
        by_session_missed[(e["analyst"], at[:10], "AM" if int(at[11:13]) < 13 else "PM")] += 1
    caught = sum(by_session_missed[(s.analyst, s.day, s.half)] for s in flagged)
    others = sorted({e["analyst"] for e in missed} - {s.analyst for s in flagged})
    say(f"  (simulation truth) wrong values left in approved files: {len(missed)}; in the suspected session: {caught}; "
        f"in sessions with normal signals: {len(missed) - caught} ({', '.join(others) or 'none'}). Careful review "
        f"catches most wrong values, not all")

    # -- spot checks -----------------------------------------------------------------------------------------
    approved = [(p.item.file_id, p.item.branch) for p in week.files
                if any(f.band == B.Band.AUTO and not f.forced for f in p.item.fields)]
    targeted = {fid for s in flagged for fid in s.files}
    picks = sampler.sample(approved, SAMPLE_KEY, targeted)
    rng = random.Random("second-read-week-1")
    checked = wrong = disagree = reader_slips = 0
    found: list[tuple[str, str]] = []
    for pk in picks:
        pf = items[pk.file_id]
        who, slip = SECOND_READER[pk.branch]
        final = {e["field"]: e for e in fields_ev if e["file_id"] == pk.file_id}
        scope = [f for f in pf.item.fields if (f.band == B.Band.AUTO and not f.forced) or pk.why != "random"]
        for f in scope:
            checked += 1
            approved_value = final[f.row.field]["new_value"]
            reader_value = f.row.label if rng.random() > slip else (f.row.label or "") + "7"
            if not norm_equal(f.row.field, approved_value, reader_value):
                disagree += 1                  # to the two team leads, who read the paper (Day 14, rule 2)
                if norm_equal(f.row.field, approved_value, f.row.label):
                    reader_slips += 1
                else:
                    wrong += 1
                    found.append((pk.why, f"{pk.file_id} {f.row.field}: approved {approved_value!r}, paper "
                                          f"{f.row.label!r} ({f.band.value}, {pk.why})"))
    rand_files = [p for p in picks if p.why == "random"]
    auto_checked = sum(len([f for f in items[p.file_id].item.fields if f.band == B.Band.AUTO and not f.forced])
                       for p in rand_files)
    auto_wrong = sum(1 for why, _ in found if why == "random")
    lo, hi = sampler.proved_so_far(auto_checked, auto_wrong)
    say()
    say("-- 4. spot checks after approval --")
    say(f"  files approved with auto-accepted fields: {len(approved)}; drawn: {len(rand_files)} at random "
        f"({sampler.SHARE:.0%} per branch, at least {sampler.MIN_PER_BRANCH}) + {len(picks) - len(rand_files)} targeted")
    say(f"  second read (blind; Kukatpally by the senior analyst, Guntur by Lakshmi): {checked} fields, {disagree} "
        f"disagreements -> team leads: {wrong} approved values wrong, {reader_slips} second-reader slips")
    for _why, text in found:
        say(f"    {text}")
    need = sampler.fields_to_detect(0.01)
    say(f"  random checks so far: {auto_wrong} wrong in {auto_checked} auto-accepted fields, upper bound {hi:.1%}; "
        f"to see one error at a true 1 percent with 95 percent probability needs {need} fields, "
        f"about {need / max(1, auto_checked):.0f} weeks at this rate")

    # -- decision records and the file pages ----------------------------------------------------------------
    for it in monday:
        ev = [e for e in week.log if e["file_id"] == it.file_id]
        fe = [e for e in ev if e["event"] == "field"]
        appr = next(e for e in ev if e["event"] == "approve")
        forced_ev = next((e for e in fe if e["forced"]), None)
        rec = {"analyst": appr["analyst"], "approved_at": appr["at"], "pages": len(items[it.file_id].bundle.pages),
               "bundle_sha256": pilot_sha(items[it.file_id].bundle),
               "accepted": sum(e["action"] == "accepted" for e in fe), "confirmed": sum(e["action"] == "confirmed" for e in fe),
               "corrected": sum(e["action"] == "corrected" for e in fe), "keyed": sum(e["action"] == "keyed" for e in fe),
               "forced_field": forced_ev["field"] if forced_ev else "-", "forced_seconds": forced_ev["seconds"] if forced_ev else 0.0,
               "corrections": [f"{e['field']}: {e['model_value']} -> {e['new_value']} ({e['analyst']})"
                               for e in fe if e["action"] == "corrected"]}
        render.write(OUT / "files" / f"{it.file_id}.html", render.render_file(it, rec))
    say()
    say(f"wrote data/pilot-week-1/: queue page and CSV, {len(monday)} file pages, action log, corrections, "
        f"development candidates, this report; {time.perf_counter() - t0:.2f} s")
    render.write(OUT / "pilot-week-report.md", "# Pilot week 1, simulated\n\n> Generated by `code/run_pilot_week.py`. "
                 "Synthetic data and simulated analysts. Do not edit by hand.\n\n```text\n" + "\n".join(lines) + "\n```")
    return 0


def pilot_sha(bundle: Any) -> str:
    from evals.golden import bundle_sha256
    return bundle_sha256(bundle)


if __name__ == "__main__":
    sys.exit(main())
