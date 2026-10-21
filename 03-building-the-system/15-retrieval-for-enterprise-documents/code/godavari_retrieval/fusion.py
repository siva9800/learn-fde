"""Reciprocal rank fusion and the reranker stand-in.

RRF (Cormack, Clarke and Buettcher, SIGIR 2009): score(d) = sum over lists of 1 / (k + rank of d in that list),
ranks from 1, k = 60 by convention (and OpenSearch's default rank_constant since 2.19). It uses ranks only, so a
BM25 score of 14.2 and a cosine of 0.31 never have to be put on one scale.

The reranker stand-in looks at the query and one candidate together, as a cross-encoder does, using features
you can read: how much of the query's vocabulary and concepts the chunk covers, query word pairs that appear in
it, and an exact identifier match. A real cross-encoder learns these and more (section 05.6).
"""

from __future__ import annotations

from collections.abc import Sequence

from .chunking import Chunk
from .dense import concepts
from .text import dense_terms, lexical_terms

RRF_K = 60


def rrf(rankings: Sequence[Sequence[int]], k: int = RRF_K) -> list[tuple[int, float]]:
    score: dict[int, float] = {}
    best: dict[int, int] = {}
    for ranking in rankings:
        for r, doc in enumerate(ranking, start=1):
            score[doc] = score.get(doc, 0.0) + 1.0 / (k + r)
            best[doc] = min(best.get(doc, r), r)
    return sorted(score.items(), key=lambda kv: (-kv[1], best[kv[0]], kv[0]))


def _is_identifier(t: str) -> bool:
    return t.startswith(("GFL/", "GF-", "pan_"))


def rerank(query: str, candidates: list[tuple[int, float]], chunks: Sequence[Chunk]) -> list[tuple[int, float]]:
    q_terms = set(lexical_terms(query))
    q_list = lexical_terms(query)
    q_pairs = set(zip(q_list, q_list[1:]))
    q_concepts = set(concepts(dense_terms(query)))
    q_ids = {t for t in q_terms if _is_identifier(t)}
    top = max((s for _, s in candidates), default=1.0) or 1.0
    out = []
    for i, fused in candidates:
        c_list = lexical_terms(chunks[i].index_text)
        c_terms = set(c_list)
        coverage = len(q_terms & c_terms) / max(1, len(q_terms))
        pairs = len(q_pairs & set(zip(c_list, c_list[1:]))) / max(1, len(q_pairs))
        concept_cov = len(q_concepts & set(concepts(dense_terms(chunks[i].index_text)))) / max(1, len(q_concepts))
        id_match = 1.0 if q_ids and q_ids & c_terms else 0.0
        out.append((i, 0.4 * coverage + 0.2 * pairs + 0.3 * concept_cov + 0.5 * id_match + 0.1 * fused / top))
    return sorted(out, key=lambda kv: (-kv[1], kv[0]))
