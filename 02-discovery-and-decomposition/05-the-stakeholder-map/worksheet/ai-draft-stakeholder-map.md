# AI draft: Godavari stakeholder map (for exercise 3.1; do not use as the answer)

> This map was produced by a coding agent from the Day 0 to Day 4 notes and the brief "draw the
> stakeholder map for the Godavari engagement". It is well formatted and reads confidently. It
> contains at least ten problems. Find them before reading section 11's solution. The same rows are
> in `ai-draft-stakeholders.csv`; the script catches some of the problems, not all.

## Summary

Godavari Finance's AI transformation has strong executive sponsorship from the CTO and a committed
champion in Lakshmi, who has been appointed by leadership to lead adoption. The main stakeholder
risk is user resistance, which will be addressed through a training session at launch. Security
sign-off will be obtained at UAT in week 8.

## Stakeholder register

| # | Stakeholder | Role | Power | Interest | Their view | Success metric | Engagement plan |
|---|---|---|---|---|---|---|---|
| A01 | CTO | executive sponsor | 5 | 5 | loan processing is slow and needs AI | turnaround days | weekly steering committee |
| A02 | Users (loan officers and analysts) | end users | 4 | 5 | loan processing is slow and needs AI | turnaround days | training session at launch |
| A03 | Lakshmi | champion | 5 | 5 | loan processing is slow and needs AI | turnaround days | appointed champion by the CTO; demo in week 4 |
| A04 | Head of AI | co-sponsor | 4 | 5 | we need an LLM platform across all 300 branches | number of branches live | weekly steering committee |
| A05 | CISO | approver | 2 | 1 | security sign-off happens at UAT | checklist signed | inform at UAT in week 8 |
| A06 | IT helpdesk | support | 1 | 1 | raise a ticket | tickets closed | inform at launch |
| A07 | Branch staff | end users | 1 | 1 | loan processing is slow and needs AI | app downloads | inform at launch |

## Power-interest analysis

All key stakeholders are in the "manage closely" quadrant, which indicates strong alignment. The
CISO and IT helpdesk are low power and low interest and can be informed at the appropriate
milestone. No conflicts between stakeholders were identified; everyone agrees that loan processing
is slow and needs AI.

## Conflict resolution

Where stakeholders disagree, the CTO as executive sponsor will make the final decision.

## Recommendation

Proceed with the RAG chatbot deployment to all 300 branches, with Lakshmi leading adoption and
security sign-off at UAT.
