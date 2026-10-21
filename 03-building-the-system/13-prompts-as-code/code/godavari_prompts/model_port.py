"""The model boundary this package talks to.

Day 12 owns this interface (`godavari_llm/provider.py`): callers ask for a tier, never a model name, and
an adapter maps the tier to a model snapshot it has pinned. This file is a minimal copy with the same
field names, so the Day 13 package runs on its own; Day 12's client and adapters accept these requests.
Retries, structured-output validation and the cost ledger are Day 12's and are not repeated here.

What Day 13 adds is one check: the snapshot the adapter has pinned must be the snapshot the prompt
release was evaluated with. `pipeline.check_models()` refuses to run a batch when they disagree.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Protocol


class Tier(StrEnum):
    SMALL = "small"   # page classification
    LARGE = "large"   # field extraction


@dataclass(frozen=True)
class ModelRequest:
    tier: Tier
    system: str                       # the stable prefix: rendered instructions (cacheable)
    user_text: str                    # the variable part: the page or pages, wrapped as untrusted data
    page_ref: str | None = None
    json_schema: dict[str, Any] | None = None
    max_output_tokens: int = 1024
    timeout_s: float = 60.0
    idempotency_key: str = ""         # Day 12 builds it from page bytes, prompt version, schema and model
    purpose: str = "first"
    metadata: dict[str, str] = field(default_factory=dict)   # prompt_id, prompt_version, release_id


@dataclass(frozen=True)
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0


@dataclass(frozen=True)
class ModelResponse:
    text: str
    usage: Usage
    model: str
    stop_reason: str = "end"
    latency_s: float = 0.0
    request_id: str = ""


class ModelProvider(Protocol):
    name: str

    def model_for(self, tier: Tier) -> str: ...

    def complete(self, request: ModelRequest) -> ModelResponse: ...


def estimate_tokens(text: str) -> int:
    """A crude, deterministic token estimate: UTF-8 bytes divided by four.

    Real tokenizers differ by vendor. This proxy is close enough for English and, like real tokenizers,
    charges Telugu script several times more per word, which matters for a mixed-language loan file.
    """
    return max(1, (len(text.encode("utf-8")) + 3) // 4)
