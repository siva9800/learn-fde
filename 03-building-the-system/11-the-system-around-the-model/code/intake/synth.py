"""Turn Day 7's sample rows into synthetic loan files: OCR'd page text plus the ground truth behind it.

Each Day 7 row (product, channel, pages, language mix, which of PAN, address proof, income proof and
photo are present) becomes a bundle of pages in tray order, with the noise a real file has: OCR
confusions on phone photos, handwritten Telugu forms, filler pages, an unmasked Aadhaar now and then,
a gas bill in the father's name. The ground truth is kept apart and is used only to score the run.

All names, numbers and documents are invented. Seeded per file, so every run is identical.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from .catalogue import PAGE_TITLES, Doc, LoanBundle, Page
from .reference import BRANCH_CODES, EMPANELLED_DEALERS, gold_rate_on
from .validators import verhoeff_check_digit

PRODUCTS_IN_SCOPE = ("two-wheeler", "gold")

GIVEN = ["RAVI TEJA", "SRAVANI", "NAGA RAJU", "VENKATA RAMANA", "PADMAVATHI", "SAI KIRAN", "ANUSHA",
         "SURESH BABU", "MADHAVI LATHA", "PRASAD", "KAVYA SRI", "RAMESH", "SUNEETHA", "HARI KRISHNA",
         "JYOTHI", "MAHESH", "SIREESHA", "GOPI CHAND", "VANI", "ANIL KUMAR"]
FATHER_GIVEN = ["VENKATESWARLU", "SUBBA RAO", "NARAYANA", "SATYANARAYANA", "RAMA RAO", "KOTESWARA RAO"]
SURNAMES = ["PASUPULETI", "KONDAPALLI", "GADDE", "VEMULA", "BANDARU", "CHILUKURI", "YARLAGADDA",
            "KOTAGIRI", "MANDAVA", "PONNAM", "ALLURI", "NALLAMOTHU", "TADIKONDA", "UPPALAPATI"]
ADDRESSES = {
    "Kukatpally": "KPHB Colony, Kukatpally, Hyderabad 500072",
    "Dilsukhnagar": "Kothapet, Dilsukhnagar, Hyderabad 500035",
    "Vijayawada-Benz Circle": "Gunadala, Vijayawada 520004",
    "Guntur": "Brodipet, Guntur 522002",
    "Warangal": "Hanamkonda, Warangal 506001",
    "Rajahmundry": "Danavaipeta, Rajahmundry 533103",
}
EMPLOYERS = ["SRI VENKATESWARA TEXTILES", "DECCAN PHARMA PACKAGING", "KRISHNA HOSPITALS",
             "GODAVARI AGRO FOODS", "SAPTAGIRI LOGISTICS"]
BUSINESSES = ["kirana store", "mobile repair shop", "tiffin centre", "tailoring unit", "auto spares shop"]
OCR_CONFUSIONS = {"O": "0", "0": "O", "I": "1", "1": "I", "S": "5", "5": "S", "B": "8", "8": "B",
                  "M": "N", "N": "M", "E": "F", "F": "E", "3": "8", "7": "1"}

# Address proofs as they arrive: (kind, holder, weight, truth label or "").
ADDRESS_PROOF_MIX: list[tuple[str, str, int, str]] = [
    ("aadhaar (masked)", "self", 30, ""), ("voter id", "self", 20, ""), ("driving licence", "self", 15, ""),
    ("passport", "self", 8, ""), ("electricity bill", "self", 8, ""), ("electricity bill (stale)", "self", 3, "ADDRESS_STALE"),
    ("registered rent agreement", "self", 6, ""), ("gas bill", "father", 5, "ADDRESS_NOT_ON_LIST"),
    ("notarised rent agreement", "self", 3, "ADDRESS_NOT_ON_LIST"), ("electricity bill", "father", 2, "ADDRESS_NOT_OWN_NAME"),
]

TW_DOCS = [Doc.APPLICATION_FORM, Doc.PHOTOGRAPH, Doc.PAN_CARD, Doc.PROOF_OF_IDENTITY, Doc.PROOF_OF_ADDRESS,
           Doc.INCOME_PROOF, Doc.BANK_STATEMENT, Doc.DEALER_QUOTATION, Doc.NACH_MANDATE, Doc.CANCELLED_CHEQUE,
           Doc.INSURANCE_PROPOSAL, Doc.CUSTOMER_DECLARATION, Doc.FIELD_VERIFICATION]
GOLD_DOCS = [Doc.APPLICATION_FORM, Doc.PHOTOGRAPH, Doc.PAN_CARD, Doc.PROOF_OF_IDENTITY, Doc.PROOF_OF_ADDRESS,
             Doc.GOLD_APPRAISAL, Doc.PLEDGE_FORM, Doc.OWNERSHIP_DECLARATION, Doc.KEY_FACT_STATEMENT]


@dataclass
class GroundTruth:
    """What is really in the file. The labeller's answer key; the pipeline never sees it."""

    file_id: str
    product: str
    fields: dict[str, str]
    present: set[Doc]
    defects: set[str] = field(default_factory=set)
    salary_page: int | None = None
    statement_pages: list[int] = field(default_factory=list)


