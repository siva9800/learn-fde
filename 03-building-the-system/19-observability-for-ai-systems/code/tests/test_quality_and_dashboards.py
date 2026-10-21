"""The quality job reads the golden-set baseline and catches drift; the pages are static, escaped and current."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any

from godavari_obs import dashboards as D
from godavari_obs import paths
from godavari_obs import quality as Q
from godavari_obs.spans import IST, Tracer, trace_id_for
from godavari_obs.store import TraceStore


def test_field_signals_use_the_golden_baseline(store: Any) -> None:
    gold = Q.golden_baseline()["strata"]
    for s in Q.field_signals(store, "pilot-week-2"):
        assert abs(s.golden_rate - (1 - gold[f"field={s.field}"]["accuracy"])) < 1e-12
        assert s.files == 60


def test_a_field_that_drifts_is_flagged() -> None:
    tracer = Tracer("t")
    at = datetime(2026, 12, 18, 10, 0, tzinfo=IST)
    for i in range(40):
        tid = trace_id_for("t", f"GF-7{i:04d}")
        root = tracer.span(tid, "loan_file", "file", at, **{"kaagaz.run": "pilot-week-9", "kaagaz.file.branch_code": "GNT04"})
        rev = tracer.span(tid, "review", "human", at, parent=root)
        if i < 12:                                    # 12 of 40 files: the income figure changed by the analyst
            rev.event("feedback", at, **{"kaagaz.feedback.field": "monthly_income", "kaagaz.feedback.content_change": True})
    store = TraceStore()
    store.write(tracer.spans, "t")
    sig = {s.field: s for s in Q.field_signals(store, "pilot-week-9")}
    assert sig["monthly_income"].status == "higher than the golden set"
    assert sig["pan"].status == "in line"


def test_rule_moves_and_golden_candidates(store: Any) -> None:
    moved = {(m.rule, m.branch) for m in Q.rule_moves(store) if m.moved}
    assert ("ENV-CONFIDENCE", "Guntur") in moved
    assert not [m for m in moved if m[1] == "Kukatpally"]
    assert any("over 60 pages" in c for c in Q.golden_candidates(store, "pilot-week-2"))


def test_policy_panel_refuses_only_when_the_snapshot_is_stale(store: Any) -> None:
    rows = store.by_name("retrieval godavari-policy-register")
    refused = [r for r in rows if r["status"] == "error"]
    assert refused and all(r["attrs"]["kaagaz.retrieval.snapshot_age_h"] > 36 for r in refused)
    assert all(r["attrs"]["kaagaz.retrieval.snapshot_age_h"] <= 36 for r in rows if r["status"] == "ok")


def test_pages_are_static_and_load_nothing(out: Path) -> None:
    for page in sorted((out / "dashboards").glob("*.html")):
        text = page.read_text(encoding="utf-8")
        assert "<script" not in text.lower(), page.name
        assert not re.search(r"(src|href)\s*=", text, re.I), page.name
        assert "http://" not in text and "https://" not in text, page.name
        assert "Content-Security-Policy" in text and "default-src 'none'" in text
        assert text.split("</head>")[0].count("<title>") == 1 and "prefers-color-scheme:dark" in text
        assert "<title>" in text.split("</head>")[1] or page.name == "coo-weekly.html"   # every mark has a tooltip


def test_every_value_is_escaped() -> None:
    hostile = "<script>alert(1)</script> & \"quoted\""
    html = D.page(hostile, hostile, D.table([hostile], [[hostile]]) + D.tile(hostile, hostile, hostile))
    assert "<script>" not in html and "&lt;script&gt;" in html and "&quot;quoted&quot;" in html


def test_the_committed_pages_are_the_ones_this_code_writes(out: Path) -> None:
    for page in sorted((out / "dashboards").glob("*.html")):
        committed = paths.DATA / "dashboards" / page.name
        assert committed.read_text(encoding="utf-8") == page.read_text(encoding="utf-8"), page.name
