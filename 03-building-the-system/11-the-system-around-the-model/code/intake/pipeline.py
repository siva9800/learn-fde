"""One file through the whole system: model, envelope, signed rules, routing, the analyst's note.

  model.read()              the model proposes: page types, fields with quotes, documents, salary account
  envelope()                code checks the proposal: grounding, confidence, formats, cross-field, lookups
  ruleset.run()             code applies the compliance head's rules to what survived the envelope
  routing.decide()          code picks the route; nothing skips the analyst
  model.draft_note()        the model explains code's findings in plain words; code checks the citation

`score()` compares the result with the synthetic ground truth. It exists only for this chapter's run.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from .catalogue import Doc, DocFinding, LoanBundle, ModelOutput
from .model import ExtractionModel
from .reference import EMPANELLED_DEALERS
from .routing import MANDATORY_FIELDS, Route, decide, threshold_for
from .ruleset import Action, Finding, RuleContext, RuleSet
from .synth import GroundTruth
from .validators import (grounding_errors, names_match, pan_format_errors, pan_matches_surname, parse_amount,
                         within_tolerance)

UNCERTAIN_PAGE_BELOW = 0.60
INCOME_TOLERANCE = 0.15


def _digits(text: str) -> str:
    return "".join(ch for ch in text if ch.isdigit())


def envelope(bundle: LoanBundle, out: ModelOutput) -> tuple[list[Finding], dict[Doc, DocFinding], tuple[int, ...]]:
    """Every check here is code. It returns the envelope's findings, the documents that survived
    grounding (the only ones a rule will see), and the pages the model could not classify."""
    findings: list[Finding] = []
    documents: dict[Doc, DocFinding] = {}
    statements: list[DocFinding] = []

    # Grounding: a claimed document must be on the page it cites.
    for claim in out.documents:
        errors = grounding_errors(bundle, claim)
        if errors:
            findings.append(Finding("ENV-GROUND", "envelope", Action.REVIEW,
                                    f"model claimed {claim.doc} on page {claim.page}, but " + "; ".join(errors),
                                    doc=claim.doc))
            continue
        if claim.doc == Doc.BANK_STATEMENT:
            statements.append(claim)
        else:
            documents.setdefault(claim.doc, claim)

    # The salary account is the model's judgement; code verifies it against the credits on the page.
    if statements:
        picked = next((s for s in statements if s.page == out.salary_account_page), statements[0])
        salaried = "Net pay" in (out.fields.get("monthly_income").evidence if out.fields.get("monthly_income") else "")
        if salaried and int(picked.attributes.get("salary_credits", "0")) < 3:
            better = next((s for s in statements if int(s.attributes.get("salary_credits", "0")) >= 3), None)
            where = f"page {better.page} does" if better else "no statement in the file does"
            findings.append(Finding("ENV-SALARY-ACCT", "envelope", Action.REVIEW,
                                    f"model picked page {picked.page} as the salary account, but it has no monthly "
                                    f"salary credits; {where}", doc=Doc.BANK_STATEMENT))
            if better:
                picked = better
        documents[Doc.BANK_STATEMENT] = picked

    # Fields: present, confident, and literally supported by the quote the model gave.
    for name in MANDATORY_FIELDS[bundle.product]:
        fv = out.fields.get(name)
        if fv is None or fv.value is None:
            findings.append(Finding("ENV-UNSURE", "envelope", Action.REVIEW,
                                    f"{name}: the model is unsure or did not find it", field_name=name))
            continue
        if fv.confidence < threshold_for(name):
            findings.append(Finding("ENV-CONFIDENCE", "envelope", Action.REVIEW,
                                    f"{name}: confidence {fv.confidence:.2f} is below {threshold_for(name):.2f}",
                                    field_name=name))
        page = bundle.page(fv.page) if fv.page is not None else None
        if page is None or fv.evidence not in page.text:
            findings.append(Finding("ENV-EVIDENCE", "envelope", Action.REVIEW,
                                    f"{name}: the quote is not on page {fv.page}", field_name=name))
        elif _digits(fv.value) and _digits(fv.value) not in _digits(fv.evidence):
            findings.append(Finding("ENV-EVIDENCE", "envelope", Action.REVIEW,
                                    f"{name}: value {fv.value} is not what the quote says ({fv.evidence.strip()!r})",
                                    field_name=name))

    # Formats and cross-field consistency.
    pan = out.fields.get("pan")
    pan_value = pan.value if pan else None
    for err in pan_format_errors(pan_value):
        if pan_value is not None:
            findings.append(Finding("ENV-PAN-FORMAT", "envelope", Action.REVIEW, err, field_name="pan"))
    form_pan = out.fields.get("form_pan")
    if pan_value and form_pan and form_pan.value and form_pan.value != pan_value:
        findings.append(Finding("ENV-PAN-MATCH", "envelope", Action.REVIEW,
                                f"PAN card says {pan_value}, the application form says {form_pan.value}",
                                field_name="pan"))
    name = out.fields.get("applicant_name")
    card_name = out.fields.get("pan_card_name")
    if name and name.value and card_name and card_name.value and not names_match(name.value, card_name.value):
        findings.append(Finding("ENV-NAME-MATCH", "envelope", Action.REVIEW,
                                f"name on the form {name.value!r} differs from the PAN card {card_name.value!r}",
                                field_name="applicant_name"))
    if pan_value and card_name and card_name.value and not pan_format_errors(pan_value) \
            and not pan_matches_surname(pan_value, card_name.value):
        findings.append(Finding("ENV-PAN-SURNAME", "envelope", Action.REVIEW,
                                f"PAN {pan_value} does not carry the surname initial of {card_name.value!r}",
                                field_name="pan"))
    if bundle.product == "two-wheeler":
        inc, form_inc = out.fields.get("monthly_income"), out.fields.get("form_monthly_income")
        a = parse_amount(inc.value) if inc else None
        b = parse_amount(form_inc.value) if form_inc else None
        if a is not None and b is not None and not within_tolerance(a, b, INCOME_TOLERANCE):
            findings.append(Finding("ENV-INCOME-MATCH", "envelope", Action.REVIEW,
                                    f"income proof gives Rs {a:,} a month, the form says Rs {b:,}",
                                    field_name="monthly_income"))
        dealer = out.fields.get("dealer_code")
        code = dealer.value if dealer else None
        if code and (code not in EMPANELLED_DEALERS or EMPANELLED_DEALERS[code][1] != bundle.branch):
            findings.append(Finding("ENV-DEALER", "envelope", Action.REVIEW,
                                    f"dealer {code} is not empanelled for {bundle.branch}", field_name="dealer_code"))

    uncertain = tuple(n for n, (doc, conf) in sorted(out.page_labels.items())
                      if doc == Doc.UNKNOWN and conf < UNCERTAIN_PAGE_BELOW)
    return findings, documents, uncertain


@dataclass
class FileResult:
    file_id: str
    product: str
    branch: str
    channel: str
    route: Route
    findings: list[Finding]
    note: str
    note_corrected: bool
    prompt_only_complete: bool
    defects: set[str] = field(default_factory=set)
    caught: set[str] = field(default_factory=set)
    missed: set[str] = field(default_factory=set)
    model_alone_shipped: set[str] = field(default_factory=set)
    caught_by: dict[str, list[str]] = field(default_factory=dict)
    false_alarms: list[str] = field(default_factory=list)
    output: ModelOutput | None = field(default=None, repr=False)   # kept for scoring only


def check_note(note: str, findings: list[Finding]) -> tuple[str, bool]:
    """The note is the model's prose; the rule ids in it are not optional. Missing ones are appended."""
    wanted = [f.rule_id for f in findings if f.action in (Action.SEND_BACK, Action.BLOCK)]
    missing = [r for r in dict.fromkeys(wanted) if r not in note]
    if not missing:
        return note, False
    return note + "\nRules that fired: " + ", ".join(missing), True


