"""The machinery for rules as signed code: a rule, its kind, what it found, the fingerprint and the sign-off.

Three kinds of rule (section 04):
  REGULATORY  from the RBI or the law; enforced every time; nobody can override it.
  POLICY      Godavari's own; enforced every time; an analyst may override it with a logged reason.
  (judgement) not here at all: judgements are the model's, behind review (see pipeline.py).
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import StrEnum
from pathlib import Path

from .catalogue import Doc, DocFinding, FieldValue, LoanBundle, ModelOutput

INTAKE_DIR = Path(__file__).resolve().parent
SIGNOFF_PATH = INTAKE_DIR / "rules_signoff.json"


class Kind(StrEnum):
    REGULATORY = "regulatory"
    POLICY = "policy"


class Action(StrEnum):
    BLOCK = "block"            # cannot proceed as it stands; the branch must fix it
    SEND_BACK = "send_back"    # a document is missing or not acceptable; tell the branch today
    REVIEW = "review"          # an analyst must look before approving


@dataclass(frozen=True)
class Finding:
    rule_id: str
    kind: str                  # "regulatory", "policy" or "envelope" (an engineering check, not a signed rule)
    action: Action
    message: str
    doc: Doc | None = None
    field_name: str | None = None


@dataclass(frozen=True)
class RuleContext:
    """What a rule may look at: the bundle, the model's fields, and only the documents whose claims were
    grounded on a real page. Ungrounded claims never reach a rule (pipeline.py removes them first)."""

    bundle: LoanBundle
    output: ModelOutput
    documents: dict[Doc, DocFinding]
    as_of: date
    uncertain_pages: tuple[int, ...] = ()

    def value(self, name: str) -> str | None:
        fv: FieldValue | None = self.output.fields.get(name)
        return None if fv is None else fv.value


@dataclass(frozen=True)
class Rule:
    rule_id: str
    kind: Kind
    text: str                   # the sentence the compliance head reads and signs
    source: str                 # where the rule comes from
    check: Callable[[RuleContext], list[Finding]]


@dataclass(frozen=True)
class RuleSet:
    product: str
    version: str
    rules: tuple[Rule, ...]
    source_files: tuple[Path, ...]

    def run(self, ctx: RuleContext) -> list[Finding]:
        findings: list[Finding] = []
        for rule in self.rules:
            findings.extend(rule.check(ctx))
        return findings

    def fingerprint(self) -> str:
        """SHA-256 over the rule code itself, with line endings normalised, so a Windows checkout and a
        Linux checkout of the same code agree, and any edit to a rule, however small, changes it."""
        digest = hashlib.sha256()
        digest.update(f"{self.product}|{self.version}\n".encode())
        for path in sorted(self.source_files, key=lambda p: p.name):
            digest.update(path.name.encode() + b"\n")
            digest.update(path.read_bytes().replace(b"\r\n", b"\n"))
        return digest.hexdigest()


class SignoffError(RuntimeError):
    pass


@dataclass(frozen=True)
class SignoffStatus:
    product: str
    version: str
    status: str                 # draft, reviewed-draft, signed
    fingerprint_ok: bool
    record: dict[str, str | None]

    @property
    def banner(self) -> str:
        who = self.record.get("signed_by") or self.record.get("reviewed_by") or "nobody yet"
        when = self.record.get("signed_on") or self.record.get("reviewed_on") or "-"
        return (f"{self.product} rules v{self.version}: {self.status} ({who}, {when}); "
                f"fingerprint {'matches' if self.fingerprint_ok else 'DOES NOT MATCH'} the record")


def load_signoff(path: Path = SIGNOFF_PATH) -> dict[str, dict[str, str | None]]:
    return json.loads(path.read_text(encoding="utf-8"))


def check_signoff(ruleset: RuleSet, mode: str, path: Path = SIGNOFF_PATH) -> SignoffStatus:
    """Prototype mode runs reviewed or draft rules whose code matches the record. Pilot mode runs only
    signed rules. Neither mode runs rules whose code has changed since the record was made."""
    records = load_signoff(path)
    record = records.get(ruleset.product)
    if record is None:
        raise SignoffError(f"no sign-off record for {ruleset.product}")
    status = SignoffStatus(
        product=ruleset.product,
        version=ruleset.version,
        status=str(record.get("status")),
        fingerprint_ok=(record.get("fingerprint") == ruleset.fingerprint()
                        and record.get("version") == ruleset.version),
        record=record,
    )
    if not status.fingerprint_ok:
        raise SignoffError(f"{ruleset.product} rules changed since the sign-off record; re-review before running")
    if mode == "pilot" and status.status != "signed":
        raise SignoffError(f"{ruleset.product} rules are {status.status}; pilot mode runs signed rules only")
    if mode not in {"prototype", "pilot"}:
        raise SignoffError(f"unknown mode {mode!r}")
    return status


# --- Overrides: policy yes, with a reason on record; regulatory never ----------------------------------
@dataclass
class OverrideLog:
    entries: list[dict[str, str]] = field(default_factory=list)

    def override(self, finding: Finding, analyst_id: str, reason: str, when: datetime) -> None:
        if finding.kind != Kind.POLICY:
            raise PermissionError(f"{finding.rule_id} is {finding.kind}; it cannot be overridden")
        if len(reason.split()) < 4:
            raise ValueError("an override needs a reason a reviewer can read, not a label")
        self.entries.append({
            "rule_id": finding.rule_id, "analyst_id": analyst_id, "reason": reason, "at": when.isoformat(),
        })


# --- Small helpers the product rule modules share --------------------------------------------------------
def missing_document(rule_id: str, doc: Doc, text: str, ctx: RuleContext, kind: Kind) -> list[Finding]:
    """A required document is absent. If some pages could not be classified, the document may be on one
    of them, so an analyst looks first; otherwise the branch is told the same day."""
    if doc in ctx.documents:
        return []
    if ctx.uncertain_pages:
        pages = ", ".join(str(p) for p in ctx.uncertain_pages)
        return [Finding(rule_id, kind, Action.REVIEW,
                        f"{text}: not found; pages {pages} could not be classified, check them first", doc=doc)]
    return [Finding(rule_id, kind, Action.SEND_BACK, f"{text}: not in the file", doc=doc)]
