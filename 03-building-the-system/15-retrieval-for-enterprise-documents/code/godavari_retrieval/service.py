"""The retrieval service behind the review queue's "Policy and precedent" panel, and the naive version it replaces.

``RetrievalService.search`` runs, in this order, for every request:

1. resolve the caller's groups from the newest snapshot (fail closed: stale snapshot, unknown user, no groups);
2. rewrite the query: PANs become keyed tokens (and a PAN restricts the search to files carrying that token);
   a superseded circular number becomes the current one, with a notice saying so;
3. build the pre-filter (permissions, approval, version in force, product, document type);
4. BM25 and the dense stand-in over the allowed chunks only; RRF; the reranker stand-in on the fused head;
5. keep one result per clause, and cite each to its document, version, clause and pages;
6. draft the panel's note from the returned results only, log only what was returned, and append a view-log
   entry (user, time, snapshot, redacted query, documents shown) for the CISO's seven-year log.

``NaivePostFilterService`` ranks everything, drafts the note and writes the debug log from the unfiltered top k,
counts every match, and filters the list last. Section 06.3 walks through what that leaks.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date, datetime

from .chunking import Chunk
from .dense import DenseIndex
from .fusion import rerank, rrf
from .lexical import BM25Index
from .permissions import Directory, Principal, SearchFilter, allowed_positions, may_see, passes_filter
from .text import normalise_space, redact_pans, tokenise_pans

CIRCULAR_ID = re.compile(r"\b[A-Z]{2,4}/[A-Z]{2,4}/\d{4}/\d{3}\b")
PAN_TOKEN = re.compile(r"pan_[0-9a-f]{12}")
DEPTH = 50            # how deep each ranked list goes into fusion
RERANK_TOP = 50       # rerank the whole fused head; 20 was measured too (section 05.6)


@dataclass(frozen=True)
class Result:
    rank: int
    chunk: Chunk
    score: float

    @property
    def citation(self) -> str:
        m, c = self.chunk.meta, self.chunk
        if m.doc_type == "loan_decision":
            return f"{m.doc_id} · {m.branch} ({m.branch_code}) · decided {m.effective_from:%d %b %Y}"
        pages = f"page {c.page_start}" if c.page_start == c.page_end else f"pages {c.page_start} to {c.page_end}"
        where = "document header" if c.clause == "header" else f"clause {c.clause}"
        return f"{m.doc_id} · {m.title} · {where} · {pages} · in force from {m.effective_from:%d %b %Y}"


@dataclass
class Response:
    user: str
    query_logged: str
    results: list[Result]
    total_matches: int
    notices: list[str] = field(default_factory=list)
    note: str = ""
    debug_log: list[str] = field(default_factory=list)

    def keys(self) -> list[str]:
        return [r.chunk.doc_id for r in self.results]


def draft_note(results: Sequence[Result]) -> str:
    """Stand-in for the model call that writes the panel's one-paragraph note (Day 20 wires Day 12's client in).
    It only ever sees the results it is given."""
    parts = []
    for r in results[:3]:
        m = r.chunk.meta
        if m.doc_type == "loan_decision":
            reason = next((ln[8:] for ln in r.chunk.text.splitlines() if ln.startswith("Reason: ")), "")
            parts.append(f"{m.doc_id} ({m.branch}, {dict(m.extra).get('decision', '')}): {reason}")
        else:
            first = r.chunk.text.split(". ")[0].split("\n")[0]
            parts.append(f"{m.doc_id} clause {r.chunk.clause}: {first}")
    return " | ".join(parts)


def collapse(ranked: list[tuple[int, float]], chunks: Sequence[Chunk]) -> list[tuple[int, float]]:
    """One result per clause: two row groups of the same table, or two windows of one clause, show once."""
    seen: set[str] = set()
    out = []
    for i, s in ranked:
        key = chunks[i].key
        if key not in seen:
            seen.add(key)
            out.append((i, s))
    return out


class _Ranker:
    """Shared ranking code: the two services differ only in where the filter sits."""

    def __init__(self, chunks: Sequence[Chunk], mode: str = "hybrid", use_rerank: bool = True,
                 rerank_top: int = RERANK_TOP) -> None:
        self.chunks = list(chunks)
        self.mode, self.use_rerank, self.rerank_top = mode, use_rerank, rerank_top
        self.bm25 = BM25Index(self.chunks)
        self.dense = DenseIndex(self.chunks)
        self.by_doc: dict[str, list[int]] = {}
        for i, c in enumerate(self.chunks):
            self.by_doc.setdefault(c.doc_id, []).append(i)

    def rank(self, query: str, allowed: set[int] | None) -> tuple[list[tuple[int, float]], int]:
        lex = self.bm25.search(query, allowed, DEPTH) if self.mode in ("hybrid", "lexical") else []
        den = self.dense.search(query, allowed, DEPTH) if self.mode in ("hybrid", "dense") else []
        total = len({i for i, _ in lex} | {i for i, _ in den})
        if self.mode == "lexical":
            fused = lex
        elif self.mode == "dense":
            fused = den
        else:
            fused = rrf([[i for i, _ in lex], [i for i, _ in den]])
        if self.use_rerank and fused:
            head = rerank(query, fused[:self.rerank_top], self.chunks)
            fused = head + fused[self.rerank_top:]
        return fused, total

    def rewrite(self, query: str, as_of: date) -> tuple[str, list[str]]:
        """PAN to token; superseded circular number to the one in force, with a notice."""
        notices: list[str] = []
        text, n = tokenise_pans(query)
        if n:
            notices.append(f"{n} PAN in the query matched by keyed token; the PAN itself is not stored or logged")
        meta_by_id = {c.doc_id: c.meta for c in self.chunks}

        def current(doc_id: str) -> str:
            seen = set()
            m = meta_by_id.get(doc_id)
            while m is not None and m.superseded_by and m.effective_to and m.effective_to <= as_of and doc_id not in seen:
                seen.add(doc_id)
                doc_id = m.superseded_by
                m = meta_by_id.get(doc_id)
            return doc_id

        for old in sorted(set(CIRCULAR_ID.findall(text))):
            new = current(old)
            if new != old:
                eff = meta_by_id[new].effective_from
                notices.append(f"{old} was superseded by {new} from {eff:%d %b %Y}; showing {new}")
                text = text.replace(old, new)
            elif old not in meta_by_id:
                notices.append(f"{old} is not in the register")
        return text, notices


class RetrievalService(_Ranker):
    def __init__(self, chunks: Sequence[Chunk], directory: Directory, mode: str = "hybrid",
                 use_rerank: bool = True, rerank_top: int = RERANK_TOP) -> None:
        super().__init__(chunks, mode, use_rerank, rerank_top)
        self.directory = directory
        self.view_log: list[dict[str, object]] = []

    def search(self, user: str, query: str, now: datetime, k: int = 5, f: SearchFilter | None = None) -> Response:
        principal: Principal = self.directory.resolve(user, now)       # raises if the snapshot is stale
        f = f or SearchFilter(as_of=now.date())
        logged = redact_pans(query)
        if not principal.groups:
            resp = Response(user, logged, [], 0, ["no groups for this user: nothing is visible"])
            self._log_view(principal, now, logged, resp)
            return resp
        text, notices = self.rewrite(query, f.as_of)
        allowed = allowed_positions(self.chunks, principal, f)
        tokens = set(PAN_TOKEN.findall(text))
        if tokens:                                   # an identifier is a lookup, not a similarity search
            allowed = {i for i in allowed if tokens & set(PAN_TOKEN.findall(self.chunks[i].text))}
            if not allowed:
                notices.append("no file you can see matches this PAN")
        ranked, total = self.rank(text, allowed)
        results = [Result(r, self.chunks[i], s) for r, (i, s) in enumerate(collapse(ranked, self.chunks)[:k], start=1)]
        resp = Response(user, logged, results, total, notices, draft_note(results))
        resp.debug_log = [f"rank {r.rank} {r.chunk.chunk_id} score {r.score:.3f}" for r in results]
        self._log_view(principal, now, logged, resp)
        return resp

    def _log_view(self, p: Principal, now: datetime, logged: str, resp: Response) -> None:
        self.view_log.append({"at": now.isoformat(timespec="minutes"), "user": p.user,
                              "snapshot": p.snapshot_taken.isoformat(timespec="minutes"), "query": logged,
                              "shown": sorted({r.chunk.doc_id for r in resp.results})})


class NaivePostFilterService(_Ranker):
    """What the first version usually looks like. Do not ship this."""

    def __init__(self, chunks: Sequence[Chunk], directory: Directory) -> None:
        super().__init__(chunks)
        self.directory = directory

    def search(self, user: str, query: str, now: datetime, k: int = 5, f: SearchFilter | None = None) -> Response:
        principal = self.directory.resolve(user, now)
        f = f or SearchFilter(as_of=now.date())
        text, notices = self.rewrite(query, f.as_of)
        everything = {i for i, c in enumerate(self.chunks) if passes_filter(c, f)}    # dates and types, no ACL
        ranked, total = self.rank(text, everything)
        top = [Result(r, self.chunks[i], s) for r, (i, s) in enumerate(ranked[:k], start=1)]
        note = draft_note(top)                                                         # drafted before filtering
        debug = [f"rank {r.rank} {r.chunk.chunk_id} score {r.score:.3f} {normalise_space(r.chunk.text)[:90]}"
                 for r in top]                                                         # snippets of everything
        shown = [r for r in top if may_see(principal, r.chunk)]                        # the filter, last
        return Response(user, query, shown, total, notices + [f"showing {len(shown)} of {total} results"], note, debug)
