# 11 · Interview Questions

> Day 13 · Section 11 of 13 · [Chapter overview](README.md) · Previous: [10 · Mistakes and debugging](10-mistakes-and-debugging.md) · Next: [12 · Exercises](12-exercises.md)

---

Fourteen questions in the forms they take in FDE and applied-AI loops: practical coding ("how would you structure
this?"), system design ("how do you change it safely?") and the hiring-manager screen ("tell me about a regression").
Answer out loud first, then compare.

## Prompts as code

**Q1. Why treat a prompt as code? It is one paragraph of English.**

Because it changes behaviour as much as a function does, and it changes far more often after launch. So it gets a file
in the repository, a reviewed diff, a test, a version and a rollback. Without them you get the quiet regression:
someone improves the wording, nothing errors, and a slice of files gets worse for a week. In a lender, the auditor's
"what was the system told to do on the day it processed this file" also needs a dated record. (01, 02)

**Q2. Where should prompts live, and why not the vendor's prompt dashboard?**

In the repository as template files, released through a registry file that is itself changed by pull request.
Dashboards often have versions; the problem is that edits there happen outside review, CI and the eval, so the
repository stops being the truth. Publishing to a dashboard from CI for browsing is fine; making it the source is not.
(02.1, 08.1)

**Q3. What is part of "the prompt" besides the instruction text?**

Partials, product variants, field descriptions, page-type routing, merge precedence, few-shot examples and variable
types, all versioned together under one content hash. The model snapshot belongs to the release record instead,
because the same prompt on a new model is a new release. (02.2)

**Q4. Should business rules ever go in a prompt?**

No. A rule in a prompt is a second, unsigned copy of a rule already in code, and the copies drift; and a prompt
requests, it does not enforce. At Godavari the compliance head signs the rules as code. A CI lint fails prompt text
with percentages, rupee thresholds, LTV, approve, reject, eligible or mandatory, and a human checks meaning, because a
rule can be written without any of those words. (02.3, 05.3)

## Versions and releases

**Q5. How do you version prompts?**

Semver, adapted: major when calls, variables or the output contract change; minor for an intended behaviour change;
patch for none. Every bump, patch included, gets a full regression run, because for a model "no intended change" is not
"no change". Released versions are immutable directories with a content hash; a change is a copy and a new version.
(04.1, 04.2)

**Q6. Why pin a prompt version to a model version?**

Because the pair is what behaves. In this chapter's drift check the same prompt on a newer snapshot kept accuracy at
97.2 percent while the wrong rate went from 0 to 2.8 percent, because the new snapshot guesses smudged digits. The
release id names both, the release refuses aliases, and the pipeline stops if the adapter would call a different model.
(04.3, 07.4)

**Q7. What is in a release record?**

Prompt id and version, content hash, model snapshots per tier, output schema version, per-field eval results with the
eval set's hash, author, approver (never the author), the compliance head's read, and notes such as a rollback. With
the release id on every logged call, that answers which prompt, which model, which score and who approved, for any
file. (04.3)

**Q8. Walk me through promoting a prompt change from dev to production.**

The PR adds a version directory. CI runs the lint, verifies the registry and gates the candidate against the release
pinned in the target environment on the same eval set. A second engineer approves, the compliance head reads the
rendered prompt, and promotion is a PR that moves one pin. Production also needs a pilot run. The runtime picks up the
pin on its next batch. (04.4, 05)

## Long documents

**Q9. A prompt works on a 3-page sample and fails on a 40-page file. Why?**

Facts in the middle of long inputs, and far from the instructions, are used less reliably; an early page that answers
wrongly (the form's "Co-applicant: none") beats a late page that answers rightly (the annexure on page 38) with no drop
in confidence; repeated headers and look-alike numbers distract; scans smudge and tables split across pages; and
handwritten Telugu costs more tokens and is read less reliably. A sample has none of these. (06.1, 06.2)

**Q10. Whole-file, chunked, or classify-then-extract?**

For field extraction, classify then extract: a cheap call per page returns its type, a call per relevant page asks only
its fields, and code merges by precedence. Page order stops mattering and failures become per page and visible.
Chunking shortens context but cannot say which chunk is authoritative. Whole-file suits cross-page reasoning. In the
chapter's lab, whole-file got 9 of 16 late co-applicants; per-page got 16 of 16 with no wrong values. (06.4, 06.5)

**Q11. Can't a million-token context window solve this?**

It solves capacity, not attention: the position effects were measured on long-context models, and a bigger window adds
distractors. Long context for reasoning across documents; split by page type for fields that each live on one page.
(06.6)

## Operating it

**Q12. A prompt change regressed in production. What do you do, and what makes that take minutes?**

Roll back first: re-pin the previous release and commit the reason. That takes minutes only if the previous version's
files are on disk unchanged, the runtime resolves the release per batch, the idempotency key includes the release so
re-runs do real work, and every call is logged with its release so the affected files can be listed and re-run. Then
add the eval slice that would have caught it. (07.1, 07.2)

**Q13. Tell me about a change that passed its tests and still broke something.**

(The chapter's drill as a story.) A teammate removed a Telugu glossary and an example to cut tokens. The gate passed on
twelve Kukatpally files, none with a Telugu declaration. Two signals were missed: a lint warning that a variable was now
unused, and a token count that did not move although saving tokens was the point. A Guntur replay showed monthly income
read as annual; I rolled back in one command, re-ran the affected files and asked for a Telugu slice in the golden set.
Now "did the gate's tokens move?" is a required review question. (05.2, 07.1)

**Q14. How do you detect that the provider changed the model under you?**

Pin dated snapshots and refuse aliases; check at every batch that the adapter would call the release's models; and run
a nightly check of the current prompt on the pinned model and the newest snapshot, watching wrong and unsure separately,
since a model that stops saying "unsure" can hold accuracy flat. Even a fixed ID can shift when serving infrastructure
changes, so the nightly check stays on. (07.4)
