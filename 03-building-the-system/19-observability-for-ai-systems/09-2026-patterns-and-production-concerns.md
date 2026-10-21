# 09 · 2026 Patterns, What Is Hype, and Production Concerns

> Day 19 · Section 9 of 15 · [Chapter overview](README.md) · Previous: [08 · Dashboards and paging](08-dashboards-for-three-audiences-and-paging.md) · Next: [10 · Project](10-project-the-godavari-observability-layer.md)

---

## 9.1 What practitioners use in October 2026

| Pattern | What it is | At Godavari |
|---|---|---|
| OpenTelemetry gen-AI conventions | standard names for model-call, retrieval, tool and agent spans, so traces land in any backend | used for every model call; still Development status, so the names sit in one file |
| an exporter, not a vendor SDK | the application emits OpenTelemetry; the customer's collector routes it | the store's JSONL export is the exporter's shape; Godavari's backend is decided with its IT team |
| LLM-observability products | hosted or self-hosted tools that store prompts, answers, scores and costs per trace; several are open source and accept OpenTelemetry | useful in Kaagaz's own development environment on synthetic data; inside Godavari only if they run in Godavari's account with content capture off |
| online evaluation on a sample | a scorer or a calibrated judge run on a sample of production outputs | Day 14's judge, calibrated on human labels, on a weekly sample; Day 27 owns running it as a production check |
| cost attribution per unit of work | rupees per file, per branch, per release, from the client's own ledger | built here |
| feedback joined to traces | operator corrections as events on the span that produced the output | built here |

Check what the customer already runs before adding anything: a team on Grafana and Loki needs spans, not a new vendor.

## 9.2 What is hype

- **"Log every prompt and answer, it is the only way to debug."** The conventions themselves make content capture
  opt-in and recommend external storage with separate access control. At a lender, the prompt is the customer's
  documents. Debug with synthetic files and the golden set; production traces carry ids and numbers.
- **"An LLM will watch your LLM."** A judge on every production output doubles the bill and inherits the judge's
  errors. Day 14's rule stands: calibrate a judge on human labels before trusting it, and run it on a sample.
- **"Automatic root cause."** Tools that summarise a trace are useful. The root cause on Tuesday was an instruction given
  to the Guntur branch's staff; no tool sees that. The trace tells you where to look and the team lead tells you why.
- **"One AI observability score."** A single quality number hides the field that is failing, exactly as Day 14's
  averages hid one stratum. Per field, per branch, with intervals.

## 9.3 Production concerns

**Volume and storage.** The pilot fortnight wrote 5,830 spans for 120 files, about 49 a file, into a 4.7 MB store. At
1,400 files a month that is under 70,000 spans and roughly 55 MB a month: trivial. Volume is not a reason to sample at
Godavari; it would be at a lender with a hundred times the files, and then sampling is by outcome (section 03).

**Late data.** A trace is not finished at 02:01. The review arrives at 10:00, the core write in the afternoon, and a spot
check may land days later. The store is append-friendly, the root span's end is updated when the write happens, and
dashboards that read "this week" must say which events they wait for.

**Clocks and time zones.** Everything is IST with the offset written into every timestamp. Day 16's write window is
evaluated in IST; the virtual clocks start at the 02:00 drop. Mixing a naive local time with UTC is the commonest way to
get a review that finishes before it starts (section 12).

**The store is sensitive even when clean.** It has no identifiers, but it does have file numbers, branch codes and
analysts' pseudonyms, and it can be joined to Godavari's systems. Access is the FDE and Godavari's application-support
engineer; retention is the compliance head's decision (section 07).

**Telemetry must never break the pipeline.** A wrapper that raises stops a file. In production every wrapper's own
failure is caught, counted and reported, and the stage it wraps carries on. (This offline project lets a wrapper
failure raise, so that the tests see it; that is the one place it should differ from production.) The opposite rule applies to the boundary:
if the redactor cannot run, nothing is written.
