# 10 · Project: The Godavari Observability Layer

> Day 19 · Section 10 of 15 · [Chapter overview](README.md) · Previous: [09 · 2026 patterns](09-2026-patterns-and-production-concerns.md) · Next: [11 · Build it with AI](11-build-with-ai-and-verification.md)

---

## 10.1 What you build

An offline observability layer for Godavari's pilot, wrapped round the code Days 11 to 18 already wrote:

1. span-style structured events from wrappers around the existing stages, one trace per loan file;
2. a local trace store in SQLite, written only through a redacting boundary, with a JSONL export;
3. a cost roll-up per file, branch, night, stage and prompt release, with ceiling, spike and latency alerts;
4. a weekly quality job comparing corrections and overrides with the golden-set baseline;
5. a redaction filter, with tests proving no PAN, Aadhaar number, mobile number or customer name reaches the store;
6. three static HTML dashboards for the FDE, the team leads and the COO.

It runs on both pilot weeks: week one is Day 18's week exactly; week two is the next 60 files, with Guntur's long
statements from Tuesday and the page filter from Thursday.

## 10.2 Setup

pytest is not on the global Python, so everything runs in a virtual environment with the chapter's pins. From the
chapter folder:

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows; on Linux or macOS: source .venv/bin/activate
pip install -r code/requirements.txt
python -X utf8 code/run_observability.py
python -X utf8 -m pytest code
```

The pins are the course-wide ones (Pydantic 2.12.5, Jinja2 3.1.6, pytest 9.1.1), needed by the chapters this one
imports. The layer itself uses only the standard library: `sqlite3`, `html`, `json`. Days 11 to 16 and 18 must be at
their FOLDERS.md paths; Day 17's audit log is read if present. No network, no API key.

## 10.3 The code

| File | What it does |
|---|---|
| `code/godavari_obs/paths.py` | puts Days 11, 12, 13, 14, 15, 16 and 18 on the path; refuses to start if one is missing; writes no bytecode into their folders |
| `code/godavari_obs/spans.py` | the span, the tracer, deterministic trace and span ids, the OpenTelemetry gen-AI attribute names |
| `code/godavari_obs/redact.py` | the allowlist schema with a validator per key, the identifier scanners, `admit()` |
| `code/godavari_obs/store.py` | the SQLite store, written only through `admit()`; queries; the JSONL export |
| `code/godavari_obs/instrument.py` | ledger rows to spans; `TracedModel`, `TracedRuleSet`, `traced_push`, `TracedRetrieval`; the Day 20 seam `as_day12_file` |
| `code/godavari_obs/statements.py` | Guntur's sixty-page statements (synthetic) and the page filter that fixed them |
| `code/godavari_obs/pilot.py` | the two traced weeks, using Day 18's files, model run and simulated analysts; the policy panel's searches |
| `code/godavari_obs/costs.py` | roll-ups, ceiling, spike and forecast |
| `code/godavari_obs/quality.py` | the weekly job: fields against the golden set, rules that moved, overrides, sessions, spot checks, retrieval, candidates for Day 14 |
| `code/godavari_obs/sources.py` | counts from Day 16's journal and Day 17's audit log; Day 18's events at the boundary; upstream scans |
| `code/godavari_obs/alerts.py` | the routing table: page, digest or weekly, and to whom |
| `code/godavari_obs/dashboards.py` | the three pages: escaped, static, light and dark, a tooltip on every mark, a table beside every chart |
| `code/run_observability.py` | runs all of it and writes `data/` |
| `code/tests/` | 30 tests in four files |

## 10.4 The run

The full output is in `data/run-report.md`. The parts that prove the layer works:

```text
== Day 19 · observability for Godavari's pilot: Kukatpally and Guntur, 7 to 18 December 2026 ==
spans written: 5830 in 180 traces; prompt release pinned for pilot: extraction@2.0.0+fake-large-2026-10
boundary: 0 attribute values dropped, 0 spans quarantined

-- 1. checks on the traces --
  SFTP arrivals 120; file traces 120; distinct file numbers 120
  traces missing a stage: 0; core.write spans 71 for 71 files written; core records created 71
  rupees: ledger Rs 676.5666, traces Rs 676.5666, difference Rs 0.000000
  models in the calls ['fake-large-2026-10', 'fake-small-2026-10']; the release pins ['fake-large-2026-10', 'fake-small-2026-10']: match
  week one's screen log against Day 18's data/pilot-week-1/action-log.jsonl: identical (840 events)

-- 2. cost per file (model calls, Rs), from the traces --
  pilot-week-1: 60 files, median 5.40, p95 7.73, max 9.46, total 320.40; at 1,400 files a month about Rs 7,476 (Day 12 measured about Rs 8,900)
  pilot-week-2: 60 files, median 5.47, p95 10.56, max 14.00, total 356.16; at 1,400 files a month about Rs 8,311 (Day 12 measured about Rs 8,900)
  ...
    Tue 15 Dec Guntur       6  10.66  14.00    95.0 /  95.0
    Wed 16 Dec Guntur       6   8.74   9.94    83.5 /  83.5
    Thu 17 Dec Guntur       6   5.15   8.65    81.5 /  22.5
    Fri 18 Dec Guntur       6   3.99   5.55    75.5 /  16.5
  ...
  alerts: 3
    Tue 15 Dec spike    Guntur median Rs 10.66 per file on Tue 15 Dec, 2.0 times its week-one median of Rs 5.42; median pages 95
    Tue 15 Dec ceiling  GF-61070 (Guntur) cost Rs 14.00 in model calls; the ceiling is Rs 12 for every file; 96 pages, 119 calls
    Wed 16 Dec spike    Guntur median Rs 8.74 per file on Wed 16 Dec, 1.6 times its week-one median of Rs 5.42; median pages 84
```

The 180 traces are the 120 files plus 60 policy-panel searches, each its own trace. Section 3 of the report is the
incident from GF-61070's trace (section 04 of these notes); section 5 is the quality job (section 05); section 6 is
the upstream scan (section 07); section 7 is the alert routing (section 08). The whole run takes about 13 seconds.

The tests:

```text
..............................                                           [100%]
30 passed in 23.24s
```

They are grouped by what they prove: the traces are complete and agree with the ledger (`test_traces.py`), the
alerts fire on the right nights and the filter is safe (`test_costs_and_alerts.py`), the quality job reads the golden
baseline and the pages load nothing and escape everything (`test_quality_and_dashboards.py`), and nothing identifying
reaches any output (`test_redaction.py`, section 11.5).

## 10.5 What goes into the engagement folder

| Path | Who reads it |
|---|---|
| `worksheet/godavari-observability-plan.md` | Srinivas, the Vijayawada team lead, the compliance head, application support: the five questions, alert routing, what is never logged, the retention and DPA questions, open items O1 to O6 |
| `data/dashboards/fde.html`, `team-leads.html`, `coo-weekly.html` | the three readers |
| `data/alerts.jsonl` | the fortnight's alerts with their owners |
| `data/sample-trace-GF-61070.jsonl` | one trace in the exporter's shape, 127 spans |
| `data/traces.sqlite` | the store (regenerated by the run) |
| `data/run-report.md` | the run, verbatim |

Day 20 ships the skeleton with this layer inside it; Day 27 turns `alerts.py` into SLOs and on-call; Day 29's weekly
readout quotes the COO's page.
