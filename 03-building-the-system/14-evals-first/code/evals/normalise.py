"""The registered normaliser: what counts as "the same value" when comparing a field to its label.

This is part of the metric definition (Day 9, section C: "equals what the eval owners would have typed").
Changing it changes every accuracy number, so it changes only with the same signatures as the definition.
It forgives format (Rs and commas, slashes in dates, case and spacing); it never forgives content (a
transliteration variant, a stray zero, one wrong PAN character).
"""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

FIELD_KIND: dict[str, str] = {
    "applicant_name": "name", "co_applicant_name": "name", "pan": "id", "dealer_code": "id",
    "date_of_birth": "date", "application_date": "date", "quotation_date": "date", "appraisal_date": "date",
    "requested_amount": "amount", "monthly_income": "amount", "on_road_price": "amount",
    "tenure_months": "integer", "purity_carat": "integer", "mobile": "mobile",
    "gross_weight_g": "weight", "net_weight_g": "weight", "address": "address",
}


def normalise(field_name: str, value: str | None) -> str | None:
    """The canonical form of a value for comparison, or None for "not in the file"."""
    if value is None:
        return None
    text = value.strip()
    if text == "":
        return None
    kind = FIELD_KIND.get(field_name, "text")
    if kind == "name":
        return " ".join(re.sub(r"[.,]", " ", text).upper().split())
    if kind == "id":
        return re.sub(r"\s+", "", text).upper()
    if kind == "date":
        m = re.fullmatch(r"(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})", text)
        return f"{int(m.group(1)):02d}-{int(m.group(2)):02d}-{m.group(3)}" if m else text
    if kind == "amount":
        digits = re.sub(r"(?i)^rs\.?\s*", "", text).replace(",", "").replace(" ", "")
        return digits.split(".")[0] if re.fullmatch(r"\d+(\.\d+)?", digits) else text
    if kind == "integer":
        return str(int(text)) if text.isdigit() else text
    if kind == "mobile":
        digits = re.sub(r"\D", "", text)
        return digits[-10:] if len(digits) >= 10 else digits
    if kind == "weight":
        try:
            return str(Decimal(text).quantize(Decimal("0.1")))
        except InvalidOperation:
            return text
    if kind == "address":
        return " ".join(re.sub(r"\s*,\s*", ", ", text).upper().split())
    return " ".join(text.split())


def exact_equal(a: str | None, b: str | None) -> bool:
    return a == b


def norm_equal(field_name: str, a: str | None, b: str | None) -> bool:
    return normalise(field_name, a) == normalise(field_name, b)
