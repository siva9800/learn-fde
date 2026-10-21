"""Durable state: one SQLite file holds the runs, the staging area, the approval queue, the outbox of
intended side effects and the audit log. Every state change and its audit event commit together.

Why one transaction matters: if the process dies between "the run is SENDING" and "the audit says SENDING",
a reviewer later finds a run in a state nobody recorded entering. Committing both in one transaction makes
that impossible. The audit table is append-only and hash-chained, so an edited or deleted row is detectable
by anyone holding the last hash (section 07).
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .states import Actor, State, check_transition

_SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    file_id TEXT PRIMARY KEY, branch TEXT NOT NULL, product TEXT NOT NULL, state TEXT NOT NULL,
    cycle INTEGER NOT NULL DEFAULT 0, bundle_version INTEGER NOT NULL DEFAULT 0, data_json TEXT NOT NULL,
    updated_at TEXT NOT NULL, version INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS bundles (
    file_id TEXT NOT NULL, version INTEGER NOT NULL, sha256 TEXT NOT NULL, row_json TEXT NOT NULL,
    arrived_at TEXT NOT NULL, PRIMARY KEY (file_id, version));
CREATE TABLE IF NOT EXISTS approvals (
    id TEXT PRIMARY KEY, file_id TEXT NOT NULL, cycle INTEGER NOT NULL, proposal_hash TEXT NOT NULL,
    draft_json TEXT NOT NULL, status TEXT NOT NULL, assigned_to TEXT NOT NULL, level INTEGER NOT NULL,
    created_at TEXT NOT NULL, due_at TEXT NOT NULL, decided_by TEXT, decided_at TEXT, decision_note TEXT,
    final_hash TEXT, final_json TEXT);
CREATE TABLE IF NOT EXISTS outbox (
    key TEXT PRIMARY KEY, file_id TEXT NOT NULL, kind TEXT NOT NULL, state TEXT NOT NULL,
    detail_json TEXT NOT NULL, intended_at TEXT NOT NULL, done_at TEXT);
CREATE TABLE IF NOT EXISTS events (
    seq INTEGER PRIMARY KEY AUTOINCREMENT, at TEXT NOT NULL, file_id TEXT NOT NULL, actor TEXT NOT NULL,
    kind TEXT NOT NULL, detail_json TEXT NOT NULL, prev_hash TEXT NOT NULL, hash TEXT NOT NULL);
"""
GENESIS = "0" * 64


@dataclass(frozen=True)
class Run:
    file_id: str
    branch: str
    product: str
    state: State
    cycle: int
    bundle_version: int
    data: dict[str, Any]
    updated_at: str
    version: int


class StaleRun(RuntimeError):
    """Someone else moved this run since it was read (optimistic concurrency)."""


def dumps(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str)


def event_hash(prev: str, at: str, file_id: str, actor: str, kind: str, detail_json: str) -> str:
    return hashlib.sha256("|".join([prev, at, file_id, actor, kind, detail_json]).encode("utf-8")).hexdigest()


