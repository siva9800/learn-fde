"""Day 11's intake package, imported by path. Never copied, never forked.

The branch codes, the AD group per branch, the empanelled dealers, the visibility rule and the product
limits all live in Day 11's code. Retrieval reads them from there so that a change to a rule (signed by
the compliance head) changes what the rulebook text says and what the filter does, in one place.
"""

from __future__ import annotations

import sys
from pathlib import Path

DAY11_CODE = (Path(__file__).resolve().parents[3]
              / "11-the-system-around-the-model" / "code")
if not (DAY11_CODE / "intake" / "__init__.py").exists():          # pragma: no cover - layout check
    raise ImportError(f"Day 11's intake package was not found at {DAY11_CODE}")
if str(DAY11_CODE) not in sys.path:
    sys.path.insert(0, str(DAY11_CODE))

from intake import rules_gold, rules_two_wheeler  # noqa: E402
from intake.reference import BRANCH_AD_GROUP, BRANCH_CODES, EMPANELLED_DEALERS  # noqa: E402
from intake.routing import visible_to  # noqa: E402

__all__ = ["BRANCH_AD_GROUP", "BRANCH_CODES", "EMPANELLED_DEALERS", "visible_to",
           "rules_gold", "rules_two_wheeler", "DAY11_CODE"]
