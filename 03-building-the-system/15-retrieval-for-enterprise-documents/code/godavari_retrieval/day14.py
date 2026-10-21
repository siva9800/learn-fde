"""Day 14's eval statistics, imported by path. Day 14 owns evals; retrieval reuses its interval code.

Day 14's harness scores extraction and completeness; it has no retrieval metric, so recall at k lives in this
chapter's evaluate.py. The confidence interval on that number comes from Day 14's ``evals.stats.wilson``, so
that both chapters report uncertainty the same way.
"""

from __future__ import annotations

import sys
from pathlib import Path

DAY14_CODE = Path(__file__).resolve().parents[3] / "14-evals-first" / "code"
if not (DAY14_CODE / "evals" / "stats.py").exists():          # pragma: no cover - layout check
    raise ImportError(f"Day 14's eval package was not found at {DAY14_CODE}")
if str(DAY14_CODE) not in sys.path:
    sys.path.append(str(DAY14_CODE))

from evals.stats import wilson  # noqa: E402

__all__ = ["wilson", "DAY14_CODE"]
