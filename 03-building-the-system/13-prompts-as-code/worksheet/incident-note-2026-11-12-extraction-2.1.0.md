# Incident note: extraction 2.1.0 rolled back in pilot (rollback drill)

> Godavari engagement · week 3 · Thursday 12 November 2026 · written by the Kaagaz FDE for the engagement folder.
> A rehearsal on replayed files, before any live traffic; the numbers are from `code/run_demo.py` on synthetic files.

---

## Summary

At 10:05 the pilot environment was moved from `extraction@2.0.0+fake-large-2026-10` to
`extraction@2.1.0+fake-large-2026-10`, a token-saving change that removed the Telugu label glossary and a few-shot
example. At 11:40 a replay of twenty recent Guntur files showed monthly income read as the annual figure on all twelve
handwritten Telugu declarations (for example 7,08,000 a month for a declaration of 59,000 a month). The FDE rolled
pilot back to 2.0.0 with one registry change, re-ran the twenty files under the restored release, and found no wrong
monthly income values. No live file was affected.

## Timeline

| Time | Event |
|---|---|
| 12 Nov 10:05 | 2.1.0 promoted to pilot after the gate passed on the twelve labelled Kukatpally files |
| 12 Nov 11:40 | Guntur replay: `monthly_income` wrong on 12 of 20 files; alert rule (wrong above 10 percent of the window) fires |
| 12 Nov 11:40 | `cli rollback --env pilot`: pilot pins 2.0.0; registry change committed with the reason |
| 12 Nov, after the rollback | the twenty files re-run under 2.0.0 with new idempotency keys: no wrong monthly income |
| 12 Nov 12:00 | re-promotion of 2.1.0 refused by the registry: a rolled-back release returns only as a new version |

## Why the checks did not stop it

- The labelled set has no handwritten Telugu income declarations, because its files are from Kukatpally. The gate
  compared like with like and found no difference.
- The lint warned that the `telugu` variable was no longer read by any template. The warning was not answered in the PR.
- The gate's token count did not move, although the change was justified by token savings.

## What changes

1. The review checklist (`prompt-change-review-checklist.md`) now requires an answer to every lint warning and an
   explanation when the gate's token count does not move as claimed.
2. Request to the eval owners for Day 14's golden set: a named slice of Guntur files with handwritten Telugu
   declarations, labelled by Lakshmi and the senior analyst. Until then, every promotion to pilot includes the Guntur
   replay.
3. The trim may return as a new version that keeps the glossary on Telugu pages, with its saving measured on a set that
   contains them.
4. Agreed with Godavari IT before the 17 December change freeze: rolling back to the previous approved release is
   always permitted, during a freeze included.

This is risk R1 in the discovery document and the 2019 OCR pilot's failure (Day 6), reintroduced by a prompt edit.
The compliance head was told the same day.
