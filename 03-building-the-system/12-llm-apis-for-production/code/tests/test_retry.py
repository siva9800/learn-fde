"""Retries: which errors are retried, how long we wait, when we stop, and when we stop calling at all."""

from __future__ import annotations

import random

import pytest
from conftest import make_request

from godavari_llm.client import RetriesExhausted
from godavari_llm.provider import BadRequest, Overloaded, ProviderTimeout, RateLimited, ServerError, SpendCapReached
from godavari_llm.retry import BreakerState, CircuitOpen, RetryPolicy, backoff_delay

OK = ('{"x": 1}', "end")


def test_backoff_is_full_jitter_under_a_growing_cap():
    policy = RetryPolicy(base_delay_s=1.0, max_delay_s=20.0)
    rng = random.Random(0)
    for attempt, cap in [(1, 1.0), (2, 2.0), (3, 4.0), (4, 8.0), (6, 20.0), (9, 20.0)]:
        draws = [backoff_delay(policy, attempt, rng) for _ in range(500)]
        assert 0.0 <= min(draws) and max(draws) <= cap
        assert max(draws) > 0.8 * cap          # it really spreads across the window
        assert len({round(d, 6) for d in draws}) > 450   # and no two workers wait the same time


def test_retry_after_is_a_floor():
    rng = random.Random(0)
    assert all(backoff_delay(RetryPolicy(), 1, rng, retry_after_s=7.0) >= 7.0 for _ in range(100))


def test_429_then_success_is_one_logical_call(harness):
    client, provider, ledger, clock = harness([RateLimited("429", retry_after_s=3.0, elapsed_s=0.1), OK])
    resp = client.call(make_request(), file_id="F1", page=1, stage="extract")
    assert resp.text == OK[0]
    assert [r.outcome for r in ledger.rows] == ["rate_limited", "ok"]
    assert clock.now() >= 3.0 + 2.0             # waited at least the server's hint, then the call itself


def test_5xx_and_timeouts_are_retried_with_the_same_key(harness):
    client, provider, ledger, _ = harness([ServerError("500", elapsed_s=1.0), ProviderTimeout("t", elapsed_s=30.0), OK])
    client.call(make_request("idem_same"), file_id="F1", page=1, stage="extract")
    assert {r.idempotency_key for r in provider.requests} == {"idem_same"}
    assert [r.outcome for r in ledger.rows] == ["server_error", "timeout", "ok"]


@pytest.mark.parametrize("error", [BadRequest("400 schema too complex"), SpendCapReached("429 monthly cap")])
def test_non_retryable_errors_fail_on_the_first_attempt(harness, error):
    client, provider, ledger, _ = harness([error, OK])
    with pytest.raises(type(error)):
        client.call(make_request(), file_id="F1", page=1, stage="extract")
    assert len(provider.requests) == 1


def test_gives_up_after_max_attempts(harness):
    script = [Overloaded("529", elapsed_s=0.2) for _ in range(4)] + [OK]
    client, provider, _, _ = harness(script, policy=RetryPolicy(max_attempts=4), threshold=99)
    with pytest.raises(RetriesExhausted) as info:
        client.call(make_request(), file_id="F1", page=1, stage="extract")
    assert info.value.attempts == 4 and len(provider.requests) == 4


def test_never_starts_a_retry_past_the_call_deadline(harness):
    script = [ProviderTimeout("t", elapsed_s=30.0) for _ in range(3)] + [OK]
    client, provider, _, clock = harness(script, policy=RetryPolicy(max_attempts=10, call_deadline_s=70.0), threshold=99)
    with pytest.raises(RetriesExhausted, match="deadline"):
        client.call(make_request(), file_id="F1", page=1, stage="extract")
    assert len(provider.requests) == 2          # a third 30 s attempt could not finish by 70 s: not started
    assert clock.now() <= 70.0


def test_breaker_opens_fails_fast_then_probes_and_closes(harness):
    script = [Overloaded("529", elapsed_s=0.1) for _ in range(3)] + [OK, OK]
    client, provider, ledger, clock = harness(script, policy=RetryPolicy(max_attempts=3), threshold=3)
    with pytest.raises(RetriesExhausted):
        client.call(make_request("a"), file_id="F1", page=1, stage="extract")
    assert client.breaker.state == BreakerState.OPEN
    with pytest.raises(CircuitOpen):
        client.call(make_request("b"), file_id="F1", page=2, stage="extract")
    assert len(provider.requests) == 3          # the open breaker did not call the provider
    clock.sleep(61.0)
    client.call(make_request("c"), file_id="F1", page=3, stage="extract")
    assert client.breaker.state == BreakerState.CLOSED
    assert [s for _, s in client.breaker.transitions] == ["open", "half_open", "closed"]


def test_429s_do_not_trip_the_breaker(harness):
    script = [RateLimited("429", retry_after_s=1.0, elapsed_s=0.1) for _ in range(3)] + [OK]
    client, _, _, _ = harness(script, threshold=2)
    client.call(make_request(), file_id="F1", page=1, stage="extract")
    assert client.breaker.state == BreakerState.CLOSED
