"""Synthetic Godavari loan files: 3-page demo samples and 40-page bundles, with the truth kept apart.

A 40-page bundle is built the way a branch staples one: the application form on top, the KYC and income
pages, a split bank statement and twelve pages of loan terms in the middle in whatever order they came
out of the tray, and the sanction annexures at the back (pages 36 to 40). When the credit officer adds a
co-applicant at sanction, the co-applicant's KYC page is page 38, and the application form on page 1
still says "Co-applicant: none", because nobody refills a signed form. That is the trap.

Guntur files carry Day 6's facts: bilingual Telugu and English forms, and handwritten Telugu income
declarations that state monthly and annual income side by side with no English label.

Every name, number and document is invented. Seeded by file id, so every run is identical.
"""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass, field

PRODUCTS = ("two-wheeler", "gold", "small-business", "personal")
COMMON_FIELDS = ("applicant_name", "applicant_pan", "requested_amount", "monthly_income", "co_applicant_name")
PRODUCT_FIELD = {"two-wheeler": "on_road_price", "gold": "net_weight_g", "small-business": "business_name",
                 "personal": "employer_name"}
BRANCH_CODES = {"Kukatpally": "KKP01", "Guntur": "GNT04"}       # as in Day 11's reference data


def fields_for(product: str) -> tuple[str, ...]:
    return (*COMMON_FIELDS, PRODUCT_FIELD[product])


GIVEN = ["RAVI TEJA", "SRAVANI", "NAGA RAJU", "VENKATA RAMANA", "PADMAVATHI", "SAI KIRAN", "ANUSHA",
         "SURESH BABU", "MADHAVI LATHA", "PRASAD", "KAVYA SRI", "RAMESH", "SUNEETHA", "HARI KRISHNA"]
SURNAMES = ["PASUPULETI", "KONDAPALLI", "GADDE", "VEMULA", "BANDARU", "CHILUKURI", "YARLAGADDA",
            "KOTAGIRI", "MANDAVA", "PONNAM", "ALLURI", "NALLAMOTHU", "TADIKONDA", "UPPALAPATI"]
EMPLOYERS = ["SRI VENKATESWARA TEXTILES", "DECCAN PHARMA PACKAGING", "KRISHNA HOSPITALS", "SAPTAGIRI LOGISTICS"]
SHOPS = ["SRI DURGA KIRANA STORE", "LAKSHMI MOBILE REPAIRS", "ANNAPURNA TIFFIN CENTRE", "SAI TAILORING UNIT",
         "BALAJI AUTO SPARES"]
DEALERS = {"Kukatpally": "Sri Sai Motors (DLR-KKP-014)", "Guntur": "Amaravathi Automobiles (DLR-GNT-011)"}
RELATIONS = ["spouse", "father", "brother", "mother"]

CLAUSES = [
    "The borrower shall repay the loan in equated monthly instalments on the due date stated in the schedule.",
    "Any instalment not paid on the due date shall attract charges as set out in the schedule of charges.",
    "The borrower authorises the lender to present the NACH mandate for each instalment on the due date.",
    "The borrower shall inform the lender in writing of any change of residence or employment within 30 days.",
    "The lender may assign or transfer the loan, and the borrower's obligations continue unchanged.",
    "Nothing in this agreement prevents the borrower from prepaying the loan subject to the schedule of charges.",
    "All notices shall be sent to the address of the borrower recorded in the application form.",
    "The borrower confirms that the information in the application form is true and complete.",
    "Disputes shall be subject to the jurisdiction of the courts at the city of the sanctioning branch.",
    "The borrower has read the key fact statement and the terms in a language the borrower understands.",
]
TELUGU_HEADER = "ఆదాయ స్వీయ ధృవీకరణ పత్రం"        # income self-declaration form


@dataclass(frozen=True)
class Page:
    number: int
    text: str                     # what the OCR layer returns; the only thing a model ever sees
    doc: str                      # the true page type: hidden from the model, used only to score


@dataclass(frozen=True)
class LoanFile:
    file_id: str
    branch: str
    product: str
    pages: tuple[Page, ...]
    truth: dict[str, str]         # the analyst's answer key: field -> value ("none" for no co-applicant)
    illegible: frozenset[str] = field(default_factory=frozenset)   # fields whose printed value is smudged
    telugu_income: bool = False   # the income proof is a handwritten Telugu declaration

    @property
    def sha256(self) -> str:
        h = hashlib.sha256()
        for p in self.pages:
            h.update(p.text.encode("utf-8"))
        return h.hexdigest()


