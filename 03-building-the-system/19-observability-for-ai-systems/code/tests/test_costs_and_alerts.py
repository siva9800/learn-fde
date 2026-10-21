"""The ceiling and spike alerts fire on Tuesday's files and not before or after; the page filter is safe and works."""

from __future__ import annotations

from datetime import date
from statistics import median
from typing import Any

from godavari_obs import alerts as A
from godavari_obs import costs as K
from godavari_obs.statements import continuation_pages, filter_for_model, lengthen_statement
from intake.catalogue import PAGE_TITLES, Doc

TUE, WED = date(2026, 12, 15), date(2026, 12, 16)


def test_ceiling_alert_names_the_file_and_its_trace(run: dict[str, Any]) -> None:
    ceiling = [a for a in run["alerts"] if a.rule == "ceiling"]
    assert ceiling and all(a.day == TUE for a in ceiling)
    for a in ceiling:
        c = next(c for c in run["fc"] if c.file_id == a.scope)
        assert c.inr > K.CEILING_INR and a.traces == (c.trace_id,)
    assert not [c for c in run["fc"] if c.run == "pilot-week-1" and c.inr > K.CEILING_INR]


def test_spike_alert_fires_while_the_statements_reach_the_model_and_stops_after_the_filter(run: dict[str, Any]) -> None:
    spikes = {(a.day, a.scope) for a in run["alerts"] if a.rule == "spike"}
    assert spikes == {(TUE, "Guntur"), (WED, "Guntur")}


def test_after_the_filter_guntur_costs_what_week_one_did(run: dict[str, Any]) -> None:
    fc = run["fc"]
    week1 = median([c.inr for c in fc if c.run == "pilot-week-1" and c.branch == "Guntur"])
    after = [c for c in fc if c.branch == "Guntur" and c.page_filter != "off"]
    assert after and all(c.pages > 60 for c in after)
    assert median([c.inr for c in after]) <= 1.25 * week1
    assert all(c.pages_to_model < c.pages - 50 for c in after)


def test_filter_keeps_page_numbers_and_never_touches_the_analysts_file(run: dict[str, Any]) -> None:
    fr = next(f for f in run["weeks"][1].files if f.filtered)
    assert len(fr.bundle.pages) - len(fr.shown.pages) == fr.filtered == len(continuation_pages(fr.bundle))
    kept = {p.number for p in fr.shown.pages}
    assert kept <= {p.number for p in fr.bundle.pages}
    first = [p for p in fr.bundle.pages if p.text.startswith(PAGE_TITLES[Doc.BANK_STATEMENT])][0]
    assert first.number in kept                                     # the statement's first page still reaches the model


def test_lengthening_appends_and_moves_no_page(run: dict[str, Any]) -> None:
    fr = run["weeks"][0].files[0]
    longer = lengthen_statement(fr.bundle)
    assert longer.pages[: len(fr.bundle.pages)] == fr.bundle.pages
    shown, n = filter_for_model(longer)
    assert shown.pages == fr.bundle.pages and n == len(longer.pages) - len(fr.bundle.pages)


def test_by_stage_sums_to_the_total(run: dict[str, Any], store: Any) -> None:
    total = sum(sum(K.by_stage(store, r).values()) for r in ("pilot-week-1", "pilot-week-2"))
    assert abs(total - run["ledger_inr"]) < 1e-6


def test_every_alert_has_an_owner_and_none_of_this_fortnight_pages_anyone(run: dict[str, Any]) -> None:
    assert all(a.rule in A.ROUTES and a.who for a in run["alerts"])
    assert A.pages(run["alerts"]) == []
    assert not [a for a in run["alerts"] if "COO" in a.who and a.how != "weekly"]
