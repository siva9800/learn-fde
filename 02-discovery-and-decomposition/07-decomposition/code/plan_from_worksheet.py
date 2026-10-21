"""Turn a filled decomposition worksheet (markdown) into a sequenced plan with risk and value scores.

Reads the "Step 4" workstream table from a worksheet such as ../worksheet/godavari-decomposition.md,
checks it, sequences the workstreams by risk and value while respecting dependencies, assigns a start
week to each, and writes ../data/<worksheet-name>-plan.json plus a Mermaid Gantt snippet you can paste
into a document.

The rule it applies is the one the chapter teaches (section 06): the riskiest unknowns go first,
value breaks ties, and nothing starts before what it depends on has started. Day 8 turns this order
into a dated 90-day plan; this script only produces the order and a suggested start week.

Python 3.14, standard library only. Run from the chapter folder:

    python -X utf8 code/plan_from_worksheet.py worksheet/godavari-decomposition.md
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

RISK_WEIGHT = 2.0     # risk counts double: an unknown found in week 2 is cheap, in week 10 it is a rewrite
VALUE_WEIGHT = 1.0
MAX_PARALLEL = 3      # how many workstreams one FDE plus the customer's engineers can keep moving at once


@dataclass
class Workstream:
    code: str
    name: str
    value: int
    risk: int
    depends_on: list[str]
    weeks: int
    owner: str
    why: str
    priority: float = 0.0
    start_week: int = 0
    end_week: int = 0
    rank: int = 0
    warnings: list[str] = field(default_factory=list)


HEADER_RE = re.compile(r"^##\s+Step 4\b", re.IGNORECASE)
ROW_RE = re.compile(r"^\|\s*(W\d+)\s*\|")


def read_step4_table(text: str) -> list[Workstream]:
    """Find the Step 4 section and parse every row whose first cell is a workstream code (W1, W2, ...)."""
    lines = text.splitlines()
    try:
        start = next(i for i, line in enumerate(lines) if HEADER_RE.match(line))
    except StopIteration as exc:
        raise SystemExit("worksheet has no '## Step 4' heading; fill the template first") from exc
    rows: list[Workstream] = []
    for line in lines[start + 1:]:
        if line.startswith("## "):
            break
        if not ROW_RE.match(line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 8:
            raise SystemExit(f"row {cells[0]!r} has {len(cells)} cells; the table needs 8 columns")
        code, name, value, risk, deps, weeks, owner, why = cells[:8]
        if not name:
            continue      # an unfilled template row
        try:
            value_n, risk_n, weeks_n = int(value), int(risk), int(weeks)
        except ValueError as exc:
            raise SystemExit(f"{code} ({name}): value, risk and weeks must be whole numbers; got {value!r}, {risk!r}, {weeks!r}") from exc
        depends_on = [d.strip() for d in re.split(r"[,; ]+", deps) if d.strip().upper().startswith("W")]
        rows.append(Workstream(
            code=code, name=name, value=value_n, risk=risk_n, depends_on=depends_on,
            weeks=weeks_n, owner=owner, why=why,
        ))
    if not rows:
        raise SystemExit("Step 4 table has no filled rows (W1, W2, ... with a workstream name): fill the worksheet first")
    return rows


def check(rows: list[Workstream]) -> list[str]:
    """The checks a reviewer would run on the table before trusting the order."""
    problems: list[str] = []
    codes = {r.code for r in rows}
    for r in rows:
        if not 1 <= r.value <= 5 or not 1 <= r.risk <= 5:
            problems.append(f"{r.code}: value and risk must be 1 to 5 (got value={r.value}, risk={r.risk})")
        for d in r.depends_on:
            if d not in codes:
                problems.append(f"{r.code} depends on {d}, which is not in the table")
        if r.weeks < 1:
            problems.append(f"{r.code}: weeks must be at least 1")
        if len(r.why.split()) < 4:
            r.warnings.append("the 'why this score' cell is too short to defend in a readout")
        if r.owner.lower() in {"", "tbd", "?"}:
            r.warnings.append("no owner: a workstream nobody owns does not start")
    names = " ".join(r.name.lower() for r in rows)
    for must in ("eval", "integrat", "security", "enable"):
        if must not in names:
            problems.append(f"no workstream mentions '{must}': the decomposition is probably missing one")
    return problems


def sequence(rows: list[Workstream]) -> list[Workstream]:
    """Risk-first, value-second order that respects dependencies, then a start week with limited parallelism."""
    for r in rows:
        r.priority = RISK_WEIGHT * r.risk + VALUE_WEIGHT * r.value
    by_code = {r.code: r for r in rows}
    done: list[Workstream] = []
    remaining = list(rows)
    while remaining:
        ready = [r for r in remaining if all(d in {x.code for x in done} for d in r.depends_on)]
        if not ready:
            cycle = ", ".join(r.code for r in remaining)
            raise SystemExit(f"dependency cycle among {cycle}")
        ready.sort(key=lambda r: (-r.priority, -r.risk, r.code))
        nxt = ready[0]
        done.append(nxt)
        remaining.remove(nxt)
    # assign start weeks: no earlier than each dependency's start + 1 (overlap on purpose), and never more
    # than MAX_PARALLEL FDE-owned workstreams running in any one week (the customer's own workstreams,
    # such as the security review, do not use the FDE's hours)
    scheduled: list[Workstream] = []
    for rank, r in enumerate(done, start=1):
        r.rank = rank
        earliest = 1
        for d in r.depends_on:
            earliest = max(earliest, by_code[d].start_week + 1)
        week = earliest
        while not fits(r, week, scheduled):
            week += 1
        r.start_week = week
        r.end_week = week + r.weeks - 1
        scheduled.append(r)
    return done


def is_fde_owned(r: Workstream) -> bool:
    return "fde" in r.owner.lower()


def fits(r: Workstream, week: int, scheduled: list[Workstream]) -> bool:
    if not is_fde_owned(r):
        return True
    for w in range(week, week + r.weeks):
        running = sum(1 for a in scheduled if is_fde_owned(a) and a.start_week <= w <= a.end_week)
        if running >= MAX_PARALLEL:
            return False
    return True


def week_grid(rows: list[Workstream]) -> str:
    """A plain-text week grid (markdown table) that shows the overlap; paste it into the discovery document."""
    last = max(r.end_week for r in rows)
    head = "| # | Workstream | " + " | ".join(f"w{w}" for w in range(1, last + 1)) + " |"
    sep = "|---|---|" + "|".join("---" for _ in range(last)) + "|"
    body = []
    for r in rows:
        cells = " | ".join("##" if r.start_week <= w <= r.end_week else "" for w in range(1, last + 1))
        body.append(f"| {r.code} | {r.name} | {cells} |")
    return "\n".join([head, sep, *body])


def main(argv: list[str]) -> None:
    if len(argv) != 2:
        raise SystemExit("usage: python code/plan_from_worksheet.py worksheet/<name>.md")
    path = Path(argv[1])
    text = path.read_text(encoding="utf-8")
    rows = read_step4_table(text)
    problems = check(rows)
    print(f"== {path.name}: {len(rows)} workstreams read from the Step 4 table ==")
    if problems:
        print("problems (fix the worksheet before trusting the order):")
        for p in problems:
            print(f"  - {p}")
        raise SystemExit(1)
    ordered = sequence(rows)
    print()
    print(f"{'rank':>4s}  {'code':4s} {'workstream':46s} {'risk':>4s} {'value':>5s} {'prio':>5s} {'weeks':>5s} {'start':>5s} {'end':>4s}  owner")
    for r in ordered:
        print(f"{r.rank:4d}  {r.code:4s} {r.name[:46]:46s} {r.risk:4d} {r.value:5d} {r.priority:5.1f} {r.weeks:5d} {r.start_week:5d} {r.end_week:4d}  {r.owner}")
    print()
    print("why each one sits where it does:")
    for r in ordered:
        deps = ", ".join(r.depends_on) if r.depends_on else "nothing"
        print(f"  {r.rank}. {r.code} {r.name}: {r.why} (after {deps})")
        for w in r.warnings:
            print(f"       warning: {w}")
    print()
    print("weeks 1 to 3, the window in which the walking skeleton is built from a thin slice of every workstream:")
    for r in ordered:
        if r.start_week <= 3:
            print(f"  running: {r.code} {r.name} (weeks {r.start_week} to {r.end_week})")
    late_risky = [r for r in ordered if r.risk >= 4 and r.start_week > 2]
    for r in late_risky:
        print(f"  warning: {r.code} has risk {r.risk} but starts in week {r.start_week}; say why in the readout")
    print(f"how to read: priority = {RISK_WEIGHT:g} x risk + {VALUE_WEIGHT:g} x value; ties go to the riskier one; "
          f"at most {MAX_PARALLEL} FDE-owned workstreams run in any week")

    out_dir = Path("data")
    out_dir.mkdir(exist_ok=True)
    out_json = out_dir / f"{path.stem}-plan.json"
    out_json.write_text(json.dumps([asdict(r) for r in ordered], indent=2), encoding="utf-8")
    out_grid = out_dir / f"{path.stem}-plan.md"
    out_grid.write_text(week_grid(ordered) + "\n", encoding="utf-8")
    print(f"wrote {out_json.as_posix()} and {out_grid.as_posix()}")


if __name__ == "__main__":
    main(sys.argv)
