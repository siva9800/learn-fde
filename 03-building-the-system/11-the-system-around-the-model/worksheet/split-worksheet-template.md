# The split worksheet · template

> Day 11 · Copy this for any customer. Fill it after discovery (Day 6) and decomposition (Day 7), before the
> first line of model code. One line per cell. If a cell needs a paragraph, the thinking is not finished.

**Customer:** · **Workflow:** · **Author:** · **Date:** · **Reviewed with (rule owner, system owner, operator lead):**

## 1. The eight boxes, in the customer's words

| # | Box | The customer's name for it | Code or model | Owner | Thin version for the skeleton |
|---|---|---|---|---|---|
| 1 | Ingestion | | | | |
| 2 | Retrieval | | | | |
| 3 | Model | | model | | |
| 4 | Rules | | code | | |
| 5 | Verification | | code | | |
| 6 | Interface | | | | |
| 7 | Integration | | code | | |
| 8 | Observability | | | | |

## 2. Every rule, sorted

| Rule, as the owner says it | Bin (regulatory / policy / judgement) | Owner | Source | Written down? | Rule id |
|---|---|---|---|---|---|
| | | | | | |

Test for policy versus judgement: can the owner say it as a sentence with no "usually", "normally" or "it
depends"? If not, can it be written if the owner spends a week? If yes, schedule the week.

## 3. Every judgement, with its check

| Judgement | What the model proposes, with what evidence | The deterministic check on it | Who decides on disagreement |
|---|---|---|---|
| | | | |

## 4. The envelope

| Check after the call | Applies to | Fails closed to |
|---|---|---|
| schema and types | | |
| grounding (quote on the cited page) | | |
| value supported by its quote | | |
| confidence against a measured threshold | | |
| formats and checksums | | |
| cross-field and cross-document | | |
| reference lookups | | |
| signed rules | | |

## 5. Where the people are

| Person | Box | Decides | What happens without them |
|---|---|---|---|
| | | | |

## 6. Failure modes, and who notices first

| Failure | Direction (too much to model / to code) | Who notices first | When | The control |
|---|---|---|---|---|
| | | | | |

## 7. Sign-off

| Artifact | Signed by | Date | Fingerprint or version |
|---|---|---|---|
| rule sheet | | | |
| thresholds | | | |
| architecture page | | | |