def _fmt_amount(n: int) -> str:
    """Indian grouping: 125000 -> 'Rs 1,25,000'."""
    s = str(n)
    if len(s) <= 3:
        return f"Rs {s}"
    head, tail = s[:-3], s[-3:]
    groups: list[str] = []
    while len(head) > 2:
        groups.insert(0, head[-2:])
        head = head[:-2]
    if head:
        groups.insert(0, head)
    return "Rs " + ",".join(groups + [tail])


def _d(day: date) -> str:
    return day.strftime("%d-%m-%Y")


def _pan(rng: random.Random, surname: str) -> str:
    letters = "ABCDEFGHJKLMNPRSTUVWXYZ"
    return ("".join(rng.choice(letters) for _ in range(3)) + "P" + surname[0]
            + f"{rng.randint(1000, 9999)}" + rng.choice(letters))


def _aadhaar(rng: random.Random) -> str:
    stem = str(rng.randint(2, 9)) + "".join(str(rng.randint(0, 9)) for _ in range(10))
    return stem + verhoeff_check_digit(stem)


def _ocr_confuse(rng: random.Random, text: str) -> str:
    positions = [i for i, ch in enumerate(text) if ch in OCR_CONFUSIONS]
    if not positions:
        return text
    i = rng.choice(positions)
    return text[:i] + OCR_CONFUSIONS[text[i]] + text[i + 1:]


def _weighted(rng: random.Random, rows: list[tuple[str, str, int, str]]) -> tuple[str, str, str]:
    kind, holder, _, label = rng.choices(rows, weights=[r[2] for r in rows])[0]
    return kind, holder, label


def _application_date(rng: random.Random) -> date:
    days = [date(2026, 10, 26) + timedelta(days=i) for i in range(12)]
    return rng.choice([d for d in days if d.weekday() < 5])


