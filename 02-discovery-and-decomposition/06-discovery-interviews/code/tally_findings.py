"""Tally coded discovery findings from interview transcripts and check a synthesis against them.

Standard library only. Run from the chapter folder:

    python -X utf8 code/tally_findings.py worksheet/transcripts worksheet/godavari-discovery-synthesis.md

Each transcript is a Markdown file with a "## Coded notes" section containing a table whose
first column is a CODE (UPPER_SNAKE_CASE), second column the verbatim evidence, third the kind
(architecture, constraint, scope, adoption, metric, evidence). The synthesis is a Markdown file
that cites codes in square brackets, like [BRANCH_ISOLATION].

The script:
  1. tallies every code across transcripts: how many interviews, which personas, which kinds;
  2. classifies each code as a requirement (3 or more independent interviews), a hypothesis
     (1 or 2), following the discovery playbooks' "three independent interviews" rule;
  3. checks the synthesis: every cited code must be supported by at least one transcript
     (anything else is an invented finding), and every requirement-level code should be cited
     (anything else is a finding the synthesis missed);
  4. writes data/<synthesis-name>-tally.csv and data/<synthesis-name>-tally.md.

Exit code is 1 if the synthesis cites a code that no transcript supports.
"""

from __future__ import annotations

import csv
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

CODE_RE = re.compile(r"^[A-Z][A-Z0-9_]{2,}$")
CITED_RE = re.compile(r"\[([A-Z][A-Z0-9_]{2,})\]")
PERSONA_RE = re.compile(r"Persona:\s*([^·\n]+)")
TITLE_RE = re.compile(r"^#\s+Transcript\s+(\d+)\s*·\s*(.+?)\s*$", re.MULTILINE)
REQUIREMENT_THRESHOLD = 3
KINDS = {"architecture", "constraint", "scope", "adoption", "metric", "evidence"}


@dataclass
class Mention:
    code: str
    transcript: str
    who: str
    persona: str
    evidence: str
    kind: str


@dataclass
class Tally:
    code: str
    mentions: list[Mention] = field(default_factory=list)

    @property
    def interviews(self) -> int:
        return len({m.transcript for m in self.mentions})

    @property
    def personas(self) -> list[str]:
        return sorted({m.persona for m in self.mentions})

    @property
    def kinds(self) -> list[str]:
        return sorted({m.kind for m in self.mentions})

    @property
    def status(self) -> str:
        return "requirement" if self.interviews >= REQUIREMENT_THRESHOLD else "hypothesis"


def split_row(line: str) -> list[str]:
    cells = line.strip().strip("|").split("|")
    return [c.strip() for c in cells]


def parse_transcript(path: Path) -> tuple[str, str, str, list[Mention], list[str]]:
    """Return (transcript id, who, persona, mentions, problems)."""
    text = path.read_text(encoding="utf-8")
    problems: list[str] = []
    title = TITLE_RE.search(text)
    who = title.group(2) if title else path.stem
    tid = f"T{int(title.group(1)):02d}" if title else path.stem
    persona_match = PERSONA_RE.search(text)
    persona = persona_match.group(1).strip() if persona_match else "unknown"
    persona = persona.split("(")[0].strip()  # "operator (upstream)" -> "operator"

    if "## Coded notes" not in text:
        problems.append(f"{path.name}: no '## Coded notes' section")
        return tid, who, persona, [], problems
    section = text.split("## Coded notes", 1)[1]
    mentions: list[Mention] = []
    seen_codes: set[str] = set()
    for line in section.splitlines():
        if not line.startswith("|"):
            continue
        cells = split_row(line)
        if len(cells) < 3 or cells[0] in ("Code", "") or set(cells[0]) <= {"-"}:
            continue
        code, evidence, kind = cells[0], cells[1], cells[2].lower()
        if not CODE_RE.match(code):
            problems.append(f"{path.name}: '{code}' is not UPPER_SNAKE_CASE")
            continue
        if kind not in KINDS:
            problems.append(f"{path.name}: {code} has kind '{kind}', expected one of {sorted(KINDS)}")
        if not evidence.strip('" '):
            problems.append(f"{path.name}: {code} has no verbatim evidence")
        if code in seen_codes:
            problems.append(f"{path.name}: {code} coded twice in one transcript (counts once)")
        seen_codes.add(code)
        mentions.append(Mention(code, tid, who, persona, evidence, kind))
    return tid, who, persona, mentions, problems


def tally(transcript_dir: Path) -> tuple[dict[str, Tally], list[tuple[str, str, str]], list[str]]:
    tallies: dict[str, Tally] = {}
    roster: list[tuple[str, str, str]] = []
    problems: list[str] = []
    for path in sorted(transcript_dir.glob("*.md")):
        tid, who, persona, mentions, probs = parse_transcript(path)
        roster.append((tid, who, persona))
        problems.extend(probs)
        for m in mentions:
            tallies.setdefault(m.code, Tally(m.code)).mentions.append(m)
    return tallies, roster, problems


