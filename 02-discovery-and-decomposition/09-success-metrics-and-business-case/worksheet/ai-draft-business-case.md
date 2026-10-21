# AI draft: Godavari business case (for exercise 3.1; do not use as the answer)

> Produced by a coding agent from the Day 4 memo, the Day 6 interview notes and the prompt "write a
> one-page business case for the COO". It reads well. It contains at least ten problems. Find them
> before reading the solution in section 13.

## Executive summary

Kaagaz AI's intelligent document platform, powered by a state-of-the-art LLM with 98 percent
extraction accuracy, will cut Godavari's loan turnaround from 9.2 days to 3 days and deliver annual
savings of **4.9 crore**, a payback of under three months on the 1.2 crore subscription.

## Baseline

The ops report gives a median turnaround of 9.2 days, 4.5 analyst hours per file and a 31 percent
send-back rate. To validate this, we reviewed 25 recent files from the Kukatpally branch's SFTP scans,
which showed a median of 8.9 days, confirming the report. Files withdrawn by customers were excluded,
as they do not represent completed work. A full baseline will be measured after deployment, once the
system's logging is available.

## Benefits

| Benefit | Calculation | Annual value |
|---|---|---|
| analyst time saved | 40 percent productivity uplift (industry studies) x 4.5 h x 16,800 files x 300 rupees | 0.91 crore |
| full automation of intake | the platform automates the analyst workflow end to end, freeing 4.5 h a file x 16,800 x 300 | 2.27 crore |
| faster disbursement | 6 days earlier x 24 crore disbursed a month x 12 months x 12 percent yield / 365 | 0.57 crore |
| avoided RBI penalties | one avoided KYC penalty of up to 2 crore a year | 2.00 crore (conservatively counted at 1.15) |
| **total** | | **4.9 crore** |

## Costs

The subscription is 1.2 crore a year. Infrastructure is included in the Kaagaz platform fee. No
additional Godavari resources are needed beyond a short training session.

## Targets

- Turnaround: 3 days across all branches by day 90.
- Compliance: zero missed documents in production.
- Accuracy: 98 percent.

## Next steps

Metric definitions will be finalised with the COO after the pilot, once we see which measures best
reflect the value delivered.
