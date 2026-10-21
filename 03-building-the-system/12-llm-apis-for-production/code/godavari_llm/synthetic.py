"""A synthetic night of Godavari's SFTP drop: scanned loan files of 8 to 40 pages, in tray order.

Every name, PAN and amount is invented. The generator also keeps the ground truth for each page, which
only the fake provider (as the model's "eyes") and the evaluation at the end of the run may read.
"""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass, field

from .contract import Doc

TITLES: dict[Doc, str] = {   # the printed title on the first line of each page type (as in Day 11)
    Doc.APPLICATION_FORM: "LOAN APPLICATION FORM",
    Doc.PHOTOGRAPH: "APPLICANT PHOTOGRAPH",
    Doc.PAN_CARD: "INCOME TAX DEPARTMENT - PERMANENT ACCOUNT NUMBER CARD",
    Doc.PROOF_OF_IDENTITY: "PROOF OF IDENTITY",
    Doc.PROOF_OF_ADDRESS: "PROOF OF ADDRESS",
    Doc.INCOME_PROOF: "INCOME PROOF",
    Doc.BANK_STATEMENT: "STATEMENT OF ACCOUNT",
    Doc.DEALER_QUOTATION: "DEALER QUOTATION / PROFORMA INVOICE",
    Doc.CO_APPLICANT_KYC: "CO-APPLICANT KYC",
    Doc.GOLD_APPRAISAL: "GOLD APPRAISAL CERTIFICATE",
    Doc.PLEDGE_FORM: "PLEDGE FORM - LIST OF ORNAMENTS",
    Doc.CUSTOMER_DECLARATION: "CUSTOMER DECLARATION AND CONSENT",
    Doc.KEY_FACT_STATEMENT: "KEY FACT STATEMENT - ACKNOWLEDGEMENT",
}

FIRST = ["Venkata Ramana", "Sai Teja", "Padma", "Kavya", "Naveen", "Swathi", "Ravi Teja", "Anusha",
         "Mahesh", "Sravani", "Prasad", "Divya", "Harika", "Suresh", "Bhargav", "Mounika", "Kiran", "Jyothi"]
SURNAMES = ["Reddy", "Naidu", "Rao", "Chowdary", "Varma", "Sastry", "Goud", "Yadav", "Shaik", "Murthy"]
BRANCHES = ["KKP", "GNT", "VJA", "AMP", "NLR", "WGL", "KMM", "ONG"]   # branch codes, invented
EMPLOYERS = ["Sri Sai Textiles", "Krishna Pharma Ltd", "Coastal Aqua Exports", "Deccan Auto Works"]


def inr(n: int) -> str:
    """1250000 -> '12,50,000' (Indian digit grouping)."""
    s = str(n)
    if len(s) <= 3:
        return s
    head, tail = s[:-3], s[-3:]
    groups = []
    while len(head) > 2:
        groups.insert(0, head[-2:])
        head = head[:-2]
    if head:
        groups.insert(0, head)
    return ",".join(groups) + "," + tail


@dataclass(frozen=True)
class SyntheticPage:
    file_id: str
    number: int
    doc: Doc
    text: str
    image_tokens: int            # full-resolution page image, as the large model sees it
    thumb_tokens: int            # low-resolution thumbnail for classification
    truth: dict[str, str | int]  # field name -> true value, for the fields printed on this page
    lines: dict[str, str]        # field name -> the exact line the value is printed on

    @property
    def ref(self) -> str:
        return f"{self.file_id}/p{self.number:02d}"

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class SyntheticFile:
    file_id: str
    branch: str
    product: str
    pages: tuple[SyntheticPage, ...]
    truth: dict[str, str | int | None] = field(default_factory=dict)

    def page(self, number: int) -> SyntheticPage | None:
        return next((p for p in self.pages if p.number == number), None)


def _pan(rng: random.Random, surname: str) -> str:
    letters = "ABCDEFGHJKLMNPQRSTUVWXYZ"
    return ("".join(rng.choice(letters) for _ in range(3)) + "P" + surname[0].upper()
            + f"{rng.randint(0, 9999):04d}" + rng.choice(letters))


