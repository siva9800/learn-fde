"""The trace store: one SQLite file, written only through the redacting boundary.

In the pilot this is a file on the machine in the Hyderabad building, inside Godavari's network, with the retention the
compliance head agrees (worksheet, section 5). In production the same records go to whatever backend Godavari runs
through an OpenTelemetry exporter; `export_jsonl` writes the shape such an exporter would carry. The store is not the
system of record for anything: the screen log (Day 18), the write journal (Day 16) and the audit log (Day 17) are.
It answers "what happened to this file, what did it cost, and is it getting worse".
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from .redact import RedactionReport, admit
from .spans import Span

_SCHEMA = """
CREATE TABLE IF NOT EXISTS spans (
    span_id TEXT PRIMARY KEY, trace_id TEXT NOT NULL, parent_id TEXT, name TEXT NOT NULL, kind TEXT NOT NULL,
    start TEXT NOT NULL, end TEXT NOT NULL, status TEXT NOT NULL, attrs TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS events (
    span_id TEXT NOT NULL, name TEXT NOT NULL, at TEXT NOT NULL, attrs TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS redaction (
    run TEXT NOT NULL, what TEXT NOT NULL, count INTEGER NOT NULL);
CREATE INDEX IF NOT EXISTS spans_trace ON spans (trace_id);
"""


def _iso(at: datetime) -> str:
    return at.isoformat(timespec="milliseconds")


class TraceStore:
    def __init__(self, path: Path | str = ":memory:", fresh: bool = True) -> None:
        if path != ":memory:" and fresh:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).unlink(missing_ok=True)          # a run rebuilds its store; nothing is appended to old runs
        self.conn = sqlite3.connect(str(path))
        self.conn.executescript(_SCHEMA)
        self.report = RedactionReport()

    def write(self, spans: list[Span], run: str) -> RedactionReport:
        """Every span passes the boundary or is not stored. Returns what was dropped, by key and reason."""
        report = RedactionReport()
        with self.conn:
            for s in spans:
                ok = admit(s.name, s.attrs, s.events, report)
                if ok is None:
                    continue
                attrs, events = ok
                self.conn.execute("INSERT INTO spans VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                  (s.span_id, s.trace_id, s.parent_id, s.name, s.kind, _iso(s.start), _iso(s.end),
                                   s.status, json.dumps(attrs, sort_keys=True, ensure_ascii=False)))
                for e in events:
                    self.conn.execute("INSERT INTO events VALUES (?, ?, ?, ?)",
                                      (s.span_id, e["name"], _iso(e["at"]), json.dumps(e["attrs"], sort_keys=True)))
            for what, n in sorted({**{f"dropped {k}": v for k, v in report.dropped.items()},
                                   **{f"quarantined {k}": v for k, v in report.quarantined.items()}}.items()):
                self.conn.execute("INSERT INTO redaction VALUES (?, ?, ?)", (run, what, n))
        self.report.dropped.update(report.dropped)
        self.report.quarantined.update(report.quarantined)
        return report

    # --- reading ----------------------------------------------------------------------------------------------
    def rows(self, where: str = "1=1", params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        cur = self.conn.execute(f"SELECT span_id, trace_id, parent_id, name, kind, start, end, status, attrs "
                                f"FROM spans WHERE {where} ORDER BY start, span_id", params)
        out = []
        for r in cur.fetchall():
            out.append({"span_id": r[0], "trace_id": r[1], "parent_id": r[2], "name": r[3], "kind": r[4],
                        "start": datetime.fromisoformat(r[5]), "end": datetime.fromisoformat(r[6]), "status": r[7],
                        "attrs": json.loads(r[8])})
        return out

    def by_name(self, name: str) -> list[dict[str, Any]]:
        return self.rows("name = ?", (name,))

    def trace(self, trace_id: str) -> list[dict[str, Any]]:
        return self.rows("trace_id = ?", (trace_id,))

    def events(self, name: str = "feedback") -> list[dict[str, Any]]:
        cur = self.conn.execute("SELECT e.span_id, s.trace_id, e.at, e.attrs FROM events e JOIN spans s "
                                "ON s.span_id = e.span_id WHERE e.name = ? ORDER BY e.at", (name,))
        return [{"span_id": a, "trace_id": b, "at": datetime.fromisoformat(c), "attrs": json.loads(d)}
                for a, b, c, d in cur.fetchall()]

    def count(self) -> tuple[int, int]:
        spans = self.conn.execute("SELECT COUNT(*) FROM spans").fetchone()[0]
        traces = self.conn.execute("SELECT COUNT(DISTINCT trace_id) FROM spans").fetchone()[0]
        return spans, traces

    def dump_text(self) -> str:
        """Everything stored, as text: what the leak tests search."""
        parts = []
        for table in ("spans", "events", "redaction"):
            for row in self.conn.execute(f"SELECT * FROM {table}"):
                parts.append(" | ".join(str(x) for x in row))
        return "\n".join(parts)

    def export_jsonl(self, path: Path, trace_ids: list[str]) -> int:
        """The exporter's shape: one span per line, with its events. Used for the sample trace in data/."""
        lines = []
        for tid in trace_ids:
            for s in self.trace(tid):
                ev = self.conn.execute("SELECT name, at, attrs FROM events WHERE span_id = ? ORDER BY at",
                                       (s["span_id"],)).fetchall()
                lines.append(json.dumps({**{k: v for k, v in s.items() if k not in ("start", "end")},
                                         "start": _iso(s["start"]), "end": _iso(s["end"]),
                                         "events": [{"name": n, "at": a, "attrs": json.loads(x)} for n, a, x in ev]},
                                        sort_keys=True, ensure_ascii=False))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        return len(lines)
