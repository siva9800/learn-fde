"""Day 11's intake package, imported by path. Never copied, never forked.

The model stub, the envelope, the compliance head's rules with their sign-off check, the routes, the
branch-visibility rule and the idempotent core-system push all stay in Day 11's folder. This chapter
puts them inside a state machine; it does not change one of them.
"""

from __future__ import annotations

import sys
from pathlib import Path

PART3 = Path(__file__).resolve().parents[3]
DAY11_CODE = PART3 / "11-the-system-around-the-model" / "code"
if not (DAY11_CODE / "intake" / "pipeline.py").exists():          # pragma: no cover - layout check
    raise ImportError(f"Day 11's intake package was not found at {DAY11_CODE}; Day 17 imports it by path")

sys.dont_write_bytecode = True          # read the earlier chapters' folders, never write into them
if str(DAY11_CODE) not in sys.path:
    sys.path.insert(0, str(DAY11_CODE))

from intake import rules_gold, rules_two_wheeler  # noqa: E402
from intake.catalogue import (Doc, DocFinding, FieldValue, LoanBundle, ModelOutput, Page,  # noqa: E402
                              PromptOnlyVerdict)
from intake.core_write import Approval, FakeCoreSandbox, PushLog, idempotency_key, push_to_core  # noqa: E402
from intake.day7_inputs import day7_sample, load_day7_module  # noqa: E402
from intake.model import ExtractionModel, StubModel  # noqa: E402
from intake.pipeline import DEFECT_RULES, envelope  # noqa: E402
from intake.reference import BRANCH_AD_GROUP, BRANCH_CODES  # noqa: E402
from intake.routing import Route, decide, visible_to  # noqa: E402
from intake.ruleset import Action, Finding, RuleContext, RuleSet, SignoffError, check_signoff  # noqa: E402
from intake.catalogue import PAGE_TITLES  # noqa: E402
from intake.synth import _fmt_amount as fmt_amount  # noqa: E402  (Day 11's Indian digit grouping)
from intake.synth import build_file  # noqa: E402

RULESETS: dict[str, RuleSet] = {"two-wheeler": rules_two_wheeler.RULESET, "gold": rules_gold.RULESET}
REQUIRED_DOC_TEXT: dict[str, dict[str, str]] = {
    "two-wheeler": {str(doc): text for _, doc, _, text in
                    (*rules_two_wheeler.REQUIRED_DOCS, rules_two_wheeler.CO_APPLICANT_RULE)},
    "gold": {str(doc): text for _, doc, _, text in rules_gold.REQUIRED_DOCS},
}

__all__ = ["Action", "Approval", "BRANCH_AD_GROUP", "BRANCH_CODES", "DAY11_CODE", "DEFECT_RULES", "Doc",
           "DocFinding", "ExtractionModel", "FakeCoreSandbox", "FieldValue", "Finding", "LoanBundle",
           "ModelOutput", "PAGE_TITLES", "PART3", "Page", "PromptOnlyVerdict", "PushLog", "REQUIRED_DOC_TEXT", "RULESETS",
           "Route", "RuleContext", "RuleSet", "SignoffError", "StubModel", "build_file", "check_signoff",
           "day7_sample", "decide", "envelope", "fmt_amount", "idempotency_key", "load_day7_module", "push_to_core",
           "visible_to"]
