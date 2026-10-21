"""Reading Godavari's reporting database: read-only, signed off per table and column, and bounded.

The reporting database is the core's nightly copy (refreshed at 05:00) that the monthly ops report is
built from. Here it is SQLite; at Godavari it is the on-prem reporting replica, reached with a read-only
account. Four locks, each of which would be enough on a good day:

  1. The connection is opened read-only (SQLite: mode=ro, and PRAGMA query_only).
  2. An authorizer allows reads only of the tables and columns the core-system owner signed off in
     reporting_signoff.json, and denies every other action. The customer's name and PAN are not in the
     sign-off, so a query that touches them fails, whoever wrote it, including a model.
  3. Every query is bounded: a row cap (fetch one more than the cap and refuse) and a step budget that
     aborts a runaway query (the SQLite stand-in for a statement timeout).
  4. Every query is logged with its purpose.

We never write to it, and we never write to the core's production database directly, whatever the
access allows. Writes go through the core's own API, where its validation, sequence and audit run.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

SIGNOFF = Path(__file__).resolve().parent / "mapping" / "reporting_signoff.json"
ROW_CAP = 5000
STEP_BUDGET = 2_000_000          # SQLite VM steps before a query is aborted


class QueryRefused(RuntimeError):
    pass


@dataclass
class QueryLog:
    entries: list[tuple[str, str, int]] = field(default_factory=list)   # (purpose, sql, rows)


class ReportingReader:
    def __init__(self, db_path: Path, signoff_path: Path = SIGNOFF, *, row_cap: int = ROW_CAP,
                 step_budget: int = STEP_BUDGET) -> None:
        signoff = json.loads(signoff_path.read_text(encoding="utf-8"))
        self.signoff = signoff
        self.allowed: dict[str, set[str]] = {t.lower(): {c.lower() for c in cols}
                                             for t, cols in signoff["tables"].items()}
        self.row_cap, self.step_budget = row_cap, step_budget
        self.log = QueryLog()
        self.denied: list[str] = []
        self.conn = sqlite3.connect(f"file:{Path(db_path).as_posix()}?mode=ro", uri=True)
        self.conn.execute("PRAGMA query_only = ON")
        self.conn.set_authorizer(self._authorize)

    def _authorize(self, action: int, arg1: str | None, arg2: str | None, db: str | None, trigger: str | None) -> int:
        if action == sqlite3.SQLITE_SELECT:
            return sqlite3.SQLITE_OK
        if action == sqlite3.SQLITE_FUNCTION:
            return sqlite3.SQLITE_OK
        if action == sqlite3.SQLITE_READ:
            table, column = (arg1 or "").lower(), (arg2 or "").lower()
            if table in self.allowed and (column in self.allowed[table] or column == ""):
                return sqlite3.SQLITE_OK
            self.denied.append(f"{arg1}.{arg2}")
            return sqlite3.SQLITE_DENY
        if action == sqlite3.SQLITE_PRAGMA and (arg1 or "").lower() in ("query_only", "table_info"):
            return sqlite3.SQLITE_OK
        self.denied.append(f"action {action} on {arg1}")
        return sqlite3.SQLITE_DENY

    def query(self, sql: str, params: tuple = (), *, purpose: str) -> list[dict[str, Any]]:
        if not purpose.strip():
            raise QueryRefused("every query states its purpose")
        steps = {"n": 0}
        self.denied = []

        def progress() -> int:
            steps["n"] += 1000
            return 1 if steps["n"] > self.step_budget else 0

        self.conn.set_progress_handler(progress, 1000)
        try:
            cur = self.conn.execute(sql, params)
            rows = cur.fetchmany(self.row_cap + 1)
        except sqlite3.DatabaseError as exc:
            raise QueryRefused(f"{exc} (denied: {', '.join(self.denied[-3:]) or 'none'})") from None
        finally:
            self.conn.set_progress_handler(None, 0)
        if len(rows) > self.row_cap:
            raise QueryRefused(f"more than {self.row_cap} rows: aggregate in SQL or page by key")
        names = [d[0] for d in cur.description]
        self.log.entries.append((purpose, " ".join(sql.split()), len(rows)))
        return [dict(zip(names, r)) for r in rows]

    def last_refresh(self) -> datetime:
        row = self.query("SELECT MAX(REFRESH_TS) AS ts FROM RPT_REFRESH_LOG", purpose="freshness of the copy")[0]
        return datetime.strptime(row["ts"], "%Y%m%d%H%M%S")

    def close(self) -> None:
        self.conn.close()
