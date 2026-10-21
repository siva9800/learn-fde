from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest

from intake import rules_gold, rules_two_wheeler
from intake.ruleset import Action, Finding, Kind, OverrideLog, RuleSet, SignoffError, check_signoff


def test_current_rules_match_their_record_in_prototype_mode() -> None:
    assert check_signoff(rules_two_wheeler.RULESET, "prototype").fingerprint_ok
    assert check_signoff(rules_gold.RULESET, "prototype").fingerprint_ok


def test_pilot_mode_refuses_rules_that_are_not_signed() -> None:
    with pytest.raises(SignoffError, match="signed rules only"):
        check_signoff(rules_two_wheeler.RULESET, "pilot")


def test_a_one_character_change_to_a_rule_breaks_the_fingerprint(tmp_path: Path) -> None:
    original = tmp_path / "rules_x.py"
    original.write_bytes(b"MAX_FINANCE_PERCENT = 90\n")
    rs = RuleSet("x", "1", (), (original,))
    before = rs.fingerprint()
    original.write_bytes(b"MAX_FINANCE_PERCENT = 95\n")
    assert rs.fingerprint() != before


def test_line_endings_do_not_change_the_fingerprint(tmp_path: Path) -> None:
    lf, crlf = tmp_path / "a" / "rules_x.py", tmp_path / "b" / "rules_x.py"
    lf.parent.mkdir()
    crlf.parent.mkdir()
    lf.write_bytes(b"A = 1\nB = 2\n")
    crlf.write_bytes(b"A = 1\r\nB = 2\r\n")
    assert RuleSet("x", "1", (), (lf,)).fingerprint() == RuleSet("x", "1", (), (crlf,)).fingerprint()


def test_rules_changed_after_review_refuse_to_run_in_any_mode(tmp_path: Path) -> None:
    record = json.loads(Path(rules_two_wheeler.__file__).with_name("rules_signoff.json").read_text(encoding="utf-8"))
    record["two-wheeler"]["fingerprint"] = "0" * 64
    fake = tmp_path / "signoff.json"
    fake.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(SignoffError, match="changed since"):
        check_signoff(rules_two_wheeler.RULESET, "prototype", fake)


def test_policy_override_is_logged_with_its_reason() -> None:
    log = OverrideLog()
    f = Finding("TW-AMT-MARGIN", Kind.POLICY, Action.REVIEW, "over 90 percent")
    log.override(f, "GF-AN-1142", "customer paid margin in cash, receipt on page 31", datetime(2026, 11, 9, 11, 0))
    assert log.entries[0]["rule_id"] == "TW-AMT-MARGIN" and log.entries[0]["analyst_id"] == "GF-AN-1142"


def test_regulatory_rules_cannot_be_overridden_by_anyone() -> None:
    f = Finding("GL-LTV", Kind.REGULATORY, Action.BLOCK, "over the cap")
    with pytest.raises(PermissionError):
        OverrideLog().override(f, "GF-AN-0001", "the branch manager approved it verbally", datetime(2026, 11, 9))


def test_an_override_needs_a_reason_not_a_label() -> None:
    f = Finding("TW-TENURE", Kind.POLICY, Action.REVIEW, "tenure 60")
    with pytest.raises(ValueError):
        OverrideLog().override(f, "GF-AN-1142", "ok", datetime(2026, 11, 9))
