"""Who is asking, and what they may see: the group snapshot and the pre-filter.

Where the groups come from (Active Directory, the nightly HR sync, SSO) is Day 22's subject. This module
consumes a snapshot file of user -> groups with the time it was taken, and does four things:

* resolves the caller's groups at the moment of the request, from the newest snapshot, never from the index;
* fails closed: an unknown user, a service account or a user with no groups sees nothing; a snapshot older
  than MAX_SNAPSHOT_AGE refuses to answer at all;
* builds the pre-filter from metadata: the ACL on each chunk, the approval status, the version in force on the
  date asked about, and any product or document-type filter from the review screen;
* uses Day 11's ``visible_to`` for every loan file, so the branch rule exists in exactly one place.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path

from .chunking import Chunk
from .day11 import visible_to
from .metadata import ROLE_COMPLIANCE

MAX_SNAPSHOT_AGE = timedelta(hours=36)     # nightly sync plus a margin; older means the sync is broken
POLICY_TYPES = frozenset({"circular", "rulebook", "annex", "rbi_digest"})


class StaleDirectoryError(RuntimeError):
    """The group snapshot is too old to trust. Retrieval refuses rather than guessing."""


@dataclass(frozen=True)
class Principal:
    user: str
    groups: frozenset[str]
    snapshot_taken: datetime

    @property
    def is_compliance(self) -> bool:
        return ROLE_COMPLIANCE in self.groups


@dataclass
class Directory:
    taken_at: datetime
    members: dict[str, frozenset[str]]
    source: str = ""

    @classmethod
    def load(cls, path: Path) -> "Directory":
        raw = json.loads(path.read_text(encoding="utf-8"))
        return cls(datetime.fromisoformat(raw["taken_at"]),
                   {u: frozenset(g) for u, g in raw["members"].items()}, source=path.name)

    def resolve(self, user: str, now: datetime) -> Principal:
        if now - self.taken_at > MAX_SNAPSHOT_AGE:
            raise StaleDirectoryError(f"group snapshot {self.source or ''} taken {self.taken_at:%Y-%m-%d %H:%M} is "
                                      f"more than {MAX_SNAPSHOT_AGE.total_seconds() / 3600:.0f} hours old; refusing to answer")
        return Principal(user, self.members.get(user, frozenset()), self.taken_at)


@dataclass(frozen=True)
class SearchFilter:
    as_of: date
    doc_types: frozenset[str] | None = None
    products: frozenset[str] | None = None        # "all" documents always pass a product filter
    include_superseded: bool = False
    extra: dict[str, str] = field(default_factory=dict)


def may_see(p: Principal, c: Chunk) -> bool:
    """The permission half of the pre-filter. Nothing about relevance, dates or products."""
    m = c.meta
    if not p.groups:
        return False
    if m.doc_type == "loan_decision":
        allowed = visible_to(p.groups, m.branch or "")          # Day 11's rule, by path
        assert allowed == bool(m.acl & p.groups), "ACL and Day 11's rule disagree"
        return allowed
    if m.approval_status != "approved" and not p.is_compliance:
        return False
    return bool(m.acl & p.groups)


def passes_filter(c: Chunk, f: SearchFilter) -> bool:
    m = c.meta
    if f.doc_types is not None and m.doc_type not in f.doc_types:
        return False
    if f.products is not None and m.product != "all" and m.product not in f.products:
        return False
    if m.doc_type == "loan_decision":
        return m.effective_from <= f.as_of
    return f.include_superseded or m.in_force(f.as_of)


def allowed_positions(chunks: Sequence[Chunk], p: Principal, f: SearchFilter) -> set[int]:
    """The pre-filter: the only chunk positions the ranking code is allowed to touch for this request."""
    return {i for i, c in enumerate(chunks) if may_see(p, c) and passes_filter(c, f)}
