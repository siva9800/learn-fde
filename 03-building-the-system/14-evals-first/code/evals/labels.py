"""Labelling the golden set: what is on the paper, what each eval owner typed, and the adjudicated truth.

Three layers, kept apart on purpose:

  paper      what a careful reader sees on the scanned pages (from the generator's hidden truth). In a
             real engagement nobody has this; here it lets the chapter show how often agreement is wrong.
  A and B    Lakshmi (Vijayawada) and the senior analyst (Hyderabad), labelling every file independently
             through the same form, each with her own habits and slips.
  final      the adjudicated truth file the harness scores against, built by a written rule (ADJUDICATION_RULE).

A label records the fields as the analyst would have typed them, the documents she found, the completeness
verdict, whether she would have sent the file back and why, and her trajectory: the steps she took, with
pages, and how long it took. All of it is synthetic.
"""

from __future__ import annotations

import math
import random
from dataclasses import asdict, dataclass, field
from typing import Any

from .day11 import DAY11_CODE  # noqa: F401
from .golden import GoldenFile
from .normalise import norm_equal, normalise
from intake import rules_gold, rules_two_wheeler
from intake.catalogue import PAGE_TITLES, Doc, LoanBundle, Page
from intake.routing import MANDATORY_FIELDS
from intake.synth import GroundTruth

LABELLERS = {"A": "Lakshmi", "B": "the senior analyst"}
FIELD_ADJUDICATORS = "Srinivas and the Vijayawada team lead"
RULE_ADJUDICATOR = "the compliance head"

ADJUDICATION_RULE = """\
1. Both labels are normalised with the registered normaliser. If they are then equal, that is the label.
2. A field the two labellers typed differently goes to the two team leads (Srinivas and the Vijayawada team
   lead), who read the source page together and record what is on the paper, citing the labelling guide.
3. A document, completeness or send-back disagreement goes to the compliance head, who decides it against
   the signed rules and the alternatives list; if no signed rule covers it, the file is sent back
   (conservative) and the case goes on the rule-gap list.
4. Nobody from Kaagaz adjudicates. An agreed label is final even if both labellers were wrong; the only
   defence against shared mistakes is the labelling guide and the double-keyed audit (Day 9, section C)."""

# Where each field is read from (labelling guide, section 4). A field whose source document is not in the
# file is labelled "not in file" (None): the PAN comes from the PAN card, never from the form.
FIELD_SOURCE: dict[str, Doc] = {
    "applicant_name": Doc.APPLICATION_FORM, "date_of_birth": Doc.APPLICATION_FORM, "address": Doc.APPLICATION_FORM,
    "mobile": Doc.APPLICATION_FORM, "requested_amount": Doc.APPLICATION_FORM, "tenure_months": Doc.APPLICATION_FORM,
    "application_date": Doc.APPLICATION_FORM, "pan": Doc.PAN_CARD, "monthly_income": Doc.INCOME_PROOF,
    "on_road_price": Doc.DEALER_QUOTATION, "dealer_code": Doc.DEALER_QUOTATION, "quotation_date": Doc.DEALER_QUOTATION,
    "gross_weight_g": Doc.GOLD_APPRAISAL, "net_weight_g": Doc.GOLD_APPRAISAL, "purity_carat": Doc.GOLD_APPRAISAL,
    "appraisal_date": Doc.GOLD_APPRAISAL,
}

# Reasons an analyst sends a file back, and the signed rule each one rests on.
REASON_RULE: dict[str, str] = {
    "ADDRESS_NOT_ON_LIST": "ADDR-LIST (alternatives list v0.3)", "ADDRESS_NOT_OWN_NAME": "ADDR-LIST (own name only)",
    "ADDRESS_STALE": "ADDR-AGE (60 days)", "AADHAAR_UNMASKED": "KYC-MASK", "STATEMENT_STALE": "TW-BANK-AGE",
    "OVER_MARGIN": "TW-AMT-MARGIN (90 percent)", "OVER_LTV": "GL-LTV (tiered cap)",
}
CONFUSE = {"0": "6", "6": "0", "1": "7", "7": "1", "3": "8", "8": "3", "5": "6", "A": "R", "E": "F", "I": "L",
           "M": "N", "N": "M", "O": "Q", "S": "B", "B": "S", "U": "V", "V": "U"}


