"""The canonical application record: Kaagaz's own shape, assembled from what Day 11's pipeline produced and
what the analyst approved. Nothing here knows a core field name; the mapping does that.

The canonical record uses plain types (ISO dates, ints, booleans, lower-case kinds) so that every source
(the core, the tracker, the reporting database, the extraction) can be translated into it and compared.
"""

from __future__ import annotations

import re
from datetime import date
from typing import Any

from .day11 import BRANCH_CODES, Doc, FileResult, LoanBundle, idempotency_key

CANONICAL_SCHEMA = "kaagaz-intake-canonical/1.0"
ADDRESS_LINE_MAX = 40


def dmy(value: str | None) -> date | None:
    if not value:
        return None
    m = re.fullmatch(r"(\d{2})-(\d{2})-(\d{4})", value.strip())
    return date(int(m.group(3)), int(m.group(2)), int(m.group(1))) if m else None


def whole_rupees(value: str | None) -> int | None:
    if not value:
        return None
    digits = value.replace(",", "").replace("Rs", "").strip()
    return int(digits) if digits.isdigit() else None


def split_address(address: str) -> dict[str, str | None]:
    """'47-18, KPHB Colony, Kukatpally, Hyderabad 500072' -> lines of at most 40 characters, city, PIN.
    No PIN at the end means no split: the field stays empty and the mapping fails closed."""
    m = re.fullmatch(r"(?P<rest>.+?),?\s+(?P<city>[A-Za-z ]+?)\s+(?P<pin>\d{6})", address.strip())
    if not m:
        return {"address_line1": None, "address_line2": None, "address_line3": None, "city": None, "pin": None}
    parts = [p.strip() for p in m.group("rest").split(",") if p.strip()]
    lines: list[str] = []
    for part in parts:
        if lines and len(lines[-1]) + 2 + len(part) <= ADDRESS_LINE_MAX:
            lines[-1] = f"{lines[-1]}, {part}"
        else:
            lines.append(part)
    if len(lines) > 3 or any(len(line) > ADDRESS_LINE_MAX for line in lines):
        return {"address_line1": None, "address_line2": None, "address_line3": None,
                "city": m.group("city").strip(), "pin": m.group("pin")}
    lines += [None] * (3 - len(lines))  # type: ignore[list-item]
    return {"address_line1": lines[0], "address_line2": lines[1], "address_line3": lines[2],
            "city": m.group("city").strip(), "pin": m.group("pin")}


def _doc_page_text(result: FileResult, bundle: LoanBundle, doc: Doc) -> str:
    out = result.output
    if out is None:
        return ""
    for claim in out.documents:
        if claim.doc == doc:
            page = bundle.page(claim.page)
            return page.text if page else ""
    return ""


def _doc_attrs(result: FileResult, doc: Doc) -> dict[str, str]:
    out = result.output
    for claim in (out.documents if out else ()):
        if claim.doc == doc:
            return dict(claim.attributes)
    return {}


def canonical_from_day11(result: FileResult, bundle: LoanBundle, approved: dict[str, str], *, approved_by: str,
                         state: str, entry_user: str, mapping_version: str) -> dict[str, Any]:
    """`approved` is what the analyst approved: Day 11's field names, Day 11's string formats."""
    income_text = _doc_page_text(result, bundle, Doc.INCOME_PROOF).lower()
    income_kind = ("salary slip" if "salary slip" in income_text else
                   "self-declaration" if "self-declaration" in income_text else None)
    employer = None
    if income_kind == "salary slip":
        m = re.search(r"Employer:\s*(.+)", _doc_page_text(result, bundle, Doc.INCOME_PROOF))
        employer = m.group(1).strip() if m else None
    consent_doc = Doc.CUSTOMER_DECLARATION if bundle.product == "two-wheeler" else Doc.KEY_FACT_STATEMENT
    present = {c.doc for c in (result.output.documents if result.output else ())}
    last4 = approved.get("aadhaar_last4")
    branch_code = BRANCH_CODES[bundle.branch]
    record: dict[str, Any] = {
        "file_number": bundle.file_id,
        "branch_code": branch_code,
        "product": bundle.product,
        "channel": bundle.channel,
        "application_date": dmy(approved.get("application_date")),
        "idempotency_key": idempotency_key(bundle.file_id, bundle.branch),
        "entry_user": entry_user,
        "approved_by": approved_by,
        "applicant_name": approved.get("applicant_name"),
        "date_of_birth": dmy(approved.get("date_of_birth")),
        "pan": approved.get("pan"),
        "aadhaar_masked": f"XXXXXXXX{last4}" if last4 and last4.isdigit() and len(last4) == 4 else None,
        "mobile": approved.get("mobile"),
        **split_address(approved.get("address") or ""),
        "state": state,
        "address_proof_kind": _doc_attrs(result, Doc.PROOF_OF_ADDRESS).get("kind"),
        "is_salaried": (income_kind == "salary slip") if bundle.product == "two-wheeler" else None,
        "employer_name": employer,
        "monthly_income": whole_rupees(approved.get("monthly_income")),
        "income_proof_kind": income_kind,
        "requested_amount": whole_rupees(approved.get("requested_amount")),
        "tenure_months": whole_rupees(approved.get("tenure_months")),
        "dealer_code": approved.get("dealer_code"),
        "on_road_price": whole_rupees(approved.get("on_road_price")),
        "quotation_date": dmy(approved.get("quotation_date")),
        "gold_gross_weight_g": approved.get("gross_weight_g"),
        "gold_net_weight_g": approved.get("net_weight_g"),
        "gold_purity_carat": whole_rupees(approved.get("purity_carat")),
        "appraisal_date": dmy(approved.get("appraisal_date")),
        "has_co_applicant": Doc.CO_APPLICANT_KYC in present,
        "kyc_status": "complete",
        "page_count": len(bundle.pages),
        "remarks": f"Kaagaz intake; mapping {mapping_version}",
        "consent_given": consent_doc in present,
    }
    return record
