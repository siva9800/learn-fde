"""Forty labelled queries, phrased the way an analyst types them into the panel.

Each label is an ANSWER SPAN (a short string that must appear in a returned chunk), not a chunk id, so the
labels survive re-chunking: the naive and the structure-aware chunker are scored against the same labels.
Policy spans exist only in the version in force on 25 November 2026, so a superseded version never counts.
Precedent spans are file numbers; the planted files make the labels complete by construction. Day 14 owns how
real labels are made with the analysts; this set is the minimum that lets retrieval be measured on its own.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LabelledQuery:
    qid: str
    user: str
    scope: str             # policy or precedent: the two sections of the review-queue panel
    category: str
    text: str
    spans: tuple[str, ...]


_Q = [
    # identifiers: circular and rulebook numbers
    ("lakshmi", "policy", "identifier", "What does GFL/CO/2025/027 say for a pensioner?", ("pension payment order and bank statement for three months",)),
    ("lakshmi", "policy", "identifier", "GFL/CO/2025/019 quotation validity", ("valid for 30 days from its date",)),
    ("srinivas", "policy", "identifier", "GFL/CO/2026/009 LTV above 5 lakh", ("above rs 500,000 | 75 percent",)),
    ("srinivas", "policy", "identifier", "annex GFL/CMP/2026/004 gas bill in father's name", ("with proof of the relationship",)),
    ("lakshmi", "policy", "identifier", "GFL/CO/2025/052 WhatsApp documents", ("is not part of the file of record and must not be printed",)),
    ("srinivas", "policy", "identifier", "GFL/RB/2026/001 finance percentage", ("finance up to 90 percent of the on-road price",)),
    # table rows
    ("lakshmi", "policy", "table-row", "what income proof is acceptable for a self-employed two-wheeler applicant in Guntur",
     ("twelve-month bank statement of the business account, or gst returns for the last four quarters",)),
    ("srinivas", "policy", "table-row", "income proof for a gig or delivery worker buying a two-wheeler", ("platform payout statements for six months",)),
    ("lakshmi", "policy", "table-row", "agriculture applicant two wheeler income proof land record", ("land record (pahani or adangal)",)),
    ("lakshmi", "policy", "table-row", "is an unregistered rent agreement accepted as address proof", ("accepted with a utility bill in the applicant's own name",)),
    ("srinivas", "policy", "table-row", "LTV cap for a gold loan of 3 lakh", ("up to rs 500,000 | 80 percent",)),
    # paraphrase: none of the circular's own words
    ("lakshmi", "policy", "paraphrase", "proof of earnings for a shop owner purchasing a scooter",
     ("twelve-month bank statement of the business account, or gst returns for the last four quarters",)),
    ("srinivas", "policy", "paraphrase", "how long is a showroom proforma valid", ("valid for 30 days from its date",)),
    ("lakshmi", "policy", "paraphrase", "can we keep a customer's uid copy without redaction if they agree", ("is not kept with consent",)),
    ("srinivas", "policy", "paraphrase", "how far back must the salary account statement go for an employee", ("covering about three months, at least 85 days",)),
    ("lakshmi", "policy", "paraphrase", "a customer sent papers to my mobile on a messaging app", ("is not part of the file of record and must not be printed",)),
    ("srinivas", "policy", "paraphrase", "oldest borrower allowed for a bike loan", ("21 to 60 years old",)),
    ("lakshmi", "policy", "paraphrase", "which identity documents does the RBI accept", ("the nrega job card",)),
    # superseded: the words match the old version; only the current one may count
    ("lakshmi", "policy", "superseded", "GFL/CO/2024/007 unmasked Aadhaar copy kept with consent", ("is not kept with consent",)),
    ("lakshmi", "policy", "superseded", "self-employed two-wheeler applicant income tax returns only",
     ("twelve-month bank statement of the business account, or gst returns for the last four quarters",)),
    ("srinivas", "policy", "superseded", "salaried bank statement six months", ("covering about three months",)),
    ("lakshmi", "policy", "superseded", "dealer quotation valid 15 days", ("valid for 30 days",)),
    ("srinivas", "policy", "superseded", "gold loan LTV 75 percent of the value", ("up to rs 250,000 | 85 percent",)),
    ("lakshmi", "policy", "superseded", "two-wheeler tenure 12 to 36 months", ("tenure is 12 to 48 months",)),
    # Telugu script
    ("lakshmi", "policy", "telugu", "స్వయం ఉపాధి ఆదాయ రుజువు", ("నాలుగు త్రైమాసికాల జీఎస్టీ రిటర్నులు",)),
    ("lakshmi", "policy", "telugu", "అద్దె ఒప్పందం చిరునామా రుజువు", ("యజమాని పేరు మీద విద్యుత్ బిల్లు",)),
    ("srinivas", "policy", "telugu", "ఆధార్ మాస్క్", ("మొదటి ఎనిమిది అంకెలు",)),
    # access: the draft is visible to the compliance desk only
    ("compliance.desk.01", "policy", "access", "video KYC for repeat customers", ("draft for the compliance head",)),
    # precedents: similar past files from the caller's own branches
    ("lakshmi", "precedent", "precedent", "similar past files: self-employed kirana shop two-wheeler, bank statement income, rent agreement with landlord electricity bill", ("GF-23417",)),
    ("lakshmi", "precedent", "precedent", "past files sent back for an unregistered rent agreement", ("GF-24105",)),
    ("lakshmi", "precedent", "precedent", "agriculture income two-wheeler approved on land record", ("GF-22730", "GF-24388")),
    ("lakshmi", "precedent", "precedent", "files sent back for unmasked Aadhaar copy after the masking circular", ("GF-23290", "GF-23301")),
    ("srinivas", "precedent", "precedent", "self-employed kirana shop two-wheeler rent agreement landlord electricity bill", ("GF-23562",)),
    ("lakshmi", "precedent", "precedent", "repeat customer with a closed gold loan in good standing", ("GF-24620",)),
    # PAN lookups: the query carries a PAN, the index holds only keyed tokens
    ("lakshmi", "precedent", "pan", "earlier files for PAN FGHPK1234J", ("GF-22015", "GF-24620")),
    ("lakshmi", "precedent", "pan", "any file for PAN AKLPR4821M", ("GF-23417",)),
    ("srinivas", "precedent", "pan", "prior applications PAN GJKPM6650R", ("GF-23911",)),
    # Telugu in Latin letters, spelled differently from the file
    ("lakshmi", "precedent", "transliteration", "vyavasayam aadayam mirchi panta pahani", ("GF-22730",)),
    ("lakshmi", "precedent", "transliteration", "vyavasaayam adayam vari panta adangal", ("GF-24388",)),
    ("lakshmi", "precedent", "transliteration", "adde agreement registered kadu utility bill ledu", ("GF-24105",)),
]

QUERIES: list[LabelledQuery] = [LabelledQuery(f"q{i:02d}", u, s, c, t, sp) for i, (u, s, c, t, sp) in enumerate(_Q, start=1)]
assert len(QUERIES) == 40
