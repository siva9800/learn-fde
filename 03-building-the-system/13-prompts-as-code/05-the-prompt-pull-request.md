# 05 · The Prompt Pull Request: Reading the Diff, and What Each Check Cannot See

> Day 13 · Section 5 of 13 · [Chapter overview](README.md) · Previous: [04 · Versions, releases and the registry](04-versions-releases-and-the-registry.md) · Next: [06 · Page 1 and page 40](06-page-1-and-page-40.md)

---

## 5.1 The pull request

Thursday 12 November 2026, morning. A Kaagaz platform engineer in Bengaluru, looking at the pilot's projected token
bill, opens a pull request: extraction 2.1.0, "same contract as 2.0.0; removes the Telugu label glossary and the
few-shot example from the extraction call: the model reads Telugu, and the page prompt is shorter". The CLI's diff of
the two version directories (`cli diff 2.0.0 2.1.0`, saved in `data/diff-2.0.0-to-2.1.0.diff`), trimmed here to the
lines that matter:

```diff
--- 2.0.0/extract.system.j2
+++ 2.1.0/extract.system.j2
@@ -14,6 +14,2 @@
 {% include "partials/_unsure.j2" %}
-{% if telugu %}
-
-{% include "partials/_telugu_glossary.j2" %}
-{% endif %}
 {% for ex in examples %}
--- 2.0.0/meta.toml
+++ 2.1.0/meta.toml
-version = "2.0.0"
+version = "2.1.0"
-author = "fde.kaagaz"
+author = "platform.kaagaz"
-[[examples]]
-file = "examples/income_proof_telugu.json"
-page_type = "income_proof"
-telugu = true
--- 2.0.0/partials/_telugu_glossary.j2
+++ /dev/null
-నెలసరి ఆదాయం = monthly income
-సంవత్సర ఆదాయం = annual income (a yearly figure: never use it as monthly_income)
```

Four files, five lines added, thirty-three removed: a clean-up, correctly bumped minor.

## 5.2 What CI says

Three checks run on every pull request that touches `prompts/`:

```text
lint extraction@2.1.0: 0 errors, 1 warnings
  WARNING call 'extract' declares 'telugu' but no template reads it
gate on the labelled set: 2.0.0 97.2% correct, 0.0% wrong, 2212 large tokens per file
                          2.1.0 97.2% correct, 0.0% wrong, 2212 large tokens per file
registry verified: every hash, approval and pin checks out
```

The gate passes. The registry refuses to let the author approve it ("platform.kaagaz wrote ... and cannot approve
it"), so the FDE approves, the compliance head reads the rendered prompt (no rules, nothing decided by the model:
correct, she has nothing to object to), and 2.1.0 is promoted to pilot at 10:05. Section 07 is what happens at 11:40.

Two lines in that output should have stopped the merge, and neither is a failure:

1. **The warning.** `telugu` is still passed by the pipeline but no template reads it. The code still detects Telugu
   pages; the prompt no longer does anything with that knowledge. A newly unused variable is a removed behaviour, and
   the question "which behaviour, and where is it tested?" has no answer in this PR.
2. **The tokens did not move.** A change whose whole justification is "shorter prompts" saved zero tokens on the gate's
   files. That is not a small saving; it is a statement that the eval set never exercises the code path the change
   touches. The labelled set is twelve Kukatpally files, and Kukatpally does not send handwritten Telugu declarations.

## 5.3 What each check cannot see

| Check | Catches | Cannot see |
|---|---|---|
| **lint** | business-rule words in prompt text, page text outside the wrapper, model names, undeclared variables, missing product variants, CRLF | meaning: "only read files with a PAN" is a rule with no rule words; a sensible-looking deletion |
| **verify** | released versions edited in place, self-approval, alias pins, pins to missing releases | whether the release is any good |
| **gate** | a field getting fewer right answers or more wrong ones *on the files in the set* | everything not in the set: Guntur, Telugu, phone photos, a new branch |
| **the compliance read** | rules and decisions in the prompt | accuracy |
| **the reviewer** | intent, the warning above, the tokens that did not move, the slice the set lacks | nothing, if they read; everything, if they skim the green ticks |

The gate's tolerances (`gate.py`): a field may lose at most one correct answer, and may not gain a single wrong one.
On twelve files one file is already eight points, so this is a smoke alarm, not a measurement. Day 14 builds the real
instrument: 150 files labelled by the analysts, with slices by branch, product and language, and the statistics to say
whether a difference is real.

## 5.4 The review checklist

The full checklist is `worksheet/prompt-change-review-checklist.md`. The questions that would have stopped 2.1.0:

- [ ] Render both versions for every product and page type the change touches, and read them side by side.
- [ ] For every removed sentence, partial or example: which files exercised it, and are they in the gate's set?
- [ ] Does the gate's token count move the way the PR claims? If not, the set does not exercise the change.
- [ ] Does every lint warning have an answer in the PR description?
- [ ] Is there a slice of real traffic (branch, product, language, channel) the set does not cover? Run it there too.
- [ ] Is the version bump honest (major for contract, minor for intended behaviour, patch for none)?
- [ ] Is the author different from the approver, and has the compliance head read the rendered prompt?
- [ ] If this goes wrong in pilot, what alert fires, and is the previous release still on disk?

Put `prompts/` under a CODEOWNERS rule naming the engagement's FDE, and `prompts/registry.json` under one that adds
the engagement lead: the people who answer for the prompt should see every change.
