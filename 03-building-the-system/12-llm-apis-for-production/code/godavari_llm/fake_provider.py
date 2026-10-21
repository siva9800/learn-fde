"""A fake model provider that misbehaves the way real ones do, reproducibly.

It reads the synthetic page truth (it is the model's "eyes") and answers classification and extraction
requests, while simulating, from one seeded random generator and a virtual clock:

- latency: time to first token grows with input size, generation time with output size, plus a heavy tail;
- 429s from a token bucket per tier, with a retry-after hint;
- overload (529) during a configured outage window, and occasional 500s;
- timeouts, after which the provider still bills the work most of the time;
- malformed JSON: truncation at the output limit, and (in "prompt" mode, no constrained decoding) code
  fences and chatty text around the object;
- wrong-but-valid answers: well-formed JSON with the wrong content and a confident score;
- prompt caching of the stable system prefix, with a time-to-live.

Nothing here is a claim about any real vendor's numbers. The shapes are real; the rates are knobs.
"""

from __future__ import annotations

import bisect
import json
import math
import random
from dataclasses import dataclass, field
from typing import Callable

from .contract import Doc
from .provider import (Clock, ModelRequest, ModelResponse, Overloaded, ProviderTimeout, RateLimited,
                       ServerError, Tier, Usage)
from .synthetic import SyntheticFile, SyntheticPage

EXTRACT_FIELDS = ("applicant_name", "applicant_pan", "co_applicant_name", "product", "requested_amount", "monthly_income")
AMOUNT_FIELDS = ("requested_amount", "monthly_income")


@dataclass
class FakeConfig:
    seed: int = 7                                   # chosen: its night shows all five wrong-answer variants
    json_mode: str = "schema"                       # "schema": constrained decoding; "prompt": asked nicely
    rpm: dict[Tier, int] = field(default_factory=lambda: {Tier.SMALL: 1200, Tier.LARGE: 240})
    per_second: dict[Tier, int] = field(default_factory=lambda: {Tier.SMALL: 25, Tier.LARGE: 8})   # short bursts are limited too
    p_server_error: float = 0.006
    p_misclassify: float = 0.03
    p_low_confidence: float = 0.03
    p_hard_field: float = 0.06                      # a correct value read with low confidence
    p_wrong: float = 0.06                           # extraction: a wrong-but-valid answer on a first attempt
    p_fix_on_repair: float = 0.8
    p_truncate: float = 0.01
    p_stray_text: float = 0.07                      # only in "prompt" mode
    p_refusal: float = 0.002
    p_billed_on_timeout: float = 0.7
    tail_p: float = 0.02
    tail_mult: float = 5.0
    outages: list[tuple[float, float]] = field(default_factory=lambda: [(240.0, 420.0)])  # 02:04 to 02:07
    cache_ttl_s: float = 300.0
    min_cacheable_tokens: int = 1024
    ttft_base_s: dict[Tier, float] = field(default_factory=lambda: {Tier.SMALL: 0.35, Tier.LARGE: 0.9})
    ttft_per_1k_input_s: dict[Tier, float] = field(default_factory=lambda: {Tier.SMALL: 0.03, Tier.LARGE: 0.12})
    output_tok_per_s: dict[Tier, float] = field(default_factory=lambda: {Tier.SMALL: 160.0, Tier.LARGE: 70.0})
    reasoning_tokens: dict[Tier, int] = field(default_factory=lambda: {Tier.SMALL: 0, Tier.LARGE: 220})


