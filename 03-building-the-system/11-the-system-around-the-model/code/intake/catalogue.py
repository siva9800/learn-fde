"""The shared vocabulary of the intake system: document types, pages, bundles and what a model returns.

Nothing in this module decides anything. It is the contract that the model side and the code side both
speak, so that a model can be swapped (stub, real LLM, self-hosted) without touching a rule.
Day 12 turns this into a versioned JSON schema for structured outputs; here it is plain dataclasses.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class Doc(StrEnum):
    """Every document type the two products can need. Which ones are *required* lives in the signed rules."""

    APPLICATION_FORM = "application_form"
    PHOTOGRAPH = "photograph"
    PAN_CARD = "pan_card"
    PROOF_OF_IDENTITY = "proof_of_identity"
    PROOF_OF_ADDRESS = "proof_of_address"
    INCOME_PROOF = "income_proof"
    BANK_STATEMENT = "bank_statement"
    DEALER_QUOTATION = "dealer_quotation"
    NACH_MANDATE = "nach_mandate"
    CANCELLED_CHEQUE = "cancelled_cheque"
    INSURANCE_PROPOSAL = "insurance_proposal"
    CUSTOMER_DECLARATION = "customer_declaration"
    FIELD_VERIFICATION = "field_verification"
    CO_APPLICANT_KYC = "co_applicant_kyc"
    GOLD_APPRAISAL = "gold_appraisal"
    PLEDGE_FORM = "pledge_form"
    OWNERSHIP_DECLARATION = "ownership_declaration"
    KEY_FACT_STATEMENT = "key_fact_statement"
    UNKNOWN = "unknown"


# The printed title at the top of each page type. The synthetic generator writes these; a real scan has
# them too, often stamped over or cut off, which is why classification is a model's job and not a regex.
PAGE_TITLES: dict[Doc, str] = {
    Doc.APPLICATION_FORM: "LOAN APPLICATION FORM",
    Doc.PHOTOGRAPH: "APPLICANT PHOTOGRAPH",
    Doc.PAN_CARD: "INCOME TAX DEPARTMENT - PERMANENT ACCOUNT NUMBER CARD",
    Doc.PROOF_OF_IDENTITY: "PROOF OF IDENTITY",
    Doc.PROOF_OF_ADDRESS: "PROOF OF ADDRESS",
    Doc.INCOME_PROOF: "INCOME PROOF",
    Doc.BANK_STATEMENT: "STATEMENT OF ACCOUNT",
    Doc.DEALER_QUOTATION: "DEALER QUOTATION / PROFORMA INVOICE",
    Doc.NACH_MANDATE: "NACH DEBIT MANDATE",
    Doc.CANCELLED_CHEQUE: "CANCELLED CHEQUE",
    Doc.INSURANCE_PROPOSAL: "VEHICLE INSURANCE PROPOSAL",
    Doc.CUSTOMER_DECLARATION: "CUSTOMER DECLARATION AND CONSENT",
    Doc.FIELD_VERIFICATION: "RESIDENCE FIELD VERIFICATION REPORT",
    Doc.CO_APPLICANT_KYC: "CO-APPLICANT KYC",
    Doc.GOLD_APPRAISAL: "GOLD APPRAISAL CERTIFICATE",
    Doc.PLEDGE_FORM: "PLEDGE FORM - LIST OF ORNAMENTS",
    Doc.OWNERSHIP_DECLARATION: "DECLARATION OF OWNERSHIP OF GOLD",
    Doc.KEY_FACT_STATEMENT: "KEY FACT STATEMENT - ACKNOWLEDGEMENT",
}


@dataclass(frozen=True)
class Page:
    number: int
    text: str
    handwritten: bool = False
    telugu: bool = False


@dataclass(frozen=True)
class LoanBundle:
    """What arrives from the branch: one scanned file, pages in whatever order they were in the tray."""

    file_id: str
    branch: str
    product: str          # "two-wheeler" or "gold"
    channel: str          # sftp_scan, phone_photo, mixed (from Day 7's sample)
    pages: tuple[Page, ...]

    def page(self, number: int) -> Page | None:
        for p in self.pages:
            if p.number == number:
                return p
        return None


@dataclass(frozen=True)
class FieldValue:
    """One extracted field. `value` is None when the model says "unsure": a first-class answer, not an error."""

    value: str | None
    confidence: float
    page: int | None
    evidence: str = ""    # the exact text on `page` the value was read from


@dataclass(frozen=True)
class DocFinding:
    """The model's claim that a document is in the bundle, with the page and a quote to check it against."""

    doc: Doc
    page: int
    confidence: float
    evidence: str                         # must appear verbatim on the cited page (checked in code)
    attributes: dict[str, str] = field(default_factory=dict)   # e.g. address-proof kind, holder, dates


@dataclass(frozen=True)
class PromptOnlyVerdict:
    """What the same model says when the prompt also asks it to *decide* completeness and compliance.

    The pipeline never uses this to route a file. It exists so the run can show, file by file, what a
    system that left the rules in the prompt would have shipped.
    """

    complete: bool
    issues: tuple[str, ...]
    eligible_amount: int | None = None    # the model's own arithmetic, for gold


@dataclass(frozen=True)
class ModelOutput:
    model_name: str
    page_labels: dict[int, tuple[Doc, float]]          # page number -> (type, confidence)
    fields: dict[str, FieldValue]
    documents: tuple[DocFinding, ...]
    salary_account_page: int | None                    # the model's pick among the bank statements
    prompt_only: PromptOnlyVerdict
