"""Day 11 project: the deterministic-versus-LLM split, end to end, over Day 7's synthetic sample.

Run from the chapter folder (no network, no API key):

    python -X utf8 code/run_batch.py                      # prototype mode, stub model
    python -X utf8 code/run_batch.py --mode pilot         # refuses: the rules are not signed yet
    python -X utf8 code/run_batch.py --model anthropic    # optional real model, synthetic text only

Writes data/godavari_intake_run.csv (one row per file) and data/godavari_intake_summary.md.
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path

from intake import rules_gold, rules_two_wheeler
from intake.core_write import Approval, FakeCoreSandbox, PushLog, push_to_core
from intake.day7_inputs import DAY7_GENERATOR, day7_sample
from intake.model import ExtractionModel, StubModel
from intake.pipeline import FileResult, process, score
from intake.reference import BRANCH_AD_GROUP
from intake.routing import THRESHOLDS_VERSION, Route, visible_to
from intake.ruleset import Action, OverrideLog, RuleSet, SignoffError, check_signoff
from intake.synth import build_batch

CHAPTER = Path(__file__).resolve().parent.parent
DATA = CHAPTER / "data"
AS_OF = date(2026, 11, 9)          # Monday of engagement week 3, when the prototype first runs end to end
RULESETS: dict[str, RuleSet] = {"two-wheeler": rules_two_wheeler.RULESET, "gold": rules_gold.RULESET}
TEAMS = {   # analysts' AD groups: each team sees only its region's branches (synthetic)
    "Hyderabad team": [BRANCH_AD_GROUP[b] for b in ("Kukatpally", "Dilsukhnagar", "Warangal")],
    "Vijayawada team": [BRANCH_AD_GROUP[b] for b in ("Vijayawada-Benz Circle", "Guntur", "Rajahmundry")],
}


def defect_class(d: str) -> str:
    return "required document missing" if d.startswith("MISSING:") else d


def build_model(name: str) -> ExtractionModel:
    if name == "stub":
        return StubModel()
    from intake.llm_adapter import AnthropicExtractionModel   # imported only when asked for
    return AnthropicExtractionModel(i_confirm_synthetic_data=True)   # Day 7 synthetic files only


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--mode", choices=["prototype", "pilot"], default="prototype")
    parser.add_argument("--model", choices=["stub", "anthropic"], default="stub")
    parser.add_argument("--limit", type=int, default=0, help="process only the first N files (0 = all)")
    args = parser.parse_args(argv)
    out: list[str] = []

    def say(line: str = "") -> None:
        print(line)
        out.append(line)

    say("== Day 11 · the system around the model: Godavari loan-file intake ==")
    say(f"mode: {args.mode} · model: {args.model} · as of {AS_OF.isoformat()} · thresholds {THRESHOLDS_VERSION}")
    try:
        statuses = [check_signoff(rs, args.mode) for rs in RULESETS.values()]
    except SignoffError as err:
        say(f"REFUSED: {err}")
        return 2
    for st in statuses:
        say(f"  {st.banner}")

    rows = day7_sample()
    batch = build_batch(rows)
    if args.limit:
        batch = batch[: args.limit]
    say(f"input: Day 7's sample via {DAY7_GENERATOR.name} (seed 7): {len(rows)} files, "
        f"{len(batch)} in scope ({sum(b.product == 'two-wheeler' for b, _ in batch)} two-wheeler, "
        f"{sum(b.product == 'gold' for b, _ in batch)} gold)")
    model = build_model(args.model)
    results: list[FileResult] = []
    for bundle, truth in batch:
        results.append(score(process(bundle, model, RULESETS[bundle.product], AS_OF), truth))

    # 1. Where the files went.
    say()
    say("-- 1. Routes (every route ends with a named analyst; none is automatic) --")
    say(f"{'route':22s}{'two-wheeler':>13s}{'gold':>7s}{'total':>7s}")
    for route in Route:
        tw = sum(r.route == route and r.product == "two-wheeler" for r in results)
        gl = sum(r.route == route and r.product == "gold" for r in results)
        say(f"{route.value:22s}{tw:13d}{gl:7d}{tw + gl:7d}")

    # 2. What the rules caught that the model alone would have shipped.
    n_files: Counter[str] = Counter()
    shipped: Counter[str] = Counter()
    caught: Counter[str] = Counter()
    missed: Counter[str] = Counter()
    caught_by: dict[str, Counter[str]] = defaultdict(Counter)
    for r in results:
        for d in r.defects:
            k = defect_class(d)
            n_files[k] += 1
            shipped[k] += d in r.model_alone_shipped
            if d in r.caught:
                caught[k] += 1
                caught_by[k].update(r.caught_by[d])
            else:
                missed[k] += 1
    say()
    say("-- 2. Problems in the files, and who catches them --")
    say("   'model alone' = the same model asked, in its prompt, to extract AND judge completeness,")
    say("   with no code after it. 'system' = model + envelope + signed rules. One row per kind of problem;")
    say("   a file with two missing documents is two cases.")
    say(f"{'problem':34s}{'cases':>6s}{'model alone shipped':>21s}{'system caught':>15s}{'missed':>8s}  caught by")
    for k in sorted(n_files, key=lambda x: (x.startswith("FIELD"), -n_files[x], x)):
        by = ", ".join(f"{rid}" for rid, _ in caught_by[k].most_common(3))
        say(f"{k:34s}{n_files[k]:6d}{shipped[k]:21d}{caught[k]:15d}{missed[k]:8d}  {by}")
    total = sum(n_files.values())
    say(f"{'total':34s}{total:6d}{sum(shipped.values()):21d}{sum(caught.values()):15d}{sum(missed.values()):8d}")

    alone_clean = [r for r in results if r.prompt_only_complete]
    alone_wrong = [r for r in alone_clean if r.defects]
    say()
    say(f"The model alone called {len(alone_clean)} files complete and clean; {len(alone_wrong)} of them were not.")
    for r in alone_wrong[:6]:
        fired = sorted({f.rule_id for f in r.findings if f.action != Action.REVIEW or f.field_name})
        say(f"  {r.file_id} {r.product:11s} -> {r.route.value:18s} real problems: {', '.join(sorted(r.defects))}"
            f"  | fired: {', '.join(fired[:4])}")

    # 3. The envelope at work.
    count = Counter(f.rule_id for r in results for f in r.findings)
    review_only_conf = sum(1 for r in results if r.route == Route.REVIEW and
                           {f.rule_id for f in r.findings} <= {"ENV-CONFIDENCE", "ENV-UNSURE"})
    uncertain_reviews = sum(1 for r in results if any(
        f.rule_id.split("-")[1] == "DOC" and f.action == Action.REVIEW for f in r.findings))
    say()
    say("-- 3. The envelope around the model --")
    say(f"  document claims rejected (quote not on the cited page):   {count['ENV-GROUND']}")
    say(f"  salary-account picks overturned by the credit check:      {count['ENV-SALARY-ACCT']}")
    say(f"  values not supported by their own quote:                  {count['ENV-EVIDENCE']}")
    say(f"  PAN card and form disagree / PAN format fails:            {count['ENV-PAN-MATCH']} / {count['ENV-PAN-FORMAT']}")
    say(f"  name on form differs from PAN card:                       {count['ENV-NAME-MATCH']}")
    say(f"  files with a document missing but unclassified pages:    {uncertain_reviews} (review first, not send-back)")
    say(f"  fields under threshold / model said unsure:               {count['ENV-CONFIDENCE']} / {count['ENV-UNSURE']}")
    say(f"  files in review for confidence alone:                     {review_only_conf}")
    say(f"  analyst notes missing a rule citation, fixed by code:     {sum(r.note_corrected for r in results)}")
    false_alarms = [fa for r in results for fa in r.false_alarms]
    say(f"  send-backs or blocks with no real problem behind them:    {len(false_alarms)}")

    # 4. What still gets through.
    say()
    say("-- 4. What the system missed (it reaches the analyst unflagged) --")
    misses = [(r, d) for r in results for d in sorted(r.missed)]
    for r, d in misses:
        say(f"  {r.file_id} {r.product:11s} {d:30s} route {r.route.value}")
    if not misses:
        say("  none in this batch")
    say("  Every file still waits for an analyst. Day 14 measures this rate on 150 files the analysts labelled.")

    # 5. The write to the core system: approved files only, safe to repeat.
    sandbox, log = FakeCoreSandbox(), PushLog()
    ready = [r for r in results if r.route == Route.READY_FOR_APPROVAL][:3]
    approval = Approval(analyst_id="GF-AN-1142", approved_on=AS_OF)
    for r in ready:
        assert r.output is not None
        fields = {k: v.value or "" for k, v in r.output.fields.items() if k in ("applicant_name", "pan", "requested_amount")}
        push_to_core(r.file_id, r.branch, r.route, fields, approval, sandbox, log)
        push_to_core(r.file_id, r.branch, r.route, fields, approval, sandbox, log)    # a retry
    refused = 0
    for r in [x for x in results if x.route in (Route.SEND_BACK, Route.BLOCKED)][:2]:
        try:
            push_to_core(r.file_id, r.branch, r.route, {}, approval, sandbox, log)
        except PermissionError:
            refused += 1
    say()
    say("-- 5. Core-system sandbox write (deterministic integration) --")
    say(f"  {len(ready)} approved files pushed twice each: {sum(e['action'] == 'created' for e in log.entries)} "
        f"created, {sum(e['action'] == 'exists' for e in log.entries)} retries found the existing record, "
        f"{len(sandbox.records) - len({x['file_number'] for x in sandbox.records})} duplicates")
    say(f"  {refused} pushes of send-back or blocked files refused before any call")

    # 6. Overrides and visibility.
    olog = OverrideLog()
    policy = next((f for r in results for f in r.findings if f.rule_id == "TW-AMT-MARGIN"), None)
    regulatory = next((f for r in results for f in r.findings if f.kind == "regulatory"), None)
    say()
    say("-- 6. Overrides and who sees what --")
    if policy:
        olog.override(policy, "GF-AN-1142", "customer brought the margin money in cash, receipt on file", datetime(2026, 11, 9, 11, 30))
        say(f"  policy override logged: {policy.rule_id} by GF-AN-1142 ({len(olog.entries)} entry)")
    if regulatory:
        try:
            olog.override(regulatory, "GF-AN-1142", "branch manager says it is fine", datetime(2026, 11, 9, 11, 31))
        except PermissionError as err:
            say(f"  regulatory override refused: {err}")
    for team, groups in TEAMS.items():
        queue = [r for r in results if r.route != Route.READY_FOR_APPROVAL and visible_to(groups, r.branch)]
        say(f"  {team}: {len(queue)} files in its queues, all from {', '.join(sorted({r.branch for r in queue}))}")

    write_outputs(results, out)
    say()
    say(f"wrote {(DATA / 'godavari_intake_run.csv').relative_to(CHAPTER).as_posix()} and "
        f"{(DATA / 'godavari_intake_summary.md').relative_to(CHAPTER).as_posix()}")
    return 0


def write_outputs(results: list[FileResult], lines: list[str]) -> None:
    DATA.mkdir(exist_ok=True)
    with (DATA / "godavari_intake_run.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["file_id", "product", "branch", "channel", "route", "rules_fired", "real_problems",
                    "system_caught", "system_missed", "model_alone_shipped", "model_alone_said_complete"])
        for r in results:
            w.writerow([r.file_id, r.product, r.branch, r.channel, r.route.value,
                        " ".join(sorted({f.rule_id for f in r.findings})), " ".join(sorted(r.defects)),
                        " ".join(sorted(r.caught)), " ".join(sorted(r.missed)),
                        " ".join(sorted(r.model_alone_shipped)), r.prompt_only_complete])
    body = "\n".join(lines)
    (DATA / "godavari_intake_summary.md").write_text(
        "# Godavari intake prototype · run summary\n\n> Generated by `code/run_batch.py`. Synthetic data. "
        "Do not edit by hand.\n\n```text\n" + body + "\n```\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    sys.exit(main())
