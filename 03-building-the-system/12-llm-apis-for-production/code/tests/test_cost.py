"""Cost: the arithmetic, the ledger, and the idempotency that keeps a re-run from paying twice."""

from __future__ import annotations

import pytest
from conftest import make_request

from godavari_llm.client import idempotency_key
from godavari_llm.ledger import PRICE_CARD, CostLedger, Price, cost_usd
from godavari_llm.provider import ProviderTimeout, Tier, Usage

OK = ('{"x": 1}', "end")


def test_cost_arithmetic_per_token_category():
    price = Price(input=2.0, cache_read=0.1, cache_write=2.5, output=10.0, source="test")
    usage = Usage(input_tokens=1_000_000, cache_read_tokens=1_000_000, cache_write_tokens=1_000_000, output_tokens=1_000_000)
    assert cost_usd(usage, price, uplift=1.0) == pytest.approx(2.0 + 0.1 + 2.5 + 10.0)
    assert cost_usd(usage, price, uplift=1.1) == pytest.approx((2.0 + 0.1 + 2.5 + 10.0) * 1.1)


def test_a_cache_hit_costs_a_twentieth_of_fresh_input_on_the_large_tier():
    fresh = cost_usd(Usage(input_tokens=1500), PRICE_CARD[Tier.LARGE])
    cached = cost_usd(Usage(cache_read_tokens=1500), PRICE_CARD[Tier.LARGE])
    assert cached == pytest.approx(fresh / 20)


def test_one_extraction_page_in_rupees():
    # 1,700 fresh input tokens, 1,380 cached, 820 output, large tier, 10 percent uplift, Rs 95 per dollar
    usage = Usage(input_tokens=1700, cache_read_tokens=1380, output_tokens=820)
    ledger = CostLedger()
    row = ledger.record(file_id="F1", page=1, stage="extract", tier=Tier.LARGE, model="m", purpose="first",
                        attempt=1, outcome="ok", usage=usage, estimated=False, started_s=0, elapsed_s=12, key="k")
    expected_usd = (1700 * 2.0 + 1380 * 0.10 + 820 * 10.0) / 1e6 * 1.10
    assert row.usd == pytest.approx(expected_usd, rel=1e-6)
    assert row.inr == pytest.approx(expected_usd * 95.0, rel=1e-6)
    assert 1.0 < row.inr < 1.3            # about one rupee and twenty paise per extracted page


def test_ledger_sums_per_file_and_keeps_estimates_apart():
    ledger = CostLedger()
    for file_id, est in [("F1", False), ("F1", False), ("F2", False), ("F2", True)]:
        ledger.record(file_id=file_id, page=1, stage="extract", tier=Tier.SMALL, model="m", purpose="first", attempt=1,
                      outcome="timeout" if est else "ok", usage=Usage(input_tokens=1_000_000), estimated=est,
                      started_s=0, elapsed_s=1, key="k")
    per_file = ledger.inr_by_file()
    assert per_file["F1"] == pytest.approx(2 * 0.10 * 1.1 * 95)
    assert per_file["F2"] == pytest.approx(1 * 0.10 * 1.1 * 95)
    assert ledger.inr_by_file(include_estimated=True)["F2"] == pytest.approx(2 * 0.10 * 1.1 * 95)


def test_a_timeout_is_recorded_as_possibly_billed(harness):
    client, _, ledger, _ = harness([ProviderTimeout("t", elapsed_s=30.0), OK])
    client.call(make_request(), file_id="F1", page=1, stage="extract")
    timeout_row = ledger.rows[0]
    assert timeout_row.outcome == "timeout" and timeout_row.estimated and timeout_row.input_tokens == 1800


def test_the_same_key_twice_costs_nothing_the_second_time(harness):
    client, provider, ledger, _ = harness([OK])
    first = client.call(make_request("idem_page7"), file_id="F1", page=7, stage="extract")
    again = client.call(make_request("idem_page7"), file_id="F1", page=7, stage="extract")
    assert again is first and len(provider.requests) == 1
    assert ledger.rows[-1].outcome == "store_hit" and ledger.rows[-1].inr == 0.0


def test_idempotency_key_follows_content_not_time():
    base = dict(file_id="KKP-26-00001", page_no=7, page_sha256="aa", stage="extract", prompt_version="extract-v1",
                schema_version="godavari-extraction/1.0", model="large-model")
    assert idempotency_key(**base) == idempotency_key(**base)                       # a re-run, a duplicate upload
    assert idempotency_key(**base) != idempotency_key(**{**base, "page_sha256": "bb"})   # a re-scanned page
    assert idempotency_key(**base) != idempotency_key(**{**base, "prompt_version": "extract-v2"})
    assert idempotency_key(**base) != idempotency_key(**{**base, "model": "other-model"})
