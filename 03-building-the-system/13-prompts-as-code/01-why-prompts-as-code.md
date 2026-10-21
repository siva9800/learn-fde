# 01 · Why Prompts as Code: Page 38, and the Edit Nobody Wrote Down

> Day 13 · Section 1 of 13 · [Chapter overview](README.md) · Next: [02 · Where prompts live](02-where-prompts-live.md)

---

## 1.1 Tuesday of week 3

Tuesday 10 November 2026, the machine in the Hyderabad building. Friday is milestone M07 (Day 8): ten real files go
from PDF to the core system's test copy, each approved by an analyst. Day 12's client calls the model once per page,
with two plain prompt files. Srinivas, the Hyderabad team lead, asks the fair question: the vendor's demo sent the
whole file in one call and read all twelve three-page samples perfectly, so why forty calls? On Monday you checked
the demo's prompt into the repository as `extraction@1.0.0`; now you run it on a real 40-page bundle from Kukatpally.

Applicant, PAN, amount: right. Co-applicant: "none", confidence 0.88. Srinivas turns to page 38: a co-applicant KYC
annexure, stapled at the back with the sanction papers, because the credit officer asked for a co-applicant after the
form was signed. The form on page 1 still says "Co-applicant: none". Nobody refills a signed form.

The model did not crash and did not say "unsure". It read the early page, which looked like an answer, and missed the
late page, which was the answer. Its confidence did not drop, because a model does not know what it did not read. On
the fifty synthetic files this chapter builds to reproduce that bundle, the same prompt gets the co-applicant right on
9 of 16 files that have one, and every miss is a confident "none" (section 06).

That is half the chapter, and it is the measured reason for Day 12's per-page shape, which becomes `extraction@2.0.0`
here. The other half arrives on Thursday, when a teammate trims that prompt to save tokens.

## 1.2 Why it matters for your career

Two things from the course research (CURRICULUM.md and the Part 3 plan):

- Applied AI work (LLM application development, retrieval, evals, guardrails) appears in 80 percent or more of the
  1,000 FDE postings analysed in 2026, beside core engineering in 95 percent or more. The work is not inventing
  prompts; it is operating them in someone else's production.
- The prompt is where most production changes happen after launch, and an untracked prompt edit is the commonest
  cause of a quiet regression. A model upgrade is an event; a prompt edit is a Tuesday.

The customer's view is simpler. Godavari's compliance head said in week 2, of the completeness rules: "I sign it, and
if it changes, I sign the change" (Day 6). Her next question is always the auditor's: what was the system told to do on
the day it processed this file, who changed it, and on what evidence? If no file in the repository answers that, you
are running an unaudited system inside a regulated lender.

## 1.3 What "prompts as code" means

A prompt changes the system's behaviour as much as any function does. So it gets the same treatment:

1. **It lives in the repository**, as files, not as a string inside Python and not in a vendor dashboard.
2. **It is a template** with typed variables, so one prompt serves four products and a dozen page types without being
   copied twelve times.
3. **It has a version**, and a released version never changes. A change is a new version.
4. **It is released by a record**: this prompt version, with this model snapshot, scored this on these files,
   written by this person, approved by that one, read by the compliance head.
5. **It is reviewed as a diff** in a pull request, with checks in CI.
6. **It can be rolled back** in one step, because the previous release is still on disk and the runtime looks up what
   to run on every batch.

None of this is exotic; it is what engineering already does for code. It needs a chapter because prompts look like
prose, so teams treat them like prose: edited in place, tested by eye, deployed by copy and paste.

## 1.4 Where this sits

| Day | What it gives this chapter | What this chapter gives back |
|---|---|---|
| [Day 6](../../02-discovery-and-decomposition/06-discovery-interviews/README.md) | RULES_AS_SIGNED_CODE, "cannot tell" over a guess, page order unlabelled, handwritten Telugu income | prompts that contain no rules, say null when unsure, and do not depend on page order |
| [Day 11](../11-the-system-around-the-model/README.md) | the line between code and model | the model side of that line, versioned |
| [Day 12](../12-llm-apis-for-production/README.md) | the adapter, tiers, the idempotency key with the prompt version in it | the prompt that goes inside each call, and the release that names the model |
| [Day 14](../14-evals-first/README.md) | (next) the golden set and the eval harness | every release here carries a score; Day 14 makes that score trustworthy |

## 1.5 The hard parts, named

1. **A prompt change has no compiler.** A deleted Jinja block is a perfectly valid template. The only evidence that it
   broke something is an eval, and the eval only sees what is in its set. The 2.1.0 trim in section 07 passes its gate
   because the set has no Telugu declarations.
2. **Long documents fail where you are not looking.** The failure moves when you move the instructions (section 06).
   You cannot reason your way to the right layout; you measure it.
3. **The model can change under a fixed name.** Aliases move, and even pinned IDs sit on serving infrastructure that
   changes (section 07). Pinning helps; it does not remove the need for a nightly check.
4. **It feels like bureaucracy for one sentence of text.** It is not, and the rollback drill in section 09 shows why in
   about seven seconds of runtime.
