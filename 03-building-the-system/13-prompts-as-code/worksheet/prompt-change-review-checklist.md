# Prompt change review checklist (Godavari engagement)

> Adopted for every pull request that touches `prompts/` or `prompts/registry.json`, from week 3 (Day 13).
> The author fills the first column; the reviewer, who is never the author, ticks the second.

---

## 1. What changed

| Question | Author's answer | Reviewer |
|---|---|---|
| Which version directory is new? (Released directories are never edited.) | | [ ] |
| Bump: major (calls, variables or output contract), minor (intended behaviour) or patch (none)? Why? | | [ ] |
| Rendered before and after for every product and page type the change touches? Paste the paths. | | [ ] |
| Every removed sentence, partial or example: which real files exercised it? | | [ ] |
| Does any new text state a business rule (thresholds, percentages, rupee limits, documents required, decisions)? | | [ ] |
| Does any customer text reach the model outside `partials/_untrusted_page*.j2`? | | [ ] |
| Any new few-shot example: source file id, split (must be train), masked? | | [ ] |

## 2. What CI said

| Check | Result | Reviewer |
|---|---|---|
| `cli lint`: errors (must be zero) and every warning explained | | [ ] |
| `cli verify`: clean | | [ ] |
| Gate on the labelled set: per field correct and wrong, candidate against the release pinned in the target environment | | [ ] |
| Tokens per file per tier: did they move the way the PR claims? If not, the set does not exercise the change | | [ ] |

## 3. What the set does not cover

| Question | Answer | Reviewer |
|---|---|---|
| Which slices of real traffic are absent from the set (branch, product, language, channel, page count)? | | [ ] |
| Was the change run on a replay of each absent slice? Result? | | [ ] |
| Does the change touch the "unsure" behaviour? Unsure and wrong reported separately? | | [ ] |

## 4. Release

| Item | Value | Reviewer |
|---|---|---|
| Release id (prompt version plus large-tier snapshot) | | [ ] |
| Models: dated snapshots, matching the adapter configuration | | [ ] |
| Approved by (not the author) | | [ ] |
| Compliance head's read recorded in the registry (pilot and production) | | [ ] |
| The alert that would catch a regression, and the rollback command, written in the PR | | [ ] |
| The previous release's directory is untouched and on disk | | [ ] |

The questions that would have stopped 2.1.0 on 12 November are 1.4, 2.4 and 3.1.