def check_synthesis(synthesis: Path, tallies: dict[str, Tally]) -> tuple[list[str], list[str], set[str]]:
    text = synthesis.read_text(encoding="utf-8")
    cited = set(CITED_RE.findall(text))
    unsupported = sorted(c for c in cited if c not in tallies)
    missed = sorted(
        c for c, t in tallies.items() if t.status == "requirement" and c not in cited
    )
    return unsupported, missed, cited


def write_outputs(tallies: dict[str, Tally], data_dir: Path, cited: set[str], label: str) -> tuple[Path, Path]:
    data_dir.mkdir(exist_ok=True)
    stem = Path(label).stem
    csv_path, md_path = data_dir / f"{stem}-tally.csv", data_dir / f"{stem}-tally.md"
    rows = sorted(tallies.values(), key=lambda t: (-t.interviews, t.code))
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["code", "interviews", "status", "personas", "kinds", "cited_in_synthesis", "transcripts"])
        for t in rows:
            w.writerow([
                t.code, t.interviews, t.status, "; ".join(t.personas), "; ".join(t.kinds),
                "yes" if t.code in cited else "no",
                "; ".join(sorted({m.transcript for m in t.mentions})),
            ])
    lines = [
        f"# Findings tally (generated by code/tally_findings.py from {label})", "",
        f"> {len(tallies)} codes across the transcripts; a code is a requirement at {REQUIREMENT_THRESHOLD} or more interviews.", "",
        "| Code | Interviews | Status | Personas | Kinds | In synthesis | Transcripts |",
        "|---|---|---|---|---|---|---|",
    ]
    for t in rows:
        lines.append(
            f"| {t.code} | {t.interviews} | {t.status} | {', '.join(t.personas)} | {', '.join(t.kinds)} | "
            f"{'yes' if t.code in cited else 'no'} | {', '.join(sorted({m.transcript for m in t.mentions}))} |"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return csv_path, md_path


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__)
        return 2
    transcript_dir, synthesis = Path(argv[1]), Path(argv[2])
    if not transcript_dir.is_dir():
        print(f"not a directory: {transcript_dir}")
        return 2
    tallies, roster, problems = tally(transcript_dir)
    if not tallies:
        print("no coded notes found: code the transcripts first")
        return 2

    print(f"== {len(roster)} transcripts read from {transcript_dir} ==")
    for tid, who, persona in roster:
        n = sum(1 for t in tallies.values() if any(m.transcript == tid for m in t.mentions))
        print(f"  {tid}  {who[:50]:<50} {persona:<14} {n:>2} codes")
    if problems:
        print("\nproblems in the coded notes:")
        for p in problems:
            print(f"  - {p}")

    by_persona: dict[str, int] = defaultdict(int)
    for _, _, persona in roster:
        by_persona[persona] += 1
    print("\ninterviews by persona: " + ", ".join(f"{k} {v}" for k, v in sorted(by_persona.items())))

    rows = sorted(tallies.values(), key=lambda t: (-t.interviews, t.code))
    print(f"\n== frequency table: {len(rows)} codes, {sum(len(t.mentions) for t in rows)} coded mentions ==")
    print(f"{'code':<32} {'ivws':>4}  {'status':<11} {'kinds':<32} personas")
    for t in rows:
        print(f"{t.code:<32} {t.interviews:>4}  {t.status:<11} {', '.join(t.kinds):<32} {', '.join(t.personas)}")

    reqs = [t for t in rows if t.status == "requirement"]
    hyps = [t for t in rows if t.status == "hypothesis"]
    print(f"\nrequirements ({REQUIREMENT_THRESHOLD}+ interviews): {len(reqs)}; hypotheses (1 to 2): {len(hyps)}")
    arch = [t for t in reqs if "architecture" in t.kinds]
    print("architecture-changing requirements:")
    for t in arch:
        print(f"  - {t.code}: {t.interviews} interviews ({', '.join(t.personas)})")

    unsupported, missed, cited = check_synthesis(synthesis, tallies)
    print(f"\n== synthesis check: {synthesis.name} cites {len(cited)} codes ==")
    if unsupported:
        print("UNSUPPORTED: cited in the synthesis but said by no interviewee (invented findings):")
        for c in unsupported:
            print(f"  - {c}")
    else:
        print("every cited code is supported by at least one transcript")
    if missed:
        print("MISSED: requirement-level codes not cited in the synthesis:")
        for c in missed:
            print(f"  - {c} ({tallies[c].interviews} interviews)")
    else:
        print("every requirement-level code is cited")
    single = [t.code for t in hyps if t.interviews == 1 and t.code in cited]
    if single:
        print("single-source codes cited (keep them labelled as hypotheses): " + ", ".join(single))

    data_dir = Path(argv[0]).resolve().parent.parent / "data"
    csv_path, md_path = write_outputs(tallies, data_dir, cited, synthesis.name)
    print(f"\nwrote data/{csv_path.name} and data/{md_path.name}")
    return 1 if unsupported else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