@dataclass
class Label:
    file_id: str
    labeller: str
    fields: dict[str, str | None]
    documents: list[str]
    missing: list[str]
    send_back: bool
    reasons: list[str]
    trajectory: list[dict[str, Any]] = field(default_factory=list)
    minutes: float = 0.0
    ambiguous: dict[str, str] = field(default_factory=dict)   # paper only: fields with a second plausible reading

    def to_json(self) -> dict[str, Any]:
        data = asdict(self)
        if self.labeller != "paper":
            data.pop("ambiguous")
        return data


def required_docs(product: str, has_co_applicant: bool) -> list[Doc]:
    if product == "gold":
        return [row[1] for row in rules_gold.REQUIRED_DOCS]
    docs = [row[1] for row in rules_two_wheeler.REQUIRED_DOCS]
    if has_co_applicant:
        docs.append(rules_two_wheeler.CO_APPLICANT_RULE[1])
    return docs


def printed_type(page: Page) -> Doc:
    """What the analyst reads at the top of the page: the printed title, longest match wins."""
    first = page.text.splitlines()[0] if page.text else ""
    best: tuple[int, Doc] = (0, Doc.UNKNOWN)
    for doc, title in PAGE_TITLES.items():
        if first.startswith(title) and len(title) > best[0]:
            best = (len(title), doc)
    return best[1]


def source_page(bundle: LoanBundle, field_name: str) -> Page | None:
    doc = FIELD_SOURCE[field_name]
    for page in bundle.pages:
        if printed_type(page) == doc and "(continued)" not in page.text.splitlines()[0]:
            return page
    return None


def _confuse(rng: random.Random, value: str) -> str:
    spots = [i for i, ch in enumerate(value) if ch in CONFUSE]
    if not spots:
        return value + "1"
    i = rng.choice(spots)
    return value[:i] + CONFUSE[value[i]] + value[i + 1:]


def _slip(rng: random.Random, value: str) -> str:
    """A keying slip: two neighbouring characters swapped, or one character confused."""
    if len(value) > 3 and rng.random() < 0.5:
        i = rng.randrange(len(value) - 1)
        if value[i] != value[i + 1]:
            return value[:i] + value[i + 1] + value[i] + value[i + 2:]
    return _confuse(rng, value)


def _indian(n: int) -> str:
    """125000 -> '1,25,000' (Indian digit grouping)."""
    s = str(n)
    if len(s) <= 3:
        return s
    head, tail = s[:-3], s[-3:]
    parts: list[str] = []
    while len(head) > 2:
        parts.insert(0, head[-2:])
        head = head[:-2]
    return ",".join(([head] if head else []) + parts + [tail])


def paper_label(gf: GoldenFile, bundle: LoanBundle, truth: GroundTruth) -> Label:
    """What is on the paper: the generator's truth, restricted to what the file actually contains."""
    rng = random.Random(f"paper-{gf.file_id}")
    present = sorted(str(d) for d in truth.present)
    has_co = bool(truth.fields.get("co_applicant_name"))
    missing = sorted(str(d) for d in required_docs(gf.product, has_co) if d not in truth.present)
    fields: dict[str, str | None] = {}
    ambiguous: dict[str, str] = {}
    for name in MANDATORY_FIELDS[gf.product]:
        page = source_page(bundle, name)
        value = truth.fields.get(name) if FIELD_SOURCE[name] in truth.present and page is not None else None
        fields[name] = value
        if value and page is not None and page.handwritten and rng.random() < 0.012:
            ambiguous[name] = _confuse(rng, value)       # a smudged digit two careful people could read two ways
    reasons = sorted([f"MISSING:{d}" for d in missing] +
                     [d for d in truth.defects if not d.startswith(("MISSING:", "FIELD_ERROR:"))])
    label = Label(gf.file_id, "paper", fields, present, missing, bool(reasons), reasons, ambiguous=ambiguous)
    label.trajectory = trajectory(gf, bundle, label, has_co)
    return label


