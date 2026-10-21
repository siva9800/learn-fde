"""Reading the Excel tracker without trusting it, migrating it into the review queue, and writing back.

The tracker is the real state of every file (finding A2), and it is forty hand-kept workbooks with no
schema. So the reader assumes nothing: it finds the header row by scoring, maps headers through the team
leads' aliases, parses every cell into (value, problem), reads colour as data, keeps hidden rows but says
so, skips total rows, and never fills a gap with a guess. A row it cannot read goes to a person.

The migration turns rows into review-queue items keyed by file number. Two workbooks claiming one file is
a conflict for the team lead, not a coin toss. Columns that must not travel (the customer's name, the
analysts' branch phone list) are listed in the mapping and left where they are.

write_back() adds one column the system owns ("Queue status (auto)") and touches nothing else, refuses to
write while Excel has the workbook open, and replaces the file atomically.
"""

from __future__ import annotations

import os
import re
import tomllib
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from openpyxl import load_workbook

TRACKER_MAPPING = Path(__file__).resolve().parent / "mapping" / "godavari_tracker_mapping.toml"
WRITE_BACK_HEADER = "Queue status (auto)"
_FILE_NO = re.compile(r"^GF-\d{5}$")
EXCEL_EPOCH = date(1899, 12, 30)


def load_tracker_mapping(path: Path = TRACKER_MAPPING) -> dict[str, Any]:
    with path.open("rb") as fh:
        return tomllib.load(fh)


def norm_header(text: object) -> str:
    return " ".join(str(text or "").strip().lower().split())


@dataclass
class Parsed:
    value: Any
    raw: Any
    problem: str = ""


def parse_file_no(raw: Any) -> Parsed:
    text = re.sub(r"\s+", "", str(raw or "")).upper().replace("GF_", "GF-")
    if text.startswith("GF") and not text.startswith("GF-"):
        text = "GF-" + text[2:]
    if _FILE_NO.match(text):
        note = "" if str(raw) == text else f"normalised {raw!r} to {text}"
        return Parsed(text, raw, note and f"info: {note}")
    return Parsed(None, raw, f"not a file number: {raw!r}")


def parse_date(raw: Any, year_hint: int | None = None, hint_source: str = "the sheet title") -> Parsed:
    if raw in (None, ""):
        return Parsed(None, raw)
    if isinstance(raw, datetime):
        return Parsed(raw.date(), raw)
    if isinstance(raw, date):
        return Parsed(raw, raw)
    if isinstance(raw, (int, float)) and 30000 < float(raw) < 60000:
        return Parsed(EXCEL_EPOCH + timedelta(days=int(raw)), raw, "info: Excel serial number")
    text = str(raw).strip()
    m = re.fullmatch(r"(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})", text)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            return Parsed(date(y, mo, d), raw)                  # day first: en-IN, from the mapping
        except ValueError:
            return Parsed(None, raw, f"not a day-first date: {raw!r}")
    m = re.fullmatch(r"(\d{1,2})[- ]([A-Za-z]{3})", text)
    if m:
        months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
        if m.group(2).lower() in months and year_hint:
            mo = months.index(m.group(2).lower()) + 1
            return Parsed(date(year_hint, mo, int(m.group(1))), raw, f"info: no year in {raw!r}; took {year_hint} from {hint_source}")
        return Parsed(None, raw, f"date without a year: {raw!r}")
    return Parsed(None, raw, f"not a date: {raw!r}")


def parse_flag(raw: Any, truthy: list[str], falsy: list[str]) -> Parsed:
    """A status cell is a tick, a word, or a date (done on that day). Anything else is a question."""
    if isinstance(raw, (datetime, date)):
        return Parsed(True, raw, "")
    text = norm_header(raw)
    if text in truthy:
        return Parsed(True, raw)
    if text in falsy:
        return Parsed(False, raw)
    as_date = parse_date(raw)
    if as_date.value is not None:
        return Parsed(True, raw)
    return Parsed(None, raw, f"unreadable status {raw!r}")


@dataclass
class TrackerRow:
    workbook: str
    row_number: int
    fields: dict[str, Any]
    fill: str | None
    hidden: bool
    problems: list[str] = field(default_factory=list)

    @property
    def ref(self) -> str:
        return f"{self.workbook}:{self.row_number}"


@dataclass
class SheetRead:
    workbook: str
    header_row: int | None
    columns: dict[str, int]
    unknown_headers: list[str]
    rows: list[TrackerRow]
    skipped: list[str]


def _tag(problem: str, column: str) -> str:
    """Keep the 'info:' marker first, so informational notes never block a row."""
    if problem.startswith("info: "):
        return f"info: {column}: {problem[6:]}"
    return f"{column}: {problem}"