def inr(n: int) -> str:
    """85000 -> 'Rs 85,000'; 480000 -> 'Rs 4,80,000' (Indian digit grouping)."""
    s = str(n)
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        groups = []
        while len(head) > 2:
            groups.insert(0, head[-2:])
            head = head[:-2]
        if head:
            groups.insert(0, head)
        s = ",".join(groups) + "," + tail
    return f"Rs {s}"


def _smudge(rng: random.Random, printed: str) -> str:
    """Replace one digit with '?', the way a stamp or a fold eats a digit on a scan."""
    positions = [i for i, ch in enumerate(printed) if ch.isdigit()]
    i = rng.choice(positions[1:] or positions)
    return printed[:i] + "?" + printed[i + 1:]


def _pan(rng: random.Random, surname: str) -> str:
    letters = "ABCDEFGHJKLMNPQRSTUVWXYZ"
    return ("".join(rng.choice(letters) for _ in range(3)) + "P" + surname[0]
            + f"{rng.randint(1000, 9999)}" + rng.choice(letters))


def build_file(file_id: str, branch: str, product: str, *, long: bool = True, co_applicant: bool | None = None,
               telugu_income: bool | None = None, smudge_rate: float = 0.06) -> LoanFile:
    rng = random.Random(f"godavari-day13-{file_id}")
    guntur = branch == "Guntur"
    surname = rng.choice(SURNAMES)
    name = f"{rng.choice(GIVEN)} {surname}"
    pan = _pan(rng, surname)
    co = co_applicant if co_applicant is not None else (product in ("two-wheeler", "small-business")
                                                        and rng.random() < 0.35)
    co_name = f"{rng.choice([g for g in GIVEN if g not in name])} {surname}" if co else ""
    bilingual = guntur and rng.random() < 0.7
    if telugu_income is None:
        telugu_income = guntur and product == "small-business" and rng.random() < 0.85 or \
            guntur and product == "two-wheeler" and rng.random() < 0.35
    salaried = product == "personal" or (product == "two-wheeler" and not telugu_income and rng.random() < 0.6)
    income = rng.randrange(18_000, 72_000, 500)
    illegible: set[str] = set()

    truth: dict[str, str] = {"applicant_name": name, "applicant_pan": pan, "monthly_income": str(income),
                             "co_applicant_name": co_name or "none"}

    def amount_line(label: str, fld: str, value: int) -> str:
        printed = inr(value)
        if rng.random() < smudge_rate:
            illegible.add(fld)
            printed = _smudge(rng, printed)
        return f"{label}: {printed}"

    def lab(te: str, en: str) -> str:
        return f"{te} / {en}" if bilingual else en

    # --- product-specific facts --------------------------------------------------------------------
    extra_form: list[str] = []
    product_page: tuple[str, str] | None = None
    if product == "two-wheeler":
        price = rng.randrange(72_000, 165_000, 50)
        ex_showroom = int(price * 0.88) // 50 * 50
        amount = int(price * rng.uniform(0.6, 0.9)) // 500 * 500
        truth["on_road_price"] = str(price)
        product_page = ("dealer_quotation", "\n".join([
            "DEALER QUOTATION / PROFORMA INVOICE", f"Dealer: {DEALERS[branch]}", "Vehicle: scooter 110cc",
            f"Ex-showroom price: {inr(ex_showroom)}", f"Registration and insurance: {inr(price - ex_showroom)}",
            amount_line("On-road price", "on_road_price", price), "Quotation date: 02-11-2026"]))
    elif product == "gold":
        gross = rng.randint(120, 850) / 10
        net = round(gross * rng.uniform(0.86, 0.96), 1)
        amount = rng.randrange(40_000, 380_000, 500)
        truth["net_weight_g"] = f"{net:.1f}"
        product_page = ("gold_appraisal", "\n".join([
            "GOLD APPRAISAL CERTIFICATE", f"Appraiser: AP-{BRANCH_CODES[branch]}", "Items: bangles and a chain",
            f"Gross weight (g): {gross:.1f}", f"Net weight (g): {net:.1f}", "Purity (carat): 22",
            "Appraisal date: 03-11-2026"]))
    elif product == "small-business":
        shop = rng.choice(SHOPS)
        amount = rng.randrange(50_000, 300_000, 1000)
        truth["business_name"] = shop
        extra_form.append(f"{lab('వ్యాపారం పేరు', 'Business name')}: {shop}")
    else:
        amount = rng.randrange(40_000, 250_000, 1000)
    truth["requested_amount"] = str(amount)
    employer = rng.choice(EMPLOYERS)
    if product == "personal":
        truth["employer_name"] = employer

    # --- the pages ---------------------------------------------------------------------------------
    co_on_form = co_name if (co and not long) else "none"
    form = "\n".join([
        lab("రుణ దరఖాస్తు ఫారం", "LOAN APPLICATION FORM"),
        f"Godavari Finance Ltd - Branch: {branch} ({BRANCH_CODES[branch]})", f"Product: {product}",
        f"File number: {file_id}", f"{lab('దరఖాస్తుదారు పేరు', 'Applicant name')}: {name}",
        f"PAN: {pan}", amount_line(lab("రుణ మొత్తం", "Loan amount requested"), "requested_amount", amount),
        "Tenure (months): 24", *extra_form, f"{lab('సహ దరఖాస్తుదారు', 'Co-applicant')}: {co_on_form}",
        "Income: see income proof attached", "Application date: 03-11-2026", "Signature of applicant: [signed]",
    ])
    pan_card = "\n".join(["INCOME TAX DEPARTMENT - PERMANENT ACCOUNT NUMBER CARD", f"Name: {name}",
                          f"Permanent Account Number: {pan}"])
    if telugu_income:
        income_page = "\n".join([TELUGU_HEADER, "[handwritten]", f"పేరు: {name}", "వ్యాపారం: కిరాణా దుకాణం",
                                 f"నెలసరి ఆదాయం: {inr(income)}", f"సంవత్సర ఆదాయం: {inr(income * 12)}",
                                 "సంతకం: [signed]   సాక్షి: [signed]"])
    elif salaried:
        gross_pay = int(income * 1.11) // 50 * 50
        income_page = "\n".join(["INCOME PROOF", "Document: salary slip, October 2026", f"Employer: {employer}",
                                 f"Employee: {name}", f"Gross pay: {inr(gross_pay)}",
                                 f"Deductions: {inr(gross_pay - income)}",
                                 amount_line("Net pay", "monthly_income", income)])
    else:
        income_page = "\n".join(["INCOME PROOF", "Document: self-declaration of income", f"Name: {name}",
                                 amount_line("Monthly income", "monthly_income", income),
                                 f"Annual income: {inr(income * 12)}", "Signature: [signed]"])

    if not long:
        pages = [("application_form", form), ("pan_card", pan_card), ("income_proof", income_page)]
        if product_page:                     # the product's own page replaces the PAN card
            pages[1] = product_page
        return _assemble(file_id, branch, product, pages, truth, illegible, telugu_income)

    def terms(k: int) -> str:
        paras = [" ".join(rng.sample(CLAUSES, 7)) for _ in range(4)]
        return "\n".join([f"LOAN AGREEMENT - TERMS AND CONDITIONS (page {k} of 12)",
                          f"Godavari Finance Ltd | Applicant: {name} | File {file_id}", *paras])

    def statement(k: int) -> str:
        rows = [f"{rng.randint(1, 28):02d}-{rng.choice(['08', '09', '10'])} "
                f"{rng.choice(['UPI CR', 'UPI DR', 'ATM WDL', 'NEFT CR', 'POS'])} {rng.choice(SURNAMES)} "
                f"{rng.randrange(200, 9000, 10)}.00" for _ in range(45)]
        title = "STATEMENT OF ACCOUNT" + (" (continued)" if k > 1 else "")
        return "\n".join([title, "Bank: Krishna Valley Bank", f"Account holder: {name}", *rows])

    middle: list[list[tuple[str, str]]] = [
        [("photograph", f"APPLICANT PHOTOGRAPH\n[photograph of {name}]\nSigned across by the applicant")],
        [("pan_card", pan_card)],
        [("proof_of_identity", f"PROOF OF IDENTITY\nDocument: voter id\nName: {name}")],
        [("proof_of_address", f"PROOF OF ADDRESS\nDocument: aadhaar (masked)\nIn the name of: {name}")],
        [("income_proof", income_page)],
        [("bank_statement", statement(k)) for k in range(1, 5)],
        [("nach_mandate", f"NACH DEBIT MANDATE\nAccount holder: {name}\nSignature: [signed]")],
        [("field_verification", f"RESIDENCE FIELD VERIFICATION REPORT\nApplicant: {name}\nVerifier: FV-117")],
        [("customer_declaration", f"CUSTOMER DECLARATION AND CONSENT\nName: {name}\n"
                                  + " ".join(rng.sample(CLAUSES, 6)) + "\nSignature: [signed]")],
        [("terms", terms(k)) for k in range(1, 13)],
    ]
    if product_page:
        middle.append([product_page])
    fillers = ["THIS PAGE IS INTENTIONALLY LEFT BLANK", "PHOTOCOPY - REVERSE SIDE\n[no text]"]
    n_middle = sum(len(block) for block in middle)
    middle += [[("other", rng.choice(fillers))] for _ in range(33 - n_middle)]
    rng.shuffle(middle)                                        # the tray: blocks in whatever order

    co_page = (("co_applicant_kyc", "\n".join([
        "CO-APPLICANT KYC", "Added at sanction stage by the credit officer", f"Co-applicant name: {co_name}",
        f"Relationship to applicant: {rng.choice(RELATIONS)}", "Document: voter id"]))
        if co else ("other", f"DOCUMENT CHECKLIST (branch copy)\nFile {file_id}\nChecked by branch officer"))
    back = [
        ("sanction_letter", f"SANCTION LETTER\nFile {file_id}\nSanctioned subject to the terms enclosed\n"
         + " ".join(rng.sample(CLAUSES, 8))),
        ("other", f"KEY FACT STATEMENT - ACKNOWLEDGEMENT\nBorrower: {name}\n" + " ".join(rng.sample(CLAUSES, 5))
         + "\nAcknowledged: [signed]"),
        co_page,
        ("other", "SCHEDULE OF CHARGES\nAs per the lender's published schedule\n" + " ".join(rng.sample(CLAUSES, 6))),
        ("other", f"ACKNOWLEDGEMENT OF DOCUMENTS RECEIVED\nFile {file_id}\nBranch officer: [signed]"),
    ]
    pages = [("application_form", form),
             ("application_form", lab("రుణ దరఖాస్తు ఫారం", "LOAN APPLICATION FORM") + " (continued)\n"
              "Declarations by the applicant\nSignature of applicant: [signed]"),
             *[pg for block in middle for pg in block], *back]
    return _assemble(file_id, branch, product, pages, truth, illegible, telugu_income)


