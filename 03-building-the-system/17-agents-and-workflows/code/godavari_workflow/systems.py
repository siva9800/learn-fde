"""Stand-ins for the Godavari systems the workflow touches, each persisted to disk because each outlives our
process: the branch directory, the mail relay, the credit-ops tracker and the core-system sandbox.

They behave like the real ones in the one way that matters here: none of them de-duplicates for us.
  BranchDirectory   the role mailbox of each branch manager. There is no customer in it, by design.
  MailRelay         Godavari's internal mail relay. send() always sends; a second call is a second email.
                    It can be searched by the X-Kaagaz-Key header (a message trace), which is what makes
                    lookup-before-send possible.
  Tracker           the "waiting on X since" column of Day 6's Excel tracker (finding A2), as a table.
                    An upsert by file number: setting it twice leaves one row.
  CoreSandbox       Day 11's FakeCoreSandbox, subclassed so its records survive a restart. Like the 2009
                    system, create_application always creates.

Crash injection lives here too: `Faults` raises `SimulatedCrash` (or, for the subprocess demo, kills the
process with os._exit) at a named point, so a test can stop the workflow between two lines of code.
"""

from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .day11 import BRANCH_CODES, FakeCoreSandbox

ROLE_DOMAIN = "branch.godavari.example"      # a reserved example domain: nothing here is a real address


@dataclass(frozen=True)
class BranchContact:
    branch: str
    branch_code: str
    mailbox: str            # the branch manager's role mailbox, not a person's
    role: str


class BranchDirectory:
    """Read-only. Built from Day 11's branch codes; in production, the branch master in the core (Day 16)."""

    def __init__(self) -> None:
        self.contacts = {b: BranchContact(b, c, f"bm.{c.lower()}@{ROLE_DOMAIN}", "branch manager")
                         for b, c in BRANCH_CODES.items()}

    def get(self, branch: str) -> BranchContact | None:
        return self.contacts.get(branch)

    def is_branch_mailbox(self, address: str) -> bool:
        return any(c.mailbox == address for c in self.contacts.values())


class _SqliteSystem:
    def __init__(self, path: Path | str, schema: str) -> None:
        self.conn = sqlite3.connect(str(path))
        self.conn.executescript(schema)

    def close(self) -> None:
        self.conn.close()


class MailRelay(_SqliteSystem):
    def __init__(self, path: Path | str = ":memory:") -> None:
        super().__init__(path, "CREATE TABLE IF NOT EXISTS sent (seq INTEGER PRIMARY KEY AUTOINCREMENT, "
                               "header_key TEXT, recipient TEXT, subject TEXT, body TEXT, sent_at TEXT);")

    def send(self, header_key: str, recipient: str, subject: str, body: str, at: str) -> int:
        with self.conn:
            cur = self.conn.execute("INSERT INTO sent (header_key, recipient, subject, body, sent_at) "
                                    "VALUES (?, ?, ?, ?, ?)", (header_key, recipient, subject, body, at))
        return int(cur.lastrowid or 0)

    def find_by_key(self, header_key: str) -> list[int]:
        return [r[0] for r in self.conn.execute("SELECT seq FROM sent WHERE header_key = ?", (header_key,))]

    def all(self) -> list[dict[str, Any]]:
        cur = self.conn.execute("SELECT seq, header_key, recipient, subject, body, sent_at FROM sent ORDER BY seq")
        return [dict(zip(["seq", "header_key", "recipient", "subject", "body", "sent_at"], r)) for r in cur]

    def count_for(self, file_id: str) -> int:
        return int(self.conn.execute("SELECT COUNT(*) FROM sent WHERE subject LIKE ?", (f"%{file_id}%",)).fetchone()[0])


class Tracker(_SqliteSystem):
    def __init__(self, path: Path | str = ":memory:") -> None:
        super().__init__(path, "CREATE TABLE IF NOT EXISTS rows (file_id TEXT PRIMARY KEY, status TEXT, "
                               "waiting_on TEXT, since TEXT, updated_by TEXT);")

    def upsert(self, file_id: str, status: str, waiting_on: str, since: str, updated_by: str) -> None:
        with self.conn:
            self.conn.execute("INSERT INTO rows VALUES (?, ?, ?, ?, ?) ON CONFLICT(file_id) DO UPDATE SET "
                              "status = excluded.status, waiting_on = excluded.waiting_on, since = excluded.since, "
                              "updated_by = excluded.updated_by", (file_id, status, waiting_on, since, updated_by))

    def row(self, file_id: str) -> dict[str, str] | None:
        r = self.conn.execute("SELECT file_id, status, waiting_on, since, updated_by FROM rows WHERE file_id = ?",
                              (file_id,)).fetchone()
        return dict(zip(["file_id", "status", "waiting_on", "since", "updated_by"], r)) if r else None


class CoreSandbox(FakeCoreSandbox):
    """Day 11's sandbox with its records on disk. Lookup and create keep Day 11's behaviour exactly."""

    def __init__(self, path: Path | str | None = None) -> None:
        super().__init__()
        self.path = Path(path) if path else None
        if self.path and self.path.exists():
            self.records = json.loads(self.path.read_text(encoding="utf-8"))

    def create_application(self, payload: dict[str, str]) -> str:
        record_id = super().create_application(payload)
        if self.path:
            self.path.write_text(json.dumps(self.records, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        return record_id

    def count_for(self, file_id: str) -> int:
        return sum(r["file_number"] == file_id for r in self.records)


class SimulatedCrash(BaseException):
    """BaseException, so no `except Exception` in the code under test can swallow it: like a power cut."""


@dataclass
class Faults:
    """Crash at a named point the Nth time it is reached (1 = the first time). Each point fires once."""

    points: dict[str, int] = field(default_factory=dict)
    hard_exit: bool = False                    # True: os._exit, for the subprocess demo; no cleanup runs
    hits: dict[str, int] = field(default_factory=dict)
    fired: list[str] = field(default_factory=list)

    def check(self, point: str) -> None:
        if point not in self.points:
            return
        self.hits[point] = self.hits.get(point, 0) + 1
        if self.hits[point] == self.points[point]:
            self.fired.append(point)
            del self.points[point]
            if self.hard_exit:
                os._exit(17)
            raise SimulatedCrash(point)
