"""Day 12's provider-neutral client, imported by path. Used only by the optional model-backed planner.

Every model call the planner makes goes through Day 12's LLMClient: the idempotency store, retries with
backoff and jitter, the structured-output repair ladder and a cost-ledger row per attempt. The planner's
rupee budget is read from that ledger, so the number the budget enforces is the number finance sees.
"""

from __future__ import annotations

import sys
from pathlib import Path

DAY12_CODE = Path(__file__).resolve().parents[3] / "12-llm-apis-for-production" / "code"
if not (DAY12_CODE / "godavari_llm" / "client.py").exists():          # pragma: no cover - layout check
    raise ImportError(f"Day 12's client was not found at {DAY12_CODE}; Day 17 imports it by path")

sys.dont_write_bytecode = True
if str(DAY12_CODE) not in sys.path:
    sys.path.append(str(DAY12_CODE))

from godavari_llm.client import LLMClient, ResponseStore  # noqa: E402
from godavari_llm.ledger import CostLedger  # noqa: E402
from godavari_llm.provider import ModelRequest, ModelResponse, Tier, Usage, VirtualClock  # noqa: E402

__all__ = ["CostLedger", "DAY12_CODE", "LLMClient", "ModelRequest", "ModelResponse", "ResponseStore", "Tier",
           "Usage", "VirtualClock"]
