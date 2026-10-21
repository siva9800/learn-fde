"""Score candidate problems from a CSV and print the ranking.

Day 4 of learn-fde. Standard library only. Run from the chapter folder:

    python code/score_candidates.py data/godavari-candidates.csv

The CSV holds one candidate problem per row with six scores (1 to 5), three
yes/no gates, and the evidence behind the pain score (volume per month and
hours per unit). The script applies the gates, computes a weighted score,
checks that the scores agree with the evidence, tests whether the winner
survives different weights, prints the ranking and writes it as a Markdown
table next to the CSV.

The script ranks. The problem selection memo (worksheet/) decides.
"""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass, field
from pathlib import Path
from statistics import median

# Criterion -> weight. "safety" is 6 minus blast_radius, so that a candidate
# whose failure is harmless scores high and one whose failure is an audit
# finding scores low. Weights are a convention to argue with, not a law.
WEIGHTS: dict[str, int] = {
    "frequency": 2,
    "pain": 3,
    "measurability": 2,
    "data": 2,
    "safety": 1,
    "sponsorship": 2,
}

# A candidate that fails any gate is listed under "not now", whatever its score.
GATES: dict[str, str] = {
    "has_baseline": "no baseline: nobody can say today how long it takes or how often it fails",
    "has_data_owner": "no data owner: nobody inside the customer can hand over the inputs",
    "operator_wants_it": "no operator who wants it: the people whose day changes have not asked for it",
}

# Planning placeholder for turning hours into rupees. Invented. Day 9 measures
# the loaded cost per analyst hour and replaces it.
DEFAULT_RUPEES_PER_HOUR = 300


@dataclass
class Candidate:
    code: str
    name: str
    raised_by: str
    volume_per_month: float
    hours_per_unit: float
    scores: dict[str, int]
    gates: dict[str, bool]
    note: str
    warnings: list[str] = field(default_factory=list)

    @property
    def hours_per_month(self) -> float:
        return self.volume_per_month * self.hours_per_unit

    def rupees_per_month(self, rate: float) -> float:
        return self.hours_per_month * rate

    def weighted(self, weights: dict[str, int]) -> float:
        total = sum(self.scores[c] * w for c, w in weights.items())
        return 100.0 * total / (5 * sum(weights.values()))

    @property
    def score(self) -> float:
        return self.weighted(WEIGHTS)

    @property
    def failed_gates(self) -> list[str]:
        return [g for g, ok in self.gates.items() if not ok]

    @property
    def passes(self) -> bool:
        return not self.failed_gates


def parse_score(row: dict[str, str], column: str, code: str) -> int:
    raw = row.get(column, "").strip()
    try:
        value = int(raw)
    except ValueError:
        sys.exit(f"{code}: '{column}' must be a whole number 1 to 5, got '{raw}'")
    if not 1 <= value <= 5:
        sys.exit(f"{code}: '{column}' must be 1 to 5, got {value}")
    return value


def parse_gate(row: dict[str, str], column: str, code: str) -> bool:
    raw = row.get(column, "").strip().lower()
    if raw not in ("yes", "no"):
        sys.exit(f"{code}: '{column}' must be yes or no, got '{raw}'")
    return raw == "yes"


def load(path: Path) -> list[Candidate]:
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        sys.exit(f"{path.name}: no candidate rows; fill the catalogue first")
    candidates: list[Candidate] = []
    for row in rows:
        code = row.get("code", "").strip()
        if not code or not row.get("candidate", "").strip():
            sys.exit("every row needs a code (C1, C2, ...) and a candidate name")
        scores = {
            "frequency": parse_score(row, "frequency", code),
            "pain": parse_score(row, "pain", code),
            "measurability": parse_score(row, "measurability", code),
            "data": parse_score(row, "data", code),
            "safety": 6 - parse_score(row, "blast_radius", code),
            "sponsorship": parse_score(row, "sponsorship", code),
        }
        gates = {g: parse_gate(row, g, code) for g in GATES}
        try:
            volume = float(row.get("volume_per_month", "0") or 0)
            hours = float(row.get("hours_per_unit", "0") or 0)
        except ValueError:
            sys.exit(f"{code}: volume_per_month and hours_per_unit must be numbers")
        candidates.append(
            Candidate(code, row["candidate"].strip(), row.get("raised_by", "").strip(),
                      volume, hours, scores, gates, row.get("note", "").strip())
        )
    return candidates


def check_consistency(candidates: list[Candidate]) -> None:
    """Scores are judgement; the evidence columns keep the judgement honest."""
    hours_median = median(c.hours_per_month for c in candidates)
    for c in candidates:
        if c.scores["pain"] >= 4 and c.hours_per_month < hours_median:
            c.warnings.append(
                f"pain {c.scores['pain']} but {c.hours_per_month:,.0f} h/month is below the "
                f"median {hours_median:,.0f}: the pain must come from something other than hours "
                f"(waiting days, errors, duplicated work); say what in the memo"
            )
        if c.scores["pain"] <= 2 and c.hours_per_month > hours_median:
            c.warnings.append(
                f"pain {c.scores['pain']} but {c.hours_per_month:,.0f} h/month is above the "
                f"median: either the volume is a guess or the pain score is too low"
            )
        if c.scores["measurability"] >= 4 and not c.gates["has_baseline"]:
            c.warnings.append("measurability 4 or more but no baseline: one of the two is wrong")
        if c.scores["data"] >= 4 and not c.gates["has_data_owner"]:
            c.warnings.append("data 4 or more but no data owner: who showed you the data?")
        if c.scores["safety"] <= 1 and c.passes:
            c.warnings.append("blast radius 5: if chosen, a human decision per unit is a condition, not an option")


