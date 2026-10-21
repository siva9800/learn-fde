from __future__ import annotations

import pytest

from intake.catalogue import PAGE_TITLES, Doc, DocFinding, LoanBundle, Page
from intake.validators import (find_unmasked_aadhaar, grounding_errors, names_match, pan_format_errors,
                               pan_matches_surname, parse_amount, parse_date, verhoeff_check_digit, verhoeff_valid,
                               within_tolerance)


@pytest.mark.parametrize("pan, ok", [("ABCPP1234K", True), ("ABCPP12E4K", False), ("ABCP1234K", False),
                                     ("abcpp1234k", False), ("ABCFP1234K", False), (" ABCPP1234K", False)])
def test_pan_format(pan: str, ok: bool) -> None:
    assert (pan_format_errors(pan) == []) is ok


def test_pan_none_is_an_error_not_a_crash() -> None:
    assert pan_format_errors(None) == ["PAN is missing or unsure"]


def test_pan_fifth_letter_is_the_surname_initial() -> None:
    assert pan_matches_surname("ABCPP1234K", "RAVI TEJA PASUPULETI")
    assert not pan_matches_surname("ABCPK1234K", "RAVI TEJA PASUPULETI")


def test_verhoeff_round_trip_and_single_digit_errors() -> None:
    stem = "23456789012"
    number = stem + verhoeff_check_digit(stem)
    assert verhoeff_valid(number)
    for i in range(12):                       # Verhoeff catches every single-digit substitution
        wrong = number[:i] + str((int(number[i]) + 1) % 10) + number[i + 1:]
        assert not verhoeff_valid(wrong)


def test_masked_aadhaar_is_not_flagged_and_unmasked_is() -> None:
    stem = "34567890123"
    number = stem + verhoeff_check_digit(stem)
    assert find_unmasked_aadhaar("Aadhaar number: XXXX XXXX 4821") == []
    spaced = f"Aadhaar number: {number[:4]} {number[4:8]} {number[8:]}"
    assert find_unmasked_aadhaar(spaced) == [number]


def test_a_twelve_digit_account_number_is_not_mistaken_for_aadhaar_unless_checksum_valid() -> None:
    stem = "45678901234"
    bad = stem + str((int(verhoeff_check_digit(stem)) + 1) % 10)
    assert find_unmasked_aadhaar(f"Account 0{bad[1:]}") == []
    assert find_unmasked_aadhaar(bad) == []


@pytest.mark.parametrize("text, value", [("Rs 1,25,000", 125000), ("125000", 125000), ("INR 90,000.50", 90000),
                                         ("₹ 3,00,000", 300000), ("12.5 lakh", None), ("", None), (None, None)])
def test_parse_amount(text: str | None, value: int | None) -> None:
    assert parse_amount(text) == value


def test_parse_date_is_strict() -> None:
    assert parse_date("02-11-2026") is not None
    assert parse_date("2026-11-02") is None          # not guessed
    assert parse_date("31-02-2026") is None
    assert parse_date("O2-11-2026") is None          # an OCR letter O


def test_names_match_handles_order_and_initials() -> None:
    assert names_match("P. RAVI TEJA", "RAVI TEJA PASUPULETI")
    assert names_match("PASUPULETI RAVI TEJA", "RAVI TEJA PASUPULETI")
    assert not names_match("RAAVI TEJA PASUPULETI", "RAVI TEJA PASUPULETI")
    assert not names_match("", "RAVI")


def test_within_tolerance_is_integer_and_symmetric() -> None:
    assert within_tolerance(100_000, 85_000, 0.15)
    assert not within_tolerance(100_000, 84_999, 0.15)
    assert within_tolerance(85_000, 100_000, 0.15)


def _bundle() -> LoanBundle:
    return LoanBundle("GF-T", "Guntur", "gold", "sftp_scan", (
        Page(1, PAGE_TITLES[Doc.PAN_CARD] + "\nName: X"), Page(2, "THIS PAGE IS INTENTIONALLY LEFT BLANK")))


def test_grounding_accepts_a_real_quote() -> None:
    claim = DocFinding(Doc.PAN_CARD, 1, 0.9, PAGE_TITLES[Doc.PAN_CARD])
    assert grounding_errors(_bundle(), claim) == []


def test_grounding_rejects_a_quote_that_is_not_on_the_page() -> None:
    claim = DocFinding(Doc.PROOF_OF_ADDRESS, 2, 0.95, PAGE_TITLES[Doc.PROOF_OF_ADDRESS])
    errors = grounding_errors(_bundle(), claim)
    assert any("quote not found" in e for e in errors)
    assert any("not proof_of_address" in e for e in errors)


def test_grounding_rejects_a_page_that_does_not_exist() -> None:
    assert grounding_errors(_bundle(), DocFinding(Doc.PAN_CARD, 9, 0.99, "x"))