def process(bundle: LoanBundle, model: ExtractionModel, ruleset: RuleSet, as_of: date) -> FileResult:
    out = model.read(bundle)
    env_findings, documents, uncertain = envelope(bundle, out)
    ctx = RuleContext(bundle, out, documents, as_of, uncertain)
    findings = env_findings + ruleset.run(ctx)
    route = decide(findings)
    branch_facing = [(f.rule_id, f.message) for f in findings if f.action in (Action.SEND_BACK, Action.BLOCK)]
    if branch_facing:              # the model writes prose only about what code has already decided
        note, corrected = check_note(model.draft_note(bundle, branch_facing), findings)
    else:                          # nothing for the branch: a fixed sentence, no model call
        flagged = sorted({f.field_name or str(f.doc) for f in findings})
        note = (f"{bundle.file_id}: ready for your approval." if not findings else
                f"{bundle.file_id}: please check {', '.join(flagged)} before approving.")
        corrected = False
    return FileResult(bundle.file_id, bundle.product, bundle.branch, bundle.channel, route, findings, note,
                      corrected, out.prompt_only.complete, output=out)


# --- Scoring against the synthetic ground truth -----------------------------------------------------------
SCORED_FIELDS: dict[str, tuple[str, ...]] = {
    "two-wheeler": ("applicant_name", "pan", "date_of_birth", "requested_amount", "monthly_income", "on_road_price"),
    "gold": ("applicant_name", "pan", "date_of_birth", "requested_amount", "gross_weight_g", "net_weight_g",
             "purity_carat"),
}
DEFECT_RULES: dict[str, tuple[str, ...]] = {
    "ADDRESS_NOT_ON_LIST": ("ADDR-LIST",), "ADDRESS_NOT_OWN_NAME": ("ADDR-LIST",), "ADDRESS_STALE": ("ADDR-AGE",),
    "AADHAAR_UNMASKED": ("KYC-MASK",), "STATEMENT_STALE": ("TW-BANK-AGE",), "OVER_MARGIN": ("TW-AMT-MARGIN",),
    "OVER_LTV": ("GL-LTV",),
}
PROMPT_WORDS: dict[str, tuple[str, ...]] = {
    "ADDRESS_NOT_ON_LIST": ("address proof",), "ADDRESS_NOT_OWN_NAME": ("address proof",),
    "ADDRESS_STALE": ("utility bill",), "AADHAAR_UNMASKED": ("Aadhaar",), "STATEMENT_STALE": ("bank statement",),
    "OVER_MARGIN": ("90 percent",), "OVER_LTV": ("LTV",),
}


