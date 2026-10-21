"""No PAN, no Aadhaar number, no mobile number and no customer name reaches the trace store, the exports or the pages."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest

from godavari_obs import redact, sources
from godavari_obs.spans import IST, Tracer
from godavari_obs.store import TraceStore
from intake.synth import SURNAMES
from intake.validators import find_unmasked_aadhaar

PAN_RE = re.compile(r"[A-Z]{5}[0-9]{4}[A-Z]")
AT = datetime(2026, 12, 15, 2, 0, tzinfo=IST)


def identifiers(run: dict[str, Any]) -> dict[str, set[str]]:
    """Every identifier printed in the pilot's files: what the boundary must keep out."""
    out: dict[str, set[str]] = {"pan": set(), "aadhaar": set(), "mobile": set(), "name": set()}
    for w in run["weeks"]:
        for f in w.files:
            text = "\n".join(p.text for p in f.bundle.pages)
            out["pan"] |= set(PAN_RE.findall(text))
            out["aadhaar"] |= set(find_unmasked_aadhaar(text))
            out["mobile"].add(f.truth.fields["mobile"])
            out["name"].add(f.truth.fields["applicant_name"])
            if f.truth.fields.get("co_applicant_name"):
                out["name"].add(f.truth.fields["co_applicant_name"])
    return out


def outputs(out: Path) -> dict[str, str]:
    return {p.name: p.read_text(encoding="utf-8") for p in out.rglob("*") if p.suffix in (".jsonl", ".md", ".html")}


def test_the_files_do_contain_identifiers(run: dict[str, Any]) -> None:
    ids = identifiers(run)
    assert len(ids["pan"]) > 100 and len(ids["name"]) >= 120 and len(ids["mobile"]) >= 100
    assert ids["aadhaar"], "some files carry an unmasked Aadhaar copy (Day 11's KYC-MASK defect): the test is not vacuous"


def test_no_identifier_reaches_the_store_or_any_output(run: dict[str, Any], out: Path) -> None:
    ids = identifiers(run)
    texts = outputs(out)
    texts["traces.sqlite (rows)"] = run["store"].dump_text()
    for name, text in texts.items():
        upper = text.upper()
        for kind in ("pan", "aadhaar", "mobile"):
            leaked = [v for v in ids[kind] if v in text]
            assert not leaked, f"{kind} found in {name}"
        assert not [n for n in ids["name"] if n.upper() in upper], f"a customer name found in {name}"
        words = set(re.findall(r"[A-Z]+", upper))
        assert not words & {s.upper() for s in SURNAMES}, f"a surname from the files found in {name}"
        assert redact.pii_hits(text) == [], f"a detector fires on {name}"


def test_hostile_span_is_cleaned_and_counted_without_its_values() -> None:
    tracer = Tracer("t")
    s = tracer.span("a" * 32, "rules", "code", AT, **{
        "kaagaz.file.id": "ABCPK1234Q",                              # a PAN in a key that wants a file number
        "message": "name on the form 'RAVI TEJA GADDE' differs",     # free text: not on the list
        "value:ABCPK1234Q": "x",                                      # a key built from data
        "kaagaz.rules.fired": ["TW-DOC-05"]})
    s.event("feedback", AT, **{"kaagaz.feedback.field": "pan", "model_value": "ABCPK1234Q"})
    s.event("analyst_note", AT, text="customer RAVI TEJA asked")
    store = TraceStore()
    report = store.write(tracer.spans, "t")
    dump = store.dump_text()
    assert "ABCPK1234Q" not in dump and "RAVI" not in dump
    assert store.rows()[0]["attrs"] == {"kaagaz.rules.fired": ["TW-DOC-05"]}
    assert report.dropped["kaagaz.file.id: value does not fit the key"] == 1
    assert report.dropped["<unsafe key name>: not on the allowlist"] == 1
    assert report.dropped["event analyst_note: not on the allowlist"] == 1
    assert all("ABCPK1234Q" not in k for k in report.dropped)


def test_a_loose_validator_is_caught_by_the_scanner(monkeypatch: pytest.MonkeyPatch) -> None:
    from intake.validators import verhoeff_check_digit
    monkeypatch.setitem(redact.SCHEMA, "kaagaz.debug", lambda v: isinstance(v, str))   # someone loosens a key
    number = "23456789012" + verhoeff_check_digit("23456789012")                     # a valid-looking Aadhaar number
    tracer = Tracer("t")
    tracer.span("b" * 32, "route", "code", AT, **{"kaagaz.debug": f"Aadhaar number: {number} on page 4"})
    store = TraceStore()
    report = store.write(tracer.spans, "t")
    assert store.count() == (0, 0)
    assert report.quarantined["route"] == 1


def test_span_names_cannot_carry_a_file_number() -> None:
    tracer = Tracer("t")
    tracer.span("c" * 32, "loan_file GF-61070", "file", AT)
    store = TraceStore()
    assert store.write(tracer.spans, "t").quarantined["<span name not on the list>"] == 1
    assert store.count() == (0, 0)


def test_day16_journal_still_carries_no_identifier() -> None:
    d16 = sources.day16_summary()
    assert d16["pii_kinds"] == []
    from godavari_integration.journal import Journal
    from godavari_obs import paths
    j = Journal(paths.DAY16_DATA / "kaagaz" / "journal.sqlite")
    text = " ".join(str(r) for t in ("writes", "events") for r in j.conn.execute(f"SELECT * FROM {t}")).upper()
    j.conn.close()
    assert not set(re.findall(r"[A-Z]+", text)) & {s.upper() for s in SURNAMES}


def test_day18_correction_events_lose_their_values_at_the_boundary() -> None:
    d18 = sources.day18_events_at_the_boundary()
    assert d18["with_values"] > 0 and "pan" in d18["pii_kinds"]       # the events as written do carry values
    assert d18["dropped"]["model_value: not on the allowlist"] == d18["events"]
    assert d18["dropped"]["analyst_value: not on the allowlist"] == d18["events"]
