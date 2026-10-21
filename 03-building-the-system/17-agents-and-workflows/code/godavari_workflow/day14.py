"""Day 14's eval code, imported by path. Day 14 owns evals; this chapter adds trajectory checks on top.

The golden set (150 test files, labelled by Lakshmi and the senior analyst and adjudicated), the expert
decision for each file, the Wilson interval and the PII patterns all come from Day 14's folder.
"""

from __future__ import annotations

import sys
from pathlib import Path

DAY14_CODE = Path(__file__).resolve().parents[3] / "14-evals-first" / "code"
if not (DAY14_CODE / "evals" / "golden.py").exists():          # pragma: no cover - layout check
    raise ImportError(f"Day 14's eval package was not found at {DAY14_CODE}; Day 17 imports it by path")

sys.dont_write_bytecode = True
if str(DAY14_CODE) not in sys.path:
    sys.path.append(str(DAY14_CODE))

from evals.golden import GoldenFile, bundle_sha256, select  # noqa: E402
from evals.hygiene import pii_hits  # noqa: E402
from evals.stats import wilson  # noqa: E402
from evals.store import load_truth, truth_sha256  # noqa: E402

__all__ = ["DAY14_CODE", "GoldenFile", "bundle_sha256", "load_truth", "pii_hits", "select", "truth_sha256", "wilson"]
