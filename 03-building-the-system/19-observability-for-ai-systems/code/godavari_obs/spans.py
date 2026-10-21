"""Spans: the unit of a trace. One trace per loan file, one span per stage, one child span per model call.

The shape follows OpenTelemetry (a trace id, a span id, a parent, a start and an end, a status, attributes and events)
so that the same records can be exported to whatever backend Godavari runs. The model-call attributes use the names of
the OpenTelemetry generative-AI semantic conventions as read on 21 October 2026 (status: Development; the conventions
now live in the open-telemetry/semantic-conventions-genai repository and still change). Everything Godavari-specific
sits under the `kaagaz.` prefix, so a renamed upstream attribute is a one-line change in this file.

Times are business time in IST. The offline run uses virtual clocks (Day 12's for model calls, Day 18's simulated
screen log for people), so the same command always writes the same traces.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

IST = timezone(timedelta(hours=5, minutes=30), "IST")

# OpenTelemetry generative-AI semantic conventions (Development status, read 21 October 2026).
GEN_AI_OPERATION = "gen_ai.operation.name"            # "chat" for an inference call, "retrieval" for a search
GEN_AI_PROVIDER = "gen_ai.provider.name"
GEN_AI_REQUEST_MODEL = "gen_ai.request.model"
GEN_AI_INPUT_TOKENS = "gen_ai.usage.input_tokens"     # the convention says: ALL input tokens, cached ones included
GEN_AI_OUTPUT_TOKENS = "gen_ai.usage.output_tokens"
GEN_AI_CACHE_READ = "gen_ai.usage.cache_read.input_tokens"
GEN_AI_CACHE_WRITE = "gen_ai.usage.cache_write.input_tokens"
GEN_AI_PROMPT_NAME = "gen_ai.prompt.name"
GEN_AI_PROMPT_VERSION = "gen_ai.prompt.version"
GEN_AI_DATA_SOURCE = "gen_ai.data_source.id"
ERROR_TYPE = "error.type"                             # stable in the core conventions


def _hex(seed: str, n: int) -> str:
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:n]


def trace_id_for(run: str, subject: str) -> str:
    """32 hex characters (16 bytes), as OpenTelemetry wants, derived from the run and the subject: replayable."""
    return _hex(f"trace|{run}|{subject}", 32)


@dataclass
class Span:
    trace_id: str
    span_id: str
    parent_id: str | None
    name: str
    kind: str                       # file | stage | model_call | code | human | write | retrieval
    start: datetime
    end: datetime
    status: str = "ok"              # ok | error
    attrs: dict[str, Any] = field(default_factory=dict)
    events: list[dict[str, Any]] = field(default_factory=list)

    @property
    def seconds(self) -> float:
        return (self.end - self.start).total_seconds()

    def event(self, name: str, at: datetime, **attrs: Any) -> None:
        self.events.append({"name": name, "at": at, "attrs": attrs})


class Tracer:
    """Collects spans for one run. Span ids are derived from the trace id and a counter, so a re-run is identical."""

    def __init__(self, run: str) -> None:
        self.run = run
        self.spans: list[Span] = []
        self._n: dict[str, int] = {}

    def span(self, trace_id: str, name: str, kind: str, start: datetime, end: datetime | None = None,
             parent: Span | None = None, status: str = "ok", **attrs: Any) -> Span:
        k = self._n.get(trace_id, 0) + 1
        self._n[trace_id] = k
        s = Span(trace_id, _hex(f"span|{trace_id}|{k}", 16), parent.span_id if parent else None, name, kind,
                 start, end or start, status, dict(attrs))
        self.spans.append(s)
        return s

    def of_trace(self, trace_id: str) -> list[Span]:
        return [s for s in self.spans if s.trace_id == trace_id]
