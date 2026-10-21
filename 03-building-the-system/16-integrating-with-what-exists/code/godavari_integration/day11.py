"""Day 11's intake package, imported by path. Never copied, never forked.

Day 11 built the reading-and-deciding half: the model stub, the envelope, the signed rules, the routes and
an idempotent push against a fake sandbox. Day 16 keeps all of it and replaces the fake sandbox with the
real integration: a SOAP client for the 2009 core. The push logic (approval check, route check, key from
file number and branch code, lookup before create) stays Day 11's, so there is one rule, in one place.
"""

from __future__ import annotations

import sys
from pathlib import Path

DAY11_CODE = Path(__file__).resolve().parents[3] / "11-the-system-around-the-model" / "code"
if not (DAY11_CODE / "intake" / "core_write.py").exists():          # pragma: no cover - layout check
    raise ImportError(f"Day 11's intake package was not found at {DAY11_CODE}; Day 16 imports it by path")

sys.dont_write_bytecode = True          # read Day 11's folder, never write into it
if str(DAY11_CODE) not in sys.path:
    sys.path.insert(0, str(DAY11_CODE))

from intake import rules_gold, rules_two_wheeler  # noqa: E402
from intake.catalogue import Doc, LoanBundle  # noqa: E402
from intake.core_write import Approval, PushLog, idempotency_key, push_to_core  # noqa: E402
from intake.day7_inputs import day7_sample  # noqa: E402
from intake.model import StubModel  # noqa: E402
from intake.pipeline import FileResult, process  # noqa: E402
from intake.reference import BRANCH_CODES  # noqa: E402
from intake.routing import Route  # noqa: E402
from intake.ruleset import RuleSet  # noqa: E402
from intake.synth import GroundTruth, build_batch  # noqa: E402

RULESETS: dict[str, RuleSet] = {"two-wheeler": rules_two_wheeler.RULESET, "gold": rules_gold.RULESET}

__all__ = ["Approval", "BRANCH_CODES", "DAY11_CODE", "Doc", "FileResult", "GroundTruth", "LoanBundle", "PushLog",
           "RULESETS", "Route", "StubModel", "build_batch", "day7_sample", "idempotency_key", "process",
           "push_to_core"]
