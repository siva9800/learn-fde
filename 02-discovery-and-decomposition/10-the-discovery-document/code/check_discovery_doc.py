"""Check a discovery document before it goes to the readout room.

Day 10 of learn-fde. Standard library only. Run from the chapter folder:

    python -X utf8 code/check_discovery_doc.py worksheet/godavari-discovery-document.md
    python -X utf8 code/check_discovery_doc.py worksheet/ai-draft-discovery-document.md

What it checks (errors fail the document; warnings are for a human to judge):

  E1  every required section is present, found by its heading
  E2  the problem statement is one sentence, in a blockquote
  E3  every decision (decided, needed, or in the log) has an owner and a date
  E4  every "will not do" or "not now" line has a reason of four words or more
  E5  every relative link resolves to a file on disk (the source artifacts)
  W1  page one names no technology (the COO reads page one)
  W2  every number on page one appears in at least one linked source file
  W3  page one fits on a page (about 450 words)
  W4  open questions have an owner and a due date
  W5  "will not do" lines name who agreed
  W6  the document links at least one artifact from each earlier Day of the Part
  W7  no placeholders (TBD, TODO, "to be confirmed" with no owner)

Exit code 0 when there are no errors, 1 otherwise, so it can run in CI or a
pre-commit hook on the engagement folder.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# The sections a discovery document must have, each found by a heading pattern.
# Order is the reading order taught in section 02.
REQUIRED_SECTIONS: list[tuple[str, str]] = [
    ("page one", r"page one|summary|at a glance"),
    ("problem statement", r"problem statement"),
    ("the people", r"people|stakeholder"),
    ("the workflow as it really is", r"workflow"),
    ("findings that change the architecture", r"finding"),
    ("decomposition and walking skeleton", r"decomposition|workstream"),
    ("the 90-day plan", r"90.day"),
    ("baseline and business case", r"baseline|business case"),
    ("data and security", r"security"),
    ("risks", r"risk"),
    ("will not do", r"will not do|not do|out of scope|non.goal"),
    ("open questions", r"open question"),
    ("decisions needed", r"decisions? needed|still to decide|decisions? to make"),
    ("decision log", r"decision log"),
    ("change log", r"change log|version history"),
    ("sign-off", r"sign.?off|signatures"),
]

# Earlier Days of Part 2 whose artifacts the document should link (W6).
SOURCE_DAYS: dict[str, str] = {
    "Day 4 (problem)": "04-picking-the-problem",
    "Day 5 (stakeholders)": "05-the-stakeholder-map",
    "Day 6 (discovery)": "06-discovery-interviews",
    "Day 7 (decomposition)": "07-decomposition",
    "Day 8 (90-day plan)": "08-scoping-the-first-90-days",
    "Day 9 (baseline and case)": "09-success-metrics-and-business-case",
}

TECH_WORDS = re.compile(
    r"\b(llm|llms|gpt[-\w.]*|claude|gemini|llama|rag|vector|embedding\w*|fine.tun\w*|"
    r"ocr|transformer\w*|agentic|langchain|pinecone|openai|bedrock)\b",
    re.IGNORECASE,
)
PLACEHOLDER = re.compile(r"\b(tbd|tbc|todo|xxx|lorem)\b|\[insert", re.IGNORECASE)
EMPTY_CELL = {"", "-", "?", "tbd", "tbc", "n/a", "na", "none", "todo", "later"}
LINK = re.compile(r"\[([^\]]*)\]\(([^)\s]+)\)")
NUMBER = re.compile(r"(?<![\w.])\d[\d,]*(?:\.\d+)?(?![\w])")
PAGE_ONE_WORD_LIMIT = 450
MIN_REASON_WORDS = 4


@dataclass
class Section:
    title: str
    level: int
    lines: list[str] = field(default_factory=list)

    @property
    def text(self) -> str:
        return "\n".join(self.lines)


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def error(self, code: str, msg: str) -> None:
        self.errors.append(f"{code} {msg}")

    def warn(self, code: str, msg: str) -> None:
        self.warnings.append(f"{code} {msg}")


def split_sections(text: str) -> list[Section]:
    """Split on ## and ### headings; a ### section also belongs to its ## parent."""
    sections: list[Section] = []
    stack: list[Section] = []
    for line in text.splitlines():
        m = re.match(r"^(#{2,3})\s+(.*)$", line)
        if m:
            level = len(m.group(1))
            sec = Section(m.group(2).strip(), level)
            sections.append(sec)
            stack = [s for s in stack if s.level < level] + [sec]
            continue
        for s in stack:
            s.lines.append(line)
    return sections


