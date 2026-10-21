"""Turn a filled skills rubric (markdown) into a gap plan.

Reads the three bucket tables from a rubric such as ../worksheet/sample-rubric-ravi.md (rows whose first
cell is E1.., A1.., C1..), checks the scores and the evidence, computes a mean per bucket, names the
weakest bucket, lists every gap (score 0 or 1) with the chapter that teaches it, and prints a plan in the
order the chapter recommends: weakest bucket first, lowest score first within a bucket. It also writes
../data/<rubric-name>-gap-plan.md so the plan can go into the engagement folder.

The rules it applies are section 08's: a score of 2 or 3 without evidence is a claim, not a skill, and is
downgraded to 1 with a warning; a bucket whose rows are all 3 is flagged for a second look, because
nobody has owned every row of a bucket in production and the rubric is for finding gaps, not for a CV.

Python 3.14, standard library only. Run from the chapter folder:

    python -X utf8 code/gap_plan.py worksheet/sample-rubric-ravi.md
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

BUCKET_NAMES = {"E": "core engineering", "A": "applied AI", "C": "customer-facing discovery"}

# Which chapter teaches each row. Paths follow curriculum/FOLDERS.md.
TEACHES = {
    "E1": "Days 12 and 20 (production code in the engagement) and the DevOps Masterclass",
    "E2": "Day 16 (integrating with what exists)",
    "E3": "Day 26 (shipping into infrastructure you do not own)",
    "E4": "Day 26 (CI/CD into the customer's account)",
    "E5": "Day 16 (SOAP, SQL, files, SFTP, the translation layer)",
    "E6": "Day 15 (chunking real PDFs) and Day 16",
    "A1": "Day 12 (LLM APIs for production)",
    "A2": "Day 13 (prompts as code)",
    "A3": "Day 14 (evals first)",
    "A4": "Day 15 (retrieval for enterprise documents)",
    "A5": "Day 17 (agents and workflows)",
    "A6": "Day 19 (observability for AI systems)",
    "C1": "Day 4 (picking the right problem)",
    "C2": "Day 5 (the stakeholder map)",
    "C3": "Day 6 (discovery interviews)",
    "C4": "Day 7 (decomposition) and Day 8 (scoping the first 90 days)",
    "C5": "Day 9 (success metrics and the business case)",
    "C6": "Day 10, Day 29, Day 30 and Day 32 (the document, the readout, bad news, pushback)",
    "C7": "Day 23 (the security review) and Day 24 (data residency)",
    "C8": "Day 28 (handoff and self-sufficiency)",
}

ROW_RE = re.compile(r"^\|\s*([EAC]\d+)\s*\|")
EVIDENCE_MIN_WORDS = 5


@dataclass
class Row:
    code: str
    skill: str
    score: int
    evidence: str
    warnings: list[str] = field(default_factory=list)

    @property
    def bucket(self) -> str:
        return self.code[0]


def read_rows(text: str) -> list[Row]:
    rows: list[Row] = []
    for line in text.splitlines():
        if not ROW_RE.match(line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4:
            raise SystemExit(f"row has {len(cells)} cells, expected 4: {line.strip()}")
        code, skill, score_text, evidence = cells[:4]
        if score_text == "":
            raise SystemExit(f"{code} has no score: fill every row before running the plan")
        try:
            score = int(score_text)
        except ValueError as exc:
            raise SystemExit(f"{code}: score must be a whole number 0 to 3, got {score_text!r}") from exc
        if not 0 <= score <= 3:
            raise SystemExit(f"{code}: score must be 0 to 3, got {score}")
        rows.append(Row(code, skill, score, evidence))
    if not rows:
        raise SystemExit("no rubric rows found; rows start with | E1 |, | A1 | or | C1 |")
    return rows


def check(rows: list[Row]) -> None:
    """Downgrade unsupported claims and flag suspicious buckets."""
    for row in rows:
        words = len(row.evidence.split())
        if row.score >= 2 and words < EVIDENCE_MIN_WORDS:
            row.warnings.append(
                f"scored {row.score} with {'no' if words == 0 else 'thin'} evidence ({row.evidence!r}); "
                f"counted as 1 until you can name the system and the result"
            )
            row.score = 1
    for bucket in BUCKET_NAMES:
        bucket_rows = [r for r in rows if r.bucket == bucket]
        if bucket_rows and all(r.score == 3 for r in bucket_rows):
            bucket_rows[0].warnings.append(
                f"every row of {BUCKET_NAMES[bucket]} is a 3: nobody has owned all of these in production; "
                f"re-score with the definitions at the top of the template"
            )


def bucket_means(rows: list[Row]) -> dict[str, float]:
    means: dict[str, float] = {}
    for bucket in BUCKET_NAMES:
        scores = [r.score for r in rows if r.bucket == bucket]
        means[bucket] = sum(scores) / len(scores) if scores else 0.0
    return means


def plan(rows: list[Row]) -> list[str]:
    means = bucket_means(rows)
    order = sorted(BUCKET_NAMES, key=lambda b: means[b])   # weakest bucket first
    lines: list[str] = []
    for bucket in order:
        gaps = sorted((r for r in rows if r.bucket == bucket and r.score <= 1), key=lambda r: (r.score, r.code))
        if not gaps:
            continue
        lines.append(f"{BUCKET_NAMES[bucket]} (mean {means[bucket]:.1f}): {len(gaps)} gap(s)")
        for r in gaps:
            lines.append(f"  {r.code} score {r.score}  {r.skill}")
            lines.append(f"      learn it in: {TEACHES.get(r.code, 'no chapter mapped; check the code')}")
    return lines


def strengths(rows: list[Row]) -> list[Row]:
    return [r for r in rows if r.score == 3 and not r.warnings]


def render(name: str, rows: list[Row]) -> str:
    means = bucket_means(rows)
    weakest = min(BUCKET_NAMES, key=lambda b: means[b])
    out: list[str] = [f"== {name}: {len(rows)} rows read =="]
    warnings = [(r.code, w) for r in rows for w in r.warnings]
    if warnings:
        out.append("warnings (read these first):")
        for code, w in warnings:
            out.append(f"  - {code}: {w}")
    out.append("")
    out.append("bucket                    mean  rows at 0/1  rows at 3")
    for bucket, label in BUCKET_NAMES.items():
        brs = [r for r in rows if r.bucket == bucket]
        low = sum(1 for r in brs if r.score <= 1)
        high = sum(1 for r in brs if r.score == 3)
        out.append(f"{label:<25} {means[bucket]:4.1f}  {low:^11}  {high:^9}")
    out.append("")
    out.append(f"weakest bucket: {BUCKET_NAMES[weakest]}; spend longest there "
               f"({'Part 2 and Part 5' if weakest == 'C' else 'Part 3' if weakest == 'A' else 'Part 3 Days 15 to 16 and Part 4'})")
    out.append("")
    out.append("the gap plan, in the order to work it (weakest bucket first, lowest score first):")
    out.extend(plan(rows))
    out.append("")
    good = strengths(rows)
    if good:
        out.append("strengths to lead with in interviews (a 3 with evidence is a story; Day 45 turns it into one):")
        for r in good:
            out.append(f"  {r.code}  {r.evidence}")
    else:
        out.append("no row scored 3 with evidence yet: pick the strongest 2 and write what would make it a 3")
    return "\n".join(out)


def main(path: Path) -> None:
    rows = read_rows(path.read_text(encoding="utf-8"))
    check(rows)
    report = render(path.name, rows)
    print(report)
    out_dir = path.parent.parent / "data"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"{path.stem}-gap-plan.md"
    out_path.write_text(f"# Gap plan from {path.name}\n\n```text\n{report}\n```\n", encoding="utf-8", newline="\n")
    print(f"\nwrote {out_path.as_posix()}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(Path(sys.argv[1]))
