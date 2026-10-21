"""Read a stakeholder map as data and print the power-interest grid, who can stop the work,
who must change their behaviour, the checks a reviewer would run, and the conflicts between
what stakeholders want.

The thinking is in the worksheet (worksheet/godavari-stakeholder-map.md); this script turns the
same rows into the three views a readout needs and refuses to stay quiet about the gaps a map
usually has: a ghost with nobody speaking for them, a veto met too late, an operator whose day
changes with no engagement planned.

Python 3.14, standard library only. Run from the chapter folder:

    python -X utf8 code/stakeholder_grid.py
    python -X utf8 code/stakeholder_grid.py data/godavari-stakeholders.csv data/godavari-conflicts.csv

Every name and number is from the course's invented engagement.
"""

from __future__ import annotations

import csv
import sys
from dataclasses import dataclass
from pathlib import Path

HIGH = 4  # power or interest of 4 or 5 counts as high on the 1-to-5 scale
LATE_FOR_A_VETO = 2  # a stakeholder who can stop the work should be met by this week

QUADRANT_ADVICE = {
    ("high", "high"): "manage closely: in the readout, signs the plan, hears bad news first",
    ("high", "low"): "keep satisfied: meet early, ask for conditions in writing, never surprise",
    ("low", "high"): "keep informed and listening: shadow, interview, show the first slice",
    ("low", "low"): "monitor: one named contact, told when their part changes",
}


@dataclass(frozen=True)
class Stakeholder:
    id: str
    name: str
    category: str
    side: str
    location: str
    power: int
    interest: int
    stops_it_by: str
    must_change: str
    proxy: str
    first_contact_week: str
    their_version: str
    they_want: str
    number_they_would_believe: str
    engagement: str

    @property
    def power_band(self) -> str:
        return "high" if self.power >= HIGH else "low"

    @property
    def interest_band(self) -> str:
        return "high" if self.interest >= HIGH else "low"

    @property
    def can_stop(self) -> bool:
        return self.stops_it_by.strip().lower() not in {"", "none", "no"}

    @property
    def contact_week(self) -> int | None:
        text = self.first_contact_week.strip().lower()
        return int(text) if text.isdigit() else None


@dataclass(frozen=True)
class Conflict:
    a: str
    b: str
    a_wants: str
    b_wants: str
    where_it_collides: str
    how_it_is_handled: str
    decided_by: str
    decided_when: str


def read_stakeholders(path: Path) -> list[Stakeholder]:
    rows: list[Stakeholder] = []
    with path.open(encoding="utf-8", newline="") as handle:
        for raw in csv.DictReader(handle):
            try:
                power, interest = int(raw["power"]), int(raw["interest"])
            except (KeyError, ValueError) as exc:
                raise SystemExit(f"{path.name}: row {raw.get('id')!r} needs integer power and interest ({exc})")
            if not (1 <= power <= 5 and 1 <= interest <= 5):
                raise SystemExit(f"{path.name}: row {raw['id']!r}: power and interest must be 1 to 5")
            rows.append(Stakeholder(
                id=raw["id"].strip(), name=raw["name"].strip(), category=raw["category"].strip(),
                side=raw["side"].strip(), location=raw["location"].strip(), power=power, interest=interest,
                stops_it_by=raw["stops_it_by"].strip(), must_change=raw["must_change"].strip(),
                proxy=raw["proxy"].strip(), first_contact_week=raw["first_contact_week"].strip(),
                their_version=raw["their_version"].strip(), they_want=raw["they_want"].strip(),
                number_they_would_believe=raw["number_they_would_believe"].strip(),
                engagement=raw["engagement"].strip(),
            ))
    if not rows:
        raise SystemExit(f"{path.name}: no stakeholders; fill the map first")
    return rows


