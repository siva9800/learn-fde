"""What the analyst's screen holds for one file, and where the file sits in the queue.

Everything here is derived from Day 11's pipeline output (the FileResult and its bundle), the bands fitted on Day 14's
golden set, and Day 15's register. It decides layout and order, never the loan: the route is Day 11's, the decision is
the analyst's (decision D07), and the approval state is Day 17's.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

from .bands import Band, CellBands, band_for, standing_forced_look
from .citations import Citation, StaleCitation, cite, load_table
from .evidence import FieldEvidence, crop
from evals.stats import wilson
from intake.catalogue import LoanBundle
from intake.pipeline import FileResult
from intake.ruleset import Action, RuleSet, check_signoff

ROUTE_TIER = {"blocked": 0, "send_back": 0, "review": 1, "ready_for_approval": 2}
TIER_WORDS = {0: "tell the branch today", 1: "fields to check", 2: "ready for approval"}
SAFE_BULK_ACTIONS = ("claim", "export_csv")                         # reversible, decide nothing
NEVER_BULK_ACTIONS = ("approve", "confirm_field", "override_policy_rule", "send_back")


@dataclass
class FieldView:
    row: FieldEvidence
    band: Band
    impact: int
    risk: float
    forced: bool = False
    quote_line: int | None = None
    crop: list[tuple[int, str, bool]] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)       # what code said about this field, in words


@dataclass
class FindingView:
    rule_id: str
    kind: str                   # regulatory, policy, envelope
    action: str
    message: str
    field_name: str | None
    citation: Citation | None
    citation_problem: str | None


@dataclass
class ReviewItem:
    file_id: str
    branch: str
    product: str
    channel: str
    arrived: datetime
    route: str
    amount: int | None
    fields: list[FieldView]
    findings: list[FindingView]
    note: str
    rules_banner: str
    rules_fingerprint: str
    bands_version: str
    tier: int = 1
    why: str = ""

    @property
    def forced(self) -> FieldView | None:
        return next((f for f in self.fields if f.forced), None)

    @property
    def branch_findings(self) -> list[FindingView]:
        return [f for f in self.findings if f.action in (Action.SEND_BACK.value, Action.BLOCK.value)]

    def in_band(self, band: Band) -> list[FieldView]:
        return [f for f in self.fields if f.band == band and not f.forced]


def _risk(row: FieldEvidence, band: Band, cb: CellBands | None) -> float:
    """Upper bound on the chance this field is wrong, from development data only (never the test split)."""
    if cb is None:
        return 1.0
    if band == Band.AUTO:
        return wilson(0, cb.dev_auto_n)[1] if cb.dev_auto_n else 1.0
    return cb.review_risk()


def choose_forced(views: list[FieldView], standing: set[tuple[str, str]]) -> FieldView | None:
    """Exactly one field per file the analyst must open before approving, even on a clean file.
    1. a field from a cell whose confirmation failed (the standing list), highest impact first;
    2. otherwise the riskiest field to be wrong: impact times the development upper bound, review band first."""
    lookable = [v for v in views if v.band != Band.REJECT]
    if not lookable:
        return None
    standing_hits = [v for v in lookable if v.row.cell in standing]
    pool = standing_hits or lookable
    return max(pool, key=lambda v: (v.impact * v.risk, v.band == Band.REVIEW, v.row.field))


def build_item(bundle: LoanBundle, result: FileResult, rows: list[FieldEvidence],
               bands: dict[tuple[str, str], CellBands], policy: dict[str, Any], ruleset: RuleSet,
               arrived: datetime, decided_on: date, bands_version: str, mode: str = "prototype") -> ReviewItem:
    """One file's screen. In pilot mode it refuses to build a screen on rules the compliance head has not signed."""
    status = check_signoff(ruleset, mode)              # raises SignoffError: no screen on unsigned rules in pilot
    impact = policy["impact"]
    by_field: dict[str, list[str]] = {}
    for f in result.findings:
        if f.field_name:
            by_field.setdefault(f.field_name, []).append(f"{f.rule_id}: {f.message}")
    views: list[FieldView] = []
    for r in rows:
        b = band_for(r, bands)
        v = FieldView(r, b, impact["fields"].get(r.field, impact["default"]), _risk(r, b, bands.get(r.cell)))
        v.quote_line, v.crop = crop(bundle, r.page, r.evidence)
        v.reasons = [m for m in by_field.get(r.field, []) if not m.startswith("ENV-CONFIDENCE")]
        if r.value is not None and r.evidence and v.quote_line is None:
            v.reasons.append("the quote the model gave is not on the page it cited")
        views.append(v)
    forced = choose_forced(views, standing_forced_look(bands))
    if forced is not None:
        forced.forced = True
    table = load_table()
    findings: list[FindingView] = []
    for f in result.findings:
        if f.rule_id == "ENV-CONFIDENCE":
            continue                                    # replaced by the bands; shown as the field's band instead
        c: Citation | None = None
        problem: str | None = None
        try:
            c = cite(f.rule_id, decided_on, table)
        except StaleCitation as exc:
            problem = str(exc)
        findings.append(FindingView(f.rule_id, str(f.kind), f.action.value, f.message, f.field_name, c, problem))
    amount_row = next((r for r in rows if r.field == "requested_amount"), None)
    amount = int(amount_row.value) if amount_row and amount_row.value and amount_row.value.isdigit() else None
    item = ReviewItem(bundle.file_id, bundle.branch, bundle.product, bundle.channel, arrived, result.route.value, amount,
                      views, findings, result.note, status.banner, ruleset.fingerprint()[:12], bands_version)
    item.tier = ROUTE_TIER[item.route]
    n_check = len([v for v in views if v.band == Band.REVIEW])
    n_key = len([v for v in views if v.band == Band.REJECT])
    branch_items = [f.rule_id for f in findings if f.action in (Action.SEND_BACK.value, Action.BLOCK.value)]
    parts = [TIER_WORDS[item.tier]]
    if branch_items:
        parts.append(f"{len(branch_items)} for the branch ({', '.join(branch_items)})")
    parts.append(f"{n_check} to check, {n_key} to key in")
    if forced is not None:
        parts.append(f"look first: {forced.row.field}")
    item.why = "; ".join(parts)
    return item


def queue_order(items: list[ReviewItem]) -> list[ReviewItem]:
    """Branch-facing files first (the branch is told the same day), then files with fields to check by loan amount,
    largest first, then oldest first; ready files last, oldest first. The order is explained on every row."""
    return sorted(items, key=lambda i: (i.tier, -(i.amount or 0) if i.tier == 1 else 0, i.arrived, i.file_id))
