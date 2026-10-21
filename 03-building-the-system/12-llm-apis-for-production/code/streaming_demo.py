"""Streaming, measured: the analyst's discrepancy note, with and without streaming.

    python -X utf8 code/streaming_demo.py

Same fake provider, virtual time. The note is Day 11's draft_note: code has already decided the findings;
the model only writes them up for Lakshmi's screen. Streaming changes when she sees the first word, not
when the last one arrives, and not what it costs.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from godavari_llm.fake_provider import FakeConfig, FakeProvider   # noqa: E402
from godavari_llm.provider import ModelRequest, Tier, VirtualClock  # noqa: E402

DRAFT = ("GNT-26-00005: the product on page 9 was read with low confidence (0.71) and needs your check "
         "[review: product]. The applicant's PAN on page 9 matches the PAN card on page 12. Income evidence "
         "on pages 2, 13 and 14 agrees at Rs. 40,000 a month. Nothing is missing for the branch.")


def note_request(tier: Tier) -> ModelRequest:
    return ModelRequest(tier=tier, system="Write a short plain note to a credit-ops analyst. Cite rule ids.",
                        user_text="Findings: product low confidence on page 9.", page_ref=None, json_schema=None,
                        max_output_tokens=600, timeout_s=30.0, idempotency_key="idem_note_demo",
                        metadata={"task": "note", "draft": DRAFT})


def main() -> None:
    for tier, mode in ((Tier.LARGE, "non-streaming"), (Tier.LARGE, "streaming"), (Tier.SMALL, "streaming")):
        clock = VirtualClock()
        provider = FakeProvider([], clock, FakeConfig(seed=3, outages=[]))
        first: list[float] = []
        if mode == "streaming":
            resp = provider.complete_streaming(note_request(tier), lambda chunk, t: first.append(t) if not first else None)
            seen = first[0]
        else:
            resp = provider.complete(note_request(tier))
            seen = clock.now()                  # nothing to show until the whole answer is back
        print(f"{tier.value:5s} tier, {mode:14s} first words on screen at {seen:4.1f} s, complete at {clock.now():4.1f} s, "
              f"{resp.usage.output_tokens} output tokens (thinking included)")
    print("\nThe same note in the 02:00 batch: nobody is watching, so streaming buys nothing and adds a "
          "parser that must survive a stream cut half way.")


if __name__ == "__main__":
    main()
