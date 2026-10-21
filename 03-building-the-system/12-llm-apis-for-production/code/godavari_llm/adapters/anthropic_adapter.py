"""Optional: the ModelProvider interface over the Anthropic Messages API. Not needed to run anything.

Not run for this chapter (no key was used; nothing in the package imports this file). Written against the
Anthropic documentation and the Python SDK as of October 2026: structured outputs through
`output_config.format`, prompt caching with `cache_control`, typed errors, `retry-after` on 429.

    pip install -r code/requirements-real-provider.txt
    export ANTHROPIC_API_KEY=...            # or `ant auth login`
    export KAAGAZ_SYNTHETIC_ONLY=yes        # the same guard as Day 11's adapter

Three decisions in this file are the chapter's argument in miniature:
1. `max_retries=0`. The SDK retries 429 and 5xx twice by default; our client retries too. Leave both on and
   one logical call can become twelve attempts, none of them in the ledger.
2. Every vendor error becomes one of our error types. Nothing above this file catches an SDK class.
3. The tier map is the only place a model name appears. Switching to another provider, or to the same models
   through a cloud in an India region (Day 24 decides), is a new adapter and a new price-card row.
"""

from __future__ import annotations

import base64
import os
from collections.abc import Callable
from typing import Any

from ..provider import (BadRequest, ModelRequest, ModelResponse, Overloaded, ProviderTimeout, RateLimited,
                        ServerError, SpendCapReached, Tier, Usage)

TIER_MODELS = {Tier.SMALL: "claude-haiku-5-5", Tier.LARGE: "claude-sonnet-5-5"}   # pinned, reviewed on change
EFFORT = {Tier.SMALL: "low", Tier.LARGE: "medium"}
STOP = {"end_turn": "end", "max_tokens": "max_tokens", "refusal": "refusal"}


class AnthropicProvider:
    name = "anthropic"

    def __init__(self, load_page: Callable[[str], bytes | str], client: Any | None = None) -> None:
        if os.environ.get("KAAGAZ_SYNTHETIC_ONLY") != "yes":
            raise PermissionError("synthetic files only: no real Godavari page may reach a public endpoint "
                                  "(the CISO's condition; production model access is Days 24 and 25)")
        if client is None:
            import anthropic                                   # optional dependency, imported only here
            client = anthropic.Anthropic(max_retries=0)        # our client owns retries (decision 1)
        self.client = client
        self.load_page = load_page                             # page_ref -> PNG bytes, or the page text

    def model_for(self, tier: Tier) -> str:
        return TIER_MODELS[tier]

    def complete(self, request: ModelRequest) -> ModelResponse:
        import anthropic

        content: list[dict[str, Any]] = []
        if request.page_ref:
            page = self.load_page(request.page_ref)
            if isinstance(page, bytes):
                content.append({"type": "image", "source": {"type": "base64", "media_type": "image/png",
                                                            "data": base64.standard_b64encode(page).decode("ascii")}})
            else:
                content.append({"type": "text", "text": page})
        content.append({"type": "text", "text": request.user_text})
        output_config: dict[str, Any] = {"effort": EFFORT[request.tier]}
        if request.json_schema is not None:
            output_config["format"] = {"type": "json_schema", "schema": request.json_schema}
        try:
            response = self.client.with_options(timeout=request.timeout_s).messages.create(
                model=self.model_for(request.tier),
                max_tokens=request.max_output_tokens,
                system=[{"type": "text", "text": request.system, "cache_control": {"type": "ephemeral"}}],
                messages=[{"role": "user", "content": content}],
                output_config=output_config,
            )
        except anthropic.RateLimitError as e:                  # most specific first
            body = e.body if isinstance(e.body, dict) else {}
            if body.get("error", {}).get("details", {}).get("error_code") == "enforced_spend_limit_reached":
                raise SpendCapReached(str(e)) from e           # a monthly cap: retrying cannot help
            after = e.response.headers.get("retry-after")
            raise RateLimited(str(e), retry_after_s=float(after) if after else None) from e
        except anthropic.APITimeoutError as e:
            raise ProviderTimeout(str(e), elapsed_s=request.timeout_s) from e
        except anthropic.APIConnectionError as e:
            raise ServerError(str(e)) from e
        except anthropic.APIStatusError as e:
            if e.status_code in (503, 529):
                raise Overloaded(str(e)) from e
            if e.status_code >= 500:
                raise ServerError(str(e)) from e
            raise BadRequest(f"{e.status_code}: {e}") from e    # 400, 401, 403, 404, 413: fix, do not retry

        u = response.usage
        usage = Usage(input_tokens=u.input_tokens, cache_read_tokens=u.cache_read_input_tokens or 0,
                      cache_write_tokens=u.cache_creation_input_tokens or 0, output_tokens=u.output_tokens)
        text = next((b.text for b in response.content if b.type == "text"), "")
        return ModelResponse(text, usage, response.model, STOP.get(response.stop_reason, str(response.stop_reason)),
                             0.0, response._request_id or "")
