"""The cost ledger: one row per attempt, priced in dollars and rupees, summed per loan file.

Prices are per million tokens, in US dollars, read on 21 October 2026 from the providers' official pricing
pages (URLs below). They will change; the ledger takes the card as data so a change is one edit.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

from .provider import Tier, Usage


@dataclass(frozen=True)
class Price:
    input: float          # USD per million uncached input tokens
    cache_read: float
    cache_write: float
    output: float
    source: str


# Both rows are real list prices as of 21 October 2026. The small tier is priced like Claude Haiku 5.5
# ($0.10 / $0.50, cache read $0.01, 5-minute cache write $0.125) and OpenAI's gpt-6-luna ($0.10 / $0.50,
# cached input $0.01); the large tier like Claude Sonnet 5.5 ($2 / $10, cache read $0.10, 5-minute cache
# write $2.50) and OpenAI's gpt-6.1-sol ($2 / $10, cached input $0.10). OpenAI lists no separate
# cache-write price, so using the Anthropic write price makes the card slightly conservative for OpenAI.
PRICE_CARD: dict[Tier, Price] = {
    Tier.SMALL: Price(0.10, 0.01, 0.125, 0.50,
                      "platform.claude.com/docs/en/about-claude/pricing; developers.openai.com/api/docs/pricing"),
    Tier.LARGE: Price(2.00, 0.10, 2.50, 10.00,
                      "platform.claude.com/docs/en/about-claude/pricing; developers.openai.com/api/docs/pricing"),
}
BATCH_DISCOUNT = 0.50        # both providers list batch processing at half price (October 2026)
RESIDENCY_UPLIFT = 1.10      # both list a 10 percent premium for regional or data-residency processing
USD_TO_INR = 95.0            # assumption: near the RBI reference rate of mid-2026; set it on the day you run


def cost_usd(usage: Usage, price: Price, uplift: float = RESIDENCY_UPLIFT) -> float:
    per_token = (usage.input_tokens * price.input + usage.cache_read_tokens * price.cache_read
                 + usage.cache_write_tokens * price.cache_write + usage.output_tokens * price.output)
    return per_token / 1_000_000 * uplift


@dataclass
class LedgerRow:
    file_id: str
    page: int | None
    stage: str            # classify | extract | escalate | repair
    tier: str
    model: str
    purpose: str
    attempt: int
    outcome: str          # ok | store_hit | rate_limited | overloaded | server_error | timeout | circuit_open | bad_request
    input_tokens: int
    cache_read_tokens: int
    cache_write_tokens: int
    output_tokens: int
    estimated: bool       # True when tokens are our estimate (a timeout: the provider may have billed it)
    usd: float
    inr: float
    started_s: float
    elapsed_s: float
    idempotency_key: str


class CostLedger:
    def __init__(self, card: dict[Tier, Price] | None = None, uplift: float = RESIDENCY_UPLIFT,
                 usd_to_inr: float = USD_TO_INR) -> None:
        self.card = card or PRICE_CARD
        self.uplift = uplift
        self.usd_to_inr = usd_to_inr
        self.rows: list[LedgerRow] = []

    def record(self, *, file_id: str, page: int | None, stage: str, tier: Tier, model: str, purpose: str,
               attempt: int, outcome: str, usage: Usage, estimated: bool, started_s: float, elapsed_s: float,
               key: str, billable: bool = True) -> LedgerRow:
        usd = cost_usd(usage, self.card[tier], self.uplift) if billable else 0.0
        row = LedgerRow(file_id, page, stage, tier.value, model, purpose, attempt, outcome,
                        usage.input_tokens, usage.cache_read_tokens, usage.cache_write_tokens, usage.output_tokens,
                        estimated, round(usd, 8), round(usd * self.usd_to_inr, 6), round(started_s, 3),
                        round(elapsed_s, 3), key)
        self.rows.append(row)
        return row

    def inr_by_file(self, include_estimated: bool = False) -> dict[str, float]:
        out: dict[str, float] = defaultdict(float)
        for r in self.rows:
            if include_estimated or not r.estimated:
                out[r.file_id] += r.inr
        return dict(out)

    def total_inr(self, include_estimated: bool = False) -> float:
        return sum(self.inr_by_file(include_estimated).values())

    def outcomes(self) -> dict[str, int]:
        out: dict[str, int] = defaultdict(int)
        for r in self.rows:
            out[r.outcome] += 1
        return dict(out)

    def write_csv(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(LedgerRow.__dataclass_fields__), lineterminator="\n")
            writer.writeheader()
            for r in self.rows:
                writer.writerow(asdict(r))