def find(sections: list[Section], pattern: str, level: int | None = None) -> list[Section]:
    rx = re.compile(pattern, re.IGNORECASE)
    return [s for s in sections if rx.search(s.title) and (level is None or s.level == level)]


def parse_tables(text: str) -> list[tuple[list[str], list[list[str]]]]:
    """Return (header, rows) for every Markdown table in the text."""
    tables: list[tuple[list[str], list[list[str]]]] = []
    block: list[str] = []
    for line in text.splitlines() + [""]:
        if line.strip().startswith("|"):
            block.append(line.strip())
            continue
        if len(block) >= 2 and re.match(r"^\|[\s:|-]+\|$", block[1]):
            cells = [[c.strip() for c in row.strip("|").split("|")] for row in block]
            tables.append((cells[0], cells[2:]))
        block = []
    return tables


def column(header: list[str], pattern: str) -> int | None:
    rx = re.compile(pattern, re.IGNORECASE)
    for i, h in enumerate(header):
        if rx.search(h):
            return i
    return None


def is_empty(cell: str) -> bool:
    return re.sub(r"[*_`]", "", cell).strip().lower() in EMPTY_CELL


def row_label(row: list[str]) -> str:
    """A short name for a table row: its ID and first words, or its first cell."""
    if not row:
        return "?"
    label = row[0]
    if len(row) > 1 and (not label or re.fullmatch(r"[A-Z]{0,2}\d+", label)):
        label = f"{label} {row[1]}".strip()
    return label if len(label) <= 40 else label[:37] + "..."


def check_sections(sections: list[Section], rep: Report) -> None:
    for name, pattern in REQUIRED_SECTIONS:
        if not find(sections, pattern):
            rep.error("E1", f"missing section: {name} (no heading matches /{pattern}/)")


def check_problem_statement(sections: list[Section], rep: Report) -> None:
    found = find(sections, r"problem statement")
    if not found:
        return
    quote = " ".join(
        ln.lstrip("> ").strip() for ln in found[0].lines if ln.startswith(">")
    ).strip()
    if not quote:
        rep.error("E2", "problem statement is not in a blockquote ('> ...'), so nobody can tell which sentence was signed")
        return
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", quote) if s.strip()]
    if len(sentences) != 1:
        rep.error("E2", f"problem statement is {len(sentences)} sentences; the signed statement is one")


def check_decisions(sections: list[Section], rep: Report) -> int:
    checked = 0
    decision_secs = [s for s in sections if re.search(r"decision|decided|still to decide", s.title, re.I)]
    seen: set[int] = set()
    for sec in decision_secs:
        if id(sec) in seen:
            continue
        # check each table once: use only the most specific section that holds it
        children = [c for c in decision_secs if c is not sec and c.level > sec.level and c.text in sec.text]
        text = sec.text
        for c in children:
            text = text.replace(c.text, "")
        for header, rows in parse_tables(text):
            owner = column(header, r"decided by|who decides|owner|decider|approver")
            date = column(header, r"^date$|^by$|^when$|due|date")
            if owner is None or date is None:
                missing = "owner" if owner is None else "date"
                rep.error("E3", f"'{sec.title}': decision table has no {missing} column")
                continue
            for row in rows:
                checked += 1
                cells = row + [""] * (len(header) - len(row))
                if is_empty(cells[owner]):
                    rep.error("E3", f"'{sec.title}': decision {row_label(row)} has no owner")
                d = cells[date]
                if is_empty(d) or not re.search(r"\d", d):
                    rep.error("E3", f"'{sec.title}': decision {row_label(row)} has no date ('{d}')")
    return checked


def check_will_not_do(sections: list[Section], rep: Report) -> int:
    checked = 0
    tops = [s for s in find(sections, r"will not do|not do|out of scope|non.goal") if s.level == 2] or \
        find(sections, r"will not do|not do|out of scope|non.goal")
    for sec in tops[:1]:
        tables = parse_tables(sec.text)
        if not tables:
            rep.error("E4", f"'{sec.title}': no table, so no line can carry its reason")
        for header, rows in tables:
            reason = column(header, r"because|reason|why")
            agreed = column(header, r"agreed|signed|who")
            for row in rows:
                checked += 1
                cells = row + [""] * (len(header) - len(row))
                if reason is None or is_empty(cells[reason]):
                    rep.error("E4", f"'{row_label(row)}' has no reason ('because')")
                elif len(cells[reason].split()) < MIN_REASON_WORDS:
                    rep.error("E4", f"'{row_label(row)}' reason is a label, not a reason: '{cells[reason]}'")
                if agreed is not None and is_empty(cells[agreed]):
                    rep.warn("W5", f"'{row_label(row)}' does not say who agreed")
            parked = re.search(r"not now|revisit", " ".join(header), re.I)
            if agreed is None and rows and not parked:
                rep.warn("W5", f"'{sec.title}': no 'agreed by' column")
    return checked


