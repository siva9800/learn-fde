"""Day 18, step 1: fit the bands on Day 14's development split, confirm them on its test split, and price them.

Run from the chapter folder (no network, no API key):

    python -X utf8 code/tune_thresholds.py

Refuses to run if the placeholder thresholds no longer reproduce Day 14's measured baseline (7 confidently wrong
fields on the test split), because then this chapter and Day 14 would be describing different systems.
Writes data/bands.json (read by run_pilot_week.py) and data/band-report.md (this output).
"""

from __future__ import annotations

import sys
import time

from godavari_review import bands as B
from godavari_review.evidence import golden_rows
from godavari_review.paths import DATA
from godavari_review.render import write

DAY14_CONFIDENT_WRONG = 7          # Day 14, section 04.3: the baseline's confidently wrong fields on the test split


def main() -> int:
    t0 = time.perf_counter()
    lines: list[str] = []

    def say(line: str = "") -> None:
        print(line)
        lines.append(line)

    policy = B.load_policy()
    rows = golden_rows()
    dev = [r for r in rows if r.split == "dev"]
    test = [r for r in rows if r.split == "test"]
    say(f"== Day 18 · bands from the golden set ({policy['version']}) ==")
    say(f"field rows: {len(dev)} development (50 files), {len(test)} test (150 files)")
    placeholder = B.cost(test, B.placeholder_band, policy)
    say(f"check: Day 11's placeholder thresholds on test leave {placeholder['auto_wrong']} confidently wrong fields "
        f"(Day 14 measured {DAY14_CONFIDENT_WRONG})")
    if placeholder["auto_wrong"] != DAY14_CONFIDENT_WRONG:
        say("REFUSED: this is not the system Day 14 measured")
        return 2

    fitted = B.fit(dev, policy)
    say()
    say("-- 1. fitted on development (no test file seen) --")
    say(f"  {'field':18} {'stratum':18} {'accept at':>9} {'reject <':>8}  dev  why")
    for cb in fitted.values():
        acc = f"{cb.accept_at:.2f}" if cb.accept_at is not None else "none"
        say(f"  {cb.field:18} {cb.stratum:18} {acc:>9} {cb.reject_below:>8.2f} {cb.dev_n:4}  {cb.reason}")

    summary = B.confirm(test, fitted, policy)
    say()
    say("-- 2. confirmed on test --")
    say(f"  before any withdrawal: {summary['auto_before']} test fields auto-accepted, {summary['auto_errors_before']} wrong; "
        f"pooled upper bound {summary['upper_before']:.2%} against a limit of {summary['pooled_limit']:.1%}")
    for cb in fitted.values():
        if cb.status in ("withdrawn", "blocked_until_proven"):
            say(f"  {cb.status.upper():20} {cb.field} | {cb.stratum}: {cb.reason}")
            for ex in cb.test["examples"]:
                say(f"      {ex}")
    say(f"  after: {summary['auto_after']} auto-accepted, {summary['auto_errors_after']} wrong; upper bound "
        f"{summary['upper_after']:.2%} (optimistic: the withdrawals used the test split; production spot checks give the honest number)")
    say(f"  a handwritten Telugu cell needs {B.fields_to_prove(policy['proof_before_auto']['max_upper_bound'])} "
        f"auto-accepted test fields, none wrong, before it is proved")

    say()
    say("-- 3. what each policy costs on the 150 test files --")
    say(f"  {'policy':28} {'auto':>5} {'review':>6} {'key in':>6} {'wrong, nobody told':>19} {'wrong, in front of her':>23} "
        f"{'min/file':>8} {'hours/month':>11}")
    costs = {"every field reviewed": B.cost(test, B.everything_reviewed, policy),
             "Day 11 placeholder": placeholder,
             "bands (this chapter)": B.cost(test, lambda r: B.band_for(r, fitted), policy)}
    for name, c in costs.items():
        b = c["bands"]
        say(f"  {name:28} {int(b['auto_accept']['fields']):5} {int(b['review']['fields']):6} {int(b['reject']['fields']):6} "
            f"{int(c['auto_wrong']):19} {int(c['review_wrong']):23} {c['minutes_per_file']:8.2f} {c['hours_per_month']:11.1f}")
    extra = costs["bands (this chapter)"]["hours_per_month"] - placeholder["hours_per_month"]
    say(f"  the bands cost {extra:.1f} analyst hours a month more than the placeholder (Rs {extra * 456:,.0f} at Day 9's "
        f"Rs 456 an hour) and leave no confidently wrong field on the test split; the placeholder left "
        f"{placeholder['auto_wrong']} in 150 files, about {placeholder['auto_wrong'] / 150 * policy['files_per_month']:.0f} a month at "
        f"{policy['files_per_month']:,} files")
    say(f"  seconds per field are assumptions until the pilot timer: {policy['seconds']['basis']}")

    say()
    say("-- 4. per band, bands policy, by stratum --")
    for stratum in ("printed", "handwritten_telugu"):
        sub = [r for r in test if r.stratum == stratum]
        c = B.cost(sub, lambda r: B.band_for(r, fitted), policy)
        b = c["bands"]
        say(f"  {stratum:18} auto {int(b['auto_accept']['fields']):4} ({int(b['auto_accept']['wrong'])} wrong) · review "
            f"{int(b['review']['fields']):4} ({int(b['review']['wrong'])} wrong, {b['review']['wrong'] / max(1, b['review']['fields']):.1%}) · "
            f"key in {int(b['reject']['fields']):3}")
    summary["expected_wrong_share_in_review"] = costs["bands (this chapter)"]["review_wrong"] / max(
        1, costs["bands (this chapter)"]["bands"]["review"]["fields"])
    B.save(fitted, summary, policy, DATA / "bands.json")
    say()
    say(f"wrote data/bands.json and data/band-report.md in {time.perf_counter() - t0:.2f} s")
    write(DATA / "band-report.md", "# Bands from the golden set\n\n> Generated by `code/tune_thresholds.py`. "
          "Synthetic data. Do not edit by hand.\n\n```text\n" + "\n".join(lines) + "\n```")
    return 0


if __name__ == "__main__":
    sys.exit(main())
