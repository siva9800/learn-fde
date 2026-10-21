"""The page: escaped, self-contained, bilingual, evidence beside every field, one look-first field, no bulk approve;
and the citations behind it: one clause per signed rule, in force on the decision date, quoted verbatim."""

from __future__ import annotations

import copy
import re
from dataclasses import replace
from datetime import date

import pytest
from jinja2 import DictLoader, Environment, select_autoescape

from godavari_review import citations, render
from godavari_review.queue import NEVER_BULK_ACTIONS, build_item, queue_order
from evals.day11 import RULESETS
from godavari_retrieval.corpus import Clause, policy_documents
from intake.ruleset import SignoffError

HOSTILE = '<script>alert("x")</script><img src=x onerror=alert(1)>'


def page_for(pf) -> str:
    return render.render_file(pf.item)


def test_every_value_from_a_document_is_escaped(week):
    item = copy.deepcopy(week.files[0].item)
    item.fields[0].row = replace(item.fields[0].row, value=HOSTILE, evidence=HOSTILE)
    item.note = HOSTILE
    html = render.render_file(item)
    assert "<script" not in html and "<img" not in html
    assert "&lt;script&gt;" in html


def test_the_pages_load_nothing_from_anywhere(week):
    html = page_for(week.files[1]) + render.render_queue([p.item for p in week.files[:5]], "test", set())
    assert "<script" not in html and "<link" not in html and "@import" not in html
    assert not re.search(r'(src|href)\s*=\s*"(https?:)?//', html)
    assert "Content-Security-Policy" in html and "default-src &#39;none&#39;" in html   # escaped inside the attribute


def test_select_autoescape_does_not_cover_a_dot_j2_template():
    """The trap the environment avoids by setting autoescape=True explicitly."""
    env = Environment(loader=DictLoader({"page.html.j2": "{{ v }}", "page.html": "{{ v }}"}),
                      autoescape=select_autoescape(["html"]))
    assert env.get_template("page.html.j2").render(v="<b>") == "<b>"            # not escaped
    assert env.get_template("page.html").render(v="<b>") == "&lt;b&gt;"


def test_labels_are_bilingual_with_the_language_marked(week):
    html = page_for(week.files[2])
    assert 'lang="te"' in html and "ఆన్-రోడ్ ధర" in html and '<html lang="en">' in html


def test_every_field_has_its_source_or_an_explicit_problem(week):
    for pf in week.files:
        for v in pf.item.fields:
            assert v.crop or v.row.value is None or v.reasons, (pf.item.file_id, v.row.field)


def test_exactly_one_look_first_field_and_it_comes_first(week):
    for pf in week.files:
        assert sum(v.forced for v in pf.item.fields) == 1
    html = page_for(week.files[3])
    assert html.index('id="look-first"') < html.index('id="h-check"') < html.index('id="h-auto"')


def test_the_queue_offers_no_bulk_approval(week):
    html = render.render_queue([p.item for p in week.files], "test", set())
    buttons = " ".join(re.findall(r"<button[^>]*>([^<]*)</button>", html)).lower()
    assert "approve" not in buttons and "confirm" not in buttons
    assert "approve" in NEVER_BULK_ACTIONS


def test_pilot_mode_refuses_a_screen_on_unsigned_rules(week, fitted, policy):
    bands, _ = fitted
    pf = week.files[0]
    with pytest.raises(SignoffError):
        build_item(pf.bundle, pf.result, pf.rows, bands, policy, RULESETS["two-wheeler"], pf.arrived,
                   pf.arrived.date(), "v", mode="pilot")


def test_queue_order_is_branch_first_then_amount_then_age(week):
    items = queue_order([p.item for p in week.files])
    tiers = [i.tier for i in items]
    assert tiers == sorted(tiers)
    middle = [i.amount or 0 for i in items if i.tier == 1]
    assert middle == sorted(middle, reverse=True)


def test_indian_grouping():
    assert render.inr(124000) == "Rs 1,24,000" and render.inr(950) == "Rs 950" and render.inr(None) == "-"


def test_every_two_wheeler_rule_cites_a_clause_in_force_on_the_first_pilot_day():
    on = date(2026, 12, 7)
    docs = {d.doc_id: d for d in policy_documents()}
    for rule in RULESETS["two-wheeler"].rules:
        c = citations.cite(rule.rule_id, on)
        assert c is not None, rule.rule_id
        doc = docs[c.doc_id]
        item = next(i for s in doc.sections for i in s.items if i.number == c.clause)
        if isinstance(item, Clause):
            assert c.text == item.text                                 # verbatim, not paraphrased


def test_a_superseded_circular_is_refused_not_shown():
    table = citations.load_table()
    stale = {**table, "rules": {**table["rules"], "TW-KYC-MASK": ["GFL/CO/2024/007", "2.2"]}}
    with pytest.raises(citations.StaleCitation, match="superseded by GFL/CO/2025/012"):
        citations.cite("TW-KYC-MASK", date(2026, 12, 7), stale)
    assert citations.cite("ENV-EVIDENCE", date(2026, 12, 7)) is None
