"""Retrieval measured on its own, before any model sees a passage: recall at k, MRR, and a permission audit.

Day 14 owns evals and golden sets. Its harness (../14-evals-first/code/evals/) scores extraction and has no
retrieval metric, so this is the minimal retrieval check: for each labelled query, run the search as the user
who asked it, and count how many answer spans appear in the top k. Recall at k is the share of spans found,
averaged over queries. The interval on it uses Day 14's Wilson function, imported by path (day14.py).
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime

from .chunking import Chunk
from .day14 import wilson
from .permissions import POLICY_TYPES, Directory, SearchFilter, may_see
from .queries import QUERIES, LabelledQuery
from .service import RetrievalService
from .text import normalise_space

KS = (1, 3, 5, 10)


def scope_filter(q: LabelledQuery, now: datetime) -> SearchFilter:
    types = POLICY_TYPES if q.scope == "policy" else frozenset({"loan_decision"})
    return SearchFilter(as_of=now.date(), doc_types=types)


def spans_found(spans: Sequence[str], texts: Sequence[str]) -> float:
    norm = [normalise_space(t) for t in texts]
    hit = sum(1 for s in spans if any(normalise_space(s) in t for t in norm))
    return hit / len(spans)


def first_hit_rank(spans: Sequence[str], texts: Sequence[str]) -> int | None:
    for r, t in enumerate(texts, start=1):
        nt = normalise_space(t)
        if any(normalise_space(s) in nt for s in spans):
            return r
    return None


@dataclass
class EvalRow:
    qid: str
    category: str
    recall: dict[int, float]
    rr: float
    top_ids: list[str]


def run_eval(service: RetrievalService, now: datetime, queries: Sequence[LabelledQuery] = QUERIES) -> list[EvalRow]:
    rows = []
    for q in queries:
        resp = service.search(q.user, q.text, now, k=max(KS), f=scope_filter(q, now))
        texts = [r.chunk.text for r in resp.results]
        rank = first_hit_rank(q.spans, texts)
        rows.append(EvalRow(q.qid, q.category, {k: spans_found(q.spans, texts[:k]) for k in KS},
                            1.0 / rank if rank else 0.0, [r.chunk.doc_id for r in resp.results]))
    return rows


def summarise(rows: Sequence[EvalRow]) -> dict[str, dict[str, float]]:
    """Mean recall at each k and MRR, overall and per category."""
    groups: dict[str, list[EvalRow]] = defaultdict(list)
    for r in rows:
        groups[r.category].append(r)
        groups["all"].append(r)
    out = {}
    for g, rs in groups.items():
        out[g] = {f"R@{k}": sum(r.recall[k] for r in rs) / len(rs) for k in KS}
        out[g]["MRR"] = sum(r.rr for r in rs) / len(rs)
        out[g]["n"] = len(rs)
    return out


def answered_at(rows: Sequence[EvalRow], k: int = 5) -> tuple[int, int, tuple[float, float]]:
    """Queries fully answered in the top k, out of n, with Day 14's 95 percent Wilson interval."""
    hit = sum(1 for r in rows if r.recall[k] == 1.0)
    return hit, len(rows), wilson(hit, len(rows))


def permission_audit(service: RetrievalService, chunks: Sequence[Chunk], directory: Directory, now: datetime,
                     users: Sequence[str]) -> tuple[int, int]:
    """Every query, as every user, both scopes, k = 10: count results the user may not see. Must be zero."""
    checked = violations = 0
    for user in users:
        principal = directory.resolve(user, now)
        for q in QUERIES:
            for scope in ("policy", "precedent"):
                f = SearchFilter(as_of=now.date(), doc_types=POLICY_TYPES if scope == "policy" else frozenset({"loan_decision"}))
                for r in service.search(user, q.text, now, k=10, f=f).results:
                    checked += 1
                    violations += 0 if may_see(principal, r.chunk) else 1
    return checked, violations
