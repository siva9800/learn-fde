# 08 · 2026 Patterns and Production Concerns

> Day 13 · Section 8 of 13 · [Chapter overview](README.md) · Previous: [07 · Rollback and drift](07-rollback-and-drift.md) · Next: [09 · Project: the Godavari prompt package](09-project-the-godavari-prompt-package.md)

---

## 8.1 What practitioners do in 2026, and what is hype

| Pattern | Verdict | Why |
|---|---|---|
| Prompt files in the repo, released through a registry with eval scores | **use** | the subject of this chapter; boring and effective |
| Prompt-management platforms (stored prompts with versions and labels, called by ID; several observability vendors and model providers offer them) | **use as a mirror, not the source** | the versioning is real; the risk is that edits and labels move outside the pull request, so the repository stops describing what runs. If the team wants the platform's viewer and playground, publish to it from CI |
| Automatic prompt optimisers (frameworks that search over instructions and examples against a metric) | **use, behind the gate** | they can find better wording than a person, and they overfit whatever metric and set you give them. Treat their output as a pull request from a very fast junior engineer: rendered, diffed, linted, scored on a set they did not optimise against |
| A coding agent writing and editing prompts | **use, review harder** | section 09.7 lists what agents get wrong here. The diff discipline matters more, not less, when changes are cheap |
| "Prompt engineering is dead, models just understand" | **hype, half true** | stronger models need less coaxing; they still need the field list, the page, the "unsure" rule and the product traps. The 2.1.0 trim was exactly this belief, and it cost Guntur |
| A million-token window, so send everything | **hype for extraction** | capacity is not attention (section 06.6) |
| One prompt per customer, copied and tweaked | **trap** | when Kaagaz has ten lenders, ten forks of the same prompt diverge; shared base templates with customer variants, versioned, is the product question Day 35 takes up |

## 8.2 Cost and latency

- **Order for caching.** Prompt caches match a stable prefix, so the instructions go first and the page last, as the
  system and user templates are split. That is in mild tension with the long-context advice (documents first, query
  last); for short per-page calls the cache wins. Day 12 owns the cache mechanics.
- **Calls per file.** Classify-then-extract makes about 45 calls a 40-page file. Run the classification calls in
  parallel within the provider's rate limits (Day 12's token bucket), or send a page thumbnail or the first lines only
  (`_untrusted_page_head.j2` sends six lines). Skip extraction for page types with no fields: terms, statements and
  blanks cost a classification and nothing else.
- **Escalation.** Pages the small tier is unsure of go to the large tier (`ESCALATE_BELOW`). Watch the escalation rate
  per release; a jump means a classification prompt regressed or a new branch's forms look different.
- **The bill follows the prompt.** One line in a partial included in forty calls is forty lines a file; tokens per
  file per tier in every release record let a reviewer see cost move.

## 8.3 Security and data

- **No secrets and no live PII in prompt files.** Prompt files are read by more people and tools than code is. Few-shot
  examples are masked pages from the training split, approved for the purpose (`"masked": true` is checked by a test).
- **Prompts are not secret either.** Assume the rendered instructions can be extracted by someone who controls a page.
  Nothing in a prompt should matter if read by an adversary; the rules that matter are in code (Day 11), and the
  defences against extraction and injection are Day 41's.
- **The rendered prompt is a compliance record.** Keep the "what the system is told to do" document per release with the
  same retention as the decisions it supported. The auditor's question in March 2027 is about a file processed in
  January.

## 8.4 Monitoring per release

Every metric on Day 19's dashboards should group by `release_id`: cost per file, latency, unsure rate, escalation
rate, correction rate. When a number moves, the registry history says whether a release changed, and the nightly drift
check says whether the model changed under it.

## 8.5 Who owns the prompts after handoff

Day 8's milestone M21 is Godavari's application-support engineer releasing a rule change without Kaagaz's help.
Prompts need the same by handoff (Day 28): Godavari's engineer opens a prompt pull request, reads the gate and rolls
back. A package that only its author can operate is folklore, not code.
