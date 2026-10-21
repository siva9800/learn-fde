"""Day 19 project: the observability layer for Godavari's pilot, end to end, offline.

Run from the chapter folder (no network, no API key):

    python -X utf8 code/run_observability.py

  1. traces both pilot weeks: Day 11's pipeline, Day 12's 02:00 job, Day 18's simulated analysts, Day 11's core write
     behind Day 16's window, Day 15's policy panel; every span through the redacting boundary into data/traces.sqlite
  2. checks the traces: one per SFTP arrival, every stage present, trace rupees equal ledger rupees, week one's screen
     log identical to Day 18's
  3. rolls up cost per file, branch, night, stage and prompt release; raises the ceiling and spike alerts
  4. runs the weekly quality job against the golden-set baseline
  5. reads Day 16's journal and Day 17's audit log for counts, and scans every upstream record for identifiers
  6. writes the three dashboards (data/dashboards/), the alerts, a sample trace and this report
"""

from __future__ import annotations

import json
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, time as clock_time
from pathlib import Path
from statistics import mean, median

sys.path.insert(0, str(Path(__file__).resolve().parent))

from godavari_obs import alerts as A                       # noqa: E402
from godavari_obs import costs as K                        # noqa: E402
from godavari_obs import dashboards as D                   # noqa: E402
from godavari_obs import paths                             # noqa: E402
from godavari_obs import pilot, quality as Q, sources      # noqa: E402
from godavari_obs.redact import pii_hits                   # noqa: E402
from godavari_obs.spans import Tracer                      # noqa: E402
from godavari_obs.statements import continuation_pages     # noqa: E402
from godavari_obs.store import TraceStore                  # noqa: E402
from godavari_review import bands as B                     # noqa: E402
from godavari_review import stamping                       # noqa: E402
from intake.core_write import FakeCoreSandbox, PushLog     # noqa: E402
from run_nightly_batch import pct                          # noqa: E402

OUT = paths.DATA
QUEUE_READY_BY = clock_time(7, 30)      # the queue opens at 08:00; half an hour to re-run a failed night


