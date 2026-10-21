"""Deterministic checks that run after the model: formats, parsing, cross-field consistency, grounding.

Every function here is pure: same input, same answer, every time. That is the whole point. None of them
calls a model, reads the clock or touches the network.
"""

from __future__ import annotations

import re
from datetime import date, datetime

from .catalogue import PAGE_TITLES, DocFinding, LoanBundle

# --- PAN -----------------------------------------------------------------------------------------------
# Ten characters: five letters, four digits, one letter. The fourth letter is the holder type
# ("P" for an individual); for an individual the fifth is the first letter of the surname.
PAN_RE = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]$")


def pan_format_errors(pan: str | None) -> list[str]:
    if pan is None:
        return ["PAN is missing or unsure"]
    errors: list[str] = []
    if not PAN_RE.fullmatch(pan):
        errors.append(f"PAN {pan!r} is not five letters, four digits, one letter")
        return errors
    if pan[3] != "P":
        errors.append(f"PAN {pan!r} is not an individual's PAN (fourth letter {pan[3]!r}, expected 'P')")
    return errors


def pan_matches_surname(pan: str, applicant_name: str) -> bool:
    """For an individual, the fifth character of the PAN is the first letter of the surname."""
    parts = normalise_name(applicant_name).split()
    return bool(parts) and len(pan) == 10 and pan[4] == parts[-1][0]


# --- Aadhaar -------------------------------------------------------------------------------------------
# Aadhaar numbers are 12 digits with a Verhoeff check digit. A copy held by a lender must be masked so
# that only the last four digits are visible.
_VERHOEFF_D = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 2, 3, 4, 0, 6, 7, 8, 9, 5], [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
    [3, 4, 0, 1, 2, 8, 9, 5, 6, 7], [4, 0, 1, 2, 3, 9, 5, 6, 7, 8], [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
    [6, 5, 9, 8, 7, 1, 0, 4, 3, 2], [7, 6, 5, 9, 8, 2, 1, 0, 4, 3], [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
    [9, 8, 7, 6, 5, 4, 3, 2, 1, 0],
]
_VERHOEFF_P = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 5, 7, 6, 2, 8, 3, 0, 9, 4], [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
    [8, 9, 1, 6, 0, 4, 3, 5, 2, 7], [9, 4, 5, 3, 1, 2, 6, 8, 7, 0], [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
    [2, 7, 9, 3, 8, 0, 6, 4, 1, 5], [7, 0, 4, 6, 9, 1, 3, 2, 5, 8],
]
_VERHOEFF_INV = [0, 4, 3, 2, 1, 5, 6, 7, 8, 9]


def verhoeff_valid(number: str) -> bool:
    if not number.isdigit():
        return False
    check = 0
    for i, ch in enumerate(reversed(number)):
        check = _VERHOEFF_D[check][_VERHOEFF_P[i % 8][int(ch)]]
    return check == 0


def verhoeff_check_digit(stem: str) -> str:
    check = 0
    for i, ch in enumerate(reversed(stem)):
        check = _VERHOEFF_D[check][_VERHOEFF_P[(i + 1) % 8][int(ch)]]
    return str(_VERHOEFF_INV[check])


_TWELVE_DIGITS_RE = re.compile(r"(?<!\d)(\d{4})[ -]?(\d{4})[ -]?(\d{4})(?!\d)")


def find_unmasked_aadhaar(text: str) -> list[str]:
    """Every 12-digit, Verhoeff-valid number in the text. A masked copy shows 'XXXX XXXX 1234' and has none."""
    found: list[str] = []
    for m in _TWELVE_DIGITS_RE.finditer(text):
        number = "".join(m.groups())
        if number[0] not in "01" and verhoeff_valid(number):
            found.append(number)
    return found


# --- Money, dates, names -------------------------------------------------------------------------------
_AMOUNT_RE = re.compile(r"^(?:Rs\.?|INR|₹)?\s*([0-9][0-9,]*)(?:\.(\d{1,2}))?$")


def parse_amount(text: str | None) -> int | None:
    """'Rs 1,25,000' -> 125000. Indian digit grouping is allowed; paise are dropped. None if unparseable."""
    if text is None:
        return None
    m = _AMOUNT_RE.fullmatch(text.strip())
    if not m:
        return None
    return int(m.group(1).replace(",", ""))


def parse_date(text: str | None) -> date | None:
    """Godavari's forms write dd-mm-yyyy. Anything else is unparseable, not guessed."""
    if text is None:
        return None
    try:
        return datetime.strptime(text.strip(), "%d-%m-%Y").date()
    except ValueError:
        return None


def parse_float(text: str | None) -> float | None:
    if text is None:
        return None
    try:
        return float(text.strip())
    except ValueError:
        return None


def normalise_name(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z ]", " ", name).upper()
    return " ".join(cleaned.split())


def names_match(a: str | None, b: str | None) -> bool:
    """Same tokens in any order; an initial matches a full token ('P. RAVI KUMAR' ~ 'RAVI KUMAR PASUPULETI')."""
    if not a or not b:
        return False
    ta, tb = normalise_name(a).split(), normalise_name(b).split()
    if not ta or not tb:
        return False
    short, long_ = (ta, tb) if len(ta) <= len(tb) else (tb, ta)
    remaining = list(long_)
    for tok in short:
        hit = next((r for r in remaining if r == tok or (len(tok) == 1 and r.startswith(tok))
                    or (len(r) == 1 and tok.startswith(r))), None)
        if hit is None:
            return False
        remaining.remove(hit)
    return True


def within_tolerance(a: int, b: int, tolerance: float) -> bool:
    """|a - b| <= tolerance * max(a, b), in integer arithmetic on rupees."""
    return abs(a - b) * 100 <= int(tolerance * 100) * max(a, b)


# --- Grounding: did the model read what it says it read? ------------------------------------------------
def grounding_errors(bundle: LoanBundle, finding: DocFinding) -> list[str]:
    """A claim is grounded if the cited page exists, the quote is on it verbatim, and the page's printed
    title is the claimed document's title. The model can be confident and wrong; this check cannot."""
    page = bundle.page(finding.page)
    if page is None:
        return [f"{finding.doc} cites page {finding.page}, which is not in the file"]
    errors: list[str] = []
    if finding.evidence and finding.evidence not in page.text:
        errors.append(f"{finding.doc} quote not found on page {finding.page}")
    title = PAGE_TITLES.get(finding.doc)
    first_line = page.text.splitlines()[0] if page.text else ""
    if title and title not in first_line:
        errors.append(f"page {finding.page} is titled {first_line[:40]!r}, not {finding.doc}")
    return errors


def evidence_on_page(bundle: LoanBundle, page_no: int | None, evidence: str) -> bool:
    if page_no is None or not evidence:
        return False
    page = bundle.page(page_no)
    return page is not None and evidence in page.text