class Store:
    def __init__(self, path: Path | str = ":memory:") -> None:
        self.path = str(path)
        self.conn = sqlite3.connect(self.path, isolation_level=None)   # explicit BEGIN and COMMIT below
        self.conn.execute("PRAGMA journal_mode=MEMORY" if self.path == ":memory:" else "PRAGMA journal_mode=DELETE")
        self.conn.execute("PRAGMA synchronous=FULL")
        self.conn.executescript(_SCHEMA)

    def close(self) -> None:
        self.conn.close()

    # ---- one transaction around every write -------------------------------------------------------
    def _tx(self, fn: Any) -> Any:
        self.conn.execute("BEGIN IMMEDIATE")
        try:
            out = fn()
            self.conn.execute("COMMIT")
            return out
        except BaseException:
            self.conn.execute("ROLLBACK")
            raise

    def _append_event(self, at: str, file_id: str, actor: str, kind: str, detail: dict[str, Any]) -> None:
        row = self.conn.execute("SELECT hash FROM events ORDER BY seq DESC LIMIT 1").fetchone()
        prev = row[0] if row else GENESIS
        dj = dumps(detail)
        self.conn.execute("INSERT INTO events (at, file_id, actor, kind, detail_json, prev_hash, hash) "
                          "VALUES (?, ?, ?, ?, ?, ?, ?)",
                          (at, file_id, str(actor), kind, dj, prev, event_hash(prev, at, file_id, str(actor), kind, dj)))

    def audit(self, at: str, file_id: str, actor: str, kind: str, **detail: Any) -> None:
        """An event with no state change: a tool call, a refusal, an escalation, a recovery."""
        self._tx(lambda: self._append_event(at, file_id, actor, kind, detail))

    # ---- runs --------------------------------------------------------------------------------------
    def create_run(self, file_id: str, branch: str, product: str, at: str, data: dict[str, Any]) -> None:
        def go() -> None:
            self.conn.execute("INSERT INTO runs (file_id, branch, product, state, data_json, updated_at) "
                              "VALUES (?, ?, ?, ?, ?, ?)", (file_id, branch, product, str(State.RECEIVED), dumps(data), at))
            self._append_event(at, file_id, Actor.SYSTEM, "run_created",
                               {"state": State.RECEIVED, "branch": branch, "product": product})
        self._tx(go)

    def get(self, file_id: str) -> Run | None:
        r = self.conn.execute("SELECT file_id, branch, product, state, cycle, bundle_version, data_json, updated_at, "
                              "version FROM runs WHERE file_id = ?", (file_id,)).fetchone()
        if r is None:
            return None
        return Run(r[0], r[1], r[2], State(r[3]), r[4], r[5], json.loads(r[6]), r[7], r[8])

    def runs(self, state: State | None = None) -> list[Run]:
        ids = [r[0] for r in self.conn.execute(
            "SELECT file_id FROM runs" + (" WHERE state = ?" if state else "") + " ORDER BY file_id",
            (str(state),) if state else ())]
        return [run for i in ids if (run := self.get(i)) is not None]

    def transition(self, run: Run, event: str, actor: Actor, at: str, *, data: dict[str, Any] | None = None,
                   cycle: int | None = None, bundle_version: int | None = None,
                   outbox: tuple[str, str, dict[str, Any]] | None = None,
                   approval: dict[str, Any] | None = None,
                   approval_update: tuple[str, dict[str, Any], dict[str, Any]] | None = None, **detail: Any) -> Run:
        """Move one run along one allowed transition, update its data, optionally record an intended side
        effect in the outbox, and append the audit event: all in one transaction, or none of it."""
        t = check_transition(run.state, event, actor)
        new_data = {**run.data, **(data or {})}

        def go() -> None:
            cur = self.conn.execute(
                "UPDATE runs SET state = ?, data_json = ?, updated_at = ?, version = version + 1, "
                "cycle = COALESCE(?, cycle), bundle_version = COALESCE(?, bundle_version) "
                "WHERE file_id = ? AND version = ?",
                (str(t.target), dumps(new_data), at, cycle, bundle_version, run.file_id, run.version))
            if cur.rowcount != 1:
                raise StaleRun(f"{run.file_id} changed since it was read (version {run.version})")
            if outbox is not None:
                key, kind, od = outbox
                self.conn.execute("INSERT OR IGNORE INTO outbox (key, file_id, kind, state, detail_json, intended_at) "
                                  "VALUES (?, ?, ?, 'INTENDED', ?, ?)", (key, run.file_id, kind, dumps(od), at))
            if approval is not None:
                self.conn.execute(
                    "INSERT INTO approvals (id, file_id, cycle, proposal_hash, draft_json, status, assigned_to, "
                    "level, created_at, due_at) VALUES (:id, :file_id, :cycle, :proposal_hash, :draft_json, "
                    "'PENDING', :assigned_to, 0, :created_at, :due_at)", approval)
                self._append_event(at, run.file_id, Actor.SYSTEM, "approval_requested",
                                   {"approval_id": approval["id"], "proposal_hash": approval["proposal_hash"],
                                    "assigned_to": approval["assigned_to"], "due_at": approval["due_at"]})
            if approval_update is not None:
                approval_id, fields, event_detail = approval_update
                sets = ", ".join(f"{k} = :{k}" for k in fields)
                cur = self.conn.execute(f"UPDATE approvals SET {sets} WHERE id = :id AND status = 'PENDING'",
                                        {**fields, "id": approval_id})
                if cur.rowcount != 1:
                    raise StaleRun(f"approval {approval_id} is no longer pending")
                self._append_event(at, run.file_id, actor, "approval_decided", {"approval_id": approval_id, **event_detail})
            self._append_event(at, run.file_id, actor, "transition",
                               {"event": event, "from": run.state, "to": t.target, **detail})
        self._tx(go)
        fresh = self.get(run.file_id)
        assert fresh is not None
        return fresh

    # ---- staging: every bundle version that arrived, by content hash -------------------------------
    def put_bundle(self, file_id: str, sha256: str, row: dict[str, Any], at: str) -> int | None:
        """The new version number, or None if these exact bytes were already staged (a duplicate upload)."""
        if self.conn.execute("SELECT 1 FROM bundles WHERE file_id = ? AND sha256 = ?", (file_id, sha256)).fetchone():
            return None
        version = self.latest_bundle_version(file_id) + 1
        self.conn.execute("INSERT INTO bundles VALUES (?, ?, ?, ?, ?)", (file_id, version, sha256, dumps(row), at))
        return version

    def bundle(self, file_id: str, version: int) -> tuple[str, dict[str, Any]]:
        r = self.conn.execute("SELECT sha256, row_json FROM bundles WHERE file_id = ? AND version = ?",
                              (file_id, version)).fetchone()
        if r is None:
            raise KeyError(f"{file_id} has no bundle version {version}")
        return r[0], json.loads(r[1])

    def latest_bundle_version(self, file_id: str) -> int:
        r = self.conn.execute("SELECT MAX(version) FROM bundles WHERE file_id = ?", (file_id,)).fetchone()
        return int(r[0]) if r and r[0] is not None else -1

    # ---- the approval queue ------------------------------------------------------------------------
    def add_approval(self, row: dict[str, Any], at: str) -> None:
        def go() -> None:
            self.conn.execute(
                "INSERT INTO approvals (id, file_id, cycle, proposal_hash, draft_json, status, assigned_to, level, "
                "created_at, due_at) VALUES (:id, :file_id, :cycle, :proposal_hash, :draft_json, 'PENDING', "
                ":assigned_to, 0, :created_at, :due_at)", row)
            self._append_event(at, row["file_id"], Actor.SYSTEM, "approval_requested",
                               {"approval_id": row["id"], "proposal_hash": row["proposal_hash"],
                                "assigned_to": row["assigned_to"], "due_at": row["due_at"]})
        self._tx(go)

    def approval(self, approval_id: str) -> dict[str, Any] | None:
        cur = self.conn.execute("SELECT * FROM approvals WHERE id = ?", (approval_id,))
        r = cur.fetchone()
        return dict(zip([c[0] for c in cur.description], r)) if r else None

    def approvals(self, status: str | None = None) -> list[dict[str, Any]]:
        cur = self.conn.execute("SELECT * FROM approvals" + (" WHERE status = ?" if status else "") +
                                " ORDER BY created_at, id", (status,) if status else ())
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]

    def update_approval(self, approval_id: str, at: str, file_id: str, actor: str, kind: str,
                        fields: dict[str, Any], **detail: Any) -> None:
        sets = ", ".join(f"{k} = :{k}" for k in fields)

        def go() -> None:
            self.conn.execute(f"UPDATE approvals SET {sets} WHERE id = :id", {**fields, "id": approval_id})
            self._append_event(at, file_id, actor, kind, {"approval_id": approval_id, **detail})
        self._tx(go)

    # ---- the outbox: side effects intended, and whether they are known to be done ------------------
    def outbox_row(self, key: str) -> dict[str, Any] | None:
        cur = self.conn.execute("SELECT * FROM outbox WHERE key = ?", (key,))
        r = cur.fetchone()
        return dict(zip([c[0] for c in cur.description], r)) if r else None

    def outbox_done(self, key: str, at: str, file_id: str, kind: str, **detail: Any) -> None:
        def go() -> None:
            self.conn.execute("UPDATE outbox SET state = 'DONE', done_at = ? WHERE key = ?", (at, key))
            self._append_event(at, file_id, Actor.SYSTEM, kind, {"key": key, **detail})
        self._tx(go)

    # ---- the audit log -----------------------------------------------------------------------------
    def events(self, file_id: str | None = None) -> list[dict[str, Any]]:
        q = "SELECT seq, at, file_id, actor, kind, detail_json, prev_hash, hash FROM events"
        rows = self.conn.execute(q + (" WHERE file_id = ?" if file_id else "") + " ORDER BY seq",
                                 (file_id,) if file_id else ()).fetchall()
        return [{"seq": r[0], "at": r[1], "file_id": r[2], "actor": r[3], "kind": r[4],
                 "detail": json.loads(r[5]), "prev_hash": r[6], "hash": r[7]} for r in rows]

    def verify_chain(self) -> tuple[bool, int | None]:
        """(True, None) if every event's hash matches its content and its predecessor; else (False, seq)."""
        prev = GENESIS
        for r in self.conn.execute("SELECT seq, at, file_id, actor, kind, detail_json, prev_hash, hash "
                                   "FROM events ORDER BY seq"):
            if r[6] != prev or r[7] != event_hash(prev, r[1], r[2], r[3], r[4], r[5]):
                return False, r[0]
            prev = r[7]
        return True, None