def _title_year(ws: Any, header_row: int) -> int | None:
    """A year in a title above the header. Never from the data rows: a date in row 2 is not a title."""
    for row in ws.iter_rows(min_row=1, max_row=header_row - 1, values_only=True):
        for v in row:
            m = re.search(r"(20\d{2})", str(v or ""))
            if m:
                return int(m.group(1))
    return None


def read_workbook(path: Path, tmap: dict[str, Any] | None = None) -> SheetRead:
    tmap = tmap or load_tracker_mapping()
    aliases = {alias: canon for canon, names in tmap["columns"].items() for alias in names}
    wb = load_workbook(path, data_only=True)        # cached values; a formula Excel never saved reads as None
    ws = wb.worksheets[0]
    best_row, best_score = None, 0
    for r in range(1, min(ws.max_row, 10) + 1):
        score = sum(1 for c in ws[r] if norm_header(c.value).rstrip(".") in aliases or norm_header(c.value) in aliases)
        if score > best_score:
            best_row, best_score = r, score
    if best_row is None or best_score < 5:
        return SheetRead(path.name, None, {}, [], [], ["no header row found in the first ten rows"])
    columns: dict[str, int] = {}
    unknown: list[str] = []
    for c in ws[best_row]:
        h = norm_header(c.value)
        canon = aliases.get(h) or aliases.get(h.rstrip("."))
        if canon and canon not in columns:
            columns[canon] = c.column
        elif h and h not in ("s.no", "s no", "sl no"):
            unknown.append(str(c.value))
    year, year_source = _title_year(ws, best_row), "the sheet title"
    if year is None:
        m = re.search(r"[A-Za-z]{3}(\d{2})$", path.stem)
        year, year_source = (2000 + int(m.group(1)), "the workbook name") if m else (None, "")
    truthy, falsy = tmap["status"]["truthy"], tmap["status"]["falsy"]
    rows: list[TrackerRow] = []
    skipped: list[str] = []
    empty_run = 0
    for r in range(best_row + 1, ws.max_row + 1):
        values = {canon: ws.cell(r, col).value for canon, col in columns.items()}
        if all(v in (None, "") for v in values.values()):
            empty_run += 1
            if empty_run >= 3:
                break
            continue
        empty_run = 0
        first = " ".join(str(c.value) for c in ws[r][:3] if c.value is not None)
        if "total" in str(values.get("file_number") or "").lower() or "total" in first.lower():
            skipped.append(f"row {r}: a total row")
            continue
        problems: list[str] = []
        parsed: dict[str, Any] = {}
        fn = parse_file_no(values.get("file_number"))
        parsed["file_number"] = fn.value
        if fn.problem:
            problems.append(fn.problem)
        parsed["branch_code"] = tmap["branches"].get(norm_header(values.get("branch")))
        if values.get("branch") and parsed["branch_code"] is None:
            problems.append(f"unknown branch name {values.get('branch')!r}")
        parsed["assigned_to"] = str(values.get("assigned_to") or "").strip() or None
        rec = parse_date(values.get("received"), year, year_source)
        parsed["received_on"] = rec.value
        if rec.problem:
            problems.append(_tag(rec.problem, "received"))
        for col in tmap["status"]["columns"]:
            if col not in columns:
                continue
            if col == "received":
                parsed[col] = rec.value is not None
                continue
            if col == "waiting_on":
                parsed[col] = str(values.get(col) or "").strip() or None
                continue
            p = parse_flag(values.get(col), truthy, falsy)
            parsed[col] = p.value
            if p.problem:
                problems.append(_tag(p.problem, col))
        if "ageing" in columns and ws.cell(r, columns["ageing"]).value is None:
            raw_formula = load_formula(path, r, columns["ageing"])
            if raw_formula:
                problems.append(f"info: ageing is a formula with no cached value ({raw_formula}); recomputed")
        parsed["remarks"] = str(values.get("remarks") or "").strip() or None
        cell = ws.cell(r, columns["file_number"])
        fill = cell.fill.fgColor.rgb if cell.fill is not None and cell.fill.fill_type == "solid" else None
        hidden = bool(ws.row_dimensions[r].hidden)
        if hidden:
            problems.append("info: hidden row")
        rows.append(TrackerRow(path.name, r, parsed, fill if isinstance(fill, str) else None, hidden, problems))
    wb.close()
    return SheetRead(path.name, best_row, columns, unknown, rows, skipped)


_FORMULA_CACHE: dict[Path, Any] = {}


def load_formula(path: Path, row: int, col: int) -> str | None:
    if path not in _FORMULA_CACHE:
        _FORMULA_CACHE[path] = load_workbook(path).worksheets[0]
    value = _FORMULA_CACHE[path].cell(row, col).value
    return value if isinstance(value, str) and value.startswith("=") else None


