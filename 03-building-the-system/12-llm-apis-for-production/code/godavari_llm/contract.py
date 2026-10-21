"""The extraction contract: what the model must return, written as Pydantic models.

Day 11 wrote this vocabulary as plain dataclasses (document types, a field with a confidence, a page and
a verbatim quote). Day 12 turns it into a versioned schema that does three jobs at once:

1. it is sent to the provider as a JSON schema, so constrained decoding can enforce the shape;
2. it validates every response locally, with constraints the provider's schema dialect cannot express;
3. it is the type the rest of the pipeline reads, so a field cannot be used before it is checked.

Bump SCHEMA_VERSION on any change. It is part of every idempotency key, so a new schema never reuses an
answer produced under the old one.
"""

from __future__ import annotations

import copy
import re
from enum import StrEnum
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

SCHEMA_VERSION = "godavari-extraction/1.0"
PAN_RE = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]$")


class Doc(StrEnum):
    """Page types, the same names as Day 11's catalogue (a subset: the ones the synthetic batch uses)."""

    APPLICATION_FORM = "application_form"
    PHOTOGRAPH = "photograph"
    PAN_CARD = "pan_card"
    PROOF_OF_IDENTITY = "proof_of_identity"
    PROOF_OF_ADDRESS = "proof_of_address"
    INCOME_PROOF = "income_proof"
    BANK_STATEMENT = "bank_statement"
    DEALER_QUOTATION = "dealer_quotation"
    CO_APPLICANT_KYC = "co_applicant_kyc"
    GOLD_APPRAISAL = "gold_appraisal"
    PLEDGE_FORM = "pledge_form"
    CUSTOMER_DECLARATION = "customer_declaration"
    KEY_FACT_STATEMENT = "key_fact_statement"
    UNKNOWN = "unknown"


class Strict(BaseModel):
    """Unknown keys are an error, not something to ignore: a model that invents a field is telling you
    the prompt and the schema disagree."""

    model_config = ConfigDict(extra="forbid")


Confidence = Annotated[float, Field(ge=0.0, le=1.0, description="0 to 1, the model's own estimate")]
Evidence = Annotated[str, Field(max_length=200, description="text copied exactly from the page; empty if no value")]


class TextField(Strict):
    value: str | None = Field(description="the value as printed on the page; null means unsure or not on this page")
    confidence: Confidence
    evidence: Evidence


class AmountField(Strict):
    value: Annotated[int, Field(ge=1)] | None = Field(description="whole rupees, digits only; null if not on this page")
    confidence: Confidence
    evidence: Evidence


class PageClassification(Strict):
    """Stage 1, on the small model and a low-resolution thumbnail."""

    page_type: Doc
    confidence: Confidence


class PageExtraction(Strict):
    """Stage 2, on the large model and the full-resolution page. One per extracted page."""

    page_type: Doc
    applicant_name: TextField
    applicant_pan: TextField
    co_applicant_name: TextField
    product: TextField
    requested_amount: AmountField
    monthly_income: AmountField

    @field_validator("applicant_pan")
    @classmethod
    def pan_shape(cls, v: TextField) -> TextField:
        # The shape check belongs in the schema; whether the PAN matches the applicant is Day 11's rule.
        if v.value is not None and not PAN_RE.fullmatch(v.value):
            raise ValueError(f"PAN {v.value!r} is not five letters, four digits, one letter")
        return v


# --- The file-level result, assembled by code from the page results (never by the model) ---------------

class FieldResult(Strict):
    value: str | int | None
    confidence: float
    page: int | None
    evidence: str
    flags: list[str] = []


class IncomeEvidence(Strict):
    doc: Doc
    page: int
    monthly_income: int | None
    confidence: float


class DocumentPresent(Strict):
    doc: Doc
    pages: list[int]
    confidence: float


class LoanFileExtraction(Strict):
    """The extraction contract for one Godavari loan file: every field with a confidence and a page."""

    schema_version: str = SCHEMA_VERSION
    file_id: str
    applicant_name: FieldResult
    applicant_pan: FieldResult
    co_applicant_name: FieldResult
    product: FieldResult
    requested_amount: FieldResult
    income_evidence: list[IncomeEvidence]
    documents_present: list[DocumentPresent]
    needs_review: bool
    review_reasons: list[str]


# --- From a Pydantic model to a schema a provider will accept -------------------------------------------

# Keywords that strict structured-output dialects reject or ignore (as of October 2026 the Anthropic
# documentation lists minimum, maximum, multipleOf, minLength and maxLength as unsupported; OpenAI's strict
# mode has its own list). We keep them for local validation and move them into the description so the model
# still reads them.
_UNSUPPORTED = ("minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum", "multipleOf", "minLength", "maxLength")


def provider_schema(model: type[BaseModel]) -> dict[str, Any]:
    """Return the JSON schema to send: every property required, no extra keys, unsupported limits moved to
    the description, titles dropped. Local validation still uses the full Pydantic model."""

    schema = copy.deepcopy(model.model_json_schema())

    def walk(node: Any) -> None:
        """`node` is always a schema, never a map of names to schemas (so a field called "title" survives)."""
        if not isinstance(node, dict):
            return
        moved = [f"{k} {node.pop(k)}" for k in _UNSUPPORTED if k in node]
        if moved:
            note = "(" + ", ".join(moved) + ")"
            node["description"] = f"{node.get('description', '')} {note}".strip()
        node.pop("title", None)
        node.pop("default", None)
        for key in ("properties", "$defs"):
            for child in node.get(key, {}).values():
                walk(child)
        if "properties" in node:
            node["additionalProperties"] = False
            node["required"] = list(node["properties"].keys())
        for key in ("anyOf", "allOf", "oneOf"):
            for child in node.get(key, []):
                walk(child)
        walk(node.get("items"))

    walk(schema)
    return schema
