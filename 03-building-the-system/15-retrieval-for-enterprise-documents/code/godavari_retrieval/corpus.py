"""The synthetic Godavari corpus: circulars with versions, product rulebooks, RBI digests and 300
masked loan-file decision summaries, rendered the way a PDF text extractor hands them to you.

Everything is invented and seeded. Two layers come out of this module, on purpose:

* ``Document`` holds the REGISTER entry (what the compliance head's circular register or the
  document-management system says about the document: type, product, dates, supersession, approval,
  branch). Metadata comes from there, not from guessing at the text.
* ``pages`` hold the TEXT as extracted: repeated headers and footers, page numbers, a rotated stamp
  read as junk, OCR letter confusions on the scanned ones, words hyphenated across lines, tables that
  run over a page break. The chunker only ever sees the pages.

The product rulebook numbers are generated from Day 11's signed rule constants, imported by path, so
the text an analyst reads cannot drift from the rule the code enforces.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import date, timedelta

from .day11 import BRANCH_CODES, EMPANELLED_DEALERS, rules_gold, rules_two_wheeler
from .text import pan_token

AS_OF = date(2026, 11, 25)       # Wednesday of engagement week 5: the day the demo and the eval run
SEED = 15
PAGE_BODY_LINES = 14             # body lines per rendered page
WRAP = 92                        # characters per line

BRANCHES = tuple(BRANCH_CODES)   # Kukatpally, Dilsukhnagar, Vijayawada-Benz Circle, Guntur, Warangal, Rajahmundry


# ----------------------------------------------------------------------------------------------- model
@dataclass(frozen=True)
class Clause:
    number: str
    text: str


@dataclass(frozen=True)
class Table:
    number: str                       # the clause the table belongs to, e.g. "4.2"
    caption: str
    header: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]


@dataclass(frozen=True)
class Section:
    number: str
    heading: str
    items: tuple[Clause | Table, ...]


@dataclass
class Document:
    doc_id: str
    title: str
    doc_type: str                     # circular, rulebook, annex, rbi_digest, loan_decision
    product: str                      # all, two-wheeler, gold, small-business
    language: str                     # en, mixed (English and Telugu script), te-latn (Telugu in Latin letters)
    issued: date
    effective_from: date
    effective_to: date | None = None
    supersedes: str | None = None
    superseded_by: str | None = None
    approval_status: str = "approved" # approved, draft
    approved_by: str = "compliance head"
    branch: str | None = None         # loan files only
    scanned: bool = False
    series: str = ""
    sections: list[Section] = field(default_factory=list)
    body_lines: list[str] = field(default_factory=list)       # loan decisions: plain lines
    pages: list[list[str]] = field(default_factory=list)
    extra: dict[str, str] = field(default_factory=dict)


def _d(s: str) -> date:
    return date.fromisoformat(s)


def _purpose(t: str) -> Section:
    return Section("1", "Purpose", (Clause("1.1", f"This circular sets out {t} for all branches and for credit "
                                                  "operations in Hyderabad and Vijayawada."),))


# ------------------------------------------------------------------------------------- rich circulars
def _rich_circulars() -> list[Document]:
    tw = rules_two_wheeler
    docs: list[Document] = []

    def circ(doc_id: str, title: str, product: str, issued: str, eff: str, sections: list[Section],
             series: str, language: str = "en", scanned: bool = False) -> None:
        docs.append(Document(doc_id, title, "circular", product, language, _d(issued), _d(eff), series=series,
                             scanned=scanned, sections=sections))

    # S-AADHAAR: the masking rule that changed in 2025 while three branches kept sending unmasked copies.
    circ("GFL/CO/2024/007", "Masking of Aadhaar numbers in KYC copies", "all", "2024-01-22", "2024-02-01", [
        _purpose("how Aadhaar copies are handled in loan files"),
        Section("2", "Rules", (
            Clause("2.1", "Where the customer offers proof of possession of Aadhaar, the branch should mask the Aadhaar "
                          "number on the copy before it is added to the loan file."),
            Clause("2.2", "If the customer has already given an unmasked copy, the branch may keep it in the file with "
                          "the customer's written consent, and the copy is stored in the physical file only."),
            Clause("2.3", "Credit operations analysts note unmasked copies in the tracker but do not return the file "
                          "for this reason alone."),
        )),
    ], series="S-AADHAAR", scanned=True)
    circ("GFL/CO/2025/012", "Masking of Aadhaar numbers in KYC copies (revised)", "all", "2025-05-19", "2025-06-01", [
        _purpose("how Aadhaar copies are handled in loan files"),
        Section("2", "Rules", (
            Clause("2.1", "The first eight digits of the Aadhaar number must be masked on every copy before the copy "
                          "enters the loan file, whether the copy is paper, a scan or a photograph."),
            Clause("2.2", "An unmasked Aadhaar copy is not kept with consent. The branch masks it and re-scans it; an "
                          "unmasked copy that reaches credit operations is returned to the branch the same day."),
            Clause("2.3", "Analysts must not upload or forward an unmasked copy to any system, including email."),
        )),
        Section("3", "Summary for branch staff", (
            Clause("3.1", "ఆధార్ కాపీలో మొదటి ఎనిమిది అంకెలు తప్పనిసరిగా మాస్క్ చేయాలి. మాస్క్ చేయని కాపీని అదే రోజు "
                          "బ్రాంచికి తిరిగి పంపాలి."),
        )),
    ], series="S-AADHAAR", language="mixed")

    # S-TW-INCOME: the analyst's question. The 2025 version has the table that runs over a page break.
    circ("GFL/CO/2024/015", "Income proof for two-wheeler loans", "two-wheeler", "2024-03-20", "2024-04-01", [
        _purpose("the income proof accepted for two-wheeler loans"),
        Section("2", "Income proof", (
            Clause("2.1", "Salaried applicants give the last three salary slips and a six-month bank statement of the "
                          "salary account."),
            Clause("2.2", "Self-employed applicants give income tax returns for the last two assessment years. No "
                          "other income proof is accepted from a self-employed applicant."),
            Clause("2.3", "Applicants whose income is from agriculture are not eligible for a two-wheeler loan under "
                          "this circular."),
        )),
    ], series="S-TW-INCOME", scanned=True)
    circ("GFL/CO/2025/027", "Income proof for two-wheeler loans by applicant type", "two-wheeler", "2025-03-18",
         "2025-04-01", [
        _purpose("the income proof accepted for two-wheeler loans, by the type of applicant"),
        Section("2", "Scope", (
            Clause("2.1", "The rules apply to every two-wheeler application received on or after the effective date, "
                          "including files returned to a branch and resubmitted."),
            Clause("2.2", "Where an applicant fits two types, the analyst applies the row for the main source of "
                          "income and records the reason in the file."),
            Clause("2.3", "The requested amount and the finance percentage are checked separately under the "
                          "two-wheeler product rulebook; this circular covers only income proof."),
        )),
        Section("3", "General conditions", (
            Clause("3.1", "Every income document must be legible, must name the applicant, and must be in the file of "
                          "record. A photograph received on a personal phone is not part of the file of record."),
            Clause("3.2", "A bank statement must be the full statement for the period, every page, as issued by the "
                          "bank or downloaded from the bank's portal; a passbook is accepted only if every page for "
                          "the period is present."),
            Clause("3.3", "Self-declarations are on the Godavari format, signed by the applicant, and countersigned by "
                          "the branch manager where this circular says so."),
        )),
        Section("4", "Income proof by applicant type", (
            Clause("4.1", "The table below lists the income proof accepted for each type of applicant. Any one "
                          "complete option in the second column is enough."),
            Table("4.2", "Table 1: Income proof by applicant type", ("Applicant type", "Acceptable income proof",
                                                                     "Conditions"), (
                ("Salaried", "last three salary slips and the bank statement of the salary account for three months",
                 "statement ends within 30 days before the application"),
                ("Self-employed (shop owner, trader, kirana shop)",
                 "twelve-month bank statement of the business account, or GST returns for the last four quarters",
                 "a self-declaration of income is also accepted when the requested amount is below Rs 1,00,000 and a "
                 "field visit confirms the business"),
                ("Self-employed professional (doctor, lawyer, chartered accountant)",
                 "income tax returns for the last two assessment years", "computation of income attached"),
                ("Agriculture", "land record (pahani or adangal) in the applicant's name and a self-declaration of "
                                "crop income", "self-declaration countersigned by the branch manager"),
                ("Pensioner", "pension payment order and bank statement for three months showing the pension credit",
                 "pension must continue for the loan tenure"),
                ("Gig or delivery worker", "platform payout statements for six months and the bank statement for the "
                                           "same period", "payouts in at least five of the six months"),
            )),
        )),
        Section("5", "Summary for branch staff", (
            Clause("5.1", "ఆదాయ రుజువు: స్వయం ఉపాధి దరఖాస్తుదారులు 12 నెలల బ్యాంకు ఖాతా వివరాలు లేదా నాలుగు "
                          "త్రైమాసికాల జీఎస్టీ రిటర్నులు ఇవ్వాలి."),
        )),
    ], series="S-TW-INCOME", language="mixed")

    # S-STMT and S-QUOTE: the numbers come from Day 11's two-wheeler rule constants.
    circ("GFL/CO/2024/021", "Bank statement period for salaried applicants", "all", "2024-05-06", "2024-05-15", [
        _purpose("the bank statement period required from salaried applicants"),
        Section("2", "Rules", (
            Clause("2.1", "Salaried applicants give a bank statement of the salary account covering the last six "
                          "months."),
            Clause("2.2", "The statement may end up to 60 days before the application date."))),
    ], series="S-STMT", scanned=True)
    circ("GFL/CO/2025/033", "Bank statement period for salaried applicants (revised)", "all", "2025-07-01",
         "2025-07-15", [
        _purpose("the bank statement period required from salaried applicants"),
        Section("2", "Rules", (
            Clause("2.1", "Salaried applicants give a bank statement of the salary account covering about three "
                          f"months, at least {tw.STATEMENT_MIN_SPAN_DAYS} days."),
            Clause("2.2", f"The statement must end within {tw.STATEMENT_MAX_GAP_DAYS} days before the application "
                          "date."))),
    ], series="S-STMT")
    circ("GFL/CO/2024/018", "Validity of dealer quotations", "two-wheeler", "2024-04-10", "2024-04-15", [
        _purpose("how long a dealer quotation stays valid"),
        Section("2", "Rules", (
            Clause("2.1", "A dealer quotation or proforma invoice is valid for 15 days from its date."),
            Clause("2.2", "Quotations are accepted only from empanelled dealers of the branch."))),
    ], series="S-QUOTE")
    circ("GFL/CO/2025/019", "Validity of dealer quotations (revised)", "two-wheeler", "2025-02-24", "2025-03-01", [
        _purpose("how long a dealer quotation stays valid"),
        Section("2", "Rules", (
            Clause("2.1", f"A dealer quotation or proforma invoice is valid for {tw.QUOTATION_MAX_AGE_DAYS} days from "
                          "its date."),
            Clause("2.2", "Quotations are accepted only from dealers empanelled with the branch that sources the file; "
                          "the dealer code is written on the quotation."))),
    ], series="S-QUOTE")

    # S-GOLD-LTV: flat 75 percent, then the tiered caps Day 11 enforces.
    circ("GFL/CO/2024/011", "Loan to value for gold loans", "gold", "2024-03-01", "2024-03-01", [
        _purpose("the loan to value (LTV) limit for gold loans"),
        Section("2", "Rules", (
            Clause("2.1", "The gold loan amount must not exceed 75 percent of the value of the gold, computed at the "
                          "22-carat rate published by treasury for the appraisal date."),)),
    ], series="S-GOLD-LTV", scanned=True)
    tiers = rules_gold.LTV_TIERS
    circ("GFL/CO/2026/009", "Loan to value for gold loans (tiered caps)", "gold", "2026-03-16", "2026-04-01", [
        _purpose("the tiered loan to value (LTV) caps for gold loans, following the RBI directions on lending "
                 "against gold collateral (2025)"),
        Section("2", "Rules", (
            Clause("2.1", "The LTV cap depends on the loan amount and is checked by the system against the signed "
                          "rule; the analyst does not compute it by hand."),
            Table("2.2", "Table 1: LTV cap by loan amount", ("Loan amount", "Maximum LTV"), (
                (f"up to Rs {tiers[0][0]:,}", f"{tiers[0][1]} percent"),
                (f"above Rs {tiers[0][0]:,} and up to Rs {tiers[1][0]:,}", f"{tiers[1][1]} percent"),
                (f"above Rs {tiers[1][0]:,}", f"{tiers[2][1]} percent"),
            )),
            Clause("2.3", "Value is computed at the 22-carat rate published by treasury for the appraisal date."),
        )),
    ], series="S-GOLD-LTV")
    circ("GFL/CO/2025/046", "Gold appraisal and purity", "gold", "2025-08-04", "2025-08-11", [
        _purpose("the appraisal requirements for gold loans"),
        Section("2", "Rules", (
            Clause("2.1", f"Gold of {rules_gold.MIN_PURITY} to {rules_gold.MAX_PURITY} carat purity is accepted; the "
                          "appraiser records gross weight, net weight and purity."),
            Clause("2.2", f"The appraisal must be 0 to {rules_gold.APPRAISAL_MAX_AGE_DAYS} days before the "
                          "application date."),
            Clause("2.3", f"Gold loan tenure is at most {rules_gold.MAX_TENURE} months."))),
    ], series="S-GOLD-APPRAISAL")

    # S-COAPP, S-PAN, S-TW-AGE.
    circ("GFL/CO/2024/026", "Co-applicants on two-wheeler loans", "two-wheeler", "2024-06-03", "2024-06-10", [
        _purpose("when a co-applicant is needed"),
        Section("2", "Rules", (
            Clause("2.1", "A co-applicant is optional for loans below Rs 1,00,000."),
            Clause("2.2", "Where a co-applicant is added, a copy of the co-applicant's PAN card is enough."))),
    ], series="S-COAPP")
    circ("GFL/CO/2025/038", "Co-applicants on two-wheeler loans (revised)", "two-wheeler", "2025-09-08", "2025-09-15", [
        _purpose("when a co-applicant is needed and what KYC the co-applicant gives"),
        Section("2", "Rules", (
            Clause("2.1", "Where the co-applicant's income is counted towards eligibility, the co-applicant KYC "
                          "annexure is mandatory, with identity proof, address proof, photograph and PAN or Form 60."),
            Clause("2.2", "A co-applicant added at sanction is recorded on the KYC annexure; the application form need "
                          "not be re-signed."))),
    ], series="S-COAPP")
    circ("GFL/CO/2024/004", "PAN or Form 60", "all", "2024-01-08", "2024-01-15", [
        _purpose("the PAN requirement"),
        Section("2", "Rules", (Clause("2.1", "Every applicant gives a PAN card copy."),)),
    ], series="S-PAN")
    circ("GFL/CO/2025/041", "PAN or Form 60 (revised)", "all", "2025-10-06", "2025-10-13", [
        _purpose("the PAN requirement and the Form 60 alternative"),
        Section("2", "Rules", (
            Clause("2.1", "Every applicant gives a PAN card copy, or Form 60 where the applicant does not have a PAN."),
            Clause("2.2", "The PAN is verified against the income tax department's records before sanction; a "
                          "mismatch in name or date of birth sends the file to review."))),
    ], series="S-PAN")
    circ("GFL/CO/2024/031", "Age and tenure limits for two-wheeler loans", "two-wheeler", "2024-07-01", "2024-07-08", [
        _purpose("the age and tenure limits for two-wheeler loans"),
        Section("2", "Rules", (
            Clause("2.1", "The applicant is 21 to 58 years old on the application date."),
            Clause("2.2", "Tenure is 12 to 36 months."))),
    ], series="S-TW-AGE")
    circ("GFL/CO/2025/049", "Age and tenure limits for two-wheeler loans (revised)", "two-wheeler", "2025-11-03",
         "2025-11-10", [
        _purpose("the age and tenure limits for two-wheeler loans"),
        Section("2", "Rules", (
            Clause("2.1", f"The applicant is {tw.MIN_AGE} to {tw.MAX_AGE} years old on the application date."),
            Clause("2.2", f"Tenure is {tw.MIN_TENURE} to {tw.MAX_TENURE} months."))),
    ], series="S-TW-AGE")

    circ("GFL/CO/2025/029", "Field verification for self-employed applicants", "two-wheeler", "2025-04-21",
         "2025-05-01", [
        _purpose("when a field visit is needed"),
        Section("2", "Rules", (
            Clause("2.1", "A field visit to the place of business is mandatory where a self-employed applicant's "
                          "income is accepted on a self-declaration."),
            Clause("2.2", "The visit report records the shop name, the photograph of the premises with the applicant, "
                          "and the visiting officer's name and date."))),
    ], series="S-FIELD")
    circ("GFL/CO/2025/050", "Documents for small-business loans", "small-business", "2025-11-17", "2025-11-24", [
        _purpose("the sixteen documents for a small-business loan"),
        Section("2", "Rules", (
            Clause("2.1", "A small-business loan file has sixteen documents, listed in the small-business rulebook, "
                          "including the GST registration and twelve months of business bank statements."),
            Clause("2.2", "Udyam registration is accepted as proof of business existence."))),
    ], series="S-SB-DOCS")
    circ("GFL/CO/2025/052", "Documents received on personal phones", "all", "2025-12-01", "2025-12-08", [
        _purpose("how documents sent to staff on messaging apps are treated"),
        Section("2", "Rules", (
            Clause("2.1", "A document received on a staff member's personal phone, including by WhatsApp, is not part "
                          "of the file of record and must not be printed into the file."),
            Clause("2.2", "The branch asks the customer to submit the document at the branch or through the official "
                          "upload link, and the file waits for it."))),
        Section("3", "Summary for branch staff", (Clause("3.1", "వాట్సాప్ ద్వారా వచ్చిన పత్రాలు ఫైల్ లో భాగం కావు."),)),
    ], series="S-PHONE", language="mixed")
    return docs


# ----------------------------------------------------------------------------- the other circulars
# (series, title, product, facts with {n}, n for each version, issue date of each version)
_FILLERS: list[tuple[str, str, str, list[str], tuple[int, ...], tuple[str, ...]]] = [
    ("S-GRIEV", "Grievance redressal at branches", "all",
     ["Every branch displays the name and phone number of the grievance redressal officer.",
      "A complaint is acknowledged within {n} working days.",
      "Complaints not resolved in 30 days are escalated to the head office nodal officer."], (3, 2),
     ("2024-02-12", "2025-08-18")),
    ("S-FPC", "Fair practices code: communication in the customer's language", "all",
     ["The sanction letter and the key fact statement are given in English and in Telugu.",
      "The branch explains the charges to the customer before signature.",
      "Changes to charges are notified {n} days in advance."], (30,), ("2024-09-02",)),
    ("S-CHARGES", "Display of interest rates and charges", "all",
     ["Every branch displays the current interest rate band and processing fee on the notice board.",
      "The processing fee is at most {n} percent of the loan amount."], (2, 1), ("2024-04-01", "2025-04-01")),
    ("S-FORECLOSE", "Foreclosure of loans", "all",
     ["Foreclosure is allowed after {n} instalments are paid.",
      "The foreclosure statement is issued within three working days of the request."], (6, 3),
     ("2024-05-20", "2025-06-16")),
    ("S-RECOVERY", "Conduct of recovery agents", "all",
     ["Recovery agents carry the authorisation letter and identity card issued by Godavari.",
      "Calls to customers are made only between 8 am and 7 pm.",
      "Each agent completes conduct training every {n} months."], (12, 6), ("2024-03-11", "2025-03-10")),
    ("S-CASH", "Cash handling at branches", "all",
     ["Cash above Rs {n} is deposited in the bank the same day.", "Two staff members count the cash at closing."],
     (50000, 25000), ("2024-01-29", "2025-01-27")),
    ("S-FRAUD", "Reporting suspected fraud", "all",
     ["Suspected fraud is reported to the head office fraud desk within {n} hours.",
      "The branch preserves the original documents and does not return them to the customer."], (48, 24),
     ("2024-06-17", "2025-07-21")),
    ("S-CERSAI", "Registration of security interest", "all",
     ["The security interest is registered with the central registry within {n} days of disbursement."], (30,),
     ("2024-08-05",)),
    ("S-INSURANCE", "Insurance offered with loans", "all",
     ["Insurance is offered, never imposed; the customer signs a separate consent.",
      "The consent form states that the loan does not depend on buying insurance.",
      "The branch keeps the consent for {n} years."], (5, 8), ("2024-02-26", "2025-02-24")),
    ("S-NPA", "Overdue follow-up and NPA classification", "all",
     ["An account overdue for more than {n} days is classified as a non-performing asset.",
      "The branch calls the customer on the first day an instalment is missed."], (90,),
     ("2024-04-22",)),
    ("S-TAT", "Turnaround time and accountability", "all",
     ["Credit operations opens every complete file within {n} working days of receipt.",
      "Files waiting for a document are marked as waiting in the tracker with the date asked."], (3,),
     ("2024-10-07",)),
    ("S-RETENTION", "Retention of loan records", "all",
     ["Loan files, decisions and the documents relied on are kept for at least {n} years after the loan is closed.",
      "Records of who viewed a loan file are kept for the same period."], (5, 7), ("2024-01-15", "2025-05-05")),
    ("S-PRIVACY", "Customer data on personal devices", "all",
     ["Customer documents are never stored on personal phones or personal email.",
      "Staff delete any customer document received on a personal device within {n} hours and inform the branch "
      "manager."], (48, 24), ("2024-11-11", "2025-09-29")),
    ("S-AUDIT", "Branch audit checklist", "all",
     ["The internal auditor samples {n} loan files per branch per quarter.",
      "The branch closes audit observations within 30 days."], (20,), ("2024-07-15",)),
    ("S-PAYOUT", "Disbursement to dealers", "two-wheeler",
     ["Disbursement is made only to the dealer's registered bank account.",
      "The dealer delivers the vehicle within {n} days of disbursement and shares the invoice and registration "
      "copy."], (7,), ("2024-09-23",)),
    ("S-SANCTION", "Sanction before disbursement", "all",
     ["No disbursement is made before the sanction date recorded in the core system.",
      "Disbursement happens within {n} days of sanction; later disbursements need a fresh sanction."], (30,),
     ("2024-05-13",)),
    ("S-BUREAU", "Credit bureau checks", "all",
     ["The customer's written consent is taken before a credit bureau check.",
      "A bureau report older than {n} days is refreshed before sanction."], (30, 15), ("2024-03-25", "2025-10-20")),
    ("S-HYPO", "Hypothecation endorsement on vehicle registration", "two-wheeler",
     ["The registration certificate carries Godavari's hypothecation endorsement.",
      "The branch follows up the endorsement within {n} days of delivery."], (30,), ("2024-12-02",)),
    ("S-VAULT", "Gold packet sealing and vault custody", "gold",
     ["Each gold packet is sealed in the customer's presence and signed across the seal.",
      "The vault register is reconciled every {n} days."], (7,), ("2024-06-24",)),
    ("S-AUCTION", "Auction of pledged gold", "gold",
     ["An auction notice is sent at least {n} days before the auction date.", "The notice is in English and in Telugu."],
     (14, 21), ("2024-10-14", "2025-10-13")),
    ("S-TELUGU", "Customer communication in Telugu", "all",
     ["Every customer letter has a Telugu version.",
      "Calls are made in the customer's preferred language; at least {n} staff per branch speak Telugu."], (2,),
     ("2024-08-26",)),
    ("S-HOLIDAY", "Branch working on festival holidays", "all",
     ["Branches remain closed on Sankranti; files received in the {n} days before are opened first after the "
      "holiday."], (2,), ("2024-12-16",)),
    ("S-SB-GST", "GST verification for small-business loans", "small-business",
     ["The GST registration is verified on the GST portal before sanction.",
      "GST returns for the last {n} quarters are checked for filing gaps."], (4,), ("2025-01-13",)),
    ("S-PEP", "Screening for politically exposed persons", "all",
     ["Every applicant is screened against the politically exposed persons list before sanction.",
      "A match is referred to the compliance head within {n} working day."], (1,), ("2024-02-05",)),
    ("S-ACCESS", "Access to loan files by branch", "all",
     ["Staff see loan files only for the branches in their Active Directory groups.",
      "Access to another branch's files needs a ticket approved by the CISO's office and is removed within {n} days "
      "of the need ending."], (7, 2), ("2024-04-08", "2025-08-11")),
    ("S-CIRCULARS", "Distribution of circulars", "all",
     ["Circulars are published on the intranet register maintained by the compliance head.",
      "Each branch acknowledges a new circular within {n} working days; printed copies are uncontrolled."], (5, 3),
     ("2024-01-02", "2025-01-06")),
    ("S-VKYC", "Video-based customer identification", "all",
     ["Video-based customer identification is done only by trained head office staff.",
      "The recording is kept for {n} years."], (8,), ("2024-09-09",)),
    ("S-DEDUPE", "Duplicate applications", "all",
     ["Before a new file is created the analyst searches the core system by PAN for an open application.",
      "A second open application for the same applicant and product within {n} days is returned to the branch."],
     (30,), ("2025-06-02",)),
]


def _filler_circulars() -> list[Document]:
    docs: list[Document] = []
    counter: dict[int, int] = {}
    for series, title, product, facts, ns, issued in _FILLERS:
        prev: Document | None = None
        for v, (n, iss) in enumerate(zip(ns, issued), start=1):
            year = int(iss[:4])
            counter[year] = counter.get(year, 55) + 1           # 056 onwards: clear of the rich circulars
            doc_id = f"GFL/CO/{year}/{counter[year]:03d}"
            eff = date.fromisoformat(iss) + timedelta(days=7)
            t = title if v == 1 else f"{title} (revised)"
            secs = [
                Section("1", "Purpose", (Clause("1.1", f"This circular sets out the rules on "
                                                       f"{title[0].lower() + title[1:]} for all branches."),)),
                Section("2", "Rules", tuple(Clause(f"2.{i}", f.format(n=n)) for i, f in enumerate(facts, start=1))),
                Section("3", "Responsibility", (Clause("3.1", "Branch managers ensure compliance; credit operations "
                                                              "reports exceptions to the compliance head every "
                                                              "month."),)),
            ]
            d = Document(doc_id, t, "circular", product, "en", date.fromisoformat(iss), eff, series=series,
                         sections=secs, scanned=(v == 1 and len(ns) > 1 and len(docs) % 3 == 0))
            if prev is not None:
                prev.effective_to, prev.superseded_by, d.supersedes = d.effective_from, d.doc_id, prev.doc_id
            docs.append(d)
            prev = d
    return docs


def _link_versions(docs: list[Document]) -> None:
    by_series: dict[str, list[Document]] = {}
    for d in docs:
        by_series.setdefault(d.series, []).append(d)
    for versions in by_series.values():
        versions.sort(key=lambda x: x.effective_from)
        for old, new in zip(versions, versions[1:]):
            old.effective_to, old.superseded_by, new.supersedes = new.effective_from, new.doc_id, old.doc_id


# ------------------------------------------------------------------- rulebooks, annex, digests, draft
def _rulebooks_and_others() -> list[Document]:
    tw, gl = rules_two_wheeler, rules_gold
    old = Document("GFL/RB/2024/001", "Two-wheeler loan product rulebook (2024)", "rulebook", "two-wheeler", "en",
                   _d("2024-03-25"), _d("2024-04-01"), series="RB-TW", scanned=True, sections=[
        Section("1", "Eligibility", (
            Clause("1.1", "Loan amount Rs 20,000 to Rs 2,50,000; finance up to 85 percent of the on-road price."),
            Clause("1.2", "Applicant 21 to 58 years old; tenure 12 to 36 months."))),
        Section("2", "Documents", (
            Clause("2.1", "Fourteen documents as listed in the 2024 checklist; the dealer quotation is valid for 15 "
                          "days."),
            Clause("2.2", "Bank statement for six months for salaried applicants."))),
    ])
    new = Document("GFL/RB/2026/001", "Two-wheeler loan product rulebook (2026)", "rulebook", "two-wheeler", "en",
                   _d("2026-01-12"), _d("2026-01-19"), series="RB-TW", sections=[
        Section("1", "Eligibility", (
            Clause("1.1", f"Loan amount Rs {tw.MIN_AMOUNT:,} to Rs {tw.MAX_AMOUNT:,}; finance up to "
                          f"{tw.MAX_FINANCE_PERCENT} percent of the on-road price, so the customer brings at least "
                          f"{100 - tw.MAX_FINANCE_PERCENT} percent."),
            Clause("1.2", f"Applicant {tw.MIN_AGE} to {tw.MAX_AGE} years old on the application date; tenure "
                          f"{tw.MIN_TENURE} to {tw.MAX_TENURE} months."))),
        Section("2", "Documents", (
            Clause("2.1", f"Fourteen documents as listed in the signed checklist; the dealer quotation is valid for "
                          f"{tw.QUOTATION_MAX_AGE_DAYS} days."),
            Clause("2.2", "Income proof by applicant type is set by circular GFL/CO/2025/027; address proof "
                          "alternatives by annex GFL/CMP/2026/004."))),
        Section("3", "Who decides", (
            Clause("3.1", "Every file is decided by a named analyst. The system checks the rules and shows the "
                          "evidence; it does not approve a file."),)),
    ])
    gold = Document("GFL/RB/2026/002", "Gold loan product rulebook (2026)", "rulebook", "gold", "en",
                    _d("2026-03-23"), _d("2026-04-01"), series="RB-GOLD", sections=[
        Section("1", "Eligibility", (
            Clause("1.1", f"Tenure at most {gl.MAX_TENURE} months; purity {gl.MIN_PURITY} to {gl.MAX_PURITY} carat; "
                          "LTV caps as in circular GFL/CO/2026/009."),)),
        Section("2", "Documents", (
            Clause("2.1", "Nine documents as listed in the signed checklist, including the appraisal certificate and "
                          "the KYC documents."),)),
    ])
    sb = Document("GFL/RB/2025/003", "Small-business loan product rulebook (2025)", "rulebook", "small-business", "en",
                  _d("2025-11-17"), _d("2025-11-24"), series="RB-SB", sections=[
        Section("1", "Documents", (
            Clause("1.1", "Sixteen documents, including GST registration, Udyam registration if available, twelve "
                          "months of business bank statements and the last two years' financial statements."),)),
    ])
    annex = Document("GFL/CMP/2026/004", "Acceptable alternatives for proof of address", "annex", "all", "mixed",
                     _d("2026-11-20"), _d("2026-11-23"), series="ANNEX-ADDR", sections=[
        Section("1", "Purpose", (
            Clause("1.1", "This annex writes down the address proof alternatives that analysts have applied by "
                          "judgement, so that every analyst applies the same list. It is signed by the compliance "
                          "head."),)),
        Section("2", "Alternatives", (
            Table("2.1", "Table 1: Address proof alternatives", ("Document offered", "Accepted?", "Condition"), (
                ("Rent agreement, registered or notarised", "accepted",
                 "with an electricity, water or piped gas bill in the landlord's name for the same address, not older "
                 "than two months"),
                ("Rent agreement, unregistered and not notarised", "not accepted alone",
                 "accepted with a utility bill in the applicant's own name at the address"),
                ("Gas or electricity bill in the father's or spouse's name", "accepted",
                 "with proof of the relationship, such as a ration card or marriage certificate"),
                ("Bank passbook with address", "accepted",
                 "printed by the bank, with the branch seal, not older than three months"),
                ("Letter from employer", "accepted",
                 "for salaried applicants staying in employer accommodation, on letterhead"),
            )),
        )),
        Section("3", "Summary for branch staff", (
            Clause("3.1", "చిరునామా రుజువు: అద్దె ఒప్పందం తో పాటు యజమాని పేరు మీద విద్యుత్ బిల్లు "
                          "అంగీకరించబడుతుంది."),)),
    ])
    kyc = Document("GFL/RBI/2025/001", "Digest: RBI Master Direction on KYC (approved for analysts)", "rbi_digest",
                   "all", "en", _d("2025-02-03"), _d("2025-02-10"), series="RBI-KYC", sections=[
        Section("1", "Status of this digest", (
            Clause("1.1", "A paraphrase prepared by Godavari compliance for analysts. The Master Direction text on the "
                          "RBI website prevails."),)),
        Section("2", "Officially valid documents", (
            Clause("2.1", "Officially valid documents for identity and address are the passport, the driving licence, "
                          "proof of possession of Aadhaar, the voter identity card, the NREGA job card, and the letter "
                          "of the National Population Register."),
            Clause("2.2", "Where proof of possession of Aadhaar is used, the Aadhaar number is redacted or blacked out "
                          "on the copy kept."),
            Clause("2.3", "Where the officially valid document does not show the current address, a utility bill not "
                          "older than two months, a property or municipal tax receipt, or a pension payment order may "
                          "be accepted for the address, and the customer gives an updated officially valid document "
                          "within three months."))),
    ])
    gold_rbi = Document("GFL/RBI/2026/002", "Digest: RBI directions on lending against gold collateral (approved for "
                        "analysts)", "rbi_digest", "gold", "en", _d("2026-03-09"), _d("2026-03-16"), series="RBI-GOLD",
                        sections=[
        Section("1", "Status of this digest", (
            Clause("1.1", "A paraphrase prepared by Godavari compliance. The directions on the RBI website prevail; "
                          "the caps Godavari applies are in circular GFL/CO/2026/009."),)),
        Section("2", "Summary", (
            Clause("2.1", "Loan to value is capped in tiers by loan amount; the valuation uses a published rate for "
                          "the purity of the gold; the lender returns the pledged gold promptly on repayment."),)),
    ])
    fpc = Document("GFL/RBI/2024/003", "Digest: RBI fair practices code for NBFCs (approved for analysts)",
                   "rbi_digest", "all", "en", _d("2024-06-03"), _d("2024-06-10"), series="RBI-FPC", sections=[
        Section("1", "Summary", (
            Clause("1.1", "Loan terms are communicated in a language the borrower understands; reasons for rejection "
                          "are communicated in writing; charges are disclosed before sanction."),)),
    ])
    draft = Document("GFL/CO/2026/041", "Video-based KYC for repeat customers (draft)", "circular", "all", "en",
                     _d("2026-11-16"), _d("2026-11-16"), series="S-VKYC-REPEAT", approval_status="draft",
                     approved_by="", sections=[
        Section("1", "Purpose", (
            Clause("1.1", "DRAFT for the compliance head, proposed to take effect from 1 December 2026. Proposes that repeat customers with a closed loan in good "
                          "standing may complete KYC by video without visiting the branch."),)),
    ])
    return [old, new, gold, sb, annex, kyc, gold_rbi, fpc, draft]


def policy_documents() -> list[Document]:
    rich = _rich_circulars()
    others = _rulebooks_and_others()
    _link_versions(rich + [d for d in others if d.series == "RB-TW"])
    fillers = _filler_circulars()
    ids = [d.doc_id for d in rich + fillers + others]
    assert len(ids) == len(set(ids)), "circular number collision"
    return rich + fillers + others


# ------------------------------------------------------------------------- 300 loan-file decisions
_APPLICANT_TYPES = (("salaried", 0.45), ("self-employed", 0.30), ("agriculture", 0.12), ("pensioner", 0.06),
                    ("gig worker", 0.07))
_INCOME = {
    "salaried": ["last three salary slips and three-month salary account statement"],
    "self-employed": ["twelve-month bank statement of the business account", "GST returns for four quarters",
                      "self-declaration with field visit report"],
    "agriculture": ["pahani land record and self-declaration countersigned by the branch manager",
                    "adangal land record and self-declaration"],
    "pensioner": ["pension payment order and three-month statement"],
    "gig worker": ["six months of platform payout statements and bank statement"],
}
_ADDRESS = ["masked Aadhaar copy", "voter identity card", "driving licence", "passport",
            "rent agreement (notarised) with landlord's water bill", "gas bill in father's name with ration card",
            "bank passbook with address"]
TELUGU_LATN_VARIANTS = {   # spellings different staff use for the same Telugu words
    "income": ["aadaayam", "aadayam", "adayam"], "salary": ["jeetham", "jitham", "jeetam"],
    "shop": ["kirana kottu", "kiraana kottu"], "farming": ["vyavasaayam", "vyavasayam"],
    "month": ["nelaki", "nelaku"], "rent": ["adde", "addhe"],
}
_REASONS = {
    "approved": ["all documents present and consistent", "income proof accepted under the applicant-type table",
                 "approved after field visit confirmed the business"],
    "sent back": ["bank statement incomplete, pages missing", "address proof not on the accepted list",
                  "dealer quotation older than the validity period", "co-applicant KYC annexure missing"],
    "declined": ["income below the eligibility needed for the requested amount",
                 "credit bureau report showed overdue accounts", "PAN details did not match"],
}

# Planted files: the labelled queries (queries.py) point at these. Generated files never copy their exact
# combination of facts, so the labels are complete by construction (section 08.4 says why real ones are not).
PLANTED: list[dict[str, str]] = [
    dict(file_no="GF-23417", branch="Guntur", product="two-wheeler", applicant_type="self-employed",
         decided="2025-08-14", decision="approved", amount="85,000", dealer="DLR-GNT-011",
         income="twelve-month bank statement of the business account and self-declaration with field visit report",
         address="rent agreement (notarised) with landlord's electricity bill",
         reason="approved after field visit confirmed the kirana shop; rent agreement accepted with the landlord's "
                "electricity bill",
         note="Applicant kirana kottu naduputhunnadu near Brodipet; nelaki aadaayam about Rs 30,000 as per statement.",
         pan="AKLPR4821M"),
    dict(file_no="GF-23562", branch="Kukatpally", product="two-wheeler", applicant_type="self-employed",
         decided="2025-09-02", decision="approved", amount="1,12,000", dealer="DLR-KKP-014",
         income="twelve-month bank statement of the business account",
         address="rent agreement (notarised) with landlord's electricity bill",
         reason="self-employed kirana shop owner; income proof bank statement accepted; rent agreement address proof "
                "accepted with landlord's electricity bill; Sri Sai Motors quotation at Rs 1,24,500 on-road",
         note="Self-employed two-wheeler applicant, kirana shop, income proof bank statement, rent agreement address "
              "proof. Dealer Sri Sai Motors offered the customer a festival discount.", pan="BQZPS7310K"),
    dict(file_no="GF-24105", branch="Rajahmundry", product="two-wheeler", applicant_type="self-employed",
         decided="2026-02-10", decision="sent back", amount="70,000", dealer="DLR-RJY-019",
         income="twelve-month bank statement of the business account",
         address="rent agreement, unregistered and not notarised",
         reason="address proof not on the accepted list: unregistered rent agreement without a utility bill",
         note="Addhe agreement registered kaadu, utility bill ledu; branch ki tirigi pampinchamu.", pan="CMNPV2234D"),
    dict(file_no="GF-22730", branch="Guntur", product="two-wheeler", applicant_type="agriculture",
         decided="2025-06-30", decision="approved", amount="60,000", dealer="DLR-GNT-011",
         income="pahani land record and self-declaration countersigned by the branch manager",
         address="voter identity card",
         reason="agriculture income accepted on the pahani and countersigned self-declaration",
         note="Vyavasaayam meeda aadaayam; mirchi panta, rendu acres; pahani applicant peru meeda undi.",
         pan="DHTPA5562Q"),
    dict(file_no="GF-24388", branch="Vijayawada-Benz Circle", product="two-wheeler", applicant_type="agriculture",
         decided="2026-05-19", decision="approved", amount="55,000", dealer="DLR-VJB-031",
         income="adangal land record and self-declaration", address="masked Aadhaar copy",
         reason="agriculture income accepted on the adangal and the self-declaration countersigned at the branch",
         note="Vyavasayam aadayam, vari panta; adangal copy icharu.", pan="EKRPN9031L"),
    # A repeat applicant: one PAN, two files in two branches the Vijayawada team can see.
    dict(file_no="GF-22015", branch="Guntur", product="gold", applicant_type="salaried", decided="2025-01-21",
         decision="approved", amount="1,80,000", dealer="",
         income="last three salary slips and three-month salary account statement", address="masked Aadhaar copy",
         reason="gold loan within the LTV cap; closed on time in July 2025", note="Repeat customer; jeetham account.",
         pan="FGHPK1234J"),
    dict(file_no="GF-24620", branch="Vijayawada-Benz Circle", product="two-wheeler", applicant_type="salaried",
         decided="2026-07-08", decision="approved", amount="95,000", dealer="DLR-VJB-035",
         income="last three salary slips and three-month salary account statement", address="masked Aadhaar copy",
         reason="repeat customer with a closed gold loan in good standing", note="Previous gold loan closed on time.",
         pan="FGHPK1234J"),
    # A PAN whose only file is in Warangal: the Vijayawada team must get nothing for it.
    dict(file_no="GF-23911", branch="Warangal", product="two-wheeler", applicant_type="salaried", decided="2025-12-03",
         decision="declined", amount="2,40,000", dealer="DLR-WGL-004",
         income="last three salary slips and three-month salary account statement", address="passport",
         reason="credit bureau report showed overdue accounts", note="Kakatiya Motors quotation; bureau overdue.",
         pan="GJKPM6650R"),
    # Unmasked Aadhaar send-backs in August 2025 (the compliance head's story), Vijayawada team branches.
    dict(file_no="GF-23290", branch="Rajahmundry", product="gold", applicant_type="pensioner", decided="2025-08-06",
         decision="sent back", amount="40,000", dealer="", income="pension payment order and three-month statement",
         address="Aadhaar copy, unmasked",
         reason="unmasked Aadhaar copy received after the June 2025 masking circular",
         note="Branch ki cheppamu: mask chesi malli scan cheyandi.", pan="HLMPB3378S"),
    dict(file_no="GF-23301", branch="Guntur", product="two-wheeler", applicant_type="gig worker", decided="2025-08-11",
         decision="sent back", amount="65,000", dealer="DLR-GNT-011",
         income="six months of platform payout statements and bank statement", address="Aadhaar copy, unmasked",
         reason="unmasked Aadhaar copy received after the June 2025 masking circular",
         note="Delivery partner; payouts six nelalu unnayi; Aadhaar mask ledu.", pan="JNPPC4410T"),
]

_PLANTED_SIGS = {(p["branch"], p["applicant_type"], p["address"], p["decision"]) for p in PLANTED}


def _decision_lines(f: dict[str, str]) -> list[str]:
    return [
        "LOAN FILE DECISION SUMMARY (masked)",
        f"File: {f['file_no']} · Branch: {f['branch']} ({BRANCH_CODES[f['branch']]}) · Product: {f['product']}",
        f"Decided: {date.fromisoformat(f['decided']).strftime('%d %B %Y')} · Decision: {f['decision']}",
        f"Applicant type: {f['applicant_type']} · Amount: Rs {f['amount']}"
        + (f" · Dealer: {f['dealer']}" if f["dealer"] else ""),
        f"PAN token: {pan_token(f['pan'])}",
        f"Income proof: {f['income']}",
        f"Address proof: {f['address']}",
        f"Reason: {f['reason']}",
        f"Analyst note: {f['note']}",
    ]


def loan_decisions(n_per_branch: int = 50) -> tuple[list[Document], dict[str, str]]:
    """300 masked decision summaries, 50 per branch. Returns (documents, file number -> raw PAN). The PAN map
    is the synthetic answer key for the PAN queries; it is never indexed."""
    rng = random.Random(SEED)
    planted_by_branch: dict[str, list[dict[str, str]]] = {}
    for p in PLANTED:
        planted_by_branch.setdefault(p["branch"], []).append(p)
    docs: list[Document] = []
    pans: dict[str, str] = {}
    used_numbers = {p["file_no"] for p in PLANTED}
    letters = "ABCDEFGHJKLMNPQRSTUVWXYZ"
    types, weights = zip(*_APPLICANT_TYPES)
    for branch in BRANCHES:
        rows = list(planted_by_branch.get(branch, []))
        dealers = [c for c, (_, b) in EMPANELLED_DEALERS.items() if b == branch]
        while len(rows) < n_per_branch:
            at = rng.choices(types, weights)[0]
            product = rng.choices(["two-wheeler", "gold", "small-business"], [0.6, 0.3, 0.1])[0]
            decision = rng.choices(["approved", "sent back", "declined"], [0.7, 0.22, 0.08])[0]
            address = rng.choice(_ADDRESS)
            if (branch, at, address, decision) in _PLANTED_SIGS:
                continue                                    # keep the planted labels complete
            decided = date(2024, 6, 1) + timedelta(days=rng.randint(0, 870))
            while True:
                num = f"GF-{rng.randint(21000, 24899)}"
                if num not in used_numbers:
                    used_numbers.add(num)
                    break
            telugu = branch != "Kukatpally" and rng.random() < 0.35
            w = {k: rng.choice(v) for k, v in TELUGU_LATN_VARIANTS.items()}
            rupees = rng.randint(18, 45)
            if at == "self-employed":
                note = (f"{w['shop'].capitalize()} business; {w['month']} {w['income']} approx Rs {rupees},000."
                        if telugu else f"Runs a small business; monthly income about Rs {rupees},000.")
            elif at == "agriculture":
                note = (f"{w['farming'].capitalize()} {w['income']}; {rng.randint(1, 5)} acres." if telugu
                        else f"Farm income from {rng.randint(1, 5)} acres.")
            elif at == "salaried":
                note = f"{w['salary'].capitalize()} account statement icharu." if telugu else "Salary account statement given."
            else:
                note = f"{w['month']} {w['income']} statement lo kanipistundi." if telugu else "Statements given for the period."
            pan = ("".join(rng.choice(letters) for _ in range(3)) + "P" + rng.choice(letters)
                   + f"{rng.randint(1000, 9999)}" + rng.choice(letters))
            rows.append(dict(file_no=num, branch=branch, product=product, applicant_type=at,
                             decided=decided.isoformat(), decision=decision, amount=f"{rng.randint(30, 280) * 1000:,}",
                             dealer=rng.choice(dealers) if product == "two-wheeler" and dealers else "",
                             income=rng.choice(_INCOME[at]), address=address, reason=rng.choice(_REASONS[decision]),
                             note=note, pan=pan))
        for r in rows:
            low = r["note"].lower()
            te = any(v in low for vs in TELUGU_LATN_VARIANTS.values() for v in vs) or " ledu" in low or "cheyandi" in low
            docs.append(Document(r["file_no"], f"Decision summary {r['file_no']}", "loan_decision", r["product"],
                                 "te-latn" if te else "en", _d(r["decided"]), _d(r["decided"]), branch=r["branch"],
                                 approved_by="", series="LOAN", body_lines=_decision_lines(r),
                                 extra={"decision": r["decision"], "applicant_type": r["applicant_type"]}))
            pans[r["file_no"]] = r["pan"]
    return docs, pans


# ---------------------------------------------------------------------------------- PDF-like text
def _wrap(text: str, width: int, rng: random.Random, hyphenate: bool) -> list[str]:
    lines: list[str] = []
    cur = ""
    for w in text.split():
        if cur and len(cur) + 1 + len(w) > width:
            if hyphenate and len(w) > 8 and w.isalpha() and rng.random() < 0.5:
                cut = len(w) // 2
                lines.append(f"{cur} {w[:cut]}-")
                cur = w[cut:]
                continue
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}" if cur else w
    if cur:
        lines.append(cur)
    return lines


_OCR = (("rn", "m"), ("e", "c"), ("l", "1"), ("o", "0"))


def _ocr_noise(line: str, rng: random.Random) -> str:
    """Letter confusions on a few words of a scanned page. Numbers and identifiers are left alone so that the
    labelled answers stay checkable; real OCR is not so kind (section 02.2)."""
    out = []
    for w in line.split(" "):
        if w.isalpha() and len(w) > 5 and rng.random() < 0.04:
            a, b = rng.choice(_OCR)
            w = w.replace(a, b, 1)
        out.append(w)
    return " ".join(out)


_KIND = {"circular": "Credit Operations Circular No.", "rulebook": "Product Rulebook No.",
         "annex": "Compliance Annex No.", "rbi_digest": "Regulatory Digest No."}


def _body_lines(doc: Document, rng: random.Random) -> list[str]:
    if doc.doc_type == "loan_decision":
        return list(doc.body_lines)
    lines = [f"{_KIND[doc.doc_type]} {doc.doc_id}", f"Subject: {doc.title}",
             f"Date: {doc.issued.strftime('%d %B %Y')} · Effective: {doc.effective_from.strftime('%d %B %Y')}"]
    if doc.supersedes:
        lines.append(f"Supersedes: {doc.supersedes}")
    if doc.approval_status == "draft":
        lines.append("Status: DRAFT, not approved, not for use")
    for sec in doc.sections:
        lines.append(f"{sec.number}. {sec.heading}")
        for item in sec.items:
            if isinstance(item, Clause):
                lines.extend(_wrap(f"{item.number} {item.text}", WRAP, rng, doc.scanned))
            else:
                lines.append(f"{item.number} {item.caption}")
                lines.append("| " + " | ".join(item.header) + " |")
                lines.extend("| " + " | ".join(row) + " |" for row in item.rows)
    return lines


def render_pages(doc: Document, rng: random.Random) -> list[list[str]]:
    """Header, footer and page number on every page; a stamp read as junk and OCR noise on scans; a table that
    crosses a page break repeats its header row on the next page, as many PDFs do."""
    body = _body_lines(doc, rng)
    groups: list[list[str]] = []
    cur: list[str] = []
    header_row: str | None = None
    for line in body:
        if line.startswith("| "):
            if header_row is None:
                header_row = line
        else:
            header_row = None
        if len(cur) >= PAGE_BODY_LINES:
            groups.append(cur)
            cur = [header_row] if header_row and line.startswith("| ") and line != header_row else []
        cur.append(line)
    if cur:
        groups.append(cur)
    pages: list[list[str]] = []
    keep = ("|", "Credit", "Date", "Supersedes", "Product", "Compliance", "Regulatory")
    for i, lines in enumerate(groups, start=1):
        body_i = [_ocr_noise(x, rng) if doc.scanned and not x.startswith(keep) else x for x in lines]
        if doc.scanned and i == 1:
            body_i.insert(min(3, len(body_i)), "~ D3V0RPPA · ECNA1LPM0C ~")    # the rotated APPROVED stamp, read by OCR
        pages.append(["GODAVARI FINANCE LTD · CREDIT OPERATIONS", f"{doc.doc_id} · {doc.title[:48].rstrip()}", *body_i,
                      f"Page {i} of {len(groups)}", "Internal · uncontrolled when printed"])
    return pages


def build_corpus() -> tuple[list[Document], dict[str, str]]:
    rng = random.Random(SEED)
    docs = policy_documents()
    loans, pans = loan_decisions()
    docs += loans
    for d in docs:
        d.pages = render_pages(d, rng)
    return docs, pans
