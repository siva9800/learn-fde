"""BM25 by hand, RRF by hand, the dense stand-in's two properties, and collapse by clause."""

from __future__ import annotations

import math
from datetime import date

from godavari_retrieval.chunking import Chunk
from godavari_retrieval.corpus import Document
from godavari_retrieval.dense import DenseIndex
from godavari_retrieval.fusion import rrf
from godavari_retrieval.lexical import BM25Index
from godavari_retrieval.metadata import meta_for
from godavari_retrieval.service import collapse

_META = meta_for(Document("X", "t", "circular", "all", "en", date(2025, 1, 1), date(2025, 1, 1)))


def _c(i: int, text: str, clause: str = "") -> Chunk:
    return Chunk(f"X#{i}", "X", clause or str(i), "clause", "", 1, 1, text, text, _META)


def test_bm25_matches_the_formula_on_a_tiny_index():
    chunks = [_c(0, "gold loan tenure"), _c(1, "gold appraisal purity"), _c(2, "dealer quotation validity")]
    idx = BM25Index(chunks)
    # "quotation" appears in 1 of 3 chunks: idf = ln(1 + (3 - 1 + 0.5) / (1 + 0.5))
    assert math.isclose(idx.idf("quotation"), math.log(1 + 2.5 / 1.5))
    # all three chunks have length 3 = avgdl, tf = 1, so the score is idf * (k1 + 1) / (1 + k1) = idf
    assert math.isclose(idx.scores("quotation")[2], idx.idf("quotation"))
    assert [i for i, _ in idx.search("gold")] == [0, 1]


def test_the_pre_filter_means_a_hidden_chunk_is_never_scored():
    chunks = [_c(0, "gold loan tenure"), _c(1, "gold appraisal purity")]
    assert set(BM25Index(chunks).scores("gold", allowed={1})) == {1}
    assert [i for i, _ in DenseIndex(chunks).search("gold", allowed={1})] == [1]


def test_rrf_by_hand():
    fused = dict(rrf([[1, 2], [2, 3]]))
    assert math.isclose(fused[2], 1 / 62 + 1 / 61)
    assert math.isclose(fused[1], 1 / 61) and math.isclose(fused[3], 1 / 62)
    assert [d for d, _ in rrf([[1, 2], [2, 3]])][0] == 2              # agreement wins


def test_dense_stand_in_matches_paraphrase_and_misses_identifiers():
    chunks = [_c(0, "two-wheeler income proof for a self-employed shop owner"), _c(1, "gold vault register")]
    dense = DenseIndex(chunks)
    assert dense.search("earnings evidence for a trader buying a scooter")[0][0] == 0
    ids = [_c(0, "circular GFL/CO/2025/027 income proof"), _c(1, "circular GFL/CO/2024/015 income proof")]
    s = dict(DenseIndex(ids).search("GFL/CO/2025/027"))
    assert s[0] > s[1] > 0                                        # shares "gfl", "co": the wrong one still scores
    assert BM25Index(ids).search("GFL/CO/2025/027") == [(0, BM25Index(ids).scores("GFL/CO/2025/027")[0])]


def test_collapse_keeps_one_result_per_clause():
    chunks = [_c(0, "a", "4.2"), _c(1, "b", "4.2"), _c(2, "c", "4.3")]
    assert [i for i, _ in collapse([(0, 3.0), (1, 2.0), (2, 1.0)], chunks)] == [0, 2]
