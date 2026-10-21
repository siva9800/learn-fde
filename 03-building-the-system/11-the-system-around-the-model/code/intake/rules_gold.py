"""Gold loan: the nine-document checklist and the loan-to-value rule, as code.

Version 0.1, DRAFT, not yet reviewed with the compliance head. Gold is the second product; the Day 10
risk register (R7) says it moves to the next 90 days if the RBI inspection takes her away first.
The LTV tiers are from the RBI (Lending Against Gold and Silver Collateral) Directions, 2025, issued
6 June 2025, to be complied with by 1 April 2026: 85 percent up to Rs 2.5 lakh, 80 percent above that up
to Rs 5 lakh, 75 percent above Rs 5 lakh. The compliance head confirms the current text before signing.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from . import rules_kyc
from .catalogue import Doc
from .reference import gold_rate_on
from .ruleset import Action, Finding, Kind, Rule, RuleContext, RuleSet, missing_document
from .validators import parse_amount, parse_date

PRODUCT = "gold"
VERSION = "0.1"

# Nine documents (Day 6: "gold loans have nine documents").
REQUIRED_DOCS: tuple[tuple[str, Doc, Kind, str], ...] = (
    ("GL-DOC-01", Doc.APPLICATION_FORM, Kind.POLICY, "Gold loan application form, signed"),
    ("GL-DOC-02", Doc.PHOTOGRAPH, Kind.REGULATORY, "Recent photograph of the applicant"),
    ("GL-DOC-03", Doc.PAN_CARD, Kind.REGULATORY, "PAN card (or Form 60)"),
    ("GL-DOC-04", Doc.PROOF_OF_IDENTITY, Kind.REGULATORY, "Proof of identity: an officially valid document"),
    ("GL-DOC-05", Doc.PROOF_OF_ADDRESS, Kind.REGULATORY, "Proof of address: an OVD or a signed alternative"),
    ("GL-DOC-06", Doc.GOLD_APPRAISAL, Kind.REGULATORY, "Appraisal certificate: purity, gross and net weight"),
    ("GL-DOC-07", Doc.PLEDGE_FORM, Kind.POLICY, "Pledge form with the list of ornaments, signed"),
    ("GL-DOC-08", Doc.OWNERSHIP_DECLARATION, Kind.POLICY, "Declaration of ownership of the gold"),
    ("GL-DOC-09", Doc.KEY_FACT_STATEMENT, Kind.REGULATORY, "Key fact statement, acknowledged"),
)

# (upper limit of the loan amount in rupees, maximum LTV in percent); None means "and above".
LTV_TIERS: tuple[tuple[int | None, int], ...] = ((250_000, 85), (500_000, 80), (None, 75))
MIN_PURITY, MAX_PURITY = 18, 24        # carats Godavari accepts
MAX_TENURE = 12                        # months
APPRAISAL_MAX_AGE_DAYS = 3


def max_ltv_percent(amount: int) -> int:
    for limit, percent in LTV_TIERS:
        if limit is None or amount <= limit:
            return percent
    raise AssertionError("unreachable")


def collateral_value(net_weight_g: Decimal, purity_carat: int, rate_22k: int) -> int:
    """Value in whole rupees: net weight x the 22-carat rate, scaled by purity. Rounded down, in Decimal,
    so that the same inputs give the same rupee on every machine."""
    value = net_weight_g * Decimal(rate_22k) * Decimal(purity_carat) / Decimal(22)
    return int(value)          # truncates toward zero: the conservative direction for a lender


def _decimal(text: str | None) -> Decimal | None:
    if text is None:
        return None
    try:
        return Decimal(text.strip())
    except InvalidOperation:
        return None


def ltv_within_limit(ctx: RuleContext) -> list[Finding]:
    amount = parse_amount(ctx.value("requested_amount"))
    net, gross = _decimal(ctx.value("net_weight_g")), _decimal(ctx.value("gross_weight_g"))
    purity_raw, appraised = ctx.value("purity_carat"), parse_date(ctx.value("appraisal_date"))
    if amount is None or net is None or gross is None or purity_raw is None or not purity_raw.isdigit() \
            or appraised is None:
        return [Finding("GL-LTV", Kind.REGULATORY, Action.REVIEW,
                        "amount, weights, purity or appraisal date unreadable; LTV cannot be computed",
                        field_name="requested_amount")]
    if net > gross:
        return [Finding("GL-LTV", Kind.REGULATORY, Action.REVIEW,
                        f"net weight {net} g is more than gross weight {gross} g", field_name="net_weight_g")]
    rate = gold_rate_on(appraised)
    if rate is None:
        return [Finding("GL-LTV", Kind.REGULATORY, Action.REVIEW,
                        f"no published gold rate for {appraised.isoformat()}; never guessed",
                        field_name="appraisal_date")]
    value = collateral_value(net, int(purity_raw), rate)
    cap = max_ltv_percent(amount)
    if amount * 100 > value * cap:
        return [Finding("GL-LTV", Kind.REGULATORY, Action.BLOCK,
                        f"requested Rs {amount:,} is {amount * 100 / value:.1f} percent of collateral worth "
                        f"Rs {value:,} (net {net} g, {purity_raw} carat, Rs {rate:,}/g); the cap for this "
                        f"amount is {cap} percent", field_name="requested_amount")]
    return []


def purity_accepted(ctx: RuleContext) -> list[Finding]:
    raw = ctx.value("purity_carat")
    if raw is None:
        return []                       # unreadable purity is GL-LTV's finding, not a second one
    if not raw.isdigit() or not MIN_PURITY <= int(raw) <= MAX_PURITY:
        return [Finding("GL-PURITY", Kind.POLICY, Action.REVIEW,
                        f"purity {raw!r} is not {MIN_PURITY} to {MAX_PURITY} carat", field_name="purity_carat")]
    return []


def tenure_ok(ctx: RuleContext) -> list[Finding]:
    raw = ctx.value("tenure_months")
    if raw is None or not raw.isdigit() or not 1 <= int(raw) <= MAX_TENURE:
        return [Finding("GL-TENURE", Kind.POLICY, Action.REVIEW, f"tenure {raw!r} months is not 1 to {MAX_TENURE}",
                        field_name="tenure_months")]
    return []


def appraisal_recent(ctx: RuleContext) -> list[Finding]:
    appraised: date | None = parse_date(ctx.value("appraisal_date"))
    applied = parse_date(ctx.value("application_date"))
    if appraised is None or applied is None:
        return []                       # GL-LTV already sends this file to review
    gap = (applied - appraised).days
    if gap < 0 or gap > APPRAISAL_MAX_AGE_DAYS:
        return [Finding("GL-APPRAISAL-DATE", Kind.POLICY, Action.REVIEW,
                        f"appraisal is {gap} days from the application; it must be 0 to {APPRAISAL_MAX_AGE_DAYS}",
                        field_name="appraisal_date")]
    return []


def _doc_rule(rule_id: str, doc: Doc, kind: Kind, text: str) -> Rule:
    return Rule(rule_id, kind, f"In the file of record: {text}.", "Godavari gold checklist v0.1",
                lambda ctx: missing_document(rule_id, doc, text, ctx, kind))


RULES: tuple[Rule, ...] = (
    *(_doc_rule(*row) for row in REQUIRED_DOCS),
    Rule("GL-ADDR-LIST", Kind.REGULATORY, "Proof of address is an OVD, or an alternative on the signed list, "
         "in the applicant's own name.", "RBI KYC Master Direction; Godavari alternatives list v0.3",
         lambda ctx: rules_kyc.address_proof_acceptable(ctx, "GL-ADDR-LIST")),
    Rule("GL-ADDR-AGE", Kind.REGULATORY, "A utility bill used as address proof is at most 60 days old.",
         "Godavari alternatives list v0.3", lambda ctx: rules_kyc.address_proof_fresh(ctx, "GL-ADDR-AGE")),
    Rule("GL-KYC-MASK", Kind.REGULATORY, "No page shows an unmasked Aadhaar number.",
         "Aadhaar masking requirement; compliance circular", lambda ctx: rules_kyc.aadhaar_masked(ctx, "GL-KYC-MASK")),
    Rule("GL-LTV", Kind.REGULATORY, "Amount is within the tiered LTV cap (85/80/75 percent) of the collateral "
         "value from net weight, purity and the published 22-carat rate on the appraisal date.",
         "RBI Lending Against Gold and Silver Collateral Directions, 2025", ltv_within_limit),
    Rule("GL-PURITY", Kind.POLICY, f"Purity is {MIN_PURITY} to {MAX_PURITY} carat.", "Godavari product note",
         purity_accepted),
    Rule("GL-TENURE", Kind.POLICY, f"Tenure is at most {MAX_TENURE} months.", "Godavari product note", tenure_ok),
    Rule("GL-APPRAISAL-DATE", Kind.POLICY, f"Appraisal is 0 to {APPRAISAL_MAX_AGE_DAYS} days before the "
         "application.", "Godavari product note", appraisal_recent),
)

# The rate table in reference.py is data the treasury publishes daily, so it is not in the fingerprint;
# the method (this file) is. Signing the data would mean a new signature every morning.
_HERE = Path(__file__).resolve().parent
RULESET = RuleSet(PRODUCT, VERSION, RULES,
                  source_files=(Path(__file__).resolve(), _HERE / "rules_kyc.py", _HERE / "validators.py",
                                _HERE / "ruleset.py"))
