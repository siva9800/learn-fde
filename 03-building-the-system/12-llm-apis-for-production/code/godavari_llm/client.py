"""The thin client layer: every model call in the system goes through LLMClient.call().

It owns, in one place: the idempotency check, the circuit breaker, retries with backoff and jitter inside
a deadline, the ledger row for every attempt, and (in call_structured) parsing and validating the answer
against the contract. Callers never see a vendor SDK, a status code or a raw string.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
import re
from dataclasses import dataclass, field, replace
from typing import Generic, TypeVar

from pydantic import BaseModel, ValidationError

from .ledger import CostLedger
from .provider import (BadRequest, Clock, ModelProvider, ModelRequest, ModelResponse, Overloaded, ProviderError,
                       ProviderTimeout, RateLimited, ServerError, SpendCapReached, Usage)
from .retry import CircuitBreaker, CircuitOpen, RetryPolicy, backoff_delay

T = TypeVar("T", bound=BaseModel)


def idempotency_key(*, file_id: str, page_no: int, page_sha256: str, stage: str, prompt_version: str,
                    schema_version: str, model: str) -> str:
    """Same page bytes + same prompt + same schema + same model = the same unit of work.

    Built from content, not from a counter or a timestamp, so that a retried call, a re-run of the 02:00 job
    and a duplicate SFTP upload all produce the same key. A re-scanned page has new bytes and a new key.
    """
    raw = "|".join([file_id, str(page_no), page_sha256, stage, prompt_version, schema_version, model])
    return "idem_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


class ResponseStore:
    """Completed responses by idempotency key. In production: a table in the customer's database, inside
    their boundary, with the same retention as the documents (Day 24). Here: a dict."""

    def __init__(self) -> None:
        self._data: dict[str, ModelResponse] = {}
        self.hits = 0

    def get(self, key: str) -> ModelResponse | None:
        resp = self._data.get(key)
        if resp is not None:
            self.hits += 1
        return resp

    def put(self, key: str, response: ModelResponse) -> None:
        self._data[key] = response

    def __len__(self) -> int:
        return len(self._data)


class RetriesExhausted(Exception):
    def __init__(self, message: str, attempts: int, last: ProviderError | None) -> None:
        super().__init__(message)
        self.attempts = attempts
        self.last = last


_OUTCOME = {RateLimited: "rate_limited", Overloaded: "overloaded", ServerError: "server_error",
            ProviderTimeout: "timeout", BadRequest: "bad_request", SpendCapReached: "spend_cap"}


@dataclass
class StructuredResult(Generic[T]):
    parsed: T | None
    problems: list[str] = field(default_factory=list)   # what had to happen to get a valid object


_FENCE = re.compile(r"```(?:json)?\s*(\{.*\})\s*```", re.DOTALL)


def lenient_json(text: str) -> tuple[object | None, str]:
    """Parse JSON, stripping only what is around the object (code fences, a sentence before or after).

    It never edits what is inside the object: no closing a truncated brace, no fixing a quote. A repair
    that guesses content is a silent wrong answer. Returns (object, "clean" | "wrapper_stripped" | "invalid").
    """
    try:
        return json.loads(text), "clean"
    except json.JSONDecodeError:
        pass
    m = _FENCE.search(text)
    candidate = m.group(1) if m else text[text.find("{"): text.rfind("}") + 1]
    try:
        return json.loads(candidate), "wrapper_stripped"
    except (json.JSONDecodeError, ValueError):
        return None, "invalid"


def short_error(e: ValidationError | str) -> str:
    if isinstance(e, str):
        return e
    parts = [f"{'.'.join(str(x) for x in err['loc'])}: {err['msg']}" for err in e.errors()[:3]]
    return "; ".join(parts)


class LLMClient:
    def __init__(self, provider: ModelProvider, ledger: CostLedger, clock: Clock, *,
                 policy: RetryPolicy | None = None, breaker: CircuitBreaker | None = None,
                 store: ResponseStore | None = None, seed: int = 7) -> None:
        self.provider = provider
        self.ledger = ledger
        self.clock = clock
        self.policy = policy or RetryPolicy()
        self.breaker = breaker or CircuitBreaker(clock)
        self.store = store if store is not None else ResponseStore()
        self.rng = random.Random(seed)             # jitter only; seeded so a run can be replayed

    def call(self, request: ModelRequest, *, file_id: str, page: int | None, stage: str) -> ModelResponse:
        model = self.provider.model_for(request.tier)
        common = dict(file_id=file_id, page=page, stage=stage, tier=request.tier, model=model,
                      purpose=request.purpose, key=request.idempotency_key)
        cached = self.store.get(request.idempotency_key)
        if cached is not None:
            self.ledger.record(**common, attempt=0, outcome="store_hit", usage=Usage(), estimated=False,
                               started_s=self.clock.now(), elapsed_s=0.0, billable=False)
            return cached
        start = self.clock.now()
        attempt = 0
        while True:
            attempt += 1
            if not self.breaker.allow():
                self.ledger.record(**common, attempt=attempt, outcome="circuit_open", usage=Usage(), estimated=False,
                                   started_s=self.clock.now(), elapsed_s=0.0, billable=False)
                raise CircuitOpen(f"breaker open; {file_id} page {page} deferred")
            t = self.clock.now()
            try:
                response = self.provider.complete(request)
            except ProviderError as e:
                timed_out = isinstance(e, ProviderTimeout)
                est = Usage(input_tokens=int(request.metadata.get("est_input_tokens", "0"))) if timed_out else Usage()
                self.ledger.record(**common, attempt=attempt, outcome=_OUTCOME.get(type(e), "error"), usage=est,
                                   estimated=timed_out, started_s=t, elapsed_s=self.clock.now() - t, billable=timed_out)
                if e.counts_against_health:
                    self.breaker.record_failure()
                if not e.retryable:
                    raise
                if attempt >= self.policy.max_attempts:
                    raise RetriesExhausted(f"gave up after {attempt} attempts: {e}", attempt, e) from e
                delay = backoff_delay(self.policy, attempt, self.rng, getattr(e, "retry_after_s", None))
                # Do not start an attempt that could not finish inside the deadline even if it succeeded.
                if self.clock.now() + delay + request.timeout_s - start > self.policy.call_deadline_s:
                    raise RetriesExhausted(f"deadline of {self.policy.call_deadline_s:.0f} s reached", attempt, e) from e
                self.clock.sleep(delay)
                continue
            self.breaker.record_success()
            self.ledger.record(**common, attempt=attempt, outcome="ok", usage=response.usage, estimated=False,
                               started_s=t, elapsed_s=self.clock.now() - t)
            self.store.put(request.idempotency_key, response)
            return response

    def call_structured(self, request: ModelRequest, schema: type[T], *, file_id: str, page: int | None,
                        stage: str) -> StructuredResult[T]:
        """One logical call that returns a validated object or None, and the list of what it took.

        The ladder: parse; if truncated, retry once with double the output budget; if the wrapper is
        chatty, strip it; if the object fails the schema, re-ask once with the error. Anything still
        invalid returns None: the caller routes the page to a human, it does not guess.
        """
        result: StructuredResult[T] = StructuredResult(None)
        response = self.call(request, file_id=file_id, page=page, stage=stage)
        if response.stop_reason == "max_tokens":
            result.problems.append("truncated")
            bigger = replace(request, max_output_tokens=request.max_output_tokens * 2, purpose="bigger_budget",
                             idempotency_key=request.idempotency_key + "#max2")
            response = self.call(bigger, file_id=file_id, page=page, stage=stage)
        for repair_round in (0, 1):
            if response.stop_reason == "refusal":
                result.problems.append("refusal")
                return result
            if response.stop_reason == "max_tokens":
                result.problems.append("still_truncated")
                return result
            obj, how = lenient_json(response.text)
            if how == "wrapper_stripped":
                result.problems.append("wrapper_stripped")
            error: ValidationError | str
            if obj is None:
                error = "the answer was not a JSON object"
            else:
                try:
                    result.parsed = schema.model_validate(obj)
                    return result
                except ValidationError as e:
                    error = e
            if repair_round == 1:
                result.problems.append("invalid_after_repair")
                return result
            result.problems.append("schema_invalid")
            response = self.call(self.repair_request(request, short_error(error)),
                                 file_id=file_id, page=page, stage="repair")
        return result

    @staticmethod
    def repair_request(request: ModelRequest, problem: str, round_no: int = 1) -> ModelRequest:
        """A re-ask that names the exact failure. Same system prefix (so the cache still hits)."""
        text = (f"{request.user_text}\n\nYour previous answer for this page was rejected: {problem}. "
                "Read the page again and return the corrected JSON object only.")
        est = request.metadata.get("est_input_tokens", "0")
        return replace(request, user_text=text, purpose="repair",
                       idempotency_key=f"{request.idempotency_key}#repair{round_no}",
                       metadata={**request.metadata, "est_input_tokens": str(int(est) + math.ceil(len(problem) / 4))})