class FakeProvider:
    name = "fake"

    def __init__(self, files: list[SyntheticFile], clock: Clock, config: FakeConfig | None = None) -> None:
        self.cfg = config or FakeConfig()
        self.clock = clock
        self.rng = random.Random(self.cfg.seed)
        self.pages: dict[str, SyntheticPage] = {p.ref: p for f in files for p in f.pages}
        self.files: dict[str, SyntheticFile] = {f.file_id: f for f in files}
        self._admitted: dict[Tier, list[float]] = {t: [] for t in Tier}     # sorted start times, for the limiter
        self._cache: dict[tuple[Tier, int], float] = {}                     # prefix -> expiry
        self._seq = 0
        self.invoice: list[tuple[Tier, Usage]] = []       # what the provider bills: the ground truth for cost
        self.injected: dict[str, str] = {}                # request key -> wrong-answer variant served
        self.calls = 0

    def model_for(self, tier: Tier) -> str:
        return f"fake-{tier.value}-2026-10"

    # --- one attempt --------------------------------------------------------------------------------
    def complete(self, request: ModelRequest) -> ModelResponse:
        return self._run(request, on_delta=None)

    def complete_streaming(self, request: ModelRequest, on_delta: Callable[[str, float], None]) -> ModelResponse:
        """Same as complete(), but calls on_delta(chunk, virtual_time) as text is produced."""
        return self._run(request, on_delta=on_delta)

    def _run(self, request: ModelRequest, on_delta: Callable[[str, float], None] | None) -> ModelResponse:
        cfg, rng, t0 = self.cfg, self.rng, self.clock.now()
        self.calls += 1
        self._seq += 1
        rid = f"fake_req_{self._seq:06d}"
        if any(a <= t0 < b for a, b in cfg.outages):
            self.clock.sleep(0.3)
            raise Overloaded("overloaded_error (simulated 529)", elapsed_s=0.3, request_id=rid)
        retry_after = self._take_token(request.tier, t0)
        if retry_after is not None:
            self.clock.sleep(0.15)
            raise RateLimited("rate_limit_error (simulated 429)", retry_after_s=retry_after, elapsed_s=0.15, request_id=rid)
        if rng.random() < cfg.p_server_error:
            wait = rng.uniform(0.5, 3.0)
            self.clock.sleep(wait)
            raise ServerError("api_error (simulated 500)", elapsed_s=wait, request_id=rid)

        page = self.pages[request.page_ref] if request.page_ref else None
        task = request.metadata.get("task", "extract")
        if task == "note":                                  # free text for a person: the streaming demo
            return self._note(request, rid, on_delta)
        obj = self._classify(request, page) if task == "classify" else self._extract(request, page)
        text, stop = json.dumps(obj, ensure_ascii=False), "end"
        if rng.random() < cfg.p_refusal:
            text, stop = "I can't help with this document.", "refusal"
        elif cfg.json_mode == "prompt" and rng.random() < cfg.p_stray_text:
            text = rng.choice([f"```json\n{text}\n```", f"Here is the extracted data:\n{text}",
                               f"{text}\nLet me know if you need anything else."])
        out_tokens = math.ceil(len(text) / 3) + cfg.reasoning_tokens[request.tier]
        if request.purpose != "bigger_budget" and rng.random() < cfg.p_truncate:
            out_tokens = request.max_output_tokens
        if out_tokens >= request.max_output_tokens:
            out_tokens = request.max_output_tokens
            text, stop = text[: int(len(text) * 0.6)], "max_tokens"

        usage = self._usage(request, page, task, out_tokens, t0)
        total_in = usage.input_tokens + usage.cache_read_tokens + usage.cache_write_tokens
        tail = cfg.tail_mult if rng.random() < cfg.tail_p else 1.0      # a slow replica, a long queue
        ttft = (cfg.ttft_base_s[request.tier] + total_in / 1000 * cfg.ttft_per_1k_input_s[request.tier])             * rng.lognormvariate(0.0, 0.3) * tail
        gen = out_tokens / cfg.output_tok_per_s[request.tier] * rng.lognormvariate(0.0, 0.15) * tail
        duration = ttft + gen
        if duration > request.timeout_s:
            self.clock.sleep(request.timeout_s)
            if rng.random() < cfg.p_billed_on_timeout:
                self.invoice.append((request.tier, usage))     # it finished after we hung up, and was billed
            raise ProviderTimeout(f"no response in {request.timeout_s:.0f} s", elapsed_s=request.timeout_s, request_id=rid)
        if on_delta is not None:
            self.clock.sleep(ttft)
            chunks = [text[i:i + 24] for i in range(0, len(text), 24)] or [""]
            for chunk in chunks:
                on_delta(chunk, self.clock.now())
                self.clock.sleep(gen / len(chunks))
        else:
            self.clock.sleep(duration)
        self.invoice.append((request.tier, usage))
        return ModelResponse(text, usage, self.model_for(request.tier), stop, duration, rid, ttft_s=ttft)

    def _note(self, request: ModelRequest, rid: str, on_delta: Callable[[str, float], None] | None) -> ModelResponse:
        """The fake has no language model: it 'writes' the draft it was handed, at a realistic pace."""
        cfg, rng = self.cfg, self.rng
        text = request.metadata.get("draft", "")
        out_tokens = math.ceil(len(text) / 3) + cfg.reasoning_tokens[request.tier]
        usage = Usage(math.ceil((len(request.system) + len(request.user_text)) / 4), 0, 0, out_tokens)
        ttft = cfg.ttft_base_s[request.tier] * rng.lognormvariate(0.0, 0.2) + cfg.reasoning_tokens[request.tier] / cfg.output_tok_per_s[request.tier]
        gen = (out_tokens - cfg.reasoning_tokens[request.tier]) / cfg.output_tok_per_s[request.tier]
        self.clock.sleep(ttft)
        words = text.split(" ")
        for i, w in enumerate(words):
            if on_delta is not None:
                on_delta(w + (" " if i < len(words) - 1 else ""), self.clock.now())
            self.clock.sleep(gen / len(words))
        self.invoice.append((request.tier, usage))
        return ModelResponse(text, usage, self.model_for(request.tier), "end", ttft + gen, rid, ttft_s=ttft)

    # --- internals ------------------------------------------------------------------------------------
    def _take_token(self, tier: Tier, t: float) -> float | None:
        """Sliding-window limiter: at most rpm requests in any 60 s and per_second in any 1 s.
        Returns None if admitted, else the retry-after hint in whole seconds."""
        times = self._admitted[tier]
        in_minute = bisect.bisect_right(times, t) - bisect.bisect_right(times, t - 60.0)
        in_second = bisect.bisect_right(times, t) - bisect.bisect_right(times, t - 1.0)
        if in_minute >= self.cfg.rpm[tier]:
            oldest = times[bisect.bisect_right(times, t - 60.0)]
            return float(max(1, math.ceil(oldest + 60.0 - t)))
        if in_second >= self.cfg.per_second[tier]:
            return 1.0
        bisect.insort(times, t)
        return None

    def _usage(self, request: ModelRequest, page: SyntheticPage | None, task: str, out_tokens: int, t: float) -> Usage:
        # The stable prefix is the instructions plus the schema (providers count the schema as input too).
        prefix = request.system + (json.dumps(request.json_schema, sort_keys=True) if request.json_schema else "")
        system_tokens = math.ceil(len(prefix) / 4)
        image = 0 if page is None else (page.thumb_tokens if task == "classify" else page.image_tokens)
        variable = math.ceil(len(request.user_text) / 4) + image
        read = write = 0
        if system_tokens >= self.cfg.min_cacheable_tokens:
            key = (request.tier, hash(prefix))
            if self._cache.get(key, -1.0) >= t:
                read = system_tokens
            else:
                write = system_tokens
            self._cache[key] = t + self.cfg.cache_ttl_s
        else:
            variable += system_tokens
        return Usage(variable, read, write, out_tokens)

    def _classify(self, request: ModelRequest, page: SyntheticPage | None) -> dict:
        rng = self.rng
        assert page is not None
        truth = page.doc
        p_mis = self.cfg.p_misclassify if request.tier == Tier.SMALL else 0.005
        if rng.random() < p_mis:
            wrong = rng.choice([d for d in Doc if d not in (truth, Doc.UNKNOWN)])
            return {"page_type": wrong.value, "confidence": round(rng.uniform(0.45, 0.75), 2)}
        if request.tier == Tier.SMALL and rng.random() < self.cfg.p_low_confidence:
            return {"page_type": truth.value, "confidence": round(rng.uniform(0.40, 0.58), 2)}
        return {"page_type": truth.value, "confidence": round(rng.uniform(0.86, 0.99), 2)}

    def _extract(self, request: ModelRequest, page: SyntheticPage | None) -> dict:
        rng = self.rng
        assert page is not None
        out: dict[str, object] = {"page_type": page.doc.value}
        for f in EXTRACT_FIELDS:
            if f in page.truth:
                hard = rng.random() < self.cfg.p_hard_field          # a stamp over it, a faint photocopy
                conf = rng.uniform(0.50, 0.74) if hard else rng.uniform(0.82, 0.98)
                out[f] = {"value": page.truth[f], "confidence": round(conf, 2), "evidence": page.lines[f]}
            else:
                out[f] = {"value": None, "confidence": 0.0, "evidence": ""}
        serve_wrong = (rng.random() < self.cfg.p_wrong if request.purpose != "repair"
                       else rng.random() > self.cfg.p_fix_on_repair and request.idempotency_key.split("#")[0] in self.injected)
        if serve_wrong:
            variant = self._wrong(out, page)
            if variant:
                self.injected[request.idempotency_key.split("#")[0]] = variant
        return out

    def _wrong(self, out: dict, page: SyntheticPage) -> str | None:
        """Mutate a correct answer into a confident, well-formed, wrong one. Returns the variant name."""
        rng = self.rng
        file = self.files[page.file_id]
        options = []
        if "requested_amount" in page.truth:
            options += ["amount_x10", "picked_the_wrong_amount_line"]
        if "monthly_income" in page.truth:
            options.append("income_as_annual")
        if "applicant_name" in page.truth and "co_applicant_name" in page.lines:
            options.append("swap_applicant_and_co_applicant")
        if "applicant_pan" in page.truth:
            options.append("pan_digit_misread")
        if not options:
            return None
        variant = rng.choice(options)
        if variant == "amount_x10":
            out["requested_amount"]["value"] = int(page.truth["requested_amount"]) * 10
        elif variant == "picked_the_wrong_amount_line":     # on the page, matches its evidence, and wrong
            line = page.lines["other_amount"]
            out["requested_amount"] = {"value": int(line.split("Rs. ")[1].replace(",", "")), "confidence": 0.91,
                                       "evidence": line}
        elif variant == "income_as_annual":
            out["monthly_income"]["value"] = int(page.truth["monthly_income"]) * 12
        elif variant == "swap_applicant_and_co_applicant":
            out["applicant_name"] = {"value": file.truth["co_applicant_name"], "confidence": 0.93,
                                     "evidence": page.lines["co_applicant_name"]}
        else:
            pan = str(page.truth["applicant_pan"])
            digit = str((int(pan[5]) + 3) % 10)
            bad = pan[:5] + digit + pan[6:]
            out["applicant_pan"] = {"value": bad, "confidence": 0.95,
                                    "evidence": page.lines["applicant_pan"].replace(pan, bad)}
        return variant