def main(out: Path = OUT, quiet: bool = False) -> dict:
    """Runs everything and writes into `out`. Returns what the dashboards were built from (the tests use it)."""
    t0 = time.perf_counter()
    lines: list[str] = []

    def say(line: str = "") -> None:
        if not quiet:
            print(line)
        lines.append(line)

    say("== Day 19 · observability for Godavari's pilot: Kukatpally and Guntur, 7 to 18 December 2026 ==")
    policy = B.load_policy()
    bands = B.load(paths.DAY18_DATA / "bands.json")
    tracer = Tracer("pilot")
    sandbox, pushlog = FakeCoreSandbox(), PushLog()
    weeks = [pilot.run_week(n, tracer, bands, policy, sandbox, pushlog) for n in (1, 2)]
    retrieval = {w.number: pilot.run_retrieval(tracer, w.days, f"pilot-week-{w.number}") for w in weeks}
    release = pilot.pinned_release()

    store = TraceStore(out / "traces.sqlite")
    report = store.write(tracer.spans, "pilot")
    n_spans, n_traces = store.count()
    say(f"spans written: {n_spans} in {n_traces} traces; prompt release pinned for pilot: {release.release_id}")
    say(f"boundary: {sum(report.dropped.values())} attribute values dropped, {sum(report.quarantined.values())} spans "
        f"quarantined")

    # -- 1. the traces are complete and agree with the ledger ------------------------------------------------------
    say()
    say("-- 1. checks on the traces --")
    arrivals = sum(len(w.files) for w in weeks)
    roots = store.by_name("loan_file")
    say(f"  SFTP arrivals {arrivals}; file traces {len(roots)}; distinct file numbers {len({r['attrs']['kaagaz.file.id'] for r in roots})}")
    need = ("classify", "extract", "pipeline.read", "rules", "route", "review")
    names_by_trace: dict[str, set[str]] = defaultdict(set)
    for r in store.rows():
        names_by_trace[r["trace_id"]].add(r["name"])
    incomplete = [r["attrs"]["kaagaz.file.id"] for r in roots if not set(need) <= names_by_trace[r["trace_id"]]]
    written = sum(1 for r in roots if r["attrs"]["kaagaz.file.outcome"] == "written to core")
    say(f"  traces missing a stage: {len(incomplete)}; core.write spans {len(store.by_name('core.write'))} for "
        f"{written} files written; core records created {len(sandbox.records)}")
    ledger_inr = sum(n.ledger.total_inr() for w in weeks for n in w.nights)
    trace_inr = sum(r["attrs"]["kaagaz.cost.inr"] for r in roots)
    say(f"  rupees: ledger Rs {ledger_inr:.4f}, traces Rs {trace_inr:.4f}, difference Rs {abs(ledger_inr - trace_inr):.6f}")
    models = {r["attrs"]["gen_ai.request.model"] for r in store.rows("kind = 'model_call'")}
    say(f"  models in the calls {sorted(models)}; the release pins {sorted(release.models.values())}: "
        f"{'match' if models <= set(release.models.values()) else 'MISMATCH'}")
    mine = [json.dumps(stamping.visible(e), sort_keys=True, ensure_ascii=False) for e in weeks[0].week.log]
    theirs = (paths.DAY18_DATA / "pilot-week-1" / "action-log.jsonl").read_text(encoding="utf-8").splitlines()
    say(f"  week one's screen log against Day 18's data/pilot-week-1/action-log.jsonl: "
        f"{'identical' if mine == theirs else 'DIFFERENT'} ({len(mine)} events)")

    # -- 2. cost ---------------------------------------------------------------------------------------------------
    say()
    say("-- 2. cost per file (model calls, Rs), from the traces --")
    fc = K.file_costs(store)
    for run in ("pilot-week-1", "pilot-week-2"):
        s = K.stats([c.inr for c in fc if c.run == run])
        f = K.forecast(fc, run)
        say(f"  {run}: {s['n']} files, median {s['p50']:.2f}, p95 {s['p95']:.2f}, max {s['max']:.2f}, total {s['total']:.2f}; "
            f"at 1,400 files a month about Rs {f['monthly']:,.0f} (Day 12 measured about Rs {f['day12_monthly']:,})")
    say("  by night and branch: files, median Rs, max Rs, median pages in the file / sent to the model")
    pl = K.pages_line(fc)
    for (night, branch), s in K.rollup(fc, "night_branch").items():
        p = pl[(night, branch)]
        say(f"    {night:%a %d %b} {branch:10} {int(s['n']):3} {s['p50']:6.2f} {s['max']:6.2f}   "
            f"{p['pages']:5.1f} / {p['to_model']:5.1f}")
    for run in ("pilot-week-1", "pilot-week-2"):
        say(f"  by stage, {run}: " + ", ".join(f"{k} {v:.2f}" for k, v in K.by_stage(store, run).items()))
    say(f"  by prompt release: " + ", ".join(f"{k}: {int(v['n'])} files, median {v['p50']:.2f}" for k, v in
                                             K.rollup(fc, "release").items()))
    say(f"  by product: " + ", ".join(f"{p}: {n} files" for p, n in
                                      Counter(r["attrs"]["kaagaz.file.product"] for r in roots).items()))
    cost_alerts = K.cost_alerts(fc)
    say(f"  alerts: {len(cost_alerts)}")
    for a in cost_alerts:
        say(f"    {a.night:%a %d %b} {a.rule:8} {a.text}")

    # -- 3. the incident, read from one trace ----------------------------------------------------------------------
    say()
    say("-- 3. Tuesday's most expensive file, from its trace --")
    worst = max((c for c in fc if c.run == "pilot-week-2"), key=lambda c: c.inr)
    fr = next(f for w in weeks for f in w.files if f.file_id == worst.file_id)
    spans = store.trace(worst.trace_id)
    calls = [s for s in spans if s["kind"] == "model_call"]
    cont = set(continuation_pages(fr.bundle))
    by_stage = Counter(s["attrs"]["kaagaz.llm.stage"] for s in calls)
    on_cont = Counter(s["attrs"]["kaagaz.llm.stage"] for s in calls if s["attrs"]["kaagaz.llm.page"] in cont)
    cost_cont = sum(s["attrs"]["kaagaz.cost.inr"] for s in calls if s["attrs"]["kaagaz.llm.page"] in cont)
    say(f"  {worst.file_id} ({worst.branch}, {worst.night:%a %d %b}): {worst.pages} pages, {len(cont)} of them statement "
        f"continuation pages; {len(calls)} model calls costing Rs {worst.inr:.2f}")
    say(f"  calls by stage: {dict(sorted(by_stage.items()))}; on continuation pages: {dict(sorted(on_cont.items()))}, "
        f"Rs {cost_cont:.2f} of the total")
    trace_file = out / f"sample-trace-{worst.file_id}.jsonl"
    store.export_jsonl(trace_file, [worst.trace_id])
    after = [c for c in fc if c.run == "pilot-week-2" and c.branch == "Guntur" and c.page_filter != "off"]
    before = [c for c in fc if c.run == "pilot-week-2" and c.branch == "Guntur" and c.page_filter == "off" and c.pages > 60]
    say(f"  Guntur files with a long statement: before the filter {len(before)} (median Rs {median([c.inr for c in before]):.2f}, "
        f"median {median([c.pages_to_model for c in before]):.0f} pages to the model); after it {len(after)} "
        f"(median Rs {median([c.inr for c in after]):.2f}, median {median([c.pages_to_model for c in after]):.0f} pages to the model)")

    g = Q.filter_on_golden_set()
    say(f"  the filter over Day 14's golden set: {g['files']} files, {g['pages_held_back']} pages held back; the "
        f"regression gate passes it without judging it")

    # -- 4. latency ------------------------------------------------------------------------------------------------
    say()
    say("-- 4. latency by stage (p50 / p95) --")
    latency: dict[str, dict[str, float]] = {}
    for run in ("pilot-week-1", "pilot-week-2"):
        ids = {r["trace_id"] for r in roots if r["attrs"]["kaagaz.run"] == run}
        st = defaultdict(list)
        for r in store.rows():
            if r["trace_id"] not in ids:
                continue
            if r["name"] in ("classify", "extract", "review"):
                st[r["name"]].append((r["end"] - r["start"]).total_seconds())
            if r["name"] == "review":
                st["queue wait h"].append(r["attrs"]["kaagaz.review.queue_wait_h"])
            if r["name"] == "core.write":
                st["write hold min"].append((r["end"] - r["start"]).total_seconds() / 60)
        ready = []
        for r in roots:
            if r["trace_id"] in ids:
                ext = next(s for s in store.trace(r["trace_id"]) if s["name"] == "extract")
                ready.append(ext["end"].hour < 9)
        latency[run] = {"classify p50": pct(st["classify"], .5), "classify p95": pct(st["classify"], .95),
                        "extract p50": pct(st["extract"], .5), "extract p95": pct(st["extract"], .95),
                        "queue p50 h": pct(st["queue wait h"], .5), "queue mean h": mean(st["queue wait h"]),
                        "review p50 min": pct(st["review"], .5) / 60, "held writes": sum(m > 0 for m in st["write hold min"]),
                        "writes": len(st["write hold min"]), "ready by 09:00": sum(ready) / len(ready)}
        L = latency[run]
        say(f"  {run}: classify stage {L['classify p50']:.1f} / {L['classify p95']:.1f} s (budget p95 20); extract stage "
            f"{L['extract p50']:.1f} / {L['extract p95']:.1f} s (budget p95 90); ready by 09:00 {L['ready by 09:00']:.0%}; "
            f"queue wait {L['queue p50 h']:.1f} h median, {L['queue mean h']:.1f} h mean; review {L['review p50 min']:.0f} min median; "
            f"writes held for the evening window {L['held writes']} of {L['writes']}")

    # -- 5. quality ------------------------------------------------------------------------------------------------
    say()
    say("-- 5. the weekly quality job (week two; baselines: Day 14's golden set and week one) --")
    fsig = {run: Q.field_signals(store, run) for run in ("pilot-week-1", "pilot-week-2")}
    say("  correction rate per field (content changes per file reviewed) against the golden set's error rate:")
    for s in fsig["pilot-week-2"]:
        say(f"    {s.field:17} {s.changed:3} of {s.files}  {s.rate:6.1%} ({s.lo:.1%} to {s.hi:.1%})   golden "
            f"{s.golden_rate:5.1%} ({s.golden_lo:.1%} to {s.golden_hi:.1%})   {s.status}")
    bsig = {run: Q.branch_signals(store, run) for run in ("pilot-week-1", "pilot-week-2")}
    for run in ("pilot-week-1", "pilot-week-2"):
        for br, v in bsig[run].items():
            f = v["files"]
            say(f"  {run} {br:10}: files {int(f)}, review {v.get('route review', 0) / f:.0%}, send back "
                f"{v.get('route send_back', 0) / f:.0%}, ENV-GROUND on {v.get('envelope ENV-GROUND', 0) / f:.0%}, "
                f"content corrections {v.get('content corrections', 0) / f:.2f} per file, unsure {v.get('unsure fields', 0) / f:.2f} "
                f"and unclassified pages {v.get('unclassified pages', 0) / f:.2f} per file")
    moves = [m for m in Q.rule_moves(store) if m.moved]
    say("  rules and envelope checks that moved, week one to week two (share of files):")
    for m in moves:
        say(f"    {m.rule:16} {m.branch:10} {m.before}/{m.before_n} -> {m.after}/{m.after_n}")
    ov = {w.number: Q.overrides(w.week) for w in weeks}
    sess = {w.number: Q.suspected_sessions(w.week) for w in weeks}
    spot = {w.number: Q.spot_checks(w.week, f"second-read-week-{w.number}") for w in weeks}
    say(f"  review-band overrides, week two (expected wrong share {Q.expected_review_share():.1%}): " +
        "; ".join(f"{o['analyst']} {o['corrections']}/{o['review_fields']} (p={o['p_this_few']:.2f}{', LOW' if o['low'] else ''})"
                  for o in ov[2]))
    say(f"  rubber-stamp sessions flagged: week one {len([s for s in sess[1] if s.verdict.startswith('suspected')])}, "
        f"week two {len([s for s in sess[2] if s.verdict.startswith('suspected')])}; fast-only sessions "
        f"{len([s for s in sess[1] if s.verdict.startswith('fast')])} and {len([s for s in sess[2] if s.verdict.startswith('fast')])}")
    for n in (1, 2):
        s = spot[n]
        say(f"  spot checks, week {n}: {s['files']} files drawn at random, {s['fields']} auto-accepted fields read again, "
            f"{s['wrong']} wrong; upper bound {s['upper']:.1%}")
    rsig = Q.retrieval_signals(store)
    say(f"  policy panel: {rsig['asked']} searches over both weeks, {rsig['empty']} with no result, {rsig['refused']} refused "
        f"(group snapshot older than 36 hours)")
    cands = Q.golden_candidates(store, "pilot-week-2")
    say("  to Day 14's development split:")
    for c in cands:
        say(f"    - {c}")

    # -- 6. the other records, and identifiers ---------------------------------------------------------------------
    say()
    say("-- 6. upstream records: counts in, identifiers out --")
    d16 = sources.day16_summary()
    say(f"  Day 16 journal: {d16['writes']} writes {d16['states']}; reconciliation history {d16['nights']} night(s), "
        f"clean run {d16['clean_run']} (last {d16['last_night']}); identifiers found: {d16['pii_kinds'] or 'none'}")
    d17 = sources.day17_summary()
    if d17 is None:
        say("  Day 17 audit log: not on disk; see Day 17 for approvals and step budgets")
    else:
        say(f"  Day 17 audit log: {d17['events']} events on {d17['files']} files; approvals asked {d17['approvals_requested']}, "
            f"decided {d17['approvals_decided']}, escalated {d17['approvals_escalated']}, refused {d17['approvals_refused']}; "
            f"wait median {d17['wait_median_min']} min, max {d17['wait_max_min']} min; drafting runs {d17['planner_runs']}, "
            f"most tool calls {d17['max_tool_calls']} of a step budget of {d17['step_budget']}; identifiers found: "
            f"{d17['pii_kinds'] or 'none'}")
    d18 = sources.day18_events_at_the_boundary()
    say(f"  Day 18's correction events as written: {d18['events']}, {d18['with_values']} carrying a value; identifier kinds "
        f"in the file: {d18['pii_kinds']}; through the boundary as raw attributes: {d18['stored']} stored, "
        f"{d18['quarantined']} quarantined; dropped {sum(d18['dropped'].values())} values, e.g. "
        f"{', '.join(list(d18['dropped'])[:3])}")
    scan = sources.upstream_scan()
    for label, kinds in scan.items():
        say(f"    {label}: {', '.join(kinds) or 'none'}")
    say(f"  the trace store itself: {', '.join(pii_hits(store.dump_text())) or 'none'}")

    # -- 7. alerts and the dashboards ------------------------------------------------------------------------------
    all_alerts: list[A.Alert] = [A.Alert(a.rule, a.night, a.scope, a.text, a.traces) for a in cost_alerts]
    for s in fsig["pilot-week-2"]:
        if s.status != "in line":
            all_alerts.append(A.Alert("field drift", pilot.WEEK2[-1], s.field,
                                      f"{s.field}: correction rate {s.rate:.1%} is {s.status} ({s.golden_rate:.1%})"))
    for m in moves:
        all_alerts.append(A.Alert("rule moved", pilot.WEEK2[-1], f"{m.rule} {m.branch}",
                                  f"{m.rule} fired on {m.after} of {m.after_n} {m.branch} files, {m.before} of {m.before_n} in week one"))
    for s in sess[2]:
        if s.verdict.startswith("suspected"):
            all_alerts.append(A.Alert("session", datetime.fromisoformat(s.day).date(), s.analyst, s.verdict))
    by_night: dict[tuple[str, object], list[float]] = defaultdict(list)
    night_of = {r["trace_id"]: r["start"].date() for r in roots}
    for r in store.by_name("classify"):
        by_night[("classify", night_of[r["trace_id"]])].append((r["end"] - r["start"]).total_seconds())
    for (stage, night), vals in sorted(by_night.items(), key=lambda kv: kv[0][1]):
        if pct(vals, .95) > 20.0:
            all_alerts.append(A.Alert("latency", night, f"{stage} stage",
                                      f"{stage} stage p95 {pct(vals, .95):.1f} s on {night:%a %d %b} ({len(vals)} files), "
                                      f"budget 20 s (Day 12)"))
    stale = [r for r in store.by_name("retrieval godavari-policy-register") if r["status"] == "error"]
    if stale:
        all_alerts.append(A.Alert("directory stale", stale[0]["start"].date(), "policy panel",
                                  f"{len(stale)} searches refused: the group snapshot is more than 36 hours old"))
    for w in weeks:                                  # the page rules are evaluated every night, not only declared
        for night in w.nights:
            end = max((night.at(r.started_s + r.elapsed_s) for r in night.ledger.rows), default=night.started)
            if end.time() >= QUEUE_READY_BY:
                all_alerts.append(A.Alert("queue not ready", end.date(), "02:00 job", f"the 02:00 job finished at {end:%H:%M}"))
    if len(sandbox.records) != len(store.by_name("core.write")) or len({r["file_number"] for r in sandbox.records}) != len(sandbox.records):
        all_alerts.append(A.Alert("core disagreement", pilot.WEEK2[-1], "core write", "core records and write spans disagree"))
    if store.report.quarantined:
        all_alerts.append(A.Alert("store quarantine", pilot.WEEK2[-1], "trace store", "spans quarantined at the boundary"))
    all_alerts.sort(key=lambda a: (a.day, a.rule))
    say()
    say("-- 7. alerts and where they went --")
    last = max((max(n.at(r.started_s + r.elapsed_s) for r in n.ledger.rows) for w in weeks for n in w.nights),
               key=lambda t: t.time())
    say(f"  page rules checked every night: the latest-finishing 02:00 job ended {last:%a %d %b %H:%M:%S}; core records {len(sandbox.records)}, "
        f"write spans {len(store.by_name('core.write'))}, files with two records {len(sandbox.records) - len({r['file_number'] for r in sandbox.records})}; "
        f"spans quarantined {sum(store.report.quarantined.values())}")
    for how in ("page", "digest", "weekly"):
        group = [a for a in all_alerts if a.how == how]
        say(f"  {how}: {len(group)}" + ("" if not group else "; " + "; ".join(sorted({f'{a.rule} -> {a.who}' for a in group}))))
    with (out / "alerts.jsonl").open("w", encoding="utf-8", newline="\n") as fh:
        for a in all_alerts:
            fh.write(json.dumps({"day": a.day.isoformat(), "rule": a.rule, "how": a.how, "who": a.who, "scope": a.scope,
                                 "text": a.text, "traces": list(a.traces)}, ensure_ascii=False, sort_keys=True) + "\n")

    data = {"weeks": weeks, "store": store, "fc": fc, "latency": latency, "fsig": fsig, "bsig": bsig, "moves": moves,
            "overrides": ov, "sessions": sess, "spot": spot, "retrieval": rsig, "d16": d16, "d17": d17, "d18": d18,
            "scan": scan, "alerts": all_alerts, "release": release.release_id, "worst": worst,
            "incident": {"calls": len(calls), "on_cont": dict(on_cont), "cost_cont": cost_cont, "cont": len(cont),
                         "before": before, "after": after}, "candidates": cands, "ledger_inr": ledger_inr}
    written_pages = D.write_all(data, out / "dashboards")
    say()
    say(f"wrote data/traces.sqlite, data/{trace_file.name}, data/alerts.jsonl, data/run-report.md and "
        f"{len(written_pages)} dashboards in data/dashboards/; {time.perf_counter() - t0:.1f} s")
    (out / "run-report.md").write_text("# Day 19 run report\n\n> The output of `python -X utf8 code/run_observability.py`, "
                                       "verbatim. Synthetic data, simulated analysts.\n\n```text\n" + "\n".join(lines) +
                                       "\n```\n", encoding="utf-8", newline="\n")
    store.conn.execute("VACUUM")
    return data


if __name__ == "__main__":
    main()