def read_conflicts(path: Path) -> list[Conflict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        return [Conflict(**{k: v.strip() for k, v in raw.items()}) for raw in csv.DictReader(handle)]


def short(name: str, width: int = 34) -> str:
    return name if len(name) <= width else name[: width - 3] + "..."


def label(name: str) -> str:
    """The part of a name before any bracket or comma: 'CISO', 'Srinivas', 'Branch managers'."""
    return name.split(" (")[0].split(",")[0].strip()


def print_grid(people: list[Stakeholder]) -> None:
    print("\n== Power against interest (customer side; high = 4 or 5) ==\n")
    cells: dict[tuple[str, str], list[Stakeholder]] = {k: [] for k in QUADRANT_ADVICE}
    for p in people:
        cells[(p.power_band, p.interest_band)].append(p)
    for pb in ("high", "low"):
        for ib in ("low", "high"):
            members = sorted(cells[(pb, ib)], key=lambda s: (-s.power, -s.interest, s.id))
            print(f"[power {pb:4}, interest {ib:4}]  {QUADRANT_ADVICE[(pb, ib)]}")
            for m in members:
                print(f"    {m.id}  {short(m.name, 52):52}  P{m.power} I{m.interest}  {m.category}")
            if not members:
                print("    (nobody)")
            print()


def print_stop_and_change(people: list[Stakeholder]) -> None:
    print("== Who can stop the work, and how ==\n")
    print(f"{'id':4} {'stakeholder':40} {'stops it by':14} {'met by week':12} proxy")
    for p in sorted(people, key=lambda s: (-s.power, s.id)):
        if p.can_stop:
            print(f"{p.id:4} {short(p.name, 40):40} {p.stops_it_by:14} {p.first_contact_week:12} {p.proxy or '-'}")
    print("\n== Whose Tuesday changes (must change their behaviour) ==\n")
    for p in sorted(people, key=lambda s: (-s.interest, s.id)):
        if p.must_change.lower() in {"yes", "partly"}:
            flag = "" if p.must_change.lower() == "yes" else "  (partly)"
            print(f"{p.id:4} {short(p.name, 40):40} wants: {short(p.they_want, 60)}{flag}")
    print()


def checks(people: list[Stakeholder]) -> list[str]:
    by_id = {p.id: p for p in people}
    problems: list[str] = []
    categories = " ".join(p.category.lower() for p in people)
    for needed in ("sponsor", "operator", "blocker", "ghost", "upstream", "system owner", "eval"):
        if needed not in categories:
            problems.append(f"no stakeholder in category '{needed}': the map is probably missing someone")
    for p in people:
        if p.category.lower().startswith("ghost") and not p.proxy:
            problems.append(f"{p.id} {p.name}: a ghost with nobody named to speak for them in the room")
        if p.proxy and p.proxy not in by_id:
            problems.append(f"{p.id} {p.name}: proxy {p.proxy!r} is not a row in the map")
        week = p.contact_week
        if p.can_stop and p.stops_it_by != "finding" and (week is None or week > LATE_FOR_A_VETO):
            problems.append(f"{p.id} {p.name}: can stop the work ({p.stops_it_by}) but first contact is week {p.first_contact_week}; meet them by week {LATE_FOR_A_VETO}")
        if p.must_change.lower() in {"yes", "partly"} and len(p.engagement.split()) < 6:
            problems.append(f"{p.id} {p.name}: their behaviour must change but the engagement plan is '{p.engagement}'")
        if p.power_band == "high" and p.interest_band == "low" and (week is None or week > 1) and p.stops_it_by != "finding":
            problems.append(f"{p.id} {p.name}: high power, low interest, not met in week 0 or 1: the quiet veto risk")
        if len(p.their_version.split()) < 4:
            problems.append(f"{p.id} {p.name}: 'their version of the problem' is not in their words yet")
    sponsors = [p for p in people if p.category.lower() == "sponsor"]
    operators = [p for p in people if p.category.lower().startswith("operator")]
    for s in sponsors:
        for o in operators:
            if s.their_version.lower() == o.their_version.lower():
                problems.append(f"{s.id} and {o.id}: the sponsor's version and an operator's version are word for word the same: you have only interviewed one of them")
    return problems


def print_conflicts(conflicts: list[Conflict], by_id: dict[str, Stakeholder]) -> None:
    print(f"== Conflicts between what stakeholders want ({len(conflicts)}) ==\n")
    if not conflicts:
        print("none listed: on an enterprise problem that means they have not been looked for\n")
        return
    for i, c in enumerate(conflicts, 1):
        a = by_id.get(c.a)
        b = by_id.get(c.b)
        a_name = label(a.name) if a else c.a
        b_name = label(b.name) if b else c.b
        print(f"{i}. {a_name}  against  {b_name}")
        print(f"     {a_name}: {c.a_wants}")
        print(f"     {b_name}: {c.b_wants}")
        print(f"     collides: {c.where_it_collides}")
        print(f"     handled:  {c.how_it_is_handled}")
        print(f"     decided by {c.decided_by} ({c.decided_when})\n")


def write_markdown(people: list[Stakeholder], conflicts: list[Conflict], out: Path) -> None:
    by_id = {p.id: p for p in people}
    lines = ["# Godavari stakeholder grid (generated by code/stakeholder_grid.py)", ""]
    lines += ["| Power | Interest | Advice | Stakeholders |", "|---|---|---|---|"]
    for pb in ("high", "low"):
        for ib in ("low", "high"):
            names = "; ".join(p.name for p in people if (p.power_band, p.interest_band) == (pb, ib))
            lines.append(f"| {pb} | {ib} | {QUADRANT_ADVICE[(pb, ib)]} | {names or '-'} |")
    lines += ["", "| Who can stop it | How | Met by week | Proxy in the room |", "|---|---|---|---|"]
    for p in sorted(people, key=lambda s: (-s.power, s.id)):
        if p.can_stop:
            proxy = by_id[p.proxy].name if p.proxy in by_id else "-"
            lines.append(f"| {p.name} | {p.stops_it_by} | {p.first_contact_week} | {proxy} |")
    lines += ["", "| Conflict | Collides where | Handled | Decided by |", "|---|---|---|---|"]
    for c in conflicts:
        a = by_id.get(c.a)
        b = by_id.get(c.b)
        lines.append(f"| {a.name if a else c.a} against {b.name if b else c.b} | {c.where_it_collides} | {c.how_it_is_handled} | {c.decided_by} ({c.decided_when}) |")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main(argv: list[str]) -> int:
    here = Path(__file__).resolve().parent.parent
    stakeholders_path = Path(argv[1]) if len(argv) > 1 else here / "data" / "godavari-stakeholders.csv"
    conflicts_path = Path(argv[2]) if len(argv) > 2 else here / "data" / "godavari-conflicts.csv"
    people = read_stakeholders(stakeholders_path)
    conflicts = read_conflicts(conflicts_path)
    customer = [p for p in people if p.side.lower() != "kaagaz"]
    own_side = [p for p in people if p.side.lower() == "kaagaz"]

    print(f"== {stakeholders_path.name}: {len(people)} stakeholders, {len(customer)} on the customer side ==")
    counts: dict[str, int] = {}
    for p in people:
        counts[p.category] = counts.get(p.category, 0) + 1
    for cat, n in sorted(counts.items()):
        print(f"  {n}  {cat}")
    print_grid(customer)
    if own_side:
        print("Our side (not on the customer's grid, still on the map):")
        for p in own_side:
            print(f"    {p.id}  {p.name}  P{p.power} I{p.interest}  wants: {short(p.they_want, 70)}")
        print()
    print_stop_and_change(customer)

    print("== Sponsor's version against operators' version ==\n")
    for p in people:
        if p.category.lower() == "sponsor" or p.category.lower().startswith("operator"):
            print(f"  {short(p.name, 44):44} \"{p.their_version}\"")
    print()

    problems = checks(people)
    print(f"== Checks ({len(problems)} warning(s)) ==\n")
    for item in problems or ["none: every role present, every ghost has a proxy, every veto met by week 2"]:
        print(f"  - {item}")
    print()
    print_conflicts(conflicts, {p.id: p for p in people})

    out = here / "data" / (stakeholders_path.stem.replace("-stakeholders", "") + "-stakeholder-grid.md")
    write_markdown(people, conflicts, out)
    print(f"wrote {out.relative_to(here).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