def trajectory(gf: GoldenFile, bundle: LoanBundle, label: Label, has_co: bool) -> list[dict[str, Any]]:
    """The expert's steps for one file, with the page each step used. Day 17 compares agent runs to these."""
    by_type: dict[Doc, int] = {}
    for p in bundle.pages:
        t = printed_type(p)
        if t != Doc.UNKNOWN and "(continued)" not in p.text.splitlines()[0]:
            by_type.setdefault(t, p.number)
    steps: list[dict[str, Any]] = [{"action": "open_file", "pages": len(bundle.pages)}]
    for doc in required_docs(gf.product, has_co):
        steps.append({"action": "find_document", "doc": str(doc), "page": by_type.get(doc)})
    for name in MANDATORY_FIELDS[gf.product]:
        page = source_page(bundle, name)
        steps.append({"action": "read_field", "field": name, "page": page.number if page else None})
    if Doc.PAN_CARD in by_type and Doc.APPLICATION_FORM in by_type:
        steps.append({"action": "cross_check", "what": "PAN card against the form",
                      "pages": [by_type[Doc.PAN_CARD], by_type[Doc.APPLICATION_FORM]]})
    if gf.product == "two-wheeler" and Doc.INCOME_PROOF in by_type:
        steps.append({"action": "cross_check", "what": "income proof against the form and the salary credits",
                      "pages": [by_type[Doc.INCOME_PROOF], by_type.get(Doc.APPLICATION_FORM)]})
    if gf.product == "gold":
        steps.append({"action": "lookup", "what": "published 22-carat rate on the appraisal date"})
    steps.append({"action": "decide", "send_back": label.send_back, "reasons": list(label.reasons)})
    for i, s in enumerate(steps, start=1):
        s["step"] = i
    return steps


def labeller_label(who: str, gf: GoldenFile, bundle: LoanBundle, paper: Label) -> Label:
    """One eval owner's label: the paper, through her habits (format) and her slips (content)."""
    rng = random.Random(f"label-{who}-{gf.file_id}")
    has_co = "co_applicant_kyc" in paper.documents + paper.missing
    fields: dict[str, str | None] = {}
    for name, value in paper.fields.items():
        if value is None:
            # The guide says PAN only from the PAN card; the senior analyst sometimes types the form's PAN.
            if who == "B" and name == "pan" and rng.random() < 0.5:
                form = source_page(bundle, "applicant_name")
                line = next((ln for ln in (form.text.splitlines() if form else []) if ln.startswith("PAN:")), None)
                fields[name] = line.split(":", 1)[1].strip() if line else None
            else:
                fields[name] = None
            continue
        typed = value
        if name in paper.ambiguous and rng.random() < 0.5:
            typed = paper.ambiguous[name]
        elif rng.random() < 0.008:
            typed = _slip(rng, typed)
        if who == "B":                                   # the senior analyst's habits: format, not content
            if name in ("requested_amount", "monthly_income", "on_road_price"):
                if typed.isdigit() and rng.random() < 0.4:
                    typed = "Rs " + _indian(int(typed))
            elif name.endswith("date") or name == "date_of_birth":
                if rng.random() < 0.3:
                    typed = typed.replace("-", "/")
            elif name == "applicant_name":
                if rng.random() < 0.15:
                    typed = typed.title()
            elif name == "address" and rng.random() < 0.05:
                typed = typed.rsplit(",", 1)[0]          # drops the city and PIN: a real disagreement
        elif name == "mobile" and rng.random() < 0.2:
            typed = typed[:5] + " " + typed[5:]          # Lakshmi's habit: a space in the middle
        fields[name] = typed
    documents = sorted(d for d in paper.documents if rng.random() >= 0.004)
    required = [str(d) for d in required_docs(gf.product, has_co)]
    missing = sorted(d for d in required if d not in documents)
    reasons = {r for r in paper.reasons if not r.startswith("MISSING:")}
    if who == "A" and "ADDRESS_STALE" in reasons and rng.random() < 0.25:
        reasons.discard("ADDRESS_STALE")                 # did not count the days on the bill
    if who == "B":
        if "ADDRESS_NOT_OWN_NAME" in reasons and rng.random() < 0.6:
            reasons.discard("ADDRESS_NOT_OWN_NAME")      # "we always accepted the father's bill"
        if "OVER_MARGIN" in reasons and rng.random() < 0.4:
            reasons.discard("OVER_MARGIN")               # would take the margin money and approve
    if rng.random() < 0.01:
        reasons.add("PHOTO_UNCLEAR")                     # not a rule; the compliance head will say so
    reasons |= {f"MISSING:{d}" for d in missing}
    pace = 1.0 if who == "A" else 1.15
    minutes = round(pace * (18 + 1.1 * len(bundle.pages) + 3 * len(reasons)) * math.exp(rng.gauss(0, 0.15)), 1)
    label = Label(gf.file_id, LABELLERS[who], fields, documents, missing, bool(reasons), sorted(reasons),
                  minutes=minutes)
    label.trajectory = trajectory(gf, bundle, label, has_co)
    return label


