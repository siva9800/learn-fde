# Is Godavari FDE-shaped? A one-page assessment for Kaagaz AI's CEO

> Engagement folder · Day 3 · Written before the contract is signed · Companion to `data/godavari-unit-economics.csv` and `code/unit_economics.py`
> Author: the FDE assigned to the Godavari Finance opportunity · Status: draft for the CEO's Friday review

## The question

The COO of Godavari Finance Ltd (Hyderabad NBFC, 1,200 staff, 300 branches, 40 credit-ops analysts
in Hyderabad and Vijayawada) has asked whether our platform can take loan turnaround from nine days
to three. The CEO has asked whether this engagement is worth committing one of our four FDEs for
twelve weeks on site, plus support afterwards. This page answers with the five qualifying questions
the published OpenAI FDE practice uses (as summarised in the 2025 and 2026 ZenML interviews), scaled
to a 40-person vendor, and with the model's numbers. Every rupee figure is invented for planning.

## The five questions

| # | Question (OpenAI's practice, scaled) | Answer | Evidence or assumption |
|---|---|---|---|
| 1 | **Is the problem FDE-shaped?** A general product, a specific gap, and the gap closable only by an engineer inside the customer's environment, data and rules | **Yes** | The platform reads documents; Godavari's gap is between "reads a salary slip" and "40 analysts process a 14-document file against a 2009 SOAP core system under RBI audit". The nine days live in an Excel tracker and a 6 pm batch job no demo can see (Day 0). Nobody closes that from Bengaluru |
| 2 | **Is there a realistic path to recurring revenue?** | **Yes, with one condition** | Subscription 1.2 crore a year renews only if the analysts use the system without us. Condition: the FDE's share of time falls below a tenth by month four, and the handoff bar (Day 28) is met. If the renewal depends on our engineer staying, it is not recurring |
| 3 | **Is there a product hypothesis, or a research-interesting problem?** | **Product hypothesis: yes. Research-interesting: no** | Hypothesis: every Indian lender needs intake classification, RBI-mandated completeness rules, a legacy-core integration layer with idempotency, and a review queue. We can name two more NBFCs in the pipeline with the same shape. Research: Telugu-English mixed forms are a data problem, not a research one. We take this on the product hypothesis alone, honestly |
| 4 | **Is the value large enough for a subscription?** (OpenAI: tens of millions to low billions; for Kaagaz: enough that 1.2 crore a year is an easy decision for the COO) | **Probably** | Nine days to three on a document-bound queue, 40 analysts at about 4.5 hours a file, 31 percent of files sent back at least once (figures the engagement later measures on Day 9). If the hours alone are worth more than the subscription, the COO's number is a bonus. Assumption until Day 9 measures the baseline |
| 5 | **Would we take it if it were pure services?** | **No, and we have said so** | The COO's second call raised a branch CRM for follow-ups. No other customer wants Godavari's CRM; we would be a services firm for a year. Declined (below). The rest of the scope is product work |

Four yes or probably, one honest no. The engagement is FDE-shaped on the product hypothesis.

## The numbers (from `code/unit_economics.py`, 36 months, invented)

| Scenario | Revenue | FDE cost | Revenue over FDE cost | ARR per FDE head at month 36 |
|---|---|---|---|---|
| A: no renewal | 1.56 cr | 0.24 cr | 6.5x | none live |
| B: renews three years | 3.96 cr | 0.36 cr | 11.0x | 12.0 cr |
| C: B plus two lenders buy the pattern | 8.56 cr | 0.77 cr | 11.1x | 12.0 cr |
| D: the services alternative (custom build, then two more) | 5.44 cr | 4.50 cr | 1.2x | 0.5 cr |
| B1: we say yes to the branch CRM (FDE full-time 36 months) | 3.96 cr | 1.80 cr | 2.2x | 1.2 cr |

Kaagaz's own floor is revenue at least three times FDE cost over three years. (This is our bar, not
a published one; Ramp publishes the measure, not a number.) Scenarios A to C clear it; the renewal
alone is worth about 1.75 crore of contribution in years two and three on a tenth of an FDE. Saying
yes to the branch CRM takes the same contract below the floor. The services alternative needs five
engineers at peak for a fifth of the ratio.

## What we will not build

**Godavari's branch CRM.** The COO asked whether we could also give branch managers a screen to track
customer follow-ups (calls made, documents promised, visits). We will not build it. Reasons, in the
order we will give them: it is not our product and no other lender would buy ours; a CRM vendor or
Godavari's own IT team does it better; and it would keep an FDE on site for a year doing work that
leaves nothing behind for the next customer. What we will do instead: expose each loan file's status
and the missing-document list through an API so any CRM, or the existing tracker, can read it. That
is product work, and the next lender will want it too.

## What the engagement needs to be true by week 13

- The FDE's time on Godavari is at or below 20 percent and falling to a tenth by month four.
- Three named patterns are in the product backlog: intake classification for scanned Indian loan
  files, RBI completeness rules as signed deterministic code, the SOAP integration layer with
  idempotency.
- A second NBFC has seen the Godavari walking skeleton (Day 20) and asked for a deployment estimate.

If none of the three is true by week 13, we are in scenario B1 whatever the invoice says, and the
CEO should ask why.

## Recommendation

Take the engagement: a subscription at 1.2 crore a year, a fixed deployment fee of 36 lakh for twelve
weeks on site, the branch CRM declined in writing, and the week-13 test above in the contract review.
Discovery (Days 4 to 10) will revise the value question; nothing it finds should move the first,
second or fifth answers.
