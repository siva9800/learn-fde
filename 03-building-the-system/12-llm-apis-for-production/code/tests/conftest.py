"""Shared test helpers: a scripted provider that replays a list of outcomes, one per attempt."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from godavari_llm.client import LLMClient, ResponseStore          # noqa: E402
from godavari_llm.ledger import CostLedger                        # noqa: E402
from godavari_llm.provider import (ModelRequest, ModelResponse, ProviderError, Tier, Usage,  # noqa: E402
                                   VirtualClock)
from godavari_llm.retry import CircuitBreaker, RetryPolicy        # noqa: E402


class ScriptedProvider:
    """Each attempt pops the next item: an exception to raise, or a (text, stop_reason) to return."""

    name = "scripted"

    def __init__(self, clock: VirtualClock, script: list, seconds_per_call: float = 2.0) -> None:
        self.clock = clock
        self.script = list(script)
        self.seconds = seconds_per_call
        self.requests: list[ModelRequest] = []

    def model_for(self, tier: Tier) -> str:
        return f"scripted-{tier.value}"

    def complete(self, request: ModelRequest) -> ModelResponse:
        self.requests.append(request)
        item = self.script.pop(0)
        if isinstance(item, ProviderError):
            self.clock.sleep(item.elapsed_s)
            raise item
        text, stop = item
        self.clock.sleep(self.seconds)
        return ModelResponse(text, Usage(1000, 0, 0, 100), self.model_for(request.tier), stop, self.seconds, "r1")


def make_request(key: str = "idem_test", **kw) -> ModelRequest:
    base = dict(tier=Tier.LARGE, system="system", user_text="page 1", page_ref=None, json_schema=None,
                max_output_tokens=500, timeout_s=30.0, idempotency_key=key,
                metadata={"task": "extract", "est_input_tokens": "1800"})
    base.update(kw)
    return ModelRequest(**base)


@pytest.fixture
def harness():
    def build(script: list, policy: RetryPolicy | None = None, threshold: int = 5):
        clock = VirtualClock()
        provider = ScriptedProvider(clock, script)
        ledger = CostLedger()
        breaker = CircuitBreaker(clock, failure_threshold=threshold, cooldown_s=60.0)
        client = LLMClient(provider, ledger, clock, policy=policy or RetryPolicy(), breaker=breaker,
                           store=ResponseStore(), seed=1)
        return client, provider, ledger, clock
    return build
