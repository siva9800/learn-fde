"""Two-wheeler loan: the completeness checklist and the product rules, as code the compliance head signs.

Version 0.3, reviewed in draft with the compliance head on Friday 6 November 2026. Signature due at
milestone M10 (Wednesday 2 December 2026). Every limit below is Godavari policy and is synthetic.
To print the sheet she reads: python -X utf8 code/print_rules.py
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from . import rules_kyc
from .catalogue import Doc
from .ruleset import Action, Finding, Kind, Rule, RuleContext, RuleSet, missing_document
from .validators import parse_amount, parse_date

PRODUCT = "two-wheeler"
VERSION = "0.3"

# The fourteen documents (Day 6: "Fourteen for two-wheeler"). The co-applicant's KYC is the fourteenth
# and is required only when the application names a co-applicant.
REQUIRED_DOCS: tuple[tuple[str, Doc, Kind, str], ...] = (
    ("TW-DOC-01", Doc.APPLICATION_FORM, Kind.POLICY, "Loan application form, signed by the applicant"),
    ("TW-DOC-02", Doc.PHOTOGRAPH, Kind.REGULATORY, "Recent photograph of the applicant"),
    ("TW-DOC-03", Doc.PAN_CARD, Kind.REGULATORY, "PAN card (or Form 60)"),
    ("TW-DOC-04", Doc.PROOF_OF_IDENTITY, Kind.REGULATORY, "Proof of identity: an officially valid document"),
    ("TW-DOC-05", Doc.PROOF_OF_ADDRESS, Kind.REGULATORY, "Proof of address: an OVD or a signed alternative"),
    ("TW-DOC-06", Doc.INCOME_PROOF, Kind.POLICY, "Income proof: salary slip, ITR or income declaration"),
    ("TW-DOC-07", Doc.BANK_STATEMENT, Kind.POLICY, "Bank statement of the salary or main account, 3 months"),
    ("TW-DOC-08", Doc.DEALER_QUOTATION, Kind.POLICY, "Dealer quotation or proforma invoice"),
    ("TW-DOC-09", Doc.NACH_MANDATE, Kind.POLICY, "NACH debit mandate, signed"),
    ("TW-DOC-10", Doc.CANCELLED_CHEQUE, Kind.POLICY, "Cancelled cheque of the repayment account"),
    ("TW-DOC-11", Doc.INSURANCE_PROPOSAL, Kind.POLICY, "Vehicle insurance proposal"),
    ("TW-DOC-12", Doc.CUSTOMER_DECLARATION, Kind.POLICY, "Customer declaration and consent, signed"),
    ("TW-DOC-13", Doc.FIELD_VERIFICATION, Kind.POLICY, "Residence field verification report"),
)
CO_APPLICANT_RULE = ("TW-DOC-14", Doc.CO_APPLICANT_KYC, Kind.REGULATORY, "Co-applicant KYC, when a co-applicant is named")

MIN_AMOUNT, MAX_AMOUNT = 20_000, 300_000      # rupees
MAX_FINANCE_PERCENT = 90                      # of the on-road price; the customer brings at least 10 percent
MIN_TENURE, MAX_TENURE = 12, 48               # months
MIN_AGE, MAX_AGE = 21, 60                     # years, on the application date
QUOTATION_MAX_AGE_DAYS = 30
STATEMENT_MAX_GAP_DAYS = 30                   # statement must end within 30 days before the application
STATEMENT_MIN_SPAN_DAYS = 85                  # and cover about three months


def _doc_rule(rule_id: str, doc: Doc, kind: Kind, text: str) -> Rule:
    return Rule(rule_id, kind, f"In the file of record: {text}.", "Godavari two-wheeler checklist v0.3",
                lambda ctx: missing_document(rule_id, doc, text, ctx, kind))


def co_applicant_kyc(ctx: RuleContext) -> list[Finding]:
    rule_id, doc, kind, text = CO_APPLICANT_RULE
    if not ctx.value("co_applicant_name"):
        return []
    return missing_document(rule_id, doc, text, ctx, kind)


def amount_in_range(ctx: RuleContext) -> list[Finding]:
    amount = parse_amount(ctx.value("requested_amount"))
    if amount is None:
        return [Finding("TW-AMT-RANGE", Kind.POLICY, Action.REVIEW, "requested amount unreadable",
                        field_name="requested_amount")]
    if not MIN_AMOUNT <= amount <= MAX_AMOUNT:
        return [Finding("TW-AMT-RANGE", Kind.POLICY, Action.REVIEW,
                        f"requested Rs {amount:,} is outside Rs {MIN_AMOUNT:,} to Rs {MAX_AMOUNT:,}",
                        field_name="requested_amount")]
    return []


def amount_within_margin(ctx: RuleContext) -> list[Finding]:
    amount = parse_amount(ctx.value("requested_amount"))
    price = parse_amount(ctx.value("on_road_price"))
    if amount is None or price is None:
        return [Finding("TW-AMT-MARGIN", Kind.POLICY, Action.REVIEW,
                        "amount or on-road price unreadable; the margin rule cannot be checked",
                        field_name="requested_amount")]
    if amount * 100 > price * MAX_FINANCE_PERCENT:            # integer rupees, no floating point
        return [Finding("TW-AMT-MARGIN", Kind.POLICY, Action.REVIEW,
                        f"requested Rs {amount:,} is {amount * 100 / price:.1f} percent of the on-road price "
                        f"Rs {price:,}; the limit is {MAX_FINANCE_PERCENT} percent", field_name="requested_amount")]
    return []


def tenure_in_range(ctx: RuleContext) -> list[Finding]:
    raw = ctx.value("tenure_months")
    if raw is None or not raw.isdigit():
        return [Finding("TW-TENURE", Kind.POLICY, Action.REVIEW, "tenure unreadable", field_name="tenure_months")]
    if not MIN_TENURE <= int(raw) <= MAX_TENURE:
        return [Finding("TW-TENURE", Kind.POLICY, Action.REVIEW,
                        f"tenure {raw} months is outside {MIN_TENURE} to {MAX_TENURE}", field_name="tenure_months")]
    return []


def age_on_application(born: date, applied: date) -> int:
    return applied.year - born.year - ((applied.month, applied.day) < (born.month, born.day))


def applicant_age(ctx: RuleContext) -> list[Finding]:
    born, applied = parse_date(ctx.value("date_of_birth")), parse_date(ctx.value("application_date"))
    if born is None or applied is None:
        return [Finding("TW-AGE", Kind.POLICY, Action.REVIEW, "date of birth or application date unreadable",
                        field_name="date_of_birth")]
    age = age_on_application(born, applied)
    if not MIN_AGE <= age <= MAX_AGE:
        return [Finding("TW-AGE", Kind.POLICY, Action.REVIEW, f"applicant is {age} on the application date; "
                        f"the product is for {MIN_AGE} to {MAX_AGE}", field_name="date_of_birth")]
    return []


def quotation_dates(ctx: RuleContext) -> list[Finding]:
    quoted, applied = parse_date(ctx.value("quotation_date")), parse_date(ctx.value("application_date"))
    if quoted is None or applied is None:
        return [Finding("TW-DATE-QUOTE", Kind.POLICY, Action.REVIEW, "quotation or application date unreadable",
                        field_name="quotation_date")]
    gap = (applied - quoted).days
    if gap < 0 or gap > QUOTATION_MAX_AGE_DAYS:
        return [Finding("TW-DATE-QUOTE", Kind.POLICY, Action.SEND_BACK,
                        f"dealer quotation is dated {gap} days before the application; it must be 0 to "
                        f"{QUOTATION_MAX_AGE_DAYS}", doc=Doc.DEALER_QUOTATION)]
    return []


def statement_recent(ctx: RuleContext) -> list[Finding]:
    found = ctx.documents.get(Doc.BANK_STATEMENT)
    if found is None:
        return []
    start, end = parse_date(found.attributes.get("period_start")), parse_date(found.attributes.get("period_end"))
    applied = parse_date(ctx.value("application_date"))
    if start is None or end is None or applied is None:
        return [Finding("TW-BANK-AGE", Kind.POLICY, Action.REVIEW, "statement period unreadable",
                        doc=Doc.BANK_STATEMENT)]
    if (applied - end).days > STATEMENT_MAX_GAP_DAYS:
        return [Finding("TW-BANK-AGE", Kind.POLICY, Action.SEND_BACK,
                        f"bank statement ends {(applied - end).days} days before the application; "
                        f"it must end within {STATEMENT_MAX_GAP_DAYS}", doc=Doc.BANK_STATEMENT)]
    if (end - start).days < STATEMENT_MIN_SPAN_DAYS:
        return [Finding("TW-BANK-AGE", Kind.POLICY, Action.SEND_BACK,
                        "bank statement covers less than three months", doc=Doc.BANK_STATEMENT)]
    return []


RULES: tuple[Rule, ...] = (
    *(_doc_rule(*row) for row in REQUIRED_DOCS),
    Rule(CO_APPLICANT_RULE[0], Kind.REGULATORY, "Co-applicant KYC must be in the file when a co-applicant is named.",
         "RBI KYC Master Direction; Godavari checklist v0.3", co_applicant_kyc),
    Rule("TW-ADDR-LIST", Kind.REGULATORY, "Proof of address is an OVD, or an alternative on the signed list, "
         "in the applicant's own name.", "RBI KYC Master Direction; Godavari alternatives list v0.3",
         lambda ctx: rules_kyc.address_proof_acceptable(ctx, "TW-ADDR-LIST")),
    Rule("TW-ADDR-AGE", Kind.REGULATORY, "A utility bill used as address proof is at most 60 days old.",
         "Godavari alternatives list v0.3", lambda ctx: rules_kyc.address_proof_fresh(ctx, "TW-ADDR-AGE")),
    Rule("TW-KYC-MASK", Kind.REGULATORY, "No page shows an unmasked Aadhaar number.",
         "Aadhaar masking requirement; compliance circular", lambda ctx: rules_kyc.aadhaar_masked(ctx, "TW-KYC-MASK")),
    Rule("TW-AMT-RANGE", Kind.POLICY, f"Amount is Rs {MIN_AMOUNT:,} to Rs {MAX_AMOUNT:,}.",
         "Godavari product note", amount_in_range),
    Rule("TW-AMT-MARGIN", Kind.POLICY, f"Amount is at most {MAX_FINANCE_PERCENT} percent of the on-road price.",
         "Godavari product note", amount_within_margin),
    Rule("TW-TENURE", Kind.POLICY, f"Tenure is {MIN_TENURE} to {MAX_TENURE} months.", "Godavari product note",
         tenure_in_range),
    Rule("TW-AGE", Kind.POLICY, f"Applicant is {MIN_AGE} to {MAX_AGE} on the application date.",
         "Godavari product note", applicant_age),
    Rule("TW-DATE-QUOTE", Kind.POLICY, f"Dealer quotation is dated 0 to {QUOTATION_MAX_AGE_DAYS} days before the "
         "application.", "Godavari product note", quotation_dates),
    Rule("TW-BANK-AGE", Kind.POLICY, "Bank statement ends within 30 days before the application and covers "
         "three months.", "Godavari product note", statement_recent),
)

_HERE = Path(__file__).resolve().parent
RULESET = RuleSet(PRODUCT, VERSION, RULES,
                  source_files=(Path(__file__).resolve(), _HERE / "rules_kyc.py", _HERE / "validators.py",
                                _HERE / "ruleset.py"))
