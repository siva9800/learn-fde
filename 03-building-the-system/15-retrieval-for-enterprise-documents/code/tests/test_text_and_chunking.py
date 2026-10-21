"""Tokenizers and the chunker, on hand-made pages and on the generated corpus."""

from __future__ import annotations

from datetime import date

from godavari_retrieval.chunking import chunk_document, chunk_naive, clean_pages, learn_boilerplate
from godavari_retrieval.corpus import Document
from godavari_retrieval.day11 import rules_two_wheeler
from godavari_retrieval.text import (PAN_RE, dense_terms, fold, lexical_terms, naive_terms, pan_token,
                                     redact_pans, tokenise_pans)


# ------------------------------------------------------------------------------------------- tokenizers
def test_telugu_is_kept_whole_by_the_lexical_analyzer_and_shredded_by_naive_w():
    assert lexical_terms("ఆదాయ రుజువు") == ["ఆదాయ", "రుజువు"]
    assert naive_terms("ఆదాయ రుజువు") != ["ఆదాయ", "రుజువు"]          # \w+ splits at the vowel signs


def test_identifiers_survive_the_lexical_analyzer_and_fall_apart_in_the_dense_view():
    terms = lexical_terms("see GFL/CO/2025/027 clause 4.2 for GF-23417")
    assert {"GFL/CO/2025/027", "4.2", "GF-23417"} <= set(terms)
    assert "GFL/CO/2025/027" not in dense_terms("GFL/CO/2025/027")
    assert dense_terms("GFL/CO/2025/027") == ["gfl", "co", "2025", "027"]


def test_transliteration_variants_fold_to_one_key():
    assert fold("aadaayam") == fold("aadayam") == fold("adayam")
    assert fold("vyavasaayam") == fold("vyavasayam")
    assert fold("addhe") == fold("adde")
    assert fold("jeetham") == fold("jitam")


def test_pan_becomes_a_keyed_token_and_is_redacted_in_logs():
    text, n = tokenise_pans("files for PAN FGHPK1234J please")
    assert n == 1 and pan_token("FGHPK1234J") in text and "FGHPK1234J" not in text
    assert redact_pans("PAN FGHPK1234J") == "PAN [PAN]"
    assert pan_token("fghpk1234j") == pan_token("FGHPK1234J")       # normalised before hashing


# ---------------------------------------------------------------------------- a hand-made two-page PDF
def _hand_doc() -> Document:
    head = ["GODAVARI FINANCE LTD · CREDIT OPERATIONS", "GFL/CO/2099/001 · Test circular"]
    foot = lambda n: [f"Page {n} of 2", "Internal · uncontrolled when printed"]  # noqa: E731
    p1 = head + ["Credit Operations Circular No. GFL/CO/2099/001", "Subject: Test circular", "1. Rules",
                 "~ D3V0RPPA · ECNA1LPM0C ~",
                 "1.1 Analysts check every docu-", "ment before the file moves.",
                 "1.2 Table 1: Income by type", "| Type | Proof |", "| Salaried | three salary slips |"] + foot(1)
    p2 = head + ["| Type | Proof |", "| Self-employed | twelve-month bank statement |",
                 "1.3 The branch keeps the copy."] + foot(2)
    return Document("GFL/CO/2099/001", "Test circular", "circular", "all", "en", date(2099, 1, 1),
                    date(2099, 1, 1), pages=[p1, p2])


def test_cleaning_removes_boilerplate_and_junk_and_rejoins_hyphenation():
    d = _hand_doc()
    bp = learn_boilerplate([d], min_share=0.5)
    lines, stats = clean_pages(d, bp)
    text = "\n".join(t for _, t in lines)
    assert "Page 1 of 2" not in text and "uncontrolled" not in text and "CREDIT OPERATIONS\n" not in text
    assert "D3V0RPPA" not in text and stats["junk"] == 1
    assert "every document before" in " ".join(text.split()) and stats["dehyphenated"] == 1


def test_table_crossing_a_page_break_stays_one_chunk_with_its_header_once():
    d = _hand_doc()
    chunks = chunk_document(d, learn_boilerplate([d], min_share=0.5))
    table = [c for c in chunks if c.clause == "1.2"]
    assert len(table) == 1
    t = table[0]
    assert (t.page_start, t.page_end) == (1, 2)
    assert t.text.count("Type | Proof") == 1                        # the repeated header row is dropped
    assert "Self-employed | twelve-month bank statement" in t.text and "Salaried" in t.text
    assert {c.clause for c in chunks} == {"header", "1.1", "1.2", "1.3"}


def test_naive_windows_keep_the_boilerplate_the_structure_chunker_removes():
    d = _hand_doc()
    assert any("Page 1 of 2" in c.text for c in chunk_naive(d))


# ------------------------------------------------------------------------------------ on the corpus
def test_no_structure_chunk_carries_headers_footers_or_stamps(chunks):
    for c in chunks:
        assert "uncontrolled when printed" not in c.text
        assert "GODAVARI FINANCE LTD · CREDIT OPERATIONS" not in c.text
        assert "D3V0RPPA" not in c.text


def test_the_income_table_keeps_each_row_whole_with_caption_and_header(chunks):
    rows = [c for c in chunks if c.doc_id == "GFL/CO/2025/027" and c.clause == "4.2"]
    assert rows and all(c.text.startswith("Table 1: Income proof by applicant type\nApplicant type |") for c in rows)
    se = [c for c in rows if "Self-employed (shop owner" in c.text]
    assert len(se) == 1 and "or GST returns for the last four quarters" in se[0].text
    assert (rows[0].page_start, rows[0].page_end) == (2, 3)


def test_every_chunk_has_a_clause_and_pages_inside_its_document(docs, chunks):
    pages = {d.doc_id: len(d.pages) for d in docs}
    for c in chunks:
        assert c.clause
        assert 1 <= c.page_start <= c.page_end <= pages[c.doc_id]


def test_loan_summaries_are_one_chunk_each_and_hold_no_pan(chunks):
    loans = [c for c in chunks if c.meta.doc_type == "loan_decision"]
    assert len(loans) == 300 and len({c.doc_id for c in loans}) == 300
    assert not any(PAN_RE.search(c.text) for c in chunks)


def test_rulebook_text_comes_from_day11_rule_constants(chunks):
    rb = next(c for c in chunks if c.doc_id == "GFL/RB/2026/001" and c.clause == "1.1")
    assert f"Rs {rules_two_wheeler.MAX_AMOUNT:,}" in rb.text
    assert f"{rules_two_wheeler.MAX_FINANCE_PERCENT} percent" in rb.text
