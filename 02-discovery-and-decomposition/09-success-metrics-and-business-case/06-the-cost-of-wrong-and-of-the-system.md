# 06 · The Cost of Being Wrong, and the Cost of the System

> Day 9 · Section 6 of 14 · [Chapter overview](README.md) · Previous: [05 · Hours into rupees](05-hours-into-rupees.md) · Next: [07 · The one-page case](07-the-one-page-case.md)

---

## 6.1 Three costs of a wrong decision

Hours are the easy side. The side that matters to a lender is what a wrong decision costs. There are
three kinds at Godavari, and each needs a method, not a guess.

| Wrong decision | How it happens today | How to price it | Godavari (invented inputs) |
|---|---|---|---|
| **a bad loan** | a file sanctioned on a missing or misread income proof (Day 6, A8) | expected loss = extra probability of default x exposure x loss given default | a 2.2 lakh loan that defaults with 60 percent loss costs about 1.3 lakh; what matters is how much the error raises the default rate, which only the credit team can estimate |
| **an RBI finding** | a file decided with a mandatory KYC document missing; 4.1 percent of files in the sample | expected cost = chance of a finding in an inspection x (penalty + remediation drive + management time) | invented: 25 lakh a finding, 30 percent odds a year at today's slip rate, 7.5 lakh a year expected |
| **a customer lost** | the customer withdraws while the file waits; 10.1 percent in the sample | lifetime contribution of the loan (interest margin after funding cost, credit cost and servicing) | invented: 24,000 rupees a loan; Godavari's finance team replaces it |

Three notes on method. **Use expected values and show the inputs**: "a finding could cost crores" is
a fear; "30 percent odds of a 25 lakh finding is 7.5 lakh a year" can be argued with. RBI publishes
each monetary penalty as a press release (section 14), so the compliance head can give a defensible
range; the remediation drive usually costs more than the penalty. **Keep risk out of the headline**
unless every input is defensible; list it. **The lost customer is the strongest lever and the least
measured**: the baseline counts who walks away, not why, so until the pilot measures it this lever
is an assumption with a break-even (07.3).

## 6.2 The system's own wrong decisions

The system will also be wrong, and its two kinds of error have very different prices. This is where
the business case meets the completeness check's precision and recall (section 02.5).

| The system says | The truth | What it costs | Who pays |
|---|---|---|---|
| "complete" | a mandatory document is missing (a recall miss) | the RBI-finding line above, per file | the compliance head, the auditor's report |
| "incomplete" | the file was complete (a precision miss) | a needless send-back: about three days for the customer, half an hour of chasing, a higher chance the customer walks | the branch manager, the customer, the walk-away line |
| a field value | the value is wrong and nobody notices | the bad-loan line, if it is an income or obligation field | the credit team |
| "unsure, please review" | the value was right | a few minutes of analyst time | the capture share |

The asymmetry is the design decision. A recall miss costs a finding; a precision miss costs three
days; an unnecessary review costs minutes. So the completeness rules are deterministic code the
compliance head signs (Day 11), set to favour recall, and uncertain fields go to review rather than
being guessed (Day 18). The business case is where you show *why*: the rupee column of this table.

## 6.3 Disbursement pulled forward: once, not every year

The most tempting line in a lending business case is "we disburse X crore five days earlier every
year". It is wrong in a way worth understanding.

When turnaround falls by 5.5 days, the files in the pipeline at the switch-over are decided sooner,
which pulls about **5.8 crore** of disbursement forward **once**. After that loans flow at the same
rate, each still earning interest for its full term. The gain is the margin on 5.8 crore for 5.5
days, about **0.9 lakh**. It sounds like crores a year because it is quoted in disbursement. The
annual value of speed is the walk-away line: loans that happen because the customer stayed.

## 6.4 What the system costs Godavari

Count everything Godavari pays, in its own accounts, including its own people.

| Line | One-time | Every year | Source |
|---|---|---|---|
| Kaagaz subscription | | 120 lakh | Day 3's price |
| Kaagaz deployment fee (twelve weeks on site) | 36 lakh | | Day 3's price |
| cloud in Godavari's AWS Mumbai account: compute, storage, model calls, logs, the VPC | | 26 lakh (range 12 to 40) | Kaagaz's sizing for about 20,000 files a year; Day 12 owns the cost budget, Day 21 the deployment |
| Godavari's own staff time | 9 lakh | 4 lakh | below |

Godavari's staff time (invented, at each person's loaded rate): one-time, about 9 lakh for labelling
the golden set (about 300 hours of Lakshmi and the senior analyst), the compliance head's rules, the
CISO's review, the core-system owner, the identity team, training, and the **learning dip** (two weeks
at reduced speed, 2.6 lakh of it); every year after, about 4 lakh for eval refresh, rule changes,
support and readouts.

The learning dip is the line most cases forget. Analysts are slower with a new screen for a week or
two, and it lands exactly when the COO is watching most closely. Put it in the case, and put it in
Day 29's first readout before anyone sees it in the numbers.

**What is not on Godavari's bill: the FDE's time.** It is Kaagaz's cost, inside the deployment fee
and the subscription. Do not add it to Godavari's case; do make sure Kaagaz's model carries it.

## 6.5 Reconciling with Kaagaz's side

Day 3 modelled the engagement from Kaagaz's side. The two ledgers must agree line by line, and the
FDE is the one person who sees both.

| Kaagaz's ledger (Day 3) | Godavari's ledger (this chapter) | Reconciled? |
|---|---|---|
| revenue: subscription 1.2 crore a year | cost: subscription 1.2 crore a year | yes |
| revenue: deployment fee 36 lakh in months 1 to 3; year-one revenue 1.56 crore | cost: 36 lakh one-time; year-one cash to Kaagaz 1.56 crore | yes |
| cost: FDE time (full-time 12 weeks, then a fifth, then a tenth) | not a Godavari line | yes |
| cost: serving at 22 percent of subscription (about 26 lakh a year) | cost: cloud in Godavari's account, about 26 lakh a year | **no: the same money is counted on both sides** |
| renewal (scenario B) assumed | renewal depends on this case being true | the link Day 37 tests |

The open line matters. Day 3 assumed Kaagaz pays for serving; the VPC in Godavari's AWS Mumbai account
(Day 8's plan, the CISO's conditions) bills compute and model calls to Godavari. Either Kaagaz credits
the infrastructure it no longer runs, or Godavari pays for serving twice. Prices are for Kaagaz's
engagement lead and the COO, on the Day 10 readout's commercial page; the FDE makes sure the question
is asked before the CFO finds it.

## 6.6 Key takeaways

- Price wrong decisions as expected values with visible inputs: a bad loan, an RBI finding, a lost
  customer.
- The system's two error types cost very different amounts; that asymmetry is the reason for
  deterministic, recall-favouring completeness rules and review routing.
- Disbursement pulled forward is a one-time timing gain worth about a lakh, not crores a year.
- The system's cost includes the customer's own staff time and the learning dip; the FDE's time is
  on Kaagaz's ledger.
- Reconcile both ledgers line by line. At Godavari the serving cost is counted twice until someone
  decides who pays it.
