"""Reach Day 11's intake package by path. Nothing from Day 11 is copied into this chapter.

Day 11 built the system: model interface and stub, envelope, signed rules, routing, core write. This
chapter only measures it, so it imports `intake` from Day 11's own folder and never forks a rule. If
Day 11 changes, this chapter's numbers change with it, which is the point of an eval harness.
"""

from __future__ import annotations

import sys
from pathlib import Path

CHAPTER_DIR = Path(__file__).resolve().parents[2]
DAY11_CODE = CHAPTER_DIR.parent / "11-the-system-around-the-model" / "code"

if not (DAY11_CODE / "intake" / "pipeline.py").exists():
    raise ImportError(f"Day 11's intake package is not at {DAY11_CODE}; this chapter imports it by path")

# Read Day 11's folder, never write into it: no __pycache__ appears there because of this chapter.
sys.dont_write_bytecode = True
if str(DAY11_CODE) not in sys.path:
    sys.path.insert(0, str(DAY11_CODE))

from intake import rules_gold, rules_two_wheeler  # noqa: E402
from intake.ruleset import RuleSet  # noqa: E402

RULESETS: dict[str, RuleSet] = {"two-wheeler": rules_two_wheeler.RULESET, "gold": rules_gold.RULESET}