# ---- migration into the review queue ----------------------------------------------------------------------
@dataclass
class QueueItem:
    file_number: str
    branch_code: str | None
    assigned_to: str | None
    state: str
    waiting_on: list[str]
    received_on: date | None
    sources: list[str]
    notes: list[str] = field(default_factory=list)


@dataclass
class Migration:
    items: dict[str, QueueItem]
    needs_a_person: list[str]
    conflicts: list[str]
    merged_duplicates: list[str]
    rows_read: int


def _state(row: TrackerRow, tmap: dict[str, Any]) -> tuple[str, list[str]]:
    f, notes = row.fields, []
    colour = tmap["colours"].get(row.fill or "")
    waiting_text = f.get("waiting_on")
    if colour == "ready_for_batch" and waiting_text:
        notes.append(f"colour says ready for batch but 'waiting on' still says {waiting_text!r}: ask the analyst")
    if f.get("memo"):
        return "memo_written", notes
    if f.get("batch"):
        return "in_credit_batch", notes
    if waiting_text or colour == "waiting_on_branch":
        return "waiting_on_branch", notes
    if colour == "query_with_senior":
        return "query_with_senior", notes
    for col, state in (("verified", "verified"), ("docs_checked", "docs_checked"), ("keyed", "keyed"),
                       ("received", "received")):
        if f.get(col):
            return state, notes
    return "unknown", notes + ["no status column is filled"]


def waiting_docs(text: str | None, tmap: dict[str, Any]) -> list[str]:
    if not text:
        return []
    low = text.lower()
    docs = sorted({doc for phrase, doc in tmap["waiting_on_phrases"].items() if phrase in low})
    return docs


def migrate(reads: list[SheetRead], tmap: dict[str, Any] | None = None) -> Migration:
    tmap = tmap or load_tracker_mapping()
    items: dict[str, QueueItem] = {}
    seen: dict[str, TrackerRow] = {}
    needs, conflicts, merged = [], [], []
    count = 0
    for read in reads:
        for row in read.rows:
            count += 1
            fn = row.fields.get("file_number")
            hard = [p for p in row.problems if not p.startswith("info:")]
            if fn is None or hard:
                needs.append(f"{row.ref}: " + "; ".join(hard or ["no file number"]))
                continue
            state, notes = _state(row, tmap)
            text = row.fields.get("waiting_on")
            if text and "wa" in re.findall(r"[a-z]+", text.lower()):
                notes.append("a page came by WhatsApp: not in the file of record; ask the branch to re-scan")
            item = QueueItem(fn, row.fields.get("branch_code"), row.fields.get("assigned_to"), state,
                             waiting_docs(text, tmap), row.fields.get("received_on"), [row.ref],
                             notes + [p[6:] for p in row.problems if p.startswith("info:")])
            if fn in items:
                prev, first = items[fn], seen[fn]
                same = (prev.assigned_to, prev.state, prev.waiting_on) == (item.assigned_to, item.state, item.waiting_on)
                if same and first.workbook == row.workbook:
                    prev.sources.append(row.ref)
                    merged.append(f"{fn}: {first.ref} and {row.ref} are the same row twice; merged")
                else:
                    conflicts.append(f"{fn}: {first.ref} says {prev.assigned_to}/{prev.state}, {row.ref} says "
                                     f"{item.assigned_to}/{item.state}; the team lead decides")
                    prev.notes.append("conflict: held until the team lead decides")
                    prev.state = "conflict"
                continue
            items[fn] = item
            seen[fn] = row
    return Migration(items, needs, conflicts, merged, count)


# ---- writing back ------------------------------------------------------------------------------------------
class WorkbookOpen(RuntimeError):
    pass


def lock_file(path: Path) -> Path:
    return path.with_name("~$" + path.name)


def write_back(path: Path, status_by_file: dict[str, str], tmap: dict[str, Any] | None = None) -> int:
    """Write the queue's status into the one column the system owns. Returns cells written."""
    if lock_file(path).exists():
        raise WorkbookOpen(f"{path.name} is open in Excel ({lock_file(path).name} exists); try after it is closed")
    read = read_workbook(path, tmap)
    if read.header_row is None:
        raise ValueError(f"{path.name}: no header row")
    wb = load_workbook(path)                         # formulas kept as formulas
    ws = wb.worksheets[0]
    col = next((c.column for c in ws[read.header_row] if c.value == WRITE_BACK_HEADER), None)
    if col is None:
        col = ws.max_column + 1
        ws.cell(read.header_row, col, WRITE_BACK_HEADER)
    written = 0
    for row in read.rows:
        fn = row.fields.get("file_number")
        if fn in status_by_file:
            ws.cell(row.row_number, col, status_by_file[fn])
            written += 1
    tmp = path.with_name(f".{path.stem}.writing.xlsx")
    wb.save(tmp)
    wb.close()
    os.replace(tmp, path)
    _FORMULA_CACHE.pop(path, None)
    return written