def build_file(row: Any) -> tuple[LoanBundle, GroundTruth]:
    """One Day 7 LoanFile row in, one bundle and its ground truth out."""
    rng = random.Random(f"godavari-day11-{row.file_id}")
    product: str = row.product
    branch: str = row.branch
    telugu = row.language_mix in ("telugu", "mixed")
    phone = row.channel == "phone_photo"
    ocr_rate = {"sftp_scan": 0.04, "mixed": 0.08, "phone_photo": 0.15}[row.channel]

    given, surname = rng.choice(GIVEN), rng.choice(SURNAMES)
    name = f"{given} {surname}"
    father = f"{rng.choice(FATHER_GIVEN)} {surname}"
    applied = _application_date(rng)
    born = applied - timedelta(days=rng.randint(22 * 365 + 10, 58 * 365))
    pan = _pan(rng, surname)
    aadhaar = _aadhaar(rng)
    masked = f"XXXX XXXX {aadhaar[-4:]}"
    mobile = rng.choice("6789") + "".join(str(rng.randint(0, 9)) for _ in range(9))
    address = f"{rng.randint(1, 48)}-{rng.randint(1, 120)}, {ADDRESSES[branch]}"
    truth: dict[str, str] = {
        "applicant_name": name, "date_of_birth": _d(born), "pan": pan, "aadhaar_last4": aadhaar[-4:],
        "address": address, "mobile": mobile, "application_date": _d(applied), "branch_code": BRANCH_CODES[branch],
    }
    defects: set[str] = set()

    # Which documents are present. Day 7's four flags decide four of them; the rest are usually there.
    required = TW_DOCS if product == "two-wheeler" else GOLD_DOCS
    day7_flags = {Doc.PAN_CARD: row.has_pan, Doc.PROOF_OF_ADDRESS: row.has_address_proof,
                  Doc.PHOTOGRAPH: row.has_photo}
    if product == "two-wheeler":
        day7_flags[Doc.INCOME_PROOF] = row.has_income_proof
    present: set[Doc] = set()
    for doc in required:
        p_missing = 0.003 if doc == Doc.APPLICATION_FORM else 0.008
        if day7_flags.get(doc, rng.random() > p_missing):
            present.add(doc)

    # Address proof and identity proof.
    poa_kind, poa_holder, poa_label = _weighted(rng, ADDRESS_PROOF_MIX)
    unmasked = rng.random() < 0.06
    poi_kind = "aadhaar" if unmasked else rng.choices(["aadhaar", "voter id", "driving licence", "passport"],
                                                      weights=[60, 20, 12, 8])[0]
    if unmasked and Doc.PROOF_OF_IDENTITY in present:
        defects.add("AADHAAR_UNMASKED")
    if Doc.PROOF_OF_ADDRESS in present and poa_label:
        defects.add(poa_label)

    # Product-specific facts.
    salaried = product == "two-wheeler" and rng.random() < 0.65
    monthly_income = rng.randrange(18_000, 70_000, 500)
    co_applicant = ""
    pages_spec: list[tuple[Doc, str, bool]] = []      # (doc, text, handwritten)
    form_handwritten = rng.random() < 0.7

    if product == "two-wheeler":
        price = rng.randrange(72_000, 165_000, 50)
        over = rng.random() < 0.06
        share = rng.uniform(0.92, 1.0) if over else rng.uniform(0.60, 0.90)
        amount = int(price * share) // 500 * 500
        if amount * 100 > price * 90:
            defects.add("OVER_MARGIN")
        dealers = [code for code, (_, b) in EMPANELLED_DEALERS.items() if b == branch]
        dealer = rng.choice(dealers)
        quoted = applied - timedelta(days=rng.randint(1, 20))
        tenure = rng.choice([12, 18, 24, 36])
        if rng.random() < 0.2:
            co_applicant = f"{rng.choice(GIVEN)} {surname}"
            if rng.random() < 0.85:
                present.add(Doc.CO_APPLICANT_KYC)
            else:
                defects.add(f"MISSING:{Doc.CO_APPLICANT_KYC}")
        truth.update({"requested_amount": str(amount), "tenure_months": str(tenure), "on_road_price": str(price),
                      "dealer_code": dealer, "quotation_date": _d(quoted), "monthly_income": str(monthly_income)})
    else:
        gross = Decimal(rng.randint(80, 850)) / 10
        net = (gross * Decimal(str(round(rng.uniform(0.86, 0.97), 3)))).quantize(Decimal("0.1"), rounding="ROUND_DOWN")
        purity = rng.choices([22, 20, 18], weights=[78, 12, 10])[0]
        appraised = applied - timedelta(days=rng.choice([0, 0, 0, 1, 2]))
        rate = gold_rate_on(appraised) or 0
        value = int(net * Decimal(rate) * Decimal(purity) / Decimal(22))
        over = rng.random() < 0.10
        ratio = rng.uniform(0.86, 0.95) if over else rng.uniform(0.55, 0.72)
        amount = max(10_000, int(value * ratio) // 500 * 500)
        cap = 85 if amount <= 250_000 else 80 if amount <= 500_000 else 75
        if amount * 100 > value * cap:
            defects.add("OVER_LTV")
        tenure = rng.choice([6, 12, 12])
        truth.update({"requested_amount": str(amount), "tenure_months": str(tenure), "gross_weight_g": str(gross),
                      "net_weight_g": str(net), "purity_carat": str(purity), "appraisal_date": _d(appraised)})

    for doc in required:
        if doc not in present:
            defects.add(f"MISSING:{doc}")

    # --- Page texts (what OCR returns) --------------------------------------------------------------
    def label(te: str, en: str) -> str:
        return f"{te} / {en}" if telugu and form_handwritten else en

    def ocr(value: str, rate: float) -> str:
        return _ocr_confuse(rng, value) if rng.random() < rate else value

    form_name = name
    if telugu and form_handwritten and rng.random() < 0.10:      # a transliteration variant on the form
        form_name = name.replace("A", "AA", 1) if "A" in name else name
    form_pan = ocr(pan, 0.06 if form_handwritten else 0.02)
    form_amount = truth["requested_amount"]
    if form_handwritten and rng.random() < 0.03:                 # a stray zero on a handwritten amount
        form_amount = str(int(form_amount) * 10)
    form_lines = [
        PAGE_TITLES[Doc.APPLICATION_FORM],
        f"Godavari Finance Ltd - Branch: {branch} ({BRANCH_CODES[branch]})",
        f"Product: {product}", f"File number: {row.file_id}",
        f"{label('దరఖాస్తుదారు పేరు', 'Applicant name')}: {form_name}",
        f"Father's name: {father}", f"Date of birth: {ocr(_d(born), 0.05 if form_handwritten else 0.0)}",
        f"PAN: {form_pan}", f"Aadhaar: {masked}",
        f"{label('చిరునామా', 'Residential address')}: {address}", f"Mobile: {mobile}",
        f"Loan amount requested: {_fmt_amount(int(form_amount))}", f"Tenure (months): {truth['tenure_months']}",
    ]
    if product == "two-wheeler":
        occupation = f"salaried, employer {rng.choice(EMPLOYERS)}" if salaried else f"self-employed, {rng.choice(BUSINESSES)}"
        form_lines += [f"{label('నెలసరి ఆదాయం', 'Monthly income')}: {_fmt_amount(monthly_income)}",
                       f"Occupation: {occupation}", f"Co-applicant: {co_applicant or 'none'}"]
    form_lines += [f"Application date: {_d(applied)}", "Signature of applicant: [signed]"]
    if phone:
        form_lines.insert(3, "[blurred region]")
    pages_spec.append((Doc.APPLICATION_FORM, "\n".join(form_lines), form_handwritten))
    pages_spec.append((Doc.APPLICATION_FORM, PAGE_TITLES[Doc.APPLICATION_FORM] + " (continued)\n"
                       "Declarations by the applicant\nSignature of applicant: [signed]", form_handwritten))

    def simple(doc: Doc, *lines: str, hw: bool = False) -> None:
        pages_spec.append((doc, "\n".join([PAGE_TITLES[doc], *lines]), hw))

    simple(Doc.PHOTOGRAPH, f"[photograph of {name}]", "Signed across by the applicant")
    simple(Doc.PAN_CARD, f"Name: {name}", f"Father's Name: {father}", f"Date of Birth: {_d(born)}",
           f"Permanent Account Number: {ocr(pan, ocr_rate)}")
    poi_number = (f"Aadhaar number: {aadhaar[:4]} {aadhaar[4:8]} {aadhaar[8:]}" if unmasked
                  else f"Aadhaar number: {masked}" if poi_kind == "aadhaar"
                  else f"Document number: {rng.choice('ABCDEFGHJK')}{rng.randint(1000000, 9999999)}")
    simple(Doc.PROOF_OF_IDENTITY, f"Document: {poi_kind}", f"Name: {name}", poi_number)

    holder_name = name if poa_holder == "self" else father
    holder_note = "" if poa_holder == "self" else f" ({poa_holder} of applicant)"
    kind_on_page = poa_kind.replace(" (stale)", "")
    bill_date = applied - timedelta(days=rng.randint(70, 120) if "stale" in poa_kind else rng.randint(5, 50))
    poa_lines = [f"Document: {kind_on_page}", f"In the name of: {holder_name}{holder_note}", f"Address: {address}"]
    if "bill" in kind_on_page:
        poa_lines.append(f"Bill date: {_d(bill_date)}")
    simple(Doc.PROOF_OF_ADDRESS, *poa_lines)

    statement_texts: list[tuple[str, bool]] = []
    if product == "two-wheeler":
        if salaried:
            employer = occupation.split("employer ")[1]
            net_pay = monthly_income
            simple(Doc.INCOME_PROOF, "Document: salary slip, September 2026", f"Employer: {employer}",
                   f"Employee: {name}", f"Net pay: {_fmt_amount(net_pay)}")
        else:
            hw = telugu and rng.random() < 0.8
            simple(Doc.INCOME_PROOF, "Document: self-declaration of income", f"Name: {name}",
                   f"{'నెలసరి ఆదాయం / ' if hw else ''}Monthly income: {_fmt_amount(monthly_income)}",
                   f"Business: {occupation.split(', ')[1]}", hw=hw)
        stale = rng.random() < 0.05
        end = applied - timedelta(days=rng.randint(45, 110) if stale else rng.randint(3, 25))
        start = end - timedelta(days=91)
        n_statements = rng.choices([1, 2, 3], weights=[55, 30, 15])[0] if salaried else 1
        salary_index = rng.randrange(n_statements)
        for k in range(n_statements):
            acct = f"XXXXXX{rng.randint(1000, 9999)}"
            is_main = k == salary_index
            if is_main and salaried:
                credits = [f"{(end - timedelta(days=30 * m)).strftime('%d-%m')} SAL CREDIT {employer} "
                           f"{_fmt_amount(monthly_income + rng.randrange(-500, 501, 100))}" for m in range(3)]
            else:
                credits = [f"{(end - timedelta(days=11 * m)).strftime('%d-%m')} UPI CR {rng.choice(SURNAMES)} "
                           f"{_fmt_amount(rng.randrange(800, 9000, 50))}" for m in range(4)]
            text = "\n".join([PAGE_TITLES[Doc.BANK_STATEMENT], "Bank: Krishna Valley Bank", f"Account holder: {name}",
                              f"Account number: {acct}", f"Period: {_d(start)} to {_d(end)}", *credits])
            statement_texts.append((text, is_main))
        if stale and Doc.BANK_STATEMENT in present:
            defects.add("STATEMENT_STALE")
        dealer_name = EMPANELLED_DEALERS[truth["dealer_code"]][0]
        simple(Doc.DEALER_QUOTATION, f"Dealer: {dealer_name} ({truth['dealer_code']})", "Vehicle: scooter 110cc",
               f"On-road price: Rs {ocr(_fmt_amount(int(truth['on_road_price']))[3:], 0.08 if phone else 0.01)}", f"Quotation date: {truth['quotation_date']}")
        simple(Doc.NACH_MANDATE, f"Account holder: {name}", "Signature: [signed]")
        simple(Doc.CANCELLED_CHEQUE, f"Payee account holder: {name}", "CANCELLED")
        simple(Doc.INSURANCE_PROPOSAL, f"Proposer: {name}", "Vehicle: scooter 110cc")
        simple(Doc.CUSTOMER_DECLARATION, f"Name: {name}", "I consent to the processing of my data for this loan.",
               "Signature: [signed]")
        simple(Doc.FIELD_VERIFICATION, f"Applicant: {name}", f"Address verified: {address}", "Verifier: FV-117")
        if co_applicant:
            simple(Doc.CO_APPLICANT_KYC, f"Co-applicant: {co_applicant}", "Document: voter id")
    else:
        simple(Doc.GOLD_APPRAISAL, f"Appraiser: AP-{BRANCH_CODES[branch]}", "Items: bangles and a chain",
               f"Gross weight (g): {truth['gross_weight_g']}", f"Net weight (g): {truth['net_weight_g']}",
               f"Purity (carat): {truth['purity_carat']}", f"Appraisal date: {truth['appraisal_date']}")
        simple(Doc.PLEDGE_FORM, f"Pledgor: {name}", "Ornaments: as per appraisal certificate", "Signature: [signed]")
        simple(Doc.OWNERSHIP_DECLARATION, f"I, {name}, declare that the ornaments are my own.", "Signature: [signed]")
        simple(Doc.KEY_FACT_STATEMENT, f"Borrower: {name}", "Acknowledged: [signed]")

    # Drop the pages of absent documents, add the statements, then pad with filler to Day 7's page count.
    kept: list[tuple[Doc | None, str, bool, bool]] = [
        (doc, text, hw, False) for doc, text, hw in pages_spec if doc in present]
    if Doc.BANK_STATEMENT in present:
        kept += [(Doc.BANK_STATEMENT, text, False, is_main) for text, is_main in statement_texts]
    fillers = ["TERMS AND CONDITIONS (continued)\nClause text", "THIS PAGE IS INTENTIONALLY LEFT BLANK",
               "PHOTOCOPY - REVERSE SIDE\n[no text]"]
    while len(kept) < row.pages:
        kept.append((None, rng.choice(fillers), False, False))
    rng.shuffle(kept)                                            # the tray, in whatever order
    if rng.random() < 0.7:                                       # usually the form's first page is on top
        top = next((i for i, k in enumerate(kept)
                    if k[0] == Doc.APPLICATION_FORM and "(continued)" not in k[1]), None)
        if top is not None:
            kept.insert(0, kept.pop(top))

    pages: list[Page] = []
    gt = GroundTruth(row.file_id, product, truth, present, defects)
    for number, (doc, text, hw, is_main) in enumerate(kept, start=1):
        pages.append(Page(number, text, handwritten=hw, telugu=telugu and hw))
        if doc == Doc.BANK_STATEMENT:
            gt.statement_pages.append(number)
            if is_main and salaried:
                gt.salary_page = number
    if product == "two-wheeler" and co_applicant:
        gt.fields["co_applicant_name"] = co_applicant
    bundle = LoanBundle(row.file_id, branch, product, row.channel, tuple(pages))
    return bundle, gt


def build_batch(rows: list[Any]) -> list[tuple[LoanBundle, GroundTruth]]:
    return [build_file(r) for r in rows if r.product in PRODUCTS_IN_SCOPE]
