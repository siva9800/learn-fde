"""Simulate one night of Godavari's 02:00 SFTP drop through the production client, and check the budgets.

    python -X utf8 code/run_nightly_batch.py            # 60 files, the full night
    python -X utf8 code/run_nightly_batch.py --files 20 # the twenty-file measurement before any demo

Offline: a fake provider, virtual time, seeded randomness. Same command, same output.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from godavari_llm.client import LLMClient, ResponseStore                                  # noqa: E402
from godavari_llm.contract import LoanFileExtraction, PageExtraction, provider_schema    # noqa: E402
from godavari_llm.extractor import FileReport, GodavariExtractor, VirtualScheduler       # noqa: E402
from godavari_llm.fake_provider import FakeConfig, FakeProvider                          # noqa: E402
from godavari_llm.ledger import BATCH_DISCOUNT, PRICE_CARD, RESIDENCY_UPLIFT, USD_TO_INR, CostLedger, cost_usd  # noqa: E402
from godavari_llm.provider import VirtualClock                                           # noqa: E402
from godavari_llm.retry import CircuitBreaker, RetryPolicy                               # noqa: E402
from godavari_llm.synthetic import SyntheticFile, make_night                             # noqa: E402

DATA = Path(__file__).resolve().parent.parent / "data"
COST_BUDGET_INR = 12.0        # per file, for model calls only: a ceiling, not an average (section 07)
FILE_P95_BUDGET_S = 120.0     # p95 processing time for a 36-to-40-page bundle
STAGE_P95_BUDGET_S = {"classify": 20.0, "extract": 90.0}
DEADLINE_S = 6 * 3600         # 02:00 to 08:00, when the analysts open the queue
CONCURRENCY = 16              # calls in flight across the whole batch


def clock_time(t: float) -> str:
    t = int(round(t)) + 2 * 3600
    return f"{t // 3600:02d}:{t % 3600 // 60:02d}:{t % 60:02d}"


def pct(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, max(0, round(q * (len(ordered) - 1))))]


def run_night(files: list[SyntheticFile], provider: FakeProvider, client: LLMClient, clock: VirtualClock,
              extractor: GodavariExtractor) -> tuple[list[FileReport], int, set[str]]:
    reports: dict[str, FileReport] = {}
    queue, passes, ever_deferred = list(files), 0, set()
    ready = 0.0
    while queue and passes < 6:
        passes += 1
        deferred = []
        for f in queue:
            rep = extractor.extract_with_report(f, ready_at=ready)
            reports[f.file_id] = rep
            if rep.status == "deferred":
                deferred.append(f)
                ever_deferred.add(f.file_id)
        queue = deferred
        # Re-queue no earlier than the breaker's next probe; completed calls will be store hits.
        reopen = (client.breaker.opened_at or 0.0) + client.breaker.cooldown_s
        ready = max(max(r.finished_at for r in reports.values()), reopen) + 1.0
    return [reports[f.file_id] for f in files], passes, ever_deferred


def evaluate(files: list[SyntheticFile], reports: list[FileReport], provider: FakeProvider,
             extractor: GodavariExtractor) -> dict[str, Counter]:
    """Score against the synthetic truth: the step a real engagement does with Day 14's golden set."""
    by_id = {f.file_id: f for f in files}
    fields = Counter()
    for rep in reports:
        if rep.extraction is None:
            continue
        truth = by_id[rep.file_id].truth
        for name in ("applicant_name", "applicant_pan", "co_applicant_name", "product", "requested_amount"):
            got = getattr(rep.extraction, name).value
            want = truth[name]
            if got is None:
                fields["withheld" if want is not None else "correct"] += 1
            elif str(got).casefold() == str(want).casefold():
                fields["correct"] += 1
            else:
                fields["wrong_accepted"] += 1
    variants: dict[str, Counter] = {}
    for key, variant in provider.injected.items():
        file_id, page_no = extractor.page_keys[key]
        rep = next(r for r in reports if r.file_id == file_id)
        field_name = {"amount_x10": "requested_amount", "picked_the_wrong_amount_line": "requested_amount",
                      "income_as_annual": "monthly_income", "swap_applicant_and_co_applicant": "applicant_name",
                      "pan_digit_misread": "applicant_pan"}[variant]
        truth = by_id[file_id].truth[field_name]
        ext = rep.extraction
        if field_name == "monthly_income":
            got = next((i.monthly_income for i in ext.income_evidence if i.page == page_no), None) if ext else None
        else:
            got = getattr(ext, field_name).value if ext else None
        outcome = ("missed (wrong value accepted)" if got is not None and str(got).casefold() != str(truth).casefold()
                   else "stopped (re-asked, withheld or flagged)")
        variants.setdefault(variant, Counter())[outcome] += 1
    return {"fields": fields, **variants}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", type=int, default=60)
    ap.add_argument("--json-mode", choices=["schema", "prompt"], default="schema")
    ap.add_argument("--full-ledger", action="store_true", help="also write every attempt to data/ledger.csv")
    args = ap.parse_args()

    files = make_night(args.files)
    clock = VirtualClock()
    provider = FakeProvider(files, clock, FakeConfig(json_mode=args.json_mode))
    ledger, store = CostLedger(), ResponseStore()
    breaker = CircuitBreaker(clock, failure_threshold=5, cooldown_s=60.0)
    client = LLMClient(provider, ledger, clock, policy=RetryPolicy(), breaker=breaker, store=store)
    extractor = GodavariExtractor(client, VirtualScheduler(clock, CONCURRENCY))

    reports, passes, deferred_ids = run_night(files, provider, client, clock, extractor)
    n_pages = sum(len(f.pages) for f in files)
    print(f"== Godavari nightly SFTP batch (simulated): {len(files)} files, {n_pages} pages, "
          f"provider '{provider.name}', json mode '{args.json_mode}' ==")
    s, l = PRICE_CARD.values()
    print(f"price card (USD per million tokens, 21 Oct 2026): small {s.input:.2f} in / {s.output:.2f} out, "
          f"large {l.input:.2f} / {l.output:.2f}; residency uplift {RESIDENCY_UPLIFT:.2f}; Rs {USD_TO_INR:.2f} per USD")

    outcomes = ledger.outcomes()
    logical = len({r.idempotency_key for r in ledger.rows})
    sent = sum(v for k, v in outcomes.items() if k not in ("store_hit", "circuit_open"))
    print(f"\ncalls: {logical} logical, {sent} attempts sent to the provider")
    print("  attempt outcomes: " + ", ".join(f"{k} {v}" for k, v in sorted(outcomes.items())))
    print("  breaker: " + ", ".join(f"{clock_time(t)} {st}" for t, st in breaker.transitions) +
          f"; files deferred and re-queued: {len(deferred_ids)}"
          f"; passes over the queue: {passes}")
    problems = Counter()
    for r in reports:
        problems.update(r.problems)
    print("  structured output: " + ", ".join(f"{k} {v}" for k, v in sorted(problems.items())))

    ev = evaluate(files, reports, provider, extractor)
    print("\nwrong-but-valid answers served by the fake model, and what happened to each:")
    for variant, c in sorted((k, v) for k, v in ev.items() if k != "fields"):
        print(f"  {variant:34s} " + ", ".join(f"{k}: {n}" for k, n in sorted(c.items())))
    f = ev["fields"]
    print(f"file-level fields vs synthetic truth: correct {f['correct']}, withheld for review {f['withheld']}, "
          f"wrong and accepted {f['wrong_accepted']}")
    done = [r for r in reports if r.extraction is not None]
    review = [r for r in done if r.extraction.needs_review]
    print(f"files: {len(done)} extracted, {len(review)} need review, {len(files) - len(done)} not finished")

    per_file = ledger.inr_by_file()
    costs = [per_file.get(fl.file_id, 0.0) for fl in files]
    big = [per_file.get(fl.file_id, 0.0) for fl in files if len(fl.pages) >= 36]
    worst = max(files, key=lambda fl: per_file.get(fl.file_id, 0.0))
    print(f"\ncost per file, model calls (Rs): p50 {pct(costs, .5):.2f}, p95 {pct(costs, .95):.2f}, "
          f"max {max(costs):.2f} ({worst.file_id}, {len(worst.pages)} pages); 36-40 page files max {max(big or [0]):.2f}")
    print(f"  budget Rs {COST_BUDGET_INR:.2f} per file: {'PASS' if max(costs) <= COST_BUDGET_INR else 'FAIL'}"
          f"; night total Rs {sum(costs):.2f}; per 1,400 files a month about Rs {sum(costs) / len(files) * 1400:,.0f}")
    by_stage = Counter()
    for r in ledger.rows:
        by_stage[r.stage] += r.inr
    print("  by stage (Rs): " + ", ".join(f"{k} {v:.2f}" for k, v in sorted(by_stage.items())))
    tokens = Counter()
    for r in ledger.rows:
        tokens["input"] += r.input_tokens
        tokens["cache_read"] += r.cache_read_tokens
        tokens["cache_write"] += r.cache_write_tokens
        tokens["output"] += r.output_tokens
    print("  tokens: " + ", ".join(f"{k} {v:,}" for k, v in tokens.items()))

    invoice_inr = sum(cost_usd(u, PRICE_CARD[t]) for t, u in provider.invoice) * USD_TO_INR
    est = ledger.total_inr(include_estimated=True) - ledger.total_inr()
    print(f"  ledger Rs {ledger.total_inr():.2f} vs provider invoice Rs {invoice_inr:.2f}: "
          f"Rs {invoice_inr - ledger.total_inr():.2f} billed for calls we timed out on "
          f"(ledger estimate for those: Rs {est:.2f})")

    finished = [r for r in reports if r.status == "done"]
    proc = [r.finished_at - r.started_at for r in finished]
    proc_big = [r.finished_at - r.started_at for r in finished if r.pages >= 36]
    cls = [r.classify_s for r in finished]
    ext = [r.extract_s for r in finished]
    print(f"\nlatency per file, processing only (s): classify p50 {pct(cls, .5):.1f} p95 {pct(cls, .95):.1f} "
          f"(budget {STAGE_P95_BUDGET_S['classify']:.0f}); extract p50 {pct(ext, .5):.1f} p95 {pct(ext, .95):.1f} "
          f"(budget {STAGE_P95_BUDGET_S['extract']:.0f})")
    ok = pct(proc_big, .95) <= FILE_P95_BUDGET_S
    print(f"  whole file p50 {pct(proc, .5):.1f}, p95 {pct(proc, .95):.1f}; 36-40 page files p95 "
          f"{pct(proc_big, .95):.1f} (n={len(proc_big)}, budget {FILE_P95_BUDGET_S:.0f}): {'PASS' if ok else 'FAIL'}")
    end = max(r.finished_at for r in reports)
    print(f"  batch: 02:00:00 to {clock_time(end)}, deadline 08:00:00, slack {(DEADLINE_S - end) / 3600:.1f} h")

    night_usd = sum(cost_usd(u, PRICE_CARD[t]) for t, u in provider.invoice)
    # Idempotency: the 02:00 job runs twice (it happens), then one page arrives re-scanned.
    calls_before, spend_before = provider.calls, ledger.total_inr()
    run_night(files, provider, client, clock, extractor)
    print(f"\nre-run of the same night: {provider.calls - calls_before} provider calls, "
          f"Rs {ledger.total_inr() - spend_before:.2f} new spend ({store.hits} store hits so far)")
    target = files[0]
    pan_page = next(p for p in target.pages if p.doc.value == "pan_card")
    rescanned = replace(pan_page, text=pan_page.text + "\n[re-scanned at branch]")
    provider.pages[rescanned.ref] = rescanned
    new_file = replace(target, pages=tuple(rescanned if p.number == pan_page.number else p for p in target.pages))
    rows_before, spend_before = len(ledger.rows), ledger.total_inr()
    extractor.extract_with_report(new_file, ready_at=clock.now())
    new = Counter(r.outcome for r in ledger.rows[rows_before:])
    print(f"re-scan of page {pan_page.number} of {target.file_id}: {new['ok']} new model calls, "
          f"{new['store_hit']} store hits, Rs {ledger.total_inr() - spend_before:.2f}")

    print(f"\nbatch-API what-if: the same tokens at a {BATCH_DISCOUNT:.0%} discount cost Rs "
          f"{night_usd * USD_TO_INR * BATCH_DISCOUNT:.2f} instead of Rs {night_usd * USD_TO_INR:.2f}; "
          "worth it only with a synchronous fallback for anything unfinished by 06:30")

    DATA.mkdir(exist_ok=True)
    if args.full_ledger:
        ledger.write_csv(DATA / "ledger.csv")
    with (DATA / "night-per-file.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["file_id", "pages", "inr_model_calls", "classify_s", "extract_s", "processing_s", "needs_review",
                    "review_reasons"])
        for rep in reports:
            w.writerow([rep.file_id, rep.pages, f"{per_file.get(rep.file_id, 0.0):.2f}", f"{rep.classify_s:.1f}",
                        f"{rep.extract_s:.1f}", f"{rep.finished_at - rep.started_at:.1f}",
                        rep.extraction.needs_review if rep.extraction else "",
                        " | ".join(rep.extraction.review_reasons) if rep.extraction else "not finished"])
    (DATA / "page-extraction.provider-schema.json").write_text(
        json.dumps(provider_schema(PageExtraction), indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    (DATA / "loan-file-extraction.schema.json").write_text(
        json.dumps(LoanFileExtraction.model_json_schema(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8",
        newline="\n")
    sample = next((r for r in reports if r.extraction is not None and r.extraction.needs_review),
                  next(r for r in reports if r.extraction is not None))
    (DATA / "sample-extraction.json").write_text(sample.extraction.model_dump_json(indent=2) + "\n", encoding="utf-8",
                                                newline="\n")
    print(f"\nwrote data/night-per-file.csv, data/page-extraction.provider-schema.json, "
          f"data/loan-file-extraction.schema.json, data/sample-extraction.json ({sample.file_id})")


if __name__ == "__main__":
    main()
