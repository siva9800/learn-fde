"""Small builders for hand-made files, so each rule can be tested on exactly the case it is about."""

from __future__ import annotations

from datetime import date

from intake.catalogue import PAGE_TITLES, Doc, DocFinding, FieldValue, LoanBundle, ModelOutput, Page, PromptOnlyVerdict
from intake.ruleset import RuleContext

AS_OF = date(2026, 11, 9)

TW_FIELDS = {
    "applicant_name": "RAVI TEJA PASUPULETI", "date_of_birth": "14-03-1991", "pan": "ABCPP1234K",
    "address": "12-4, KPHB Colony, Kukatpally, Hyderabad 500072", "mobile": "9876543210",
    "requested_amount": "90000", "tenure_months": "24", "monthly_income": "32000", "form_monthly_income": "32000",
    "application_date": "02-11-2026", "on_road_price": "110000", "dealer_code": "DLR-KKP-014",
    "quotation_date": "25-10-2026",
}
GOLD_FIELDS = {
    "applicant_name": "SRAVANI KONDAPALLI", "date_of_birth": "01-01-1985", "pan": "XYZPK4321L",
    "address": "3-9, Brodipet, Guntur 522002", "mobile": "9123456780", "requested_amount": "200000",
    "tenure_months": "12", "application_date": "04-11-2026", "gross_weight_g": "30.0", "net_weight_g": "28.0",
    "purity_carat": "22", "appraisal_date": "04-11-2026",
}
TW_DOCS = [Doc.APPLICATION_FORM, Doc.PHOTOGRAPH, Doc.PAN_CARD, Doc.PROOF_OF_IDENTITY, Doc.PROOF_OF_ADDRESS,
           Doc.INCOME_PROOF, Doc.BANK_STATEMENT, Doc.DEALER_QUOTATION, Doc.NACH_MANDATE, Doc.CANCELLED_CHEQUE,
           Doc.INSURANCE_PROPOSAL, Doc.CUSTOMER_DECLARATION, Doc.FIELD_VERIFICATION]
GOLD_DOCS = [Doc.APPLICATION_FORM, Doc.PHOTOGRAPH, Doc.PAN_CARD, Doc.PROOF_OF_IDENTITY, Doc.PROOF_OF_ADDRESS,
             Doc.GOLD_APPRAISAL, Doc.PLEDGE_FORM, Doc.OWNERSHIP_DECLARATION, Doc.KEY_FACT_STATEMENT]


def make_ctx(product: str = "two-wheeler", *, drop: tuple[Doc, ...] = (), fields: dict[str, str | None] | None = None,
             attrs: dict[Doc, dict[str, str]] | None = None, extra_page_text: str = "",
             uncertain_pages: tuple[int, ...] = ()) -> RuleContext:
    base = dict(TW_FIELDS if product == "two-wheeler" else GOLD_FIELDS)
    base.update(fields or {})
    docs = [d for d in (TW_DOCS if product == "two-wheeler" else GOLD_DOCS) if d not in drop]
    default_attrs: dict[Doc, dict[str, str]] = {
        Doc.PROOF_OF_ADDRESS: {"kind": "voter id", "holder": "self"},
        Doc.BANK_STATEMENT: {"period_start": "20-07-2026", "period_end": "20-10-2026", "salary_credits": "3"},
    }
    default_attrs.update(attrs or {})
    pages = [Page(i + 1, PAGE_TITLES[d] + "\nName: test") for i, d in enumerate(docs)]
    if extra_page_text:
        pages.append(Page(len(pages) + 1, extra_page_text))
    bundle = LoanBundle("GF-TEST", "Kukatpally", product, "sftp_scan", tuple(pages))
    found = {d: DocFinding(d, i + 1, 0.97, PAGE_TITLES[d], default_attrs.get(d, {})) for i, d in enumerate(docs)}
    out = ModelOutput("hand-made", {p.number: (docs[p.number - 1] if p.number <= len(docs) else Doc.UNKNOWN, 0.97)
                                    for p in pages},
                      {k: FieldValue(v, 0.97, 1, "") for k, v in base.items()}, tuple(found.values()), None,
                      PromptOnlyVerdict(True, ()))
    return RuleContext(bundle, out, found, AS_OF, uncertain_pages)


def ids(findings: list) -> list[str]:
    return sorted(f.rule_id for f in findings)
