# 10 · Common Mistakes and Debugging

> Day 13 · Section 10 of 13 · [Chapter overview](README.md) · Previous: [09 · Project: the Godavari prompt package](09-project-the-godavari-prompt-package.md) · Next: [11 · Interview questions](11-interview-questions.md)

---

Each row is **symptom, likely cause, fix**, with the section that explains it.

## 10.1 Prompts and templates

| Symptom | Likely cause | Fix |
|---|---|---|
| The model is told "This page was classified as: ." | default `Undefined` and a typo in a variable name | `StrictUndefined`; a test that renders a deliberate typo (03.2) |
| A change to the gold prompt broke two-wheeler extraction | one giant template with an `if` chain per product | a variant file per product, a template per page type (03.1, 03.4) |
| Editing a partial for the new version changed the old version's output | partials shared across versions | per-version partials; the content hash covers them (03.3) |
| The prompt mentions the 90 percent margin or the LTV caps | a rule copied into the prompt "to help" | delete it; the rule is in signed code; the lint fails it (02.3) |
| The model sees `&#39;` and `&amp;` in page text | `autoescape=True` on the prompt environment | autoescape off for prompts (03.5) |
| A page containing `{{ 7*7 }}` printed 49 somewhere | customer text rendered as a template | customer text only as a variable value, through the wrapper partial (03.5) |

## 10.2 Versions and the registry

| Symptom | Likely cause | Fix |
|---|---|---|
| "edited after release" on one laptop only | CRLF line endings from a Windows checkout changed the hash | normalise CRLF before hashing; `.gitattributes` with `* text=auto eol=lf` for `prompts/` (04.2) |
| Nobody can say which prompt processed a January file | the call log has no release id | log `release_id` on every call; Day 19 traces it (04.3) |
| Output changed with no prompt change | the model under the name changed: an alias moved, or serving changed under a fixed ID | pin snapshots in the release; `check_models()`; the nightly drift check (07.4) |
| The batch stopped with `ModelMismatch` | the adapter is configured with an alias or a different snapshot from the release | configure the adapter from the release record; or score the new snapshot as a new release (07.4) |
| A PATCH bump moved the score | the change was not a patch | re-label it MINOR in the PR; the eval decides, not the label (04.1) |
| The approver is the author in the history | someone used a shared account or edited the JSON by hand | named identities; `verify` in CI; CODEOWNERS on `registry.json` (05.4) |

## 10.3 Long documents

| Symptom | Likely cause | Fix |
|---|---|---|
| 100 percent on the demo, misses on real files | samples are three pages; real files are forty in tray order | test on long files built like real bundles; score by page band (06.1, 06.5) |
| A late field comes back as a confident default ("none", 0, the form's value) | an early page answers wrongly and wins over the late page | classify pages; merge by precedence in code (06.4) |
| Repeating the instructions at the end fixed the back of the file and broke the middle | the failure moved, it did not go away | measure by page band; split by page type (06.5) |
| Monthly income twelve times too high on Guntur files | Telugu label not read; the annual figure taken | the glossary for Telugu pages; a Telugu slice in the golden set (06.2, 07.1) |
| Per-page cost far above the estimate | classification instructions repeated per page with no caching, or every page sent to the large tier | cache the stable prefix (Day 12); first lines only for classification; skip page types with no fields (08.2) |

## 10.4 Rollback

| Symptom | Likely cause | Fix |
|---|---|---|
| "nothing to roll back to" | the release had no predecessor in that environment, or the history was edited | promote through the registry only; never hand-edit pins (07.2) |
| Rollback done, files still wrong | the re-run hit the cache: the idempotency key has no release in it | include `release_id` in the key (Day 12); re-run the files the bad release touched (07.2) |
| Rollback means a redeploy | the prompt is loaded at import or build time | resolve the release per batch (04.5, 07.2) |

## 10.5 A routine for "the extraction got worse"

Check the registry history (did a release change?), the call logs (is every call on the pinned release and model?)
and the drift check (is the pinned model behaving as it did?); then slice the bad results by branch, product,
language, channel and page band, render the prompt for one failing page, and if a release caused it, roll back first
and investigate second.
