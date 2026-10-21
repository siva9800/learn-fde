"""Chunking: structure first, fixed size as the fallback, and a naive baseline to measure against.

The structure-aware chunker sees only the extracted pages. It

1. learns the boilerplate (running headers, footers, page numbers) from repetition and drops it;
2. drops junk lines (a rotated stamp read by OCR) and re-joins words hyphenated across lines;
3. parses headings, numbered clauses and table rows, keeping the page of every line;
4. emits one chunk per clause, keeps a small table whole, splits a big one into row groups that each repeat
   the caption and header, and falls back to fixed-size windows with overlap only for text with no structure.

Every chunk carries its clause number and pages, so a citation can point at "clause 4.2, pages 2 to 3".
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field

from .corpus import Document
from .metadata import DocMeta, meta_for

MAX_CLAUSE_WORDS = 200        # a clause longer than this falls back to fixed windows
TABLE_MAX_WORDS = 160         # a table up to this size stays one chunk; bigger tables split by rows
WINDOW, OVERLAP = 80, 20      # the fixed-size fallback
NAIVE_WINDOW = 80             # the baseline: fixed windows, no overlap, no cleaning

_SECTION = re.compile(r"^(\d{1,2})\. (\S.*)$")
_CLAUSE = re.compile(r"^(\d{1,2}\.\d{1,2}(?:\.\d{1,2})?) (\S.*)$")
_TABLE_CAPTION = re.compile(r"^Table \d+: ")
_ID_LIKE = re.compile(r"^(?:GF-\d{5}|GFL|\d+(?:\.\d+)*|pan_[0-9a-f]{12})$")
_HEADER_LINES = ("Credit Operations Circular No.", "Product Rulebook No.", "Compliance Annex No.",
                 "Regulatory Digest No.", "Subject:", "Date:", "Supersedes:", "Status:")


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    doc_id: str
    clause: str               # "4.2", "header", "summary", "w3" (a fallback window), "" for naive chunks
    kind: str                 # header, clause, table, table_rows, summary, window, naive
    heading: str
    page_start: int
    page_end: int
    text: str                 # what the analyst sees and what a citation quotes
    index_text: str           # what is indexed: title and heading prepended (a contextual header)
    meta: DocMeta = field(compare=False)

    @property
    def key(self) -> str:
        """The citation key: document and clause. A naive window has no clause, so it is its own key."""
        return f"{self.doc_id}#{self.clause}" if self.clause else self.chunk_id


# --------------------------------------------------------------------------------------- cleaning
def _norm(line: str) -> str:
    return re.sub(r"\d+", "#", line.strip())


def learn_boilerplate(docs: list[Document], min_share: float = 0.10) -> frozenset[str]:
    """Edge lines (first two, last two) that recur on at least min_share of all pages, digits normalised."""
    edges: Counter[str] = Counter()
    pages = 0
    for d in docs:
        for p in d.pages:
            pages += 1
            for line in {*p[:2], *p[-2:]}:
                edges[_norm(line)] += 1
    return frozenset(k for k, n in edges.items() if n >= min_share * pages)


def _is_junk(line: str) -> bool:
    s = line.strip()
    if not s:
        return True
    if s.startswith("~") and s.endswith("~"):
        return True
    tokens = re.findall(r"[A-Za-z0-9]+", s)
    if not tokens:
        return False
    garbled = [t for t in tokens if re.search(r"[A-Za-z]", t) and re.search(r"\d", t) and not _ID_LIKE.match(t)]
    return len(garbled) / len(tokens) > 0.5


def clean_pages(doc: Document, boilerplate: frozenset[str]) -> tuple[list[tuple[int, str]], dict[str, int]]:
    """Return (page number, line) pairs with boilerplate and junk removed and hyphenation repaired, plus counts."""
    stats = Counter[str]()
    out: list[tuple[int, str]] = []
    running = f"{doc.doc_id} · "
    for pno, page in enumerate(doc.pages, start=1):
        for i, line in enumerate(page):
            edge = i < 2 or i >= len(page) - 2
            if edge and (_norm(line) in boilerplate or line.startswith(running)):
                stats["boilerplate"] += 1
                continue
            if _is_junk(line):
                stats["junk"] += 1
                continue
            out.append((pno, line.rstrip()))
    merged: list[tuple[int, str]] = []
    for pno, line in out:
        if merged and merged[-1][1].endswith("-") and line[:1].islower():
            ppage, prev = merged[-1]
            head, _, frag = prev.rpartition(" ")
            word, _, rest = line.partition(" ")
            merged[-1] = (ppage, f"{head} {frag[:-1]}{word}".strip())
            stats["dehyphenated"] += 1
            if rest:
                merged.append((pno, rest))
            continue
        merged.append((pno, line))
    return merged, dict(stats)


# ---------------------------------------------------------------------------------------- parsing
@dataclass
class _Block:
    kind: str
    number: str
    heading: str
    pages: list[int]
    lines: list[str]
    caption: str = ""
    header: str = ""
    rows: list[str] = field(default_factory=list)


def _parse(lines: list[tuple[int, str]]) -> list[_Block]:
    blocks: list[_Block] = []
    section_heading = ""
    section_no = ""
    head = _Block("header", "header", "Document header", [], [])
    cur: _Block | None = None
    for pno, line in lines:
        if line.startswith(_HEADER_LINES) and not blocks and cur is None:
            head.pages.append(pno)
            head.lines.append(line)
            continue
        if line.startswith("|"):
            if cur is None or cur.kind != "table":          # a table with no caption: give it one
                cur = _Block("table", section_no or "table", section_heading, [pno], [], caption="Table")
                blocks.append(cur)
            if not cur.header:
                cur.header = line
            elif line == cur.header:
                pass                                         # the header row repeated after a page break
            else:
                cur.rows.append(line)
            cur.pages.append(pno)
            continue
        m = _SECTION.match(line)
        if m and not _CLAUSE.match(line):
            section_no, section_heading = m.group(1), m.group(2)
            cur = None
            continue
        m = _CLAUSE.match(line)
        if m:
            number, rest = m.group(1), m.group(2)
            if _TABLE_CAPTION.match(rest):
                cur = _Block("table", number, section_heading, [pno], [], caption=rest)
            else:
                cur = _Block("clause", number, section_heading, [pno], [rest])
            blocks.append(cur)
            continue
        if cur is None:
            cur = _Block("text", section_no or "text", section_heading, [pno], [])
            blocks.append(cur)
        cur.lines.append(line)
        cur.pages.append(pno)
    if head.lines:
        blocks.insert(0, head)
    return blocks


def _windows(words: list[str], size: int, overlap: int) -> list[tuple[int, int]]:
    spans, i = [], 0
    step = max(1, size - overlap)
    while i < len(words):
        spans.append((i, min(len(words), i + size)))
        if i + size >= len(words):
            break
        i += step
    return spans


def _row_text(row: str) -> str:
    return " | ".join(c.strip() for c in row.strip().strip("|").split("|"))


# --------------------------------------------------------------------------------------- chunkers
def chunk_document(doc: Document, boilerplate: frozenset[str]) -> list[Chunk]:
    meta = meta_for(doc)
    lines, _ = clean_pages(doc, boilerplate)
    out: list[Chunk] = []

    def emit(clause: str, kind: str, heading: str, pages: list[int], text: str) -> None:
        n = sum(1 for c in out if c.clause == clause)
        context = f"{doc.title} · {heading}" if heading else doc.title
        out.append(Chunk(f"{doc.doc_id}#{clause}#{n}", doc.doc_id, clause, kind, heading, min(pages), max(pages),
                         text, f"{context} · {text}", meta))

    if doc.doc_type == "loan_decision":                       # short documents: never split what fits
        emit("summary", "summary", "", [p for p, _ in lines], "\n".join(t for _, t in lines))
        return out
    for b in _parse(lines):
        if b.kind == "table":
            header = _row_text(b.header)
            rows = [_row_text(r) for r in b.rows]
            whole = "\n".join([b.caption, header, *rows])
            if len(whole.split()) <= TABLE_MAX_WORDS:
                emit(b.number, "table", b.heading, b.pages, whole)
            else:
                group: list[str] = []
                for r in rows:
                    if group and len(" ".join([b.caption, header, *group, r]).split()) > TABLE_MAX_WORDS:
                        emit(b.number, "table_rows", b.heading, b.pages, "\n".join([b.caption, header, *group]))
                        group = []
                    group.append(r)
                if group:
                    emit(b.number, "table_rows", b.heading, b.pages, "\n".join([b.caption, header, *group]))
            continue
        text = " ".join(b.lines).strip()
        if not text:
            continue
        words = text.split()
        if b.kind in ("clause", "header") and len(words) <= MAX_CLAUSE_WORDS:
            emit(b.number, b.kind, b.heading, b.pages, text)
        else:                                                  # no structure, or too long: fixed windows
            for k, (a, z) in enumerate(_windows(words, WINDOW, OVERLAP)):
                emit(f"{b.number}.w{k}", "window", b.heading, b.pages, " ".join(words[a:z]))
    return out


def chunk_naive(doc: Document) -> list[Chunk]:
    """The baseline most first versions ship: raw extracted text, fixed windows, no overlap, no cleaning."""
    meta = meta_for(doc)
    words: list[tuple[int, str]] = [(pno, w) for pno, page in enumerate(doc.pages, start=1)
                                    for line in page for w in line.split()]
    out = []
    for k, i in enumerate(range(0, len(words), NAIVE_WINDOW)):
        part = words[i:i + NAIVE_WINDOW]
        text = " ".join(w for _, w in part)
        out.append(Chunk(f"{doc.doc_id}#n{k}", doc.doc_id, "", "naive", "", part[0][0], part[-1][0], text, text, meta))
    return out


def chunk_corpus(docs: list[Document], strategy: str = "structure") -> list[Chunk]:
    if strategy == "naive":
        return [c for d in docs for c in chunk_naive(d)]
    boilerplate = learn_boilerplate(docs)
    return [c for d in docs for c in chunk_document(d, boilerplate)]