def score(result: FileResult, truth: GroundTruth) -> FileResult:
    out = result.output
    assert out is not None, "score() needs the result of process()"
    issues = " | ".join(out.prompt_only.issues)
    defects = set(truth.defects)
    for name in SCORED_FIELDS[truth.product]:
        fv = out.fields.get(name)
        if fv is not None and fv.value is not None and fv.value != truth.fields.get(name):
            defects.add(f"FIELD_ERROR:{name}")
    result.defects = defects
    for d in defects:
        kind, _, target = d.partition(":")
        if kind == "MISSING":
            hits = [f for f in result.findings if f.doc == Doc(target) and f.action in (Action.SEND_BACK, Action.REVIEW)]
            alone_caught = f"missing {target}" in issues
        elif kind == "FIELD_ERROR":
            hits = [f for f in result.findings if f.field_name == target]
            alone_caught = False      # with no envelope, the extracted value is what reaches the core system
        else:
            hits = [f for f in result.findings if any(f.rule_id.endswith(s) for s in DEFECT_RULES[d])]
            alone_caught = any(w in issues for w in PROMPT_WORDS[d])
        if hits:
            result.caught.add(d)
            result.caught_by[d] = sorted({f.rule_id for f in hits})
        else:
            result.missed.add(d)
        if not alone_caught:
            result.model_alone_shipped.add(d)
    for f in result.findings:
        if f.action in (Action.SEND_BACK, Action.BLOCK):
            if f.doc is not None and f"MISSING:{f.doc}" not in defects and not any(
                    f.rule_id.endswith(s) for d in defects for s in DEFECT_RULES.get(d, ())):
                result.false_alarms.append(f"{f.rule_id}: {f.message}")
    return result
