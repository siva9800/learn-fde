"""The write journal: Kaagaz's own record of every write it intended and what became of it.

The core has no idempotency key, so the memory of "have we done this?" has to live on our side as well as
in the core's EXT_REF field. The journal records intent before the call and the outcome after it. It holds
no customer data: the key, the file number, a hash of the payload and the payload's business fields only
(amounts, codes, flags). The workflow (Day 17) keeps the approved file and re-submits it; the journal
never needs the PAN to answer "did this write happen".
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path

PENDING, DEFERRED, UNKNOWN, CONFIRMED = "PENDING", "DEFERRED", "UNKNOWN", "CONFIRMED"
EXISTS_NOT_OURS, DUPLICATE_IN_CORE, FAILED = "EXISTS_NOT_OURS", "DUPLICATE_IN_CORE", "FAILED"
STATES = (PENDING, DEFERRED, UNKNOWN, CONFIRMED, EXISTS_NOT_OURS, DUPLICATE_IN_CORE, FAILED)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS writes (
    key TEXT PRIMARY KEY, file_no TEXT NOT NULL, branch_cd TEXT NOT NULL, state TEXT NOT NULL,
    appl_id TEXT, payload_sha256 TEXT, business_json TEXT, mapping_version TEXT,
    attempts INTEGER NOT NULL DEFAULT 0, first_at TEXT, last_at TEXT, unknown_since REAL, note TEXT);
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT, at TEXT NOT NULL, key TEXT NOT NULL, event TEXT NOT NULL, detail TEXT);
"""


@dataclass(frozen=True)
class WriteRow:
    key: str
    file_no: str
    branch_cd: str
    state: str
    appl_id: str | None
    payload_sha256: str | None
    business: dict[str, str]
    mapping_version: str | None
    attempts: int
    first_at: str | None
    last_at: str | None
    unknown_since: float | None
    note: str | None


class Journal:
    def __init__(self, path: Path | str = ":memory:") -> None:
        self.conn = sqlite3.connect(str(path), check_same_thread=False)
        self.conn.executescript(_SCHEMA)

    def _row(self, r: tuple) -> WriteRow:
        return WriteRow(r[0], r[1], r[2], r[3], r[4], r[5], json.loads(r[6] or "{}"), r[7], r[8], r[9], r[10], r[11], r[12])

    def get(self, key: str) -> WriteRow | None:
        r = self.conn.execute("SELECT * FROM writes WHERE key = ?", (key,)).fetchone()
        return self._row(r) if r else None

    def all(self) -> list[WriteRow]:
        return [self._row(r) for r in self.conn.execute("SELECT * FROM writes ORDER BY file_no")]

    def in_state(self, state: str) -> list[WriteRow]:
        return [self._row(r) for r in self.conn.execute("SELECT * FROM writes WHERE state = ? ORDER BY file_no", (state,))]

    def intend(self, key: str, file_no: str, branch_cd: str, payload_sha256: str, business: dict[str, str],
               mapping_version: str, at: str) -> None:
        """Record the intent before the call. Re-intending an existing key keeps its history."""
        with self.conn:
            self.conn.execute(
                "INSERT INTO writes (key, file_no, branch_cd, state, payload_sha256, business_json, mapping_version, "
                "first_at, last_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(key) DO UPDATE SET "
                "payload_sha256 = excluded.payload_sha256, business_json = excluded.business_json, "
                "mapping_version = excluded.mapping_version, last_at = excluded.last_at",
                (key, file_no, branch_cd, PENDING, payload_sha256, json.dumps(business, sort_keys=True),
                 mapping_version, at, at))
            self.conn.execute("INSERT INTO events (at, key, event, detail) VALUES (?, ?, 'intend', ?)",
                              (at, key, payload_sha256))

    def attempt(self, key: str, at: str) -> None:
        with self.conn:
            self.conn.execute("UPDATE writes SET attempts = attempts + 1, last_at = ? WHERE key = ?", (at, key))

    def set_state(self, key: str, state: str, at: str, *, appl_id: str | None = None, note: str = "",
                  unknown_since: float | None = None) -> None:
        if state not in STATES:
            raise ValueError(state)
        with self.conn:
            self.conn.execute("UPDATE writes SET state = ?, appl_id = COALESCE(?, appl_id), note = ?, last_at = ?, "
                              "unknown_since = ? WHERE key = ?", (state, appl_id, note, at, unknown_since, key))
            self.conn.execute("INSERT INTO events (at, key, event, detail) VALUES (?, ?, ?, ?)",
                              (at, key, state, note or appl_id or ""))

    def events(self, key: str | None = None) -> list[tuple[str, str, str, str]]:
        q = "SELECT at, key, event, detail FROM events" + (" WHERE key = ?" if key else "") + " ORDER BY id"
        return list(self.conn.execute(q, (key,) if key else ()))

    def dump_text(self) -> str:
        """Everything in the journal as text: what the 'no customer data in our store' test scans."""
        rows = list(self.conn.execute("SELECT * FROM writes")) + list(self.conn.execute("SELECT * FROM events"))
        return "\n".join("|".join(str(c) for c in r) for r in rows)
