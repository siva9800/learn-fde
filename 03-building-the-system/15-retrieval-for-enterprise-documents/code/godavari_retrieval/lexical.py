"""BM25, written out in full (Robertson and Zaragoza's formulation, Lucene's always-positive idf).

The pre-filter is a set of allowed chunk positions passed INTO the scoring loop: a chunk the caller may not see
is never scored, never ranked and never counted. Corpus statistics (document frequency, average length) are
global; section 06.7 discusses the small side channel that leaves and when to split the index instead.
"""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from collections.abc import Callable, Sequence

from .chunking import Chunk
from .text import lexical_terms


class BM25Index:
    def __init__(self, chunks: Sequence[Chunk], analyzer: Callable[[str], list[str]] = lexical_terms,
                 k1: float = 1.2, b: float = 0.75) -> None:
        self.analyzer, self.k1, self.b = analyzer, k1, b
        self.postings: dict[str, list[tuple[int, int]]] = defaultdict(list)
        self.lengths: list[int] = []
        for i, c in enumerate(chunks):
            terms = analyzer(c.index_text)
            self.lengths.append(len(terms))
            for t, tf in Counter(terms).items():
                self.postings[t].append((i, tf))
        self.n = len(self.lengths)
        self.avgdl = sum(self.lengths) / max(1, self.n)

    def idf(self, term: str) -> float:
        df = len(self.postings.get(term, ()))
        return math.log(1 + (self.n - df + 0.5) / (df + 0.5))

    def scores(self, query: str, allowed: set[int] | None = None) -> dict[int, float]:
        out: dict[int, float] = defaultdict(float)
        for term in set(self.analyzer(query)):
            idf = self.idf(term)
            for i, tf in self.postings.get(term, ()):
                if allowed is not None and i not in allowed:
                    continue                                 # pre-filter: never scored
                norm = tf + self.k1 * (1 - self.b + self.b * self.lengths[i] / self.avgdl)
                out[i] += idf * tf * (self.k1 + 1) / norm
        return dict(out)

    def search(self, query: str, allowed: set[int] | None = None, k: int = 50) -> list[tuple[int, float]]:
        s = self.scores(query, allowed)
        return sorted(s.items(), key=lambda kv: (-kv[1], kv[0]))[:k]
