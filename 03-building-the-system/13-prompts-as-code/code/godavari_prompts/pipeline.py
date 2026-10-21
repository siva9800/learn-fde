"""Run one prompt release over loan files: the whole-file strategy (1.x) or classify-then-extract (2.x).

The pipeline never holds a prompt string. It asks the registry which release is current, loads that
version from disk with its recorded hash, checks that the adapter's pinned models are the ones the
release was evaluated with, renders, calls, parses and merges. Which page type wins for a field is
decided here from the version's `[merge]` table, in code, not by asking the model.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from typing import Any

from .loader import PageView, PromptVersion, load
from .model_port import ModelProvider, ModelRequest, Tier
from .registry import Registry, Release
from .synth import LoanFile, fields_for

TELUGU = re.compile(r"[ఀ-౿]")
ESCALATE_BELOW = 0.70          # classification confidence below which the large tier is asked


class ModelMismatch(Exception):
    """The adapter would call a different model from the one this release was scored with."""


@dataclass(frozen=True)
class CallLog:
    file_id: str
    release_id: str
    call: str
    tier: str
    model: str
    page: int | None
    input_tokens: int
    output_tokens: int


@dataclass
class FileResult:
    file_id: str
    release_id: str
    fields: dict[str, dict[str, Any]]
    calls: list[CallLog] = field(default_factory=list)
    page_types: dict[int, str] = field(default_factory=dict)

    def tokens(self, tier: str) -> int:
        return sum(c.input_tokens for c in self.calls if c.tier == tier)


def check_models(release: Release, provider: ModelProvider) -> None:
    for tier, pinned in release.models.items():
        actual = provider.model_for(Tier(tier))
        if actual != pinned:
            raise ModelMismatch(f"{release.release_id} was evaluated on {tier}={pinned}, "
                                f"but the adapter would call {actual}; stop the batch")


def resolve(registry: Registry, env: str, prompt_id: str = "extraction") -> tuple[Release, PromptVersion]:
    rel = registry.current(env, prompt_id)
    if rel is None:
        raise LookupError(f"no {prompt_id} release pinned in {env}")
    return rel, load(rel.prompt_id, rel.version, expected_sha256=rel.content_sha256, root=registry.root)


def _key(f: LoanFile, page: int | None, call: str, rel: Release, model: str) -> str:
    """Day 12's idempotency key, with the prompt release in it: a rolled-back file is new work."""
    raw = "|".join([f.file_id, str(page), f.sha256, call, rel.release_id, rel.output_schema, model])
    return "idem_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def _call(provider: ModelProvider, rel: Release, f: LoanFile, call: str, tier: Tier, system: str, user: str,
          page: int | None, result: FileResult) -> dict[str, Any]:
    model = provider.model_for(tier)
    req = ModelRequest(tier=tier, system=system, user_text=user, idempotency_key=_key(f, page, call, rel, model),
                       metadata={"file_id": f.file_id, "release_id": rel.release_id, "call": call})
    resp = provider.complete(req)
    result.calls.append(CallLog(f.file_id, rel.release_id, call, tier.value, resp.model, page,
                                resp.usage.input_tokens, resp.usage.output_tokens))
    return json.loads(resp.text)          # Day 12 validates against the schema and repairs; not repeated here


def run_file(rel: Release, pv: PromptVersion, f: LoanFile, provider: ModelProvider) -> FileResult:
    if pv.strategy == "whole_file":
        return _whole_file(rel, pv, f, provider)
    if pv.strategy == "classify_then_extract":
        return _classify_then_extract(rel, pv, f, provider)
    raise ValueError(f"unknown strategy {pv.strategy!r}")


def run_batch(rel: Release, pv: PromptVersion, files: list[LoanFile], provider: ModelProvider) -> list[FileResult]:
    check_models(rel, provider)
    return [run_file(rel, pv, f, provider) for f in files]


def _whole_file(rel: Release, pv: PromptVersion, f: LoanFile, provider: ModelProvider) -> FileResult:
    result = FileResult(f.file_id, rel.release_id, {})
    spec = pv.call("extract_file")
    system, user = pv.render("extract_file", product=f.product, file_id=f.file_id,
                             fields=pv.field_defs(fields_for(f.product)),
                             pages=[PageView(p.number, p.text) for p in f.pages])
    answer = _call(provider, rel, f, "extract_file", Tier(spec["tier"]), system, user, None, result)
    result.fields = {k: answer["fields"].get(k, {"value": None, "page": None, "confidence": 0.0})
                     for k in fields_for(f.product)}
    return result


def _examples(pv: PromptVersion) -> list[dict[str, Any]]:
    out = []
    for ex in pv.meta.get("examples", []):
        data = json.loads((pv.path / ex["file"]).read_text(encoding="utf-8"))
        out.append({"page_type": ex["page_type"], "telugu": bool(ex["telugu"]),
                    "page_text": data["page_text"], "answer": data["answer"], "source_file_id": data["source_file_id"]})
    return out


def _classify_then_extract(rel: Release, pv: PromptVersion, f: LoanFile, provider: ModelProvider) -> FileResult:
    result = FileResult(f.file_id, rel.release_id, {})
    page_types = [{"name": k, "description": v["description"], "titles": v["titles"]}
                  for k, v in pv.meta["page_types"].items()]
    examples = _examples(pv)
    wanted = set(fields_for(f.product))
    found: dict[str, list[tuple[str, int, dict[str, Any]]]] = {k: [] for k in wanted}
    tier_c, tier_e = Tier(pv.call("classify")["tier"]), Tier(pv.call("extract")["tier"])

    for page in f.pages:
        view = PageView(page.number, page.text)
        system, user = pv.render("classify", page=view, page_types=page_types)
        answer = _call(provider, rel, f, "classify", tier_c, system, user, page.number, result)
        if float(answer.get("confidence", 0.0)) < ESCALATE_BELOW:
            # Model tiering (Day 12): a page the small model is unsure of is asked again on the large tier.
            answer = _call(provider, rel, f, "classify", tier_e, system, user, page.number, result)
        page_type = str(answer["page_type"])
        result.page_types[page.number] = page_type
        names = [n for n in pv.meta["page_fields"].get(page_type, []) if n in wanted]
        if not names:
            continue                                 # terms, statements, fillers: no extraction call at all
        telugu = TELUGU.search(page.text) is not None
        exs = [{"page_text": e["page_text"], "answer": e["answer"]} for e in examples
               if e["page_type"] == page_type and e["telugu"] == telugu]
        system, user = pv.render("extract", product=f.product, page_type=page_type, fields=pv.field_defs(names),
                                 telugu=telugu, examples=exs, page=view)
        answer = _call(provider, rel, f, "extract", tier_e, system, user, page.number, result)
        for n in names:
            value = answer["fields"].get(n)
            if value is not None:
                found[n].append((page_type, page.number, value))

    merge: dict[str, list[str]] = pv.meta.get("merge", {})
    for n in fields_for(f.product):
        order = merge.get(n, [])
        ranked = sorted(found[n], key=lambda c: (order.index(c[0]) if c[0] in order else len(order), c[1]))
        pick = next((v for _, _, v in ranked if v.get("value") is not None), None)
        result.fields[n] = pick or {"value": None, "page": None, "confidence": 0.0}
    return result