def _assemble(file_id: str, branch: str, product: str, pages: list[tuple[str, str]], truth: dict[str, str],
              illegible: set[str], telugu_income: bool) -> LoanFile:
    built = tuple(Page(i, text, doc) for i, (doc, text) in enumerate(pages, start=1))
    keep = set(fields_for(product))
    return LoanFile(file_id, branch, product, built, {k: v for k, v in truth.items() if k in keep},
                    frozenset(illegible & keep), telugu_income)


# --- the sets the chapter uses -------------------------------------------------------------------------

def lab_set() -> list[LoanFile]:
    """50 synthetic 40-page bundles, 30 Kukatpally and 20 Guntur: the lab experiment of section 06.

    Only a generator knows the truth for every file. On the engagement, these stand in for the fifty
    masked files the compliance head approved (Day 6); they get labels only through Day 14's golden set.
    """
    out: list[LoanFile] = []
    for i in range(50):
        branch = "Kukatpally" if i < 30 else "Guntur"
        product = ["two-wheeler", "two-wheeler", "gold", "small-business", "personal"][i % 5]
        out.append(build_file(f"GF-31{i:03d}", branch, product))
    return out


def three_page_samples() -> list[LoanFile]:
    """The vendor-demo shape: form, PAN or appraisal, income proof. Prompt v1 was written against these."""
    return [build_file(f"GF-30{i:03d}", "Kukatpally", PRODUCTS[i % 4], long=False, smudge_rate=0.0)
            for i in range(12)]


LABELLED_IDS = tuple(f"GF-32{i:03d}" for i in range(12))


def labelled_set() -> list[LoanFile]:
    """The regression check's files: 12 Kukatpally files from the thirty the branch offered and the
    analysts labelled in week 2 (milestone M05). Note what is missing: no handwritten Telugu income
    declaration, because Kukatpally does not send them. Day 14 builds the real golden set."""
    plan = [("two-wheeler", True), ("two-wheeler", False), ("two-wheeler", True), ("gold", False),
            ("small-business", True), ("personal", False), ("two-wheeler", False), ("gold", False),
            ("small-business", False), ("personal", False), ("two-wheeler", True), ("small-business", True)]
    return [build_file(fid, "Kukatpally", product, co_applicant=co, telugu_income=False)
            for fid, (product, co) in zip(LABELLED_IDS, plan)]


def guntur_replay() -> list[LoanFile]:
    """20 recent Guntur files (the branch manager offered them in Day 6), replayed against a candidate
    release with the values analysts keyed into the core system as the answer key."""
    products = ["small-business", "two-wheeler", "small-business", "gold", "two-wheeler"]
    return [build_file(f"GF-33{i:03d}", "Guntur", products[i % 5]) for i in range(20)]
