"""A deterministic fake model that reads the prompt and loses facts the further they sit from the request.

It sees only what a real model sees: the rendered system and user text. It finds the `<instructions>`
blocks, the requested fields and the `<page>` blocks, and answers the way the task tag asks. Its
behaviour is a caricature built so that the failures of section 06 reproduce on every run:

- Context position. The chance of using a fact falls with its distance, in tokens, from the nearest
  instruction block: near-certain within 1,500 tokens, then about three points lower per thousand.
  With instructions only at the top, the back of a 40-page file is worst; with the request repeated at
  the end, the middle is worst (the "lost in the middle" shape Liu et al. measured on real models).
- A missed fact is not always a null. When the annexure is missed, the form's "Co-applicant: none" is
  read instead; when an amount is missed, a figure from the wrong page sometimes comes back. Confidence
  does not drop for either, because the model does not know what it did not read.
- Telugu labels are read only when the prompt carries the glossary. Without it, a handwritten Telugu
  income declaration gives the largest figure on the page: the annual income, read as monthly, which is
  the 2019 OCR pilot's failure from Day 6.
- Snapshots differ. fake-large-2026-10 returns null for a smudged digit when the prompt asks it to;
  fake-large-2026-11, where the provider's "latest" alias moves on 16 November, guesses the digit.

None of these numbers describes a real vendor's model. The shapes are real; the rates are knobs.
Randomness is a hash of (file, field, page, model family), so a prompt change moves outcomes only
through the mechanisms above, never by reshuffling luck.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass

from .model_port import ModelRequest, ModelResponse, Tier, Usage, estimate_tokens


@dataclass(frozen=True)
class Snapshot:
    honours_null: bool          # returns null for a smudged digit when the prompt says so
    knee_tokens: int = 1500     # distance from the instructions at which recall starts to fall
    slope_per_1k: float = 0.033
    floor: float = 0.45


SNAPSHOTS: dict[str, Snapshot] = {
    "fake-small-2026-10": Snapshot(honours_null=True),
    "fake-large-2026-10": Snapshot(honours_null=True),
    "fake-large-2026-11": Snapshot(honours_null=False),
}
# A moving alias, as some providers offer: (date from which it points at, snapshot).
ALIASES: dict[str, list[tuple[str, str]]] = {
    "fake-large-latest": [("2026-10-01", "fake-large-2026-10"), ("2026-11-16", "fake-large-2026-11")],
    "fake-small-latest": [("2026-10-01", "fake-small-2026-10")],
}

TELUGU = re.compile(r"[ఀ-౿]")
AMOUNT = re.compile(r"Rs ([0-9?][0-9,?]*)")


def h01(*parts: object) -> float:
    digest = hashlib.sha256("|".join(str(p) for p in parts).encode("utf-8")).hexdigest()
    return int(digest[:12], 16) / 16**12


def family(model: str) -> str:
    return re.sub(r"-\d{4}-\d{2}$", "", model)


# Labels the model reads in English on any page: field -> [(priority, label)]. Lower priority wins.
ENGLISH_LABELS: dict[str, list[tuple[int, str]]] = {
    "applicant_name": [(1, "Applicant name"), (2, "Name")],
    "applicant_pan": [(1, "Permanent Account Number"), (2, "PAN")],
    "requested_amount": [(1, "Loan amount requested")],
    "monthly_income": [(1, "Net pay"), (1, "Monthly income")],
    "co_applicant_name": [(1, "Co-applicant name"), (2, "Co-applicant")],
    "on_road_price": [(1, "On-road price")],
    "net_weight_g": [(1, "Net weight (g)")],
    "business_name": [(1, "Business name")],
    "employer_name": [(1, "Employer")],
}
GLOSSARY_LABELS: dict[str, list[tuple[int, str]]] = {   # usable only when the glossary is in the prompt
    "applicant_name": [(1, "దరఖాస్తుదారు పేరు"), (2, "పేరు")],
    "monthly_income": [(1, "నెలసరి ఆదాయం")],
}
AMOUNT_FIELDS = {"requested_amount", "monthly_income", "on_road_price"}


@dataclass
class _Page:
    number: int
    lines: list[str]
    start_tok: int


@dataclass
class _Candidate:
    priority: int
    page: int
    tok: int
    raw: str


class FakeProvider:
    """Implements Day 12's ModelProvider shape. `pins` maps a tier to a snapshot or an alias."""

    name = "fake"

    def __init__(self, pins: dict[Tier, str], today: str = "2026-11-12") -> None:
        self.pins = dict(pins)
        self.today = today
        self.calls = 0

    def model_for(self, tier: Tier) -> str:
        model = self.pins[tier]
        if model in ALIASES:                        # an alias resolves to whatever it points at today
            model = [snap for since, snap in ALIASES[model] if since <= self.today][-1]
        return model

    # --- one call -----------------------------------------------------------------------------------
    def complete(self, request: ModelRequest) -> ModelResponse:
        self.calls += 1
        model = self.model_for(request.tier)
        snap = SNAPSHOTS[model]
        prompt = request.system + "\n" + request.user_text
        task = re.search(r'<task name="([a-z_]+)">', prompt)
        file_id = request.metadata.get("file_id", "")
        if task and task.group(1) == "classify_page":
            answer = self._classify(prompt, file_id, model)
        else:
            answer = self._extract(prompt, file_id, model, snap)
        text = json.dumps(answer, ensure_ascii=False)
        return ModelResponse(text, Usage(estimate_tokens(prompt), estimate_tokens(text)), model,
                             request_id=f"fake-{self.calls:06d}")

    # --- reading the prompt -------------------------------------------------------------------------
    @staticmethod
    def _instruction_spans(prompt: str) -> list[tuple[int, int]]:
        spans = []
        for m in re.finditer(r"<instructions>(.*?)</instructions>", prompt, re.DOTALL):
            spans.append((estimate_tokens(prompt[:m.start()]), estimate_tokens(prompt[:m.end()])))
        return spans

    @staticmethod
    def _pages(prompt: str) -> list[_Page]:
        pages = []
        for m in re.finditer(r'<page number="(\d+)">\n(.*?)\n</page>', prompt, re.DOTALL):
            pages.append(_Page(int(m.group(1)), m.group(2).splitlines(), estimate_tokens(prompt[:m.start(2)])))
        return pages

    @staticmethod
    def _recall(snap: Snapshot, tok: int, spans: list[tuple[int, int]]) -> float:
        if not spans:
            return snap.floor
        dist = min(0 if a <= tok <= b else (tok - b if tok > b else a - tok) for a, b in spans)
        if dist <= snap.knee_tokens:
            return 0.999
        return max(snap.floor, 0.999 - snap.slope_per_1k * (dist - snap.knee_tokens) / 1000)

    # --- classification -----------------------------------------------------------------------------
    def _classify(self, prompt: str, file_id: str, model: str) -> dict[str, object]:
        types: list[tuple[str, list[str]]] = []
        block = re.search(r"<page_types>\n(.*?)</page_types>", prompt, re.DOTALL)
        for line in (block.group(1).splitlines() if block else []):
            m = re.match(r"- ([a-z_]+): .*Printed titles: (.*)$", line)
            if m:
                types.append((m.group(1), [t.strip() for t in m.group(2).split(" | ")]))
        pages = self._pages(prompt)
        if not pages:
            return {"page_type": "other", "confidence": 0.0}
        page = pages[0]
        first = page.lines[0] if page.lines else ""
        best, best_len = "other", 0
        for name, titles in types:
            for title in titles:
                if first.startswith(title) and len(title) > best_len:
                    best, best_len = name, len(title)
        hard = "[handwritten]" in "\n".join(page.lines) or bool(TELUGU.search(first))
        if best != "other" and h01(file_id, page.number, family(model), "classify") < (0.04 if hard else 0.01):
            return {"page_type": "other", "confidence": 0.55}           # a misread title
        return {"page_type": best, "confidence": 0.97 if best != "other" else 0.8}

    # --- extraction ---------------------------------------------------------------------------------
    def _extract(self, prompt: str, file_id: str, model: str, snap: Snapshot) -> dict[str, object]:
        spans = self._instruction_spans(prompt)
        instructions = " ".join(prompt[a:b] for a, b in
                                ((m.start(), m.end()) for m in re.finditer(r"<instructions>.*?</instructions>",
                                                                        prompt, re.DOTALL)))
        block = re.search(r"<fields>\n(.*?)</fields>", prompt, re.DOTALL)
        fields = re.findall(r"^- ([a-z_]+):", block.group(1), re.MULTILINE) if block else []
        glossary = "<telugu_glossary>" in instructions
        null_rule = snap.honours_null and "return null" in instructions
        pages = self._pages(prompt)
        out: dict[str, dict[str, object]] = {}
        for fld in fields:
            cands = self._candidates(fld, pages, glossary)
            chosen: _Candidate | None = None
            for c in sorted(cands, key=lambda c: (c.priority, c.page)):
                if h01(file_id, fld, c.page, family(model), "recall") < self._recall(snap, c.tok, spans):
                    chosen = c
                    break
            if chosen is None:
                out[fld] = self._missed(fld, pages, file_id, model)
                continue
            out[fld] = self._value(fld, chosen, null_rule, file_id, model)
        return {"fields": out}

    @staticmethod
    def _candidates(fld: str, pages: list[_Page], glossary: bool) -> list[_Candidate]:
        labels = list(ENGLISH_LABELS.get(fld, []))
        if glossary:
            labels += GLOSSARY_LABELS.get(fld, [])
        cands: list[_Candidate] = []
        for page in pages:
            first = page.lines[0] if page.lines else ""
            # a page titled only in Telugu (a bilingual form has "Telugu / ENGLISH" and does not count)
            telugu_only_income = TELUGU.search(first) is not None and re.search(r"[A-Z]{3}", first) is None
            for i, line in enumerate(page.lines):
                for prio, label in labels:
                    # match "label: value" or "telugu / label: value", never a longer label
                    m = re.match(rf"^(?:.* / )?{re.escape(label)}: (.+)$", line)
                    if m and not (label == "Name" and not line.startswith("Name:")) \
                            and not (label == "PAN" and not line.startswith("PAN:")) \
                            and not (label == "Co-applicant" and "Co-applicant name" in line) \
                            and not (label == "పేరు" and not line.startswith("పేరు:")):
                        tok = page.start_tok + estimate_tokens("\n".join(page.lines[:i]))
                        cands.append(_Candidate(prio, page.number, tok, m.group(1).strip()))
            if fld == "monthly_income" and not glossary and telugu_only_income:
                amounts = [(int(a.replace(",", "")), a) for a in AMOUNT.findall("\n".join(page.lines)) if "?" not in a]
                if amounts and not any(c.page == page.number for c in cands):
                    # No label it can read: it takes the biggest rupee figure on the page.
                    cands.append(_Candidate(1, page.number, page.start_tok, "Rs " + max(amounts)[1]))
        return cands

    @staticmethod
    def _missed(fld: str, pages: list[_Page], file_id: str, model: str) -> dict[str, object]:
        if fld in AMOUNT_FIELDS and h01(file_id, fld, family(model), "distractor") < 0.5:
            for page in pages:
                for line in page.lines:
                    if " NEFT CR " in line:                      # a figure from the wrong page, said confidently
                        value = line.rsplit(" ", 1)[1].split(".")[0]
                        return {"value": value, "page": page.number, "confidence": 0.82}
        return {"value": None, "page": None, "confidence": 0.3}

    @staticmethod
    def _value(fld: str, c: _Candidate, null_rule: bool, file_id: str, model: str) -> dict[str, object]:
        raw = c.raw
        if fld in AMOUNT_FIELDS:
            m = AMOUNT.search(raw)
            raw = m.group(1) if m else raw
            raw = raw.replace(",", "")
        if "?" in raw:
            if null_rule:
                return {"value": None, "page": c.page, "confidence": 0.3}
            guess = str(int(h01(file_id, fld, "digit") * 10))
            return {"value": raw.replace("?", guess), "page": c.page, "confidence": 0.86}
        return {"value": raw, "page": c.page, "confidence": 0.9 if c.priority == 1 else 0.88}
