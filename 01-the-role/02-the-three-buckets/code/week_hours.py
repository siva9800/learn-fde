"""Count the hours per bucket in a week-as-calendar markdown file.

Reads every table row of the form
    | Day | Start | End | Hours | Bucket | With | What |
under each "## Week ..." heading in a calendar such as ../worksheet/godavari-weeks-1-2-calendar.md,
checks that Hours matches Start and End, sums hours per bucket per week and overall, and prints the
split beside the 60/30/10 that 2026 postings describe (section 04).

Python 3.14, standard library only. Run from the chapter folder:

    python -X utf8 code/week_hours.py worksheet/godavari-weeks-1-2-calendar.md
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

BUCKETS = {"C": "customer-facing", "D": "deployment code", "I": "internal"}
REFERENCE = {"C": 60, "D": 30, "I": 10}   # the split postings describe; a reference, not a rule
MAX_HOURS_PER_DAY = 9.0

WEEK_RE = re.compile(r"^##\s+(Week\s+\d+)", re.IGNORECASE)
ROW_RE = re.compile(r"^\|\s*(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s*\|")
TIME_RE = re.compile(r"^(\d{1,2}):(\d{2})$")


@dataclass
class Block:
    week: str
    day: str
    start: str
    end: str
    hours: float
    bucket: str
    with_whom: str
    what: str


def minutes(clock: str) -> int:
    match = TIME_RE.match(clock)
    if not match:
        raise ValueError(f"bad time {clock!r}; use HH:MM")
    return int(match.group(1)) * 60 + int(match.group(2))


def read_blocks(text: str) -> list[Block]:
    blocks: list[Block] = []
    week = ""
    for line in text.splitlines():
        heading = WEEK_RE.match(line)
        if heading:
            week = heading.group(1)
            continue
        if not ROW_RE.match(line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 7:
            raise SystemExit(f"row has {len(cells)} cells, expected 7: {line.strip()}")
        day, start, end, hours, bucket, with_whom, what = cells[:7]
        if bucket not in BUCKETS:
            raise SystemExit(f"{week} {day} {start}: bucket must be one of {sorted(BUCKETS)}, got {bucket!r}")
        blocks.append(Block(week, day, start, end, float(hours), bucket, with_whom, what))
    if not blocks:
        raise SystemExit("no calendar rows found; rows start with | Mon | ... under a '## Week' heading")
    return blocks


def check(blocks: list[Block]) -> list[str]:
    problems: list[str] = []
    per_day: dict[tuple[str, str], float] = defaultdict(float)
    for b in blocks:
        span = (minutes(b.end) - minutes(b.start)) / 60
        if abs(span - b.hours) > 0.01:
            problems.append(f"{b.week} {b.day} {b.start} to {b.end}: hours says {b.hours}, clock says {span:g}")
        per_day[(b.week, b.day)] += b.hours
    for (week, day), total in per_day.items():
        if total > MAX_HOURS_PER_DAY:
            problems.append(f"{week} {day}: {total:g} hours in one day; a calendar that needs this is not a plan")
    return problems


def split(blocks: list[Block]) -> dict[str, float]:
    totals: dict[str, float] = {k: 0.0 for k in BUCKETS}
    for b in blocks:
        totals[b.bucket] += b.hours
    return totals


def print_split(label: str, totals: dict[str, float]) -> None:
    grand = sum(totals.values())
    print(f"{label}: {grand:g} hours")
    for key, name in BUCKETS.items():
        share = 100 * totals[key] / grand if grand else 0
        print(f"  {name:<16} {totals[key]:5.2f} h  {share:5.1f}%   (reference {REFERENCE[key]}%)")


def main(path: Path) -> None:
    blocks = read_blocks(path.read_text(encoding="utf-8"))
    problems = check(blocks)
    if problems:
        print("problems (fix the calendar before trusting the split):")
        for p in problems:
            print("  -", p)
        raise SystemExit(1)
    weeks = sorted({b.week for b in blocks}, key=lambda w: int(w.split()[-1]))
    print(f"== {path.name}: {len(blocks)} blocks across {len(weeks)} week(s) ==")
    for week in weeks:
        print_split(week, split([b for b in blocks if b.week == week]))
    overall = split(blocks)
    print_split("Both weeks", overall)
    grand = sum(overall.values())
    c, d, i = (round(100 * overall[k] / grand) for k in ("C", "D", "I"))
    print(f"\nlands at about {c}/{d}/{i} against the 60/30/10 that postings describe")
    people = sorted({b.with_whom for b in blocks if b.bucket == "C" and b.with_whom != "alone"
                     and not b.with_whom.startswith("alone")})
    print(f"customer-facing hours were spent with {len(people)} different people or groups:")
    for p in people:
        print("  -", p)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(Path(sys.argv[1]))
