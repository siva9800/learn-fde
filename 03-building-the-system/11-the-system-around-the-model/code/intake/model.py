"""The model box: one interface, two implementations.

`ExtractionModel` is the only thing the pipeline knows about a model. `StubModel` is a deterministic
stand-in that reads the synthetic page text and makes the mistakes real document models make, seeded per
file so that every run and every test sees the same mistakes. `llm_adapter.AnthropicExtractionModel`
is the optional real one. The rules never import either.

The stub's error patterns, and where each comes from:
  - a document claimed present with a quote that is not on the cited page (hallucinated presence)
  - a page on a long file left unclassified ("lost in the middle")
  - a handwritten Telugu income declaration read as annual instead of monthly (the 2019 OCR pilot, Day 6)
  - the wrong bank statement picked as the salary account
  - "unsure" on fields it cannot read, and confidence that does not know about the OCR layer's mistakes
  - when asked to judge completeness in the prompt: rules applied loosely, arithmetic done badly
"""

from __future__ import annotations

import random
import re
from collections.abc import Sequence
from datetime import date
from typing import Protocol

from .catalogue import PAGE_TITLES, Doc, DocFinding, FieldValue, LoanBundle, ModelOutput, Page, PromptOnlyVerdict
from .reference import gold_rate_on

# The document list the extraction prompt asks the model to look for. This is prompt text, not a rule:
# it says what to look for, and decides nothing.
PROMPT_DOCS: dict[str, tuple[Doc, ...]] = {
    "two-wheeler": (Doc.APPLICATION_FORM, Doc.PHOTOGRAPH, Doc.PAN_CARD, Doc.PROOF_OF_IDENTITY,
                    Doc.PROOF_OF_ADDRESS, Doc.INCOME_PROOF, Doc.BANK_STATEMENT, Doc.DEALER_QUOTATION,
                    Doc.NACH_MANDATE, Doc.CANCELLED_CHEQUE, Doc.INSURANCE_PROPOSAL, Doc.CUSTOMER_DECLARATION,
                    Doc.FIELD_VERIFICATION),
    "gold": (Doc.APPLICATION_FORM, Doc.PHOTOGRAPH, Doc.PAN_CARD, Doc.PROOF_OF_IDENTITY, Doc.PROOF_OF_ADDRESS,
             Doc.GOLD_APPRAISAL, Doc.PLEDGE_FORM, Doc.OWNERSHIP_DECLARATION, Doc.KEY_FACT_STATEMENT),
}

UNSURE_BELOW = 0.55       # the stub says "unsure" (value None) rather than guess below this


class ExtractionModel(Protocol):
    name: str

    def read(self, bundle: LoanBundle) -> ModelOutput:
        """Classify every page, extract the fields with a page and a quote each, list the documents."""
        ...

    def draft_note(self, bundle: LoanBundle, findings: Sequence[tuple[str, str]]) -> str:
        """Write the plain-language note to the analyst for findings that code has already decided."""
        ...


def _line(page: Page, label: str) -> str | None:
    """The full line holding `label:`, exactly as it appears on the page."""
    for line in page.text.splitlines():
        if f"{label}:" in line:
            return line
    return None


def _after(line: str, label: str) -> str:
    return line.split(f"{label}:", 1)[1].strip()


def _digits(text: str) -> str:
    return re.sub(r"[^0-9]", "", text)


def _classify(first_line: str) -> Doc:
    best: tuple[int, Doc] = (0, Doc.UNKNOWN)
    for doc, title in PAGE_TITLES.items():
        if first_line.startswith(title) and len(title) > best[0]:
            best = (len(title), doc)
    return best[1]