@dataclass
class Adjudication:
    file_id: str
    item: str
    a: str
    b: str
    final: str
    by: str
    reason: str


def adjudicate(gf: GoldenFile, a: Label, b: Label, paper: Label) -> tuple[Label, list[Adjudication]]:
    """Apply ADJUDICATION_RULE. Returns the final label (values in canonical form) and the log."""
    rng = random.Random(f"adjudicate-{gf.file_id}")
    log: list[Adjudication] = []
    fields: dict[str, str | None] = {}
    for name in paper.fields:
        va, vb = a.fields.get(name), b.fields.get(name)
        if norm_equal(name, va, vb):
            fields[name] = normalise(name, va)
            continue
        on_paper = paper.fields[name]
        if name in paper.ambiguous and rng.random() < 0.2:
            on_paper = paper.ambiguous[name]             # even the leads can read a smudge the other way
        fields[name] = normalise(name, on_paper)
        why = ("labelling guide 4.2: PAN only from the PAN card" if name == "pan" and paper.fields[name] is None
               else "labelling guide 4.1: the full address as on the form" if name == "address"
               else "read from the source page")
        log.append(Adjudication(gf.file_id, f"field:{name}", str(va), str(vb), str(fields[name]),
                                FIELD_ADJUDICATORS, why))
    docs: list[str] = []
    for d in sorted(set(a.documents) | set(b.documents) | set(paper.documents)):
        in_a, in_b = d in a.documents, d in b.documents
        if in_a and in_b:
            docs.append(d)
            continue
        if d in paper.documents:
            docs.append(d)
        log.append(Adjudication(gf.file_id, f"document:{d}", str(in_a), str(in_b), str(d in paper.documents),
                                RULE_ADJUDICATOR, "page checked against the checklist"))
    has_co = "co_applicant_kyc" in paper.documents + paper.missing
    missing = sorted(x for x in (str(d) for d in required_docs(gf.product, has_co)) if x not in docs)
    ra, rb = set(a.reasons), set(b.reasons)
    if ra == rb:
        reasons = sorted(ra | {f"MISSING:{x}" for x in missing})
    else:
        reasons = sorted({r for r in paper.reasons if not r.startswith("MISSING:")} | {f"MISSING:{x}" for x in missing})
        for r in sorted(ra ^ rb):
            if r in REASON_RULE or r.startswith("MISSING:"):
                why = f"decided against {REASON_RULE.get(r, 'the checklist')}"
            else:
                why = "no signed rule makes this a send-back reason"
            log.append(Adjudication(gf.file_id, f"reason:{r}", str(r in ra), str(r in rb), str(r in reasons),
                                    RULE_ADJUDICATOR, why))
    # The recorded expert trajectory is Lakshmi's, with its last step replaced by the adjudicated decision.
    steps = [dict(s) for s in a.trajectory]
    steps[-1] = {**steps[-1], "send_back": bool(reasons), "reasons": list(reasons)}
    final = Label(gf.file_id, "adjudicated", fields, docs, missing, bool(reasons), reasons,
                  trajectory=steps, minutes=a.minutes)
    return final, log


@dataclass
class LabelSet:
    files: list[GoldenFile]
    bundles: dict[str, LoanBundle]
    paper: dict[str, Label]
    a: dict[str, Label]
    b: dict[str, Label]
    final: dict[str, Label]
    log: list[Adjudication]


def label_all(files: list[GoldenFile]) -> LabelSet:
    bundles: dict[str, LoanBundle] = {}
    paper: dict[str, Label] = {}
    a: dict[str, Label] = {}
    b: dict[str, Label] = {}
    final: dict[str, Label] = {}
    log: list[Adjudication] = []
    for gf in files:
        bundle, truth = gf.build()
        bundles[gf.file_id] = bundle
        paper[gf.file_id] = paper_label(gf, bundle, truth)
        a[gf.file_id] = labeller_label("A", gf, bundle, paper[gf.file_id])
        b[gf.file_id] = labeller_label("B", gf, bundle, paper[gf.file_id])
        final[gf.file_id], entries = adjudicate(gf, a[gf.file_id], b[gf.file_id], paper[gf.file_id])
        log.extend(entries)
    return LabelSet(files, bundles, paper, a, b, final, log)
