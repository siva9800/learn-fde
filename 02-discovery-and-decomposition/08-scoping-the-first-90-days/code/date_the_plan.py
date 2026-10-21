"""Turn Day 7's sequenced workstreams into a dated 90-day plan, checked against the customer's calendar.

Reads:
  - the Day 7 plan JSON (../07-decomposition/data/godavari-decomposition-plan.json): the workstream
    order and a suggested start and end week for each;
  - data/godavari-plan-adjustments.csv: Day 8's changes to those weeks, each with a reason, plus the
    phases of the 90 days;
  - data/godavari-calendar.csv: the customer's blackout dates (holidays, the release freeze, Sankranti
    week, the RBI inspection, month end), each saying which kinds of work it blocks;
  - data/godavari-milestones.csv: the milestones and checkpoints, each with an owner on both sides,
    a sentence a COO can read, its dependencies and any hard date;
  - data/godavari-raci.csv: the two-company RACI.

Prints the dated workstreams, the dated milestones (moved out of blackouts, with the reason), the
checks a reviewer would run, and, with --slip, what a late workstream does to everything after it.
On a normal run it writes data/godavari-90-day-schedule.json and data/godavari-90-day-plan.md (the
milestone table and a Mermaid Gantt).

Python 3.14, standard library only. Run from the chapter folder:

    python -X utf8 code/date_the_plan.py
    python -X utf8 code/date_the_plan.py --slip W5=2
    python -X utf8 code/date_the_plan.py --no-write --milestones my-variant.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import date, timedelta
from pathlib import Path

WEEKDAYS = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4}
CHECKPOINT_WEEKS = (2, 4, 6, 12)           # Part 2's checkpoints; each needs a question the customer answers
THIN_BUFFER_DAYS = 5                       # less than a working week before a hard date is a risk to name
JARGON = ("api", "soap", "sftp", "idempot", "llm", "model", "rag", "json", "endpoint",
          "pipeline", "vector", "schema", "sandbox", "vpc", "deploy")
GODAVARI, KAAGAZ = "G:", "K:"


@dataclass
class Blackout:
    start: date
    end: date
    name: str
    blocks: set[str]
    site: str

    def hits(self, day: date, tags: set[str], site: str) -> bool:
        if not self.start <= day <= self.end:
            return False
        if "none" in self.blocks:
            return False
        if self.site != "all" and site != "all" and self.site != site:
            return False
        return "all" in self.blocks or bool(self.blocks & tags)


@dataclass
class Workstream:
    code: str
    name: str
    start_week: int
    end_week: int
    depends_on: list[str]
    owner: str
    tags: set[str] = field(default_factory=set)
    reason: str = ""
    changed: bool = False
    kind: str = "workstream"
    start: date | None = None
    end: date | None = None
    working_days: int = 0
    blocked: dict[str, int] = field(default_factory=dict)


@dataclass
class Milestone:
    id: str
    week: int
    weekday: str
    workstream: str
    kind: str
    tags: set[str]
    site: str
    depends_on: list[str]
    direction: str
    hard_by: date | None
    kaagaz_owner: str
    godavari_owner: str
    coo_line: str
    question: str
    planned: date | None = None
    dated: date | None = None
    moved_by: list[str] = field(default_factory=list)
    buffer_days: int | None = None
    problems: list[str] = field(default_factory=list)


def split(cell: str, sep: str = "|") -> set[str]:
    return {t.strip() for t in cell.split(sep) if t.strip()}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def load_calendar(path: Path) -> list[Blackout]:
    return [Blackout(date.fromisoformat(r["start"]), date.fromisoformat(r["end"]), r["name"],
                     split(r["blocks"]), r["site"]) for r in read_csv(path)]


def load_workstreams(plan_json: Path, adjustments: Path) -> tuple[list[Workstream], list[Workstream]]:
    day7 = json.loads(plan_json.read_text(encoding="utf-8"))
    streams = {w["code"]: Workstream(w["code"], w["name"], w["start_week"], w["end_week"],
                                     w["depends_on"], w["owner"]) for w in day7}
    phases: list[Workstream] = []
    for r in read_csv(adjustments):
        if r["kind"] == "phase":
            phases.append(Workstream(r["code"], r["name"], int(r["start_week"]), int(r["end_week"]),
                                     [], "", reason=r["reason"], kind="phase"))
            continue
        w = streams.get(r["code"])
        if w is None:
            raise SystemExit(f"adjustment for {r['code']}, which is not in the Day 7 plan")
        new_start = int(r["start_week"]) if r["start_week"] else w.start_week
        new_end = int(r["end_week"]) if r["end_week"] else w.end_week
        w.changed = (new_start, new_end) != (w.start_week, w.end_week)
        w.start_week, w.end_week = new_start, new_end
        w.tags, w.reason = split(r["tags"]), r["reason"]
    return list(streams.values()), phases


def load_milestones(path: Path, start: date) -> list[Milestone]:
    out = []
    for r in read_csv(path):
        m = Milestone(r["id"], int(r["week"]), r["weekday"], r["workstream"], r["kind"],
                      split(r["tags"]), r["site"], r["depends_on"].split(), r["direction"] or "later",
                      date.fromisoformat(r["hard_by"]) if r["hard_by"] else None,
                      r["kaagaz_owner"], r["godavari_owner"], r["coo_line"], r["question"])
        m.planned = start + timedelta(days=7 * (m.week - 1) + WEEKDAYS[m.weekday])
        out.append(m)
    return out


def is_working_day(day: date, cal: list[Blackout]) -> bool:
    return day.weekday() < 5 and not any(b.hits(day, {"all"}, "all") and "all" in b.blocks for b in cal)


def working_days_between(a: date, b: date, cal: list[Blackout]) -> int:
    """Working days after a, up to and including b."""
    n, d = 0, a
    while d < b:
        d += timedelta(days=1)
        n += is_working_day(d, cal)
    return n


def date_workstreams(rows: list[Workstream], start: date, cal: list[Blackout]) -> None:
    for w in rows:
        w.start = start + timedelta(days=7 * (w.start_week - 1))
        w.end = w.start + timedelta(days=7 * (w.end_week - w.start_week) + 4)
        d = w.start
        while d <= w.end:
            if is_working_day(d, cal):
                w.working_days += 1
                for b in cal:
                    if "all" not in b.blocks and b.hits(d, w.tags, "all"):
                        w.blocked[b.name] = w.blocked.get(b.name, 0) + 1
            d += timedelta(days=1)


def schedule(ms: list[Milestone], cal: list[Blackout], slips: dict[str, int]) -> dict[str, Milestone]:
    """Date every milestone: planned date, plus any slip on its workstream, after its dependencies,
    then out of any blackout that blocks its kind of work, in its preferred direction."""
    by_id = {m.id: m for m in ms}
    done: dict[str, Milestone] = {}
    pending = list(ms)
    while pending:
        ready = [m for m in pending if all(d in done for d in m.depends_on)]
        if not ready:
            raise SystemExit("dependency cycle among " + ", ".join(m.id for m in pending))
        for m in ready:
            m.moved_by = []
            day = m.planned + timedelta(days=7 * slips.get(m.workstream, 0))
            floor = max((done[d].dated for d in m.depends_on), default=None)
            if floor is not None and day <= floor:
                day = floor + timedelta(days=1)
                m.moved_by.append("after " + ", ".join(m.depends_on))
            step = -1 if m.direction == "earlier" else 1
            while True:
                hit = [b.name for b in cal if b.hits(day, m.tags, m.site)]
                if day.weekday() < 5 and not hit:
                    break
                for name in hit:
                    if name not in m.moved_by:
                        m.moved_by.append(name)
                day += timedelta(days=step)
                if step < 0 and floor is not None and day <= floor:
                    step, day = 1, floor + timedelta(days=1)      # cannot go earlier than a dependency
            m.dated = day
            done[m.id] = m
            pending.remove(m)
    return {k: by_id[k] for k in by_id}


def check(ms: dict[str, Milestone], streams: list[Workstream], start: date, cal: list[Blackout],
          raci: list[dict[str, str]]) -> list[str]:
    day90 = start + timedelta(days=89)
    findings: list[str] = []
    codes = {w.code for w in streams}
    for m in ms.values():
        m.problems = []
        if m.dated > day90:
            m.problems.append(f"after day 90 ({day90:%d %b})")
        if m.hard_by:
            if m.dated > m.hard_by:
                m.problems.append(f"HARD DATE MISSED: due by {m.hard_by:%a %d %b}")
                m.buffer_days = -working_days_between(m.hard_by, m.dated, cal)
            else:
                m.buffer_days = working_days_between(m.dated, m.hard_by, cal)
                if m.buffer_days < THIN_BUFFER_DAYS:
                    m.problems.append(f"thin buffer: {m.buffer_days} working days before {m.hard_by:%d %b}")
        if not m.kaagaz_owner or not m.godavari_owner:
            m.problems.append("needs an owner on both sides")
        words = m.coo_line.lower().replace(",", " ").replace(";", " ").split()
        jargon = [j for j in JARGON if any(w.startswith(j) for w in words)]
        if jargon:
            m.problems.append("COO line uses " + ", ".join(jargon))
        if len(words) > 25:
            m.problems.append(f"COO line is {len(words)} words; keep it under 25")
        if m.kind == "checkpoint" and not m.question:
            m.problems.append("a checkpoint without a question for the customer")
    for wk in CHECKPOINT_WEEKS:
        hits = [m for m in ms.values() if m.kind == "checkpoint"
                and (m.dated - start).days // 7 + 1 == wk]
        if not hits:
            findings.append(f"no checkpoint lands in week {wk}")
    for w in streams:
        for d in w.depends_on:
            dep = next(x for x in streams if x.code == d)
            if w.start_week < dep.start_week + 1:
                findings.append(f"{w.code} starts in week {w.start_week}, before the week after {d} starts "
                                f"(week {dep.start_week}): Day 7's dependency rule is broken")
    rows = {r["code"]: r for r in raci}
    for w in streams:
        r = rows.get(w.code)
        if r is None:
            findings.append(f"{w.code} has no RACI row")
            continue
    for code, r in rows.items():
        a = [k for k, v in r.items() if k != "code" and "A" in v]
        if len(a) != 1:
            findings.append(f"RACI {code}: {len(a)} people accountable; exactly one is allowed")
        w = next((x for x in streams if x.code == code), None)
        if (w is None or w.end_week >= 11) and not any(k.startswith(GODAVARI) and "R" in v
                                                       for k, v in r.items()):
            findings.append(f"RACI {code}: runs past week 10 with nobody at Godavari responsible")
        if code not in codes and code not in {"PLAN", "RUN"}:
            findings.append(f"RACI row {code} matches no workstream")
    return findings


def print_report(streams, phases, ms, findings, start, cal, raci) -> None:
    day90 = start + timedelta(days=89)
    print(f"== Godavari 90-day plan: day 1 {start:%a %d %b %Y}, day 90 {day90:%a %d %b %Y} ==\n")
    print("phases (they overlap on purpose):")
    for p in phases:
        print(f"  {p.code} {p.name:22s} weeks {p.start_week:2d} to {p.end_week:2d}  {p.start:%d %b} to {p.end:%d %b}")
    print("\nworkstreams, dated (Day 7's order; changed weeks are marked *):")
    print(f"  {'code':4s} {'workstream':44s} {'weeks':>7s}  {'from':6s}  {'to':6s} {'days':>4s}  accountable")
    acc = {r["code"]: next((k for k, v in r.items() if k != "code" and "A" in v), "?") for r in raci}
    for w in streams:
        mark = "*" if w.changed else " "
        print(f"  {w.code:4s} {w.name[:44]:44s} {w.start_week:2d} to {w.end_week:2d}{mark} "
              f"{w.start:%d %b}  {w.end:%d %b} {w.working_days:4d}  {acc.get(w.code, '?')}")
    print("\nwhy the weeks changed from Day 7, and what the calendar takes away:")
    for w in streams:
        if w.changed:
            print(f"  {w.code}: {w.reason}")
        for name, n in w.blocked.items():
            print(f"  {w.code}: {n} working day(s) inside '{name}'")
    print("\nmilestones (moved out of blackouts where needed):")
    print(f"  {'id':3s} {'kind':10s} {'planned':10s} {'dated':10s} {'wk':>2s}  {'Kaagaz':22s} {'Godavari':26s} moved by")
    for m in sorted(ms.values(), key=lambda m: (m.dated, m.id)):
        wk = (m.dated - start).days // 7 + 1
        moved = "; ".join(m.moved_by) if m.dated != m.planned else ""
        print(f"  {m.id:3s} {m.kind:10s} {m.planned:%a %d %b} {m.dated:%a %d %b} {wk:2d}  "
              f"{m.kaagaz_owner[:22]:22s} {m.godavari_owner[:26]:26s} {moved}")
    print("\nthe COO's view (one line per milestone, in date order):")
    for m in sorted(ms.values(), key=lambda m: (m.dated, m.id)):
        print(f"  {m.dated:%d %b}  {m.coo_line}")
    print("\ncheckpoints and the question the customer answers at each:")
    for m in sorted((m for m in ms.values() if m.kind == "checkpoint"), key=lambda m: m.dated):
        wk = (m.dated - start).days // 7 + 1
        print(f"  week {wk:2d} {m.dated:%a %d %b}: {m.question}")
    print("\nhard dates and buffers:")
    for m in sorted((m for m in ms.values() if m.hard_by), key=lambda m: m.dated):
        print(f"  {m.id} due by {m.hard_by:%a %d %b}, dated {m.dated:%a %d %b}: buffer {m.buffer_days} working day(s)")
    print("\nchecks:")
    issues = [f"{m.id}: {p}" for m in sorted(ms.values(), key=lambda m: m.id) for p in m.problems] + findings
    for line in issues or ["all clear"]:
        print(f"  - {line}")


def print_slip(base: dict[str, date], ms: dict[str, Milestone], slips: dict[str, int], cal,
               findings: list[str]) -> None:
    label = ", ".join(f"{k} +{v} week(s)" for k, v in slips.items())
    print(f"== what a slip of {label} does ==")
    moved = [m for m in sorted(ms.values(), key=lambda m: m.id) if m.dated != base[m.id]]
    if not moved:
        print("  nothing moves")
    for m in moved:
        shift = working_days_between(base[m.id], m.dated, cal)
        direct = m.workstream in slips
        note = "direct" if direct else "knock-on"
        if direct and shift > 5 * slips[m.workstream]:
            note += f", amplified by {shift - 5 * slips[m.workstream]} working day(s)"
        extra = f" ({'; '.join(m.moved_by)})" if m.moved_by else ""
        print(f"  {m.id} {base[m.id]:%a %d %b} -> {m.dated:%a %d %b}  +{shift} working days, {note}{extra}")
    print("\nchecks after the slip:")
    issues = [f"{m.id}: {p}" for m in sorted(ms.values(), key=lambda m: m.id) for p in m.problems] + findings
    for line in issues or ["all clear"]:
        print(f"  - {line}")


def gantt(streams, phases, ms, cal, start) -> str:
    day90 = start + timedelta(days=89)
    clean = lambda s: s.replace(":", "").replace("#", "").replace(";", ",")
    lines = ["```mermaid", "gantt", "    title Godavari Finance: the first 90 days", "    dateFormat YYYY-MM-DD",
             "    axisFormat %d %b", "    section Phases"]
    for p in phases:
        lines.append(f"    {clean(p.name)} :{p.code.lower()}, {p.start}, {p.end + timedelta(days=1)}")
    lines.append("    section Workstreams")
    for w in streams:
        lines.append(f"    {w.code} {clean(w.name.split(':')[0])} :{w.code.lower()}, {w.start}, {w.end + timedelta(days=1)}")
    lines.append("    section Customer calendar")
    for i, b in enumerate(cal):
        if b.end >= start and b.start <= day90 and b.end > b.start:
            lines.append(f"    {clean(b.name.split('(')[0].strip())} :crit, cal{i}, {b.start}, {b.end + timedelta(days=1)}")
    lines.append("    section Milestones")
    for m in sorted(ms.values(), key=lambda m: m.dated):
        label = clean(m.coo_line.split(";")[0].split(",")[0]).rstrip(".")
        if len(label) > 44:
            label = label[:44].rsplit(" ", 1)[0] + "..."
        lines.append(f"    {m.id} {label} :milestone, {m.id.lower()}, {m.dated}, 0d")
    lines.append("```")
    return "\n".join(lines)


def plan_markdown(streams, ms, start, chart) -> str:
    out = ["# Godavari 90-day plan: generated tables", "",
           "> Written by `code/date_the_plan.py` from the Day 7 plan, the adjustments, the calendar and the",
           "> milestones. Do not edit by hand; edit the CSVs and rerun.", "",
           "| Code | Workstream | Weeks | From | To |", "|---|---|---|---|---|"]
    for w in streams:
        out.append(f"| {w.code} | {w.name} | {w.start_week} to {w.end_week} | {w.start:%a %d %b %Y} | {w.end:%a %d %b %Y} |")
    out += ["", "| Date | Week | Id | What the COO reads | Kaagaz | Godavari |", "|---|---|---|---|---|---|"]
    for m in sorted(ms.values(), key=lambda m: (m.dated, m.id)):
        wk = (m.dated - start).days // 7 + 1
        out.append(f"| {m.dated:%a %d %b %Y} | {wk} | {m.id} | {m.coo_line} | {m.kaagaz_owner} | {m.godavari_owner} |")
    out += ["", chart, ""]
    return "\n".join(out)


def main(argv: list[str]) -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--start", default="2026-10-26", help="day 1 of the engagement (a Monday)")
    ap.add_argument("--plan", default="../07-decomposition/data/godavari-decomposition-plan.json")
    ap.add_argument("--adjust", default="data/godavari-plan-adjustments.csv")
    ap.add_argument("--calendar", default="data/godavari-calendar.csv")
    ap.add_argument("--milestones", default="data/godavari-milestones.csv")
    ap.add_argument("--raci", default="data/godavari-raci.csv")
    ap.add_argument("--slip", action="append", default=[], help="CODE=WEEKS, e.g. W5=2 (repeatable)")
    ap.add_argument("--no-write", action="store_true", help="print only; leave data/ untouched (for experiments)")
    args = ap.parse_args(argv[1:])
    start = date.fromisoformat(args.start)
    if start.weekday() != 0:
        raise SystemExit(f"--start must be a Monday; {start} is a {start:%A}")
    cal = load_calendar(Path(args.calendar))
    streams, phases = load_workstreams(Path(args.plan), Path(args.adjust))
    date_workstreams(streams, start, cal)
    date_workstreams(phases, start, cal)
    raci = read_csv(Path(args.raci))
    known = {w.code for w in streams} | {p.code for p in phases} | {"PLAN"}
    ms_list = load_milestones(Path(args.milestones), start)
    for m in ms_list:
        if m.workstream not in known:
            raise SystemExit(f"{m.id} belongs to {m.workstream!r}, which is not a workstream, phase or PLAN")
    ms = schedule(ms_list, cal, {})
    findings = check(ms, streams, start, cal, raci)
    if not args.slip:
        print_report(streams, phases, ms, findings, start, cal, raci)
        if args.no_write:
            return
        chart = gantt(streams, phases, ms, cal, start)
        out = Path("data")
        (out / "godavari-90-day-schedule.json").write_text(json.dumps({
            "day_1": str(start), "day_90": str(start + timedelta(days=89)),
            "workstreams": [{**asdict(w), "tags": sorted(w.tags)} for w in streams],
            "milestones": [{**asdict(m), "tags": sorted(m.tags)} for m in ms.values()],
            "findings": findings}, indent=2, default=str) + "\n", encoding="utf-8", newline="\n")
        (out / "godavari-90-day-plan.md").write_text(plan_markdown(streams, ms, start, chart),
                                                     encoding="utf-8", newline="\n")
        print("\nwrote data/godavari-90-day-schedule.json and data/godavari-90-day-plan.md")
        return
    slips = {}
    for s in args.slip:
        code, _, weeks = s.partition("=")
        slips[code.strip()] = int(weeks)
    base = {k: m.dated for k, m in ms.items()}
    ms = schedule(load_milestones(Path(args.milestones), start), cal, slips)
    print_slip(base, ms, slips, cal, check(ms, streams, start, cal, raci))


if __name__ == "__main__":
    main(sys.argv)