class StubModel:
    """Deterministic stand-in for a document model. No network, no key, same output every run."""

    name = "stub-model-v1"

    def read(self, bundle: LoanBundle) -> ModelOutput:
        rng = random.Random(f"stub-model-v1-{bundle.file_id}")
        long_file = len(bundle.pages) > 30
        phone = bundle.channel == "phone_photo"

        # 1. Page classification.
        labels: dict[int, tuple[Doc, float]] = {}
        for page in bundle.pages:
            doc = _classify(page.text.splitlines()[0])
            conf = 0.97 - (0.07 if page.handwritten else 0.0) - (0.08 if phone else 0.0)
            if doc != Doc.UNKNOWN and long_file and rng.random() < 0.05:
                labels[page.number] = (Doc.UNKNOWN, 0.45)          # lost in the middle of a 40-page scan
            elif doc != Doc.UNKNOWN and phone and rng.random() < 0.03:
                labels[page.number] = (Doc.UNKNOWN, 0.40)
            else:
                labels[page.number] = (doc, round(conf, 2))

        def pages_of(doc: Doc) -> list[Page]:
            return [p for p in bundle.pages if labels[p.number][0] == doc]

        # 2. Documents, each with the page and the printed title as its quote.
        findings: list[DocFinding] = []
        for doc in PAGE_TITLES:
            found = pages_of(doc)
            if not found:
                continue
            targets = found if doc == Doc.BANK_STATEMENT else [found[0]]
            for page in targets:
                findings.append(DocFinding(doc, page.number, labels[page.number][1], page.text.splitlines()[0],
                                           self._attributes(doc, page)))
        claimed = {f.doc for f in findings}
        p_halluc = 0.18 if long_file else 0.10
        spare = [p.number for p in bundle.pages if labels[p.number][0] == Doc.UNKNOWN] or [p.number for p in bundle.pages]
        for doc in PROMPT_DOCS[bundle.product]:
            if doc not in claimed and rng.random() < p_halluc:
                fake_attrs = {"kind": "aadhaar (masked)", "holder": "self"} if doc == Doc.PROOF_OF_ADDRESS else {}
                findings.append(DocFinding(doc, rng.choice(spare), 0.84, PAGE_TITLES[doc], fake_attrs))

        # 3. Fields.
        fields: dict[str, FieldValue] = {}

        def put(name: str, page: Page | None, label: str, transform: str = "text", hint: float = 0.0) -> None:
            line = _line(page, label) if page else None
            if line is None:
                fields[name] = FieldValue(None, 0.0, None, "")
                return
            raw = _after(line, label)
            value = _digits(raw) if transform == "digits" else raw
            conf = 0.97 - (0.04 if page.handwritten else 0.0) - (0.09 if page.telugu else 0.0) \
                - (0.06 if phone else 0.0) + hint + rng.uniform(-0.05, 0.02)
            conf = round(max(0.05, min(0.99, conf)), 2)
            if conf < UNSURE_BELOW:
                fields[name] = FieldValue(None, conf, page.number, line)   # "unsure", said out loud
            else:
                fields[name] = FieldValue(value, conf, page.number, line)

        forms = [p for p in pages_of(Doc.APPLICATION_FORM) if "(continued)" not in p.text.splitlines()[0]]
        form = forms[0] if forms else None
        put("applicant_name", form, "Applicant name")
        put("date_of_birth", form, "Date of birth")
        put("form_pan", form, "PAN")
        put("address", form, "Residential address")
        put("mobile", form, "Mobile", "digits")
        put("requested_amount", form, "Loan amount requested", "digits")
        put("tenure_months", form, "Tenure (months)", "digits")
        put("application_date", form, "Application date")
        aadhaar_line = _line(form, "Aadhaar") if form else None
        fields["aadhaar_last4"] = FieldValue(_digits(aadhaar_line)[-4:] if aadhaar_line else None,
                                             0.9 if aadhaar_line else 0.0, form.number if form else None,
                                             aadhaar_line or "")
        pan_pages = pages_of(Doc.PAN_CARD)
        put("pan", pan_pages[0] if pan_pages else None, "Permanent Account Number", hint=0.02)
        put("pan_card_name", pan_pages[0] if pan_pages else None, "Name")

        if bundle.product == "two-wheeler":
            put("form_monthly_income", form, "Monthly income", "digits")
            co_line = _line(form, "Co-applicant") if form else None
            co = _after(co_line, "Co-applicant") if co_line else None
            fields["co_applicant_name"] = FieldValue(None if co in (None, "none") else co, 0.9,
                                                     form.number if form else None, co_line or "")
            income_pages = pages_of(Doc.INCOME_PROOF)
            income_page = income_pages[0] if income_pages else None
            label = "Net pay" if income_page and _line(income_page, "Net pay") else "Monthly income"
            put("monthly_income", income_page, label, "digits")
            fv = fields["monthly_income"]
            if income_page and income_page.telugu and fv.value and rng.random() < 0.30:
                # The 2019 failure: the figure is read as annual, so the "monthly" income is a twelfth of it.
                fields["monthly_income"] = FieldValue(str(int(fv.value) // 12), 0.78, fv.page, fv.evidence)
            quote_pages = pages_of(Doc.DEALER_QUOTATION)
            qp = quote_pages[0] if quote_pages else None
            put("on_road_price", qp, "On-road price", "digits")
            put("quotation_date", qp, "Quotation date")
            dealer_line = _line(qp, "Dealer") if qp else None
            m = re.search(r"\((DLR-[A-Z]+-\d+)\)", dealer_line or "")
            fields["dealer_code"] = FieldValue(m.group(1) if m else None, 0.93 if m else 0.0,
                                               qp.number if qp else None, dealer_line or "")
        else:
            ap_pages = pages_of(Doc.GOLD_APPRAISAL)
            ap = ap_pages[0] if ap_pages else None
            put("gross_weight_g", ap, "Gross weight (g)")
            put("net_weight_g", ap, "Net weight (g)")
            put("purity_carat", ap, "Purity (carat)")
            put("appraisal_date", ap, "Appraisal date")

        # 4. Which bank statement is the salary account? A judgement: proposed here, checked in code.
        statements = [f for f in findings if f.doc == Doc.BANK_STATEMENT]
        salary_page: int | None = None
        if statements:
            best = max(statements, key=lambda f: int(f.attributes.get("salary_credits", "0")))
            others = [f for f in statements if f is not best]
            salary_page = (rng.choice(others).page if others and rng.random() < 0.15 else best.page)

        return ModelOutput(self.name, labels, fields, tuple(findings), salary_page,
                           self._prompt_only(bundle, findings, fields, rng))

    @staticmethod
    def _attributes(doc: Doc, page: Page) -> dict[str, str]:
        attrs: dict[str, str] = {}
        if doc == Doc.PROOF_OF_ADDRESS:
            kind = _line(page, "Document")
            holder = _line(page, "In the name of")
            bill = _line(page, "Bill date")
            attrs["kind"] = _after(kind, "Document") if kind else ""
            m = re.search(r"\((\w+) of applicant\)", holder or "")
            attrs["holder"] = m.group(1) if m else "self"
            if bill:
                attrs["date"] = _after(bill, "Bill date")
        elif doc == Doc.BANK_STATEMENT:
            period = _line(page, "Period")
            if period:
                start, _, end = _after(period, "Period").partition(" to ")
                attrs["period_start"], attrs["period_end"] = start, end
            attrs["salary_credits"] = str(sum("SAL CREDIT" in line for line in page.text.splitlines()))
        return attrs

    @staticmethod
    def _prompt_only(bundle: LoanBundle, findings: list[DocFinding], fields: dict[str, FieldValue],
                     rng: random.Random) -> PromptOnlyVerdict:
        """What the model says when the prompt also carries the rules. Loose, and sometimes wrong."""
        issues: list[str] = []
        claimed = {f.doc for f in findings}
        attention = 0.75 if len(bundle.pages) > 30 else 0.90
        for doc in PROMPT_DOCS[bundle.product]:
            if doc not in claimed and rng.random() < attention:
                issues.append(f"missing {doc}")
        poa = next((f for f in findings if f.doc == Doc.PROOF_OF_ADDRESS), None)
        if poa:
            kind, holder = poa.attributes.get("kind", ""), poa.attributes.get("holder", "self")
            if kind in ("gas bill", "notarised rent agreement") and rng.random() < 0.2:
                issues.append("address proof may not be acceptable")
            if holder != "self" and kind not in ("gas bill",) and rng.random() < 0.3:
                issues.append("address proof not in applicant's name")
            if kind == "electricity bill" and rng.random() < 0.35:
                issues.append("check utility bill date")
        if any(re.search(r"Aadhaar number: \d{4} \d{4} \d{4}", p.text) for p in bundle.pages) and rng.random() < 0.3:
            issues.append("Aadhaar copy appears unmasked")
        stmts = [f for f in findings if f.doc == Doc.BANK_STATEMENT]
        if stmts and rng.random() < 0.4:
            issues.append("verify bank statement period")
        eligible: int | None = None
        amount = int(fields["requested_amount"].value) if fields.get("requested_amount") and fields["requested_amount"].value else None
        if bundle.product == "two-wheeler":
            price = fields.get("on_road_price")
            if amount and price and price.value and amount > 0.9 * int(price.value) and rng.random() < 0.5:
                issues.append("amount above 90 percent of on-road price")
        else:
            gross, net = fields.get("gross_weight_g"), fields.get("net_weight_g")
            purity, appraised = fields.get("purity_carat"), fields.get("appraisal_date")
            if amount and gross and net and gross.value and net.value and purity and purity.value and appraised and appraised.value:
                d, mth, y = appraised.value.split("-")
                rate = gold_rate_on(date(int(y), int(mth), int(d))) or 0
                weight = float(gross.value) if rng.random() < 0.35 else float(net.value)   # uses gross weight
                cap = 0.75 if rng.random() < 0.3 else (0.85 if amount <= 250_000 else 0.80 if amount <= 500_000 else 0.75)
                factor = 1.0 if rng.random() < 0.25 else int(purity.value) / 22             # forgets purity
                slip = rng.uniform(0.96, 1.04) if rng.random() < 0.2 else 1.0              # arithmetic slip
                eligible = int(weight * rate * factor * cap * slip)
                if amount > eligible:
                    issues.append("requested amount exceeds LTV limit")
        return PromptOnlyVerdict(complete=not issues, issues=tuple(issues), eligible_amount=eligible)

    def draft_note(self, bundle: LoanBundle, findings: Sequence[tuple[str, str]]) -> str:
        """A short note in plain words. It sometimes forgets to cite a rule; code checks for that."""
        rng = random.Random(f"stub-note-{bundle.file_id}")
        if not findings:
            return f"{bundle.file_id}: nothing for the branch; the file is ready for your approval."
        lines = [f"{bundle.file_id}: {len(findings)} point(s) before this file can move."]
        for i, (rule_id, message) in enumerate(findings, start=1):
            cite = "" if rng.random() < 0.10 else f" (rule {rule_id})"
            lines.append(f"{i}. {message[0].upper() + message[1:]}{cite}.")
        return "\n".join(lines)