def check_open_questions(sections: list[Section], rep: Report) -> None:
    for sec in find(sections, r"open question"):
        for header, rows in parse_tables(sec.text):
            owner = column(header, r"owner|who")
            due = column(header, r"due|by|date|when")
            for row in rows:
                cells = row + [""] * (len(header) - len(row))
                if owner is None or is_empty(cells[owner]):
                    rep.warn("W4", f"open question {row_label(row)} has no owner")
                if due is None or is_empty(cells[due]):
                    rep.warn("W4", f"open question {row_label(row)} has no due date")


def check_links(doc: Path, text: str, rep: Report) -> list[Path]:
    resolved: list[Path] = []
    seen: set[str] = set()
    for _, target in LINK.findall(text):
        if re.match(r"^(https?:|mailto:|#)", target):
            continue
        path_part = target.split("#", 1)[0]
        if path_part in seen:
            continue
        seen.add(path_part)
        p = (doc.parent / path_part).resolve()
        if p.exists():
            resolved.append(p)
        else:
            rep.error("E5", f"broken link: {target}")
    return resolved


def check_page_one(sections: list[Section], sources: list[Path], rep: Report) -> None:
    found = find(sections, r"page one|summary|at a glance", level=2)
    if not found:
        return
    page = found[0].text
    words = len(LINK.sub(r"\1", page).split())
    if words > PAGE_ONE_WORD_LIMIT:
        rep.warn("W3", f"page one is {words} words; the COO reads about {PAGE_ONE_WORD_LIMIT}")
    for m in sorted({m.group(0) for m in TECH_WORDS.finditer(LINK.sub(r"\1", page))}, key=str.lower):
        rep.warn("W1", f"page one names technology: '{m}' (the COO signs outcomes, not components)")
    corpus = ""
    for p in sources:
        if p.is_file() and p.suffix in {".md", ".csv", ".json", ".txt"}:
            corpus += p.read_text(encoding="utf-8", errors="replace").replace(",", "") + "\n"
    plain = LINK.sub(r"\1", page)
    unsourced: list[str] = []
    for tok in sorted({n.replace(",", "") for n in NUMBER.findall(plain)}, key=lambda t: float(t)):
        if not re.search(r"(?<![\d.])" + re.escape(tok) + r"(?!\d)", corpus):
            unsourced.append(tok)
    if unsourced:
        rep.warn("W2", "page-one numbers found in no linked source: " + ", ".join(unsourced))


def check_continuity(sources: list[Path], rep: Report) -> None:
    joined = [str(p).replace("\\", "/") for p in sources]
    for day, folder in SOURCE_DAYS.items():
        if not any(f"/{folder}/" in j for j in joined):
            rep.warn("W6", f"no link to any {day} artifact ({folder}/)")


def check_placeholders(text: str, rep: Report) -> None:
    for n, line in enumerate(text.splitlines(), 1):
        if PLACEHOLDER.search(line):
            rep.warn("W7", f"line {n}: placeholder: {line.strip()[:70]}")


def check(doc: Path) -> Report:
    text = doc.read_text(encoding="utf-8")
    sections = split_sections(text)
    rep = Report()
    check_sections(sections, rep)
    check_problem_statement(sections, rep)
    n_dec = check_decisions(sections, rep)
    n_wnd = check_will_not_do(sections, rep)
    check_open_questions(sections, rep)
    sources = check_links(doc, text, rep)
    check_page_one(sections, sources, rep)
    check_continuity(sources, rep)
    check_placeholders(text, rep)
    found = sum(1 for _, pat in REQUIRED_SECTIONS if find(sections, pat))
    print(f"== {doc.name}: {found} of {len(REQUIRED_SECTIONS)} required sections, "
          f"{n_dec} decisions, {n_wnd} will-not-do lines, {len(sources)} linked files resolved ==")
    return rep


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Check a discovery document before the readout.")
    ap.add_argument("docs", nargs="+", type=Path, help="discovery document(s) in Markdown")
    args = ap.parse_args(argv)
    failed = 0
    for doc in args.docs:
        if not doc.is_file():
            print(f"no such file: {doc}")
            failed += 1
            continue
        rep = check(doc)
        for e in rep.errors:
            print(f"  ERROR   {e}")
        for w in rep.warnings:
            print(f"  warning {w}")
        verdict = "FAIL" if rep.errors else "PASS"
        print(f"{verdict}: {len(rep.errors)} errors, {len(rep.warnings)} warnings\n")
        failed += bool(rep.errors)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