def sensitivity(ranked: list[Candidate]) -> list[tuple[str, str]]:
    """Does the winner survive other reasonable weightings?"""
    if len(ranked) < 2:
        return []
    alternatives: dict[str, dict[str, int]] = {"equal weights": {c: 1 for c in WEIGHTS}}
    for criterion in WEIGHTS:
        alt = dict(WEIGHTS)
        alt[criterion] = 0
        alternatives[f"ignore {criterion}"] = alt
    for criterion in WEIGHTS:
        alt = dict(WEIGHTS)
        alt[criterion] = WEIGHTS[criterion] * 3
        alternatives[f"triple {criterion}"] = alt
    results = []
    for label, weights in alternatives.items():
        top = max(ranked, key=lambda c: c.weighted(weights))
        results.append((label, top.code))
    return results


def write_markdown(path: Path, source: Path, ranked: list[Candidate],
                   not_now: list[Candidate], rate: float) -> None:
    lines = [
        "# Godavari candidate problems, scored",
        "",
        f"> Generated by `code/score_candidates.py` from `data/{source.name}`. "
        f"Rupees use a planning rate of {rate:,.0f} per analyst hour (invented; Day 9 measures it).",
        "",
        "## Ranked (all three gates passed)",
        "",
        "| Rank | Code | Candidate | Score /100 | Freq | Pain | Meas | Data | Safety | Spons | Hours/month | Rupees/month |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for i, c in enumerate(ranked, 1):
        s = c.scores
        lines.append(
            f"| {i} | {c.code} | {c.name} | {c.score:.0f} | {s['frequency']} | {s['pain']} | "
            f"{s['measurability']} | {s['data']} | {s['safety']} | {s['sponsorship']} | "
            f"{c.hours_per_month:,.0f} | {c.rupees_per_month(rate) / 1e5:.1f} lakh |"
        )
    lines += ["", "## Not now (failed a gate)", "",
              "| Code | Candidate | Score /100 | Failed gate(s) |", "|---|---|---|---|"]
    for c in not_now:
        lines.append(f"| {c.code} | {c.name} | {c.score:.0f} | {'; '.join(c.failed_gates)} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Score candidate problems from a CSV.")
    parser.add_argument("csv", type=Path, help="the candidate catalogue, one row per problem")
    parser.add_argument("--rate", type=float, default=DEFAULT_RUPEES_PER_HOUR,
                        help="rupees per analyst hour for the pain column (planning placeholder)")
    args = parser.parse_args()

    candidates = load(args.csv)
    check_consistency(candidates)
    # Ties go to the candidate with more hours a month: evidence beats judgement.
    order = lambda c: (-c.score, -c.hours_per_month)  # noqa: E731
    passing = sorted((c for c in candidates if c.passes), key=order)
    not_now = sorted((c for c in candidates if not c.passes), key=order)

    print(f"== {args.csv.name}: {len(candidates)} candidates, {len(passing)} pass all three gates ==\n")
    header = (f"{'rank':>4}  {'code':<4} {'candidate':<42} {'score':>5}  "
              f"{'hours/mo':>8}  {'rupees/mo':>10}  raised by")
    print(header)
    print("-" * len(header))
    for i, c in enumerate(passing, 1):
        print(f"{i:>4}  {c.code:<4} {c.name[:42]:<42} {c.score:>5.0f}  {c.hours_per_month:>8,.0f}  "
              f"{c.rupees_per_month(args.rate) / 1e5:>5.1f} lakh  {c.raised_by}")

    print("\nnot now (a failed gate is a reason, not a score):")
    for c in not_now:
        print(f"      {c.code:<4} {c.name[:42]:<42} {c.score:>5.0f}  {c.hours_per_month:>8,.0f}  "
              f"{c.rupees_per_month(args.rate) / 1e5:>5.1f} lakh")
        for g in c.failed_gates:
            print(f"           - {GATES[g]}")

    warnings = [(c.code, w) for c in candidates for w in c.warnings]
    if warnings:
        print("\nconsistency warnings (the scores must agree with the evidence):")
        for code, w in warnings:
            print(f"  - {code}: {w}")

    if passing:
        print("\nsensitivity: who wins under other weightings?")
        changes = 0
        for label, top in sensitivity(passing):
            flag = "" if top == passing[0].code else "  <-- the winner changes"
            changes += bool(flag)
            print(f"  {label:<22} {top}{flag}")
        verdict = ("stable under every alternative" if changes == 0 else
                   f"changes under {changes} weighting(s): the pick is a judgement call, say so in the memo")
        print(f"  winner {passing[0].code} is {verdict}")

    print("\nhow to read: score = weighted sum of six 1-to-5 scores, scaled to 100; weights "
          + ", ".join(f"{k} {v}" for k, v in WEIGHTS.items())
          + f"; safety = 6 - blast radius; rupees at {args.rate:,.0f}/hour (planning placeholder)")
    out = args.csv.with_name(args.csv.stem + "-ranking.md")
    write_markdown(out, args.csv, passing, not_now, args.rate)
    print(f"wrote {out.as_posix()}")


if __name__ == "__main__":
    main()
