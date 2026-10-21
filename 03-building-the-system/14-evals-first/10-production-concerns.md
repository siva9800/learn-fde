# 10 · Production Concerns: Running the Eval Inside Their World, and Keeping It True After You Leave

> Day 14 · Section 10 of 16 · [Chapter overview](README.md) · Previous: [09 · Advanced and 2026 patterns](09-advanced-and-2026-patterns.md) · Next: [11 · Project: the golden set and the harness](11-project-the-golden-set-and-harness.md)

---

## 10.1 Where it runs, and who can see it

The real eval runs where the real files are: on the machine in the Hyderabad building until the security review
passes (16 December 2026), then in the approved AWS Mumbai environment after the cutover (4 January 2027). Its
inputs are the most sensitive data in the engagement after the core system itself, so it gets the same treatment:

| Concern | Decision |
|---|---|
| who can run it | the Kaagaz FDE and Godavari's application-support engineer, under named service accounts (Day 22) |
| who can read the full report | the eval owners, the two team leads, the compliance head; access logged (seven-year view log) |
| what leaves | the masked export only (section 08.3), to named people at Kaagaz |
| where the truth file lives | beside the files, versioned, with write access for the eval owners' adjudication tool and nobody else |
| model calls during the eval | through the same model gateway and region as production (Day 25), never a developer's personal key |

A golden set run from an engineer's laptop with a personal API key is a data-protection incident, however good the
numbers are.

## 10.2 The eval is a release criterion, not a report

Day 13's registry promotes a prompt release from dev to pilot to production; Day 26 ships changes into Godavari's
own CI/CD. In both, the golden-set gate is a required check, the same as the tests:

- **dev to pilot:** the gate on the masked set in CI, and the real-model run in the building, both passing;
- **pilot to production:** the same, plus a week of pilot corrections reviewed by the eval owners;
- **after every production deployment:** the golden set run as a smoke check against the deployed system (Day 27
  owns it as part of the release runbook).

If the real-model run is skipped "because CI passed", the release record says so, and the compliance head can see
that it did.

## 10.3 Latency and cost of the eval itself

With the stub, the full test split runs in about 0.15 seconds, and the whole gate (including a five-run noise floor
on the development split) in under a second. With the real model, 150 files at Day 12's measured p95 of a couple of
dozen seconds for a long bundle is minutes, not seconds, and about Rs 950 to Rs 1,300. Two consequences:

- **CI uses recorded responses.** The real model's outputs for the golden files are captured once per model and
  prompt version, inside the building, and replayed in CI. A pull request that changes only the envelope or the
  rules can be gated in a second on real model output without calling the model or moving PII.
- **Prompt and model changes need a fresh real run.** Recorded responses are stale the moment the prompt or model
  changes; the nightly run (and the pre-promotion run) is what measures those.

## 10.4 Monitoring: the same metrics, in production

The golden set answers "is this change worse on known cases". Production monitoring answers "is the system getting
worse on today's files". Day 19 owns the dashboards; this chapter owns the definitions they compute, which must be
identical:

| Golden set (this chapter) | Production signal (Day 19) |
|---|---|
| field-level accuracy, by stratum | corrections per field per file in the review queue, by branch and channel |
| confidently wrong | corrections to fields that were not flagged |
| flag rate | review-queue rate, by field |
| completeness recall | the compliance head's monthly re-draw of decided files (Day 9) |
| page classification | share of unclassified pages per file, per branch |

When a production signal moves (a new branch, a scanner change, a provider's model update), the response is the
same: find the files, label a few, add them to the set, and let the gate protect the fix.

## 10.5 When the eval itself is broken

An eval harness is software, and it fails like software. The failures that matter most are silent:

| Failure | How it shows | Guard in this chapter |
|---|---|---|
| the harness scores the wrong files | numbers jump with no change | the manifest fingerprint; `LabelsChanged` |
| the normaliser starts forgiving content | normalised accuracy rises, exact accuracy does not | both reported; the "never forgiven" tests |
| the truth file is edited in place | a regression disappears | truth files replaced and versioned, never edited; the gate refuses a different set |
| a field silently stops being scored | accuracy rises because a hard field left | `test_every_mandatory_field_of_every_golden_file_is_scored` |
| the gate passes everything | nothing ever fails | the planted bad candidate (`trimmed`) must fail on every run, in CI |
| the gate fails everything | it gets switched off | the measured false-alarm rate, rerun when the policy changes |

The fifth row is worth copying to every customer: **keep a known-bad candidate in CI and require the gate to fail
it.** It is the eval's own regression test.

## 10.6 Ownership after handoff

Day 28 hands the system to Godavari. The eval is part of the system, so it has owners on Godavari's side by name:

- **the eval owners** (Lakshmi and the senior analyst, or whoever the team leads nominate after them) own the labels,
  the guide and the policy thresholds;
- **the compliance head** owns the completeness labels and the rule-gap list;
- **Godavari's application-support engineer** (assigned by IT in week 2, Day 8) owns the harness, the nightly run and
  the gate in their CI;
- **Kaagaz** receives the masked export and owns nothing that requires the real files.

A golden set that only the FDE can run stops running the week the FDE leaves, and the next prompt change ships on
an average.

## 10.7 Key takeaways

- The real eval runs where the real files are, through the production gateway, with logged access.
- The gate is a required release check at every promotion and after every deployment.
- CI replays recorded real-model responses; prompt and model changes need a fresh real run.
- Production monitoring computes the same definitions; a moved signal becomes new golden files.
- Guard the eval against its own silent failures; keep a known-bad candidate that must fail.
- Name the owners on the customer's side before handoff.