def make_file(rng: random.Random, seq: int) -> SyntheticFile:
    branch = rng.choice(BRANCHES)
    file_id = f"{branch}-26-{seq:05d}"
    product = "two-wheeler" if rng.random() < 0.7 else "gold"
    surname = rng.choice(SURNAMES)
    name = f"{rng.choice(FIRST)} {surname}"
    pan = _pan(rng, surname)
    has_co = rng.random() < 0.35
    co_surname = surname if rng.random() < 0.6 else rng.choice(SURNAMES)   # spouses often share a surname
    co_name = f"{rng.choice(FIRST)} {co_surname}" if has_co else None
    co_pan = _pan(rng, co_surname) if has_co else None
    amount = rng.randrange(60_000, 180_001, 500) if product == "two-wheeler" else rng.randrange(20_000, 300_001, 1000)
    income = rng.randrange(15_000, 90_001, 500)
    employer = rng.choice(EMPLOYERS)
    telugu = rng.random() < 0.4
    label = "Applicant name / దరఖాస్తుదారు పేరు" if telugu else "Applicant name"
    product_line = "Product: Two-wheeler loan" if product == "two-wheeler" else "Product: Gold loan"

    blocks: list[list[tuple[Doc, list[str], dict[str, str | int], dict[str, str]]]] = []

    def page(doc: Doc, body: list[str], truth: dict[str, str | int], lines: dict[str, str]):
        return (doc, body, truth, lines)

    app_lines = {
        "applicant_name": f"{label}: {name}",
        "applicant_pan": f"PAN: {pan}",
        "product": product_line,
        "requested_amount": f"Loan amount requested: Rs. {inr(amount)}",
    }
    app_truth: dict[str, str | int] = {"applicant_name": name, "applicant_pan": pan,
                                       "product": product, "requested_amount": amount}
    if has_co:
        app_lines["co_applicant_name"] = f"Co-applicant name: {co_name}"
        app_truth["co_applicant_name"] = co_name  # type: ignore[assignment]
    other = (f"Vehicle ex-showroom price: Rs. {inr(amount + 9000)}" if product == "two-wheeler"
             else f"Gold value as per appraisal: Rs. {inr(int(amount * 1.33) // 100 * 100)}")
    first = [f"File no: {file_id}", *app_lines.values(), other, "Branch: " + branch]
    app_lines = {**app_lines, "other_amount": other}      # printed, but not a field: the trap for the model
    form = [page(Doc.APPLICATION_FORM, first, app_truth, app_lines)]
    for k in range(rng.randint(1, 2)):
        form.append(page(Doc.APPLICATION_FORM, [f"(contd. {k + 2})", "Residential address: H.No 4-12, Ward 7",
                                                 "Employment: salaried", f"Employer: {employer}"], {}, {}))
    blocks.append(form)
    blocks.append([page(Doc.PHOTOGRAPH, ["[photograph]", "Signature across photo"], {}, {})])
    pan_lines = {"applicant_name": f"Name: {name.upper()}", "applicant_pan": f"Permanent Account Number: {pan}"}
    blocks.append([page(Doc.PAN_CARD, list(pan_lines.values()),
                        {"applicant_name": name.upper(), "applicant_pan": pan}, pan_lines)])
    blocks.append([page(Doc.PROOF_OF_IDENTITY, ["Aadhaar (masked): XXXX XXXX " + f"{rng.randint(1000, 9999)}"], {}, {})])
    blocks.append([page(Doc.PROOF_OF_ADDRESS, ["Electricity bill", "Consumer: " + name], {}, {})])
    inc_lines = {"monthly_income": f"Net monthly salary: Rs. {inr(income)}"}
    blocks.append([page(Doc.INCOME_PROOF, [f"Employer: {employer}", f"Employee: {name}", inc_lines["monthly_income"]],
                        {"monthly_income": income}, inc_lines)
                   for _ in range(rng.randint(1, 2))])
    if has_co:
        co_lines = {"co_applicant_name": f"Name: {co_name}"}
        blocks.append([page(Doc.CO_APPLICANT_KYC, [co_lines["co_applicant_name"], f"PAN: {co_pan}"],
                            {"co_applicant_name": co_name}, co_lines)])  # type: ignore[dict-item]
    if product == "two-wheeler":
        blocks.append([page(Doc.DEALER_QUOTATION, ["Model: 110cc motorcycle", f"Ex-showroom: Rs. {inr(amount + 9000)}"], {}, {})])
    else:
        blocks.append([page(Doc.GOLD_APPRAISAL, ["Gross weight: 41.2 g", "Purity: 22 carat"], {}, {}),
                       page(Doc.PLEDGE_FORM, ["Chain 1, bangles 2", "Customer signature"], {}, {})])
    blocks.append([page(Doc.CUSTOMER_DECLARATION, ["I confirm the information above is true."], {}, {})])
    blocks.append([page(Doc.KEY_FACT_STATEMENT, ["Annual percentage rate: as per sanction letter"], {}, {})])

    base = sum(len(b) for b in blocks)
    target = rng.choice([rng.randint(8, 15), rng.randint(16, 30), rng.randint(16, 30), rng.randint(31, 40)])
    n_bank = max(1, target - base)
    bank: list = []
    for k in range(n_bank):
        body = [f"Account holder: {name}", f"Page {k + 1} of {n_bank}"]
        truth: dict[str, str | int] = {}
        lines: dict[str, str] = {}
        if k == 0:
            lines = {"monthly_income": f"SALARY CREDIT {employer.upper()} {inr(income)}.00"}
            body.append(lines["monthly_income"])
            truth = {"monthly_income": income}
        bank.append(page(Doc.BANK_STATEMENT, body, truth, lines))
    blocks.append(bank)

    rng.shuffle(blocks)                       # trays are not in any order; stapled blocks stay together
    pages = []
    for number, (doc, body, truth, lines) in enumerate((p for b in blocks for p in b), start=1):
        text = "\n".join([TITLES[doc], *body])
        pages.append(SyntheticPage(file_id, number, doc, text, rng.randint(1550, 1700), rng.randint(420, 480),
                                   truth, lines))
    file_truth = {"applicant_name": name, "applicant_pan": pan, "co_applicant_name": co_name,
                  "product": product, "requested_amount": amount, "monthly_income": income}
    return SyntheticFile(file_id, branch, product, tuple(pages), file_truth)


def make_night(n_files: int = 60, seed: int = 2611) -> list[SyntheticFile]:
    rng = random.Random(seed)
    return [make_file(rng, i + 1) for i in range(n_files)]
