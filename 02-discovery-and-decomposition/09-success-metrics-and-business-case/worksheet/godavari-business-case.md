# Business case · Godavari Finance: loan-file intake and completeness

> One page for the COO and the CFO · Day 9 · Discovery week 4 · Version 1 · Every number is invented for the course; every number has its method in `godavari-baseline-pack.md` or `code/baseline_and_case.py`

**The decision asked for:** proceed to the pilot in two branches (weeks 7 to 10) and full rollout by
day 90, on the condition in the last section.

**Today, measured** (120 files, stratified by branch cluster and product, a fortnight with no
month-end or festival; 95 percent intervals): median **9.1 days** from signing to decision (8.7 to
9.7; the ops report's 9.2 is consistent); **4.6 analyst hours** a file, of which **1.59** are re-keying,
completeness checks and chasing branches; **28 percent** sent back (21 to 35); **6.4 days** of every
file's time is waiting in the queue to be opened; analysts are about **97 percent** busy. Also: **4.1
percent** of files are decided with a mandatory document missing, and **10.1 percent** of customers
withdraw.

**What changes:** the system removes most re-keying and checks completeness on the day the file
arrives. Fewer hours per file bring utilisation from about 97 to about 84 percent, which shortens the
queue from 6.4 days to about 1.2. Day-one detection means the branch's resend runs while the file
waits instead of after. The median falls to about **3.6 days**.

**The money (steady state, from year two, three of the seven planned hires made):**

| | Lakh a year |
|---|---|
| capacity: 4.2 hires not made at 9.13 lakh loaded | +38.3 |
| retention: about 44 loans a month kept that today walk away, at 24,000 lifetime contribution | +126.6 |
| cost: subscription 120, cloud in Godavari's AWS account 26, Godavari staff time 4 | -150.0 |
| **net** | **+15.0** |
| one-time: deployment fee 36, staff time and learning dip 9 | -45.0 |

On capacity alone the system costs 1.12 crore a year more than it saves, and the cost per file rises
from about 2,170 to 2,740 rupees. **This is a speed case, not a cost case.** It breaks even if faster
turnaround keeps **about 39 loans a month**: roughly three in ten of the customers who would be
sanctioned and walk away today.

**Not counted (listed, not added):** a lower risk of an RBI finding (expected 7.5 lakh a year at
invented odds; the compliance head's view matters more than the rupees); disbursement pulled
forward (5.8 crore arrives 5.5 days earlier once, worth about 0.9 lakh); branch staff time saved on
resends; the customer's time.

**What breaks it** (net a year, one input moved):

| Input | Low | Base | High |
|---|---|---|---|
| walk-aways kept per day of turnaround cut (0 / 6 / 9 percent) | -111.7 | +15.0 | +78.3 |
| contribution per loan (12,000 / 24,000 / 36,000) | -48.3 | +15.0 | +78.3 |
| capture share of addressable hours (30 / 60 / 70 percent; set by field accuracy) | -53.0 | +15.0 | +21.1 |
| cloud bill (40 / 26 / 12 lakh) | +1.0 | +15.0 | +29.0 |
| loaded cost per analyst (7.5 / 9.13 / 10.5 lakh) | +8.1 | +15.0 | +20.7 |

**Promised, as ranges:** the COO, median 3 to 4 days in the pilot branches by day 90 · the team leads,
addressable hours 0.5 to 0.9 a file and queue age under 2 days · the compliance head, no mandatory
document missed by the rules on the golden set and fewer than today's 4.1 percent decided incomplete in
production, monthly · branch managers, a missing-document notice the day the file arrives.

**What decides it:** (1) field-level accuracy on the mandatory fields of the golden set (Day 14) of
at least 90 to 95 percent, or the case is below break-even before the pilot starts; (2) the pilot's
withdrawal rate against the baseline's 10.1 percent, reported weekly; (3) the contribution per loan
confirmed in writing by finance this week; (4) who pays for serving, raised on the readout's
commercial page (Kaagaz's Day 3 model carries the same 26 lakh). Definitions are pre-registered in
`godavari-metric-definitions.md`.

Prepared by the Kaagaz AI FDE · For: the COO (sponsor), the CFO · Copy: the compliance head, Kaagaz's engagement lead
