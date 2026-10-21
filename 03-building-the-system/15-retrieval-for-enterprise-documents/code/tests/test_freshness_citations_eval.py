"""Superseded documents, the version in force, citations to the clause, the labels, and the recall gate."""

from __future__ import annotations

from datetime import date

from godavari_retrieval.chunking import clean_pages, learn_boilerplate
from godavari_retrieval.evaluate import first_hit_rank, run_eval, spans_found, summarise
from godavari_retrieval.permissions import POLICY_TYPES, SearchFilter
from godavari_retrieval.queries import QUERIES
from godavari_retrieval.service import RetrievalService
from godavari_retrieval.text import normalise_space

HEADLINE = "what income proof is acceptable for a self-employed two-wheeler applicant in Guntur"


def test_superseded_versions_are_filtered_out_by_default(svc, now):
    f = SearchFilter(as_of=now.date(), doc_types=POLICY_TYPES)
    r = svc.search("lakshmi", "self-employed income tax returns only two-wheeler", now, k=10, f=f)
    assert "GFL/CO/2024/015" not in r.keys() and r.keys()[0] == "GFL/CO/2025/027"


def test_a_superseded_number_is_redirected_with_a_notice(svc, now):
    f = SearchFilter(as_of=now.date(), doc_types=POLICY_TYPES)
    r = svc.search("lakshmi", "GFL/CO/2024/007 unmasked Aadhaar copy", now, k=3, f=f)
    assert any("GFL/CO/2024/007 was superseded by GFL/CO/2025/012" in n for n in r.notices)
    assert set(r.keys()) == {"GFL/CO/2025/012"}


def test_as_of_returns_the_version_in_force_on_that_day(svc, now):
    r = svc.search("lakshmi", HEADLINE, now, k=3, f=SearchFilter(as_of=date(2025, 3, 1), doc_types=POLICY_TYPES))
    assert r.keys()[0] == "GFL/CO/2024/015"


def test_every_citation_quotes_text_that_is_on_the_cited_pages(docs, svc, now):
    bp = learn_boilerplate(docs)
    by_id = {d.doc_id: d for d in docs}
    for q in QUERIES[:20]:
        for res in svc.search(q.user, q.text, now, k=5).results:
            c = res.chunk
            lines, _ = clean_pages(by_id[c.doc_id], bp)
            pages_text = normalise_space(" ".join(t.strip("| ") for p, t in lines if c.page_start <= p <= c.page_end))
            first_words = normalise_space(c.text.splitlines()[-1].split(" | ")[0])[:40]
            assert first_words in pages_text.replace(" | ", " ").replace("|", ""), res.citation


def test_recall_helpers():
    assert spans_found(["abc", "xyz"], ["... ABC ...", "nothing"]) == 0.5
    assert first_hit_rank(["xyz"], ["a", "b xyz"]) == 2 and first_hit_rank(["q"], ["a"]) is None


def test_every_label_is_answerable_and_superseded_labels_exist_only_in_force(chunks):
    in_force = [c for c in chunks if c.meta.doc_type == "loan_decision" or c.meta.in_force(date(2026, 11, 25))]
    old = [c for c in chunks if c.meta.doc_type != "loan_decision" and not c.meta.in_force(date(2026, 11, 25))]
    for q in QUERIES:
        for span in q.spans:
            s = normalise_space(span)
            assert any(s in normalise_space(c.text) for c in in_force), (q.qid, span)
            if q.category == "superseded":
                assert not any(s in normalise_space(c.text) for c in old), (q.qid, span)


def test_the_recall_gate(svc, chunks, naive_chunks, day1, now):
    final = summarise(run_eval(svc, now))["all"]
    naive = summarise(run_eval(RetrievalService(naive_chunks, day1), now))["all"]
    assert final["R@5"] >= 0.95                     # the gate for this synthetic set; Day 14 sets the real one
    assert naive["R@5"] < final["R@5"]
