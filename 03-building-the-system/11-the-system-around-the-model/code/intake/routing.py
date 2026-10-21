"""Confidence routing and the review queue: where every file goes, and who may see it.

The thresholds are placeholders on purpose. Day 14 measures per-field accuracy on the golden set and
Day 18 sets each threshold from it; until then they are written down, versioned and visible here, not
buried in a prompt. No route skips the analyst: every file, including a clean one, waits for a named
analyst's approval (decision D07, Day 10).
"""

from __future__ import annotations

from collections.abc import Iterable
from enum import StrEnum

from .reference import BRANCH_AD_GROUP
from .ruleset import Action, Finding

THRESHOLDS_VERSION = "placeholder-2026-11-09"     # replaced by golden-set values (Day 14, Day 18)
FIELD_THRESHOLDS: dict[str, float] = {
    "applicant_name": 0.90, "pan": 0.90, "date_of_birth": 0.90,
    "requested_amount": 0.85, "monthly_income": 0.85, "on_road_price": 0.85,
    "gross_weight_g": 0.85, "net_weight_g": 0.85, "purity_carat": 0.85,
}
DEFAULT_THRESHOLD = 0.75

MANDATORY_FIELDS: dict[str, tuple[str, ...]] = {
    "two-wheeler": ("applicant_name", "date_of_birth", "pan", "address", "mobile", "requested_amount",
                    "tenure_months", "monthly_income", "application_date", "on_road_price", "dealer_code",
                    "quotation_date"),
    "gold": ("applicant_name", "date_of_birth", "pan", "address", "mobile", "requested_amount", "tenure_months",
             "application_date", "gross_weight_g", "net_weight_g", "purity_carat", "appraisal_date"),
}


class Route(StrEnum):
    BLOCKED = "blocked"                        # a regulatory rule failed; the branch must fix the file
    SEND_BACK = "send_back"                    # tell the branch today what is missing, with the rule
    REVIEW = "review"                          # an analyst looks at the flagged fields first
    READY_FOR_APPROVAL = "ready_for_approval"  # every check passed; an analyst still approves


_SEVERITY = {Action.BLOCK: 3, Action.SEND_BACK: 2, Action.REVIEW: 1}
_ROUTE_FOR = {3: Route.BLOCKED, 2: Route.SEND_BACK, 1: Route.REVIEW, 0: Route.READY_FOR_APPROVAL}


def threshold_for(field_name: str) -> float:
    return FIELD_THRESHOLDS.get(field_name, DEFAULT_THRESHOLD)


def decide(findings: Iterable[Finding]) -> Route:
    """The most severe finding decides the route. Order of rules never matters."""
    worst = max((_SEVERITY[f.action] for f in findings), default=0)
    return _ROUTE_FOR[worst]


def visible_to(analyst_groups: Iterable[str], branch: str) -> bool:
    """The branch-visibility rule (Day 6, A1): an analyst sees a file only through a group for its branch.
    Resolved at the moment of the request; there is no all-branches group to fall back on."""
    return BRANCH_AD_GROUP.get(branch) in set(analyst_groups)
