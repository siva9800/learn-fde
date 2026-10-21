# AI draft: problem selection memo for Godavari Finance (for exercise 3.1; do not use as the answer)

> This memo was produced by a coding agent from the chapter's brief, the Day 0 notes and the COO's
> list. It reads well. It contains at least nine problems. Find them before reading section 11's
> solution.

## Summary

Godavari Finance presents seven high-value AI opportunities, and our document platform can address
all of them. Applying Atlassian's "frequent, painful, measurable" filter and OpenAI's threshold of
tens of millions of dollars in value, we recommend leading with the **branch policy assistant**
(chatbot) as the first deliverable, with loan-file intake as a parallel second workstream, and
scoping the remaining five as phases three to seven of a twelve-month programme.

## Problem statement

> Deploy an LLM-powered assistant over Godavari's policy circulars and loan documents so that
> branches, analysts and the collections team get instant answers, reducing loan turnaround from
> nine days to three within twelve weeks.

## The candidates, scored

| Candidate | Frequency | Pain | Measurability | Data | Risk | Sponsorship | Total /30 |
|---|---|---|---|---|---|---|---|
| Branch policy assistant | 5 | 5 | 4 | 5 | 1 | 5 | 25 |
| Loan-file intake | 5 | 5 | 5 | 4 | 3 | 4 | 26 |
| Collections call summaries | 5 | 4 | 4 | 4 | 1 | 4 | 22 |
| KYC and re-KYC automation | 5 | 4 | 4 | 4 | 2 | 5 | 24 |
| Credit-memo drafting | 5 | 3 | 3 | 4 | 2 | 4 | 21 |
| Income verification | 4 | 4 | 3 | 4 | 2 | 4 | 21 |
| Title-deed review | 2 | 3 | 2 | 3 | 3 | 4 | 17 |
| Excel tracker replacement | 5 | 4 | 4 | 5 | 1 | 2 | 21 |

Scoring notes: the policy assistant scores 5 on frequency because the 300 branches generate an
estimated 12,000 policy questions a month, and 5 on pain because each unanswered question delays a
loan. Its measurability is 4 since we will instrument the assistant from day one and have full
usage analytics within a week of launch. Data is 5: the circulars are PDFs and the model handles
PDFs with 97 percent accuracy as shown in the sales demo. Risk is 1 because the assistant only
answers questions and takes no actions. Sponsorship is 5: the COO specifically asked for it and the
board has seen it.

KYC automation scores 5 on sponsorship because the compliance head, as the owner of KYC, will be
delighted to have the manual checks removed.

Intake scores higher in total but is the slower path to visible value, and its blast radius (a
missed KYC document is an audit finding) argues for starting with the lower-risk assistant to build
trust.

## Value

At a fully loaded cost of USD 85,000 per analyst per year (the 2026 FDE posting median), the
collections and intake hours together are worth about USD 2.4 million a year, which clears OpenAI's
tens-of-millions threshold once the twelve-month programme is complete.

## Recommendation

Proceed with the policy assistant in weeks one to six and intake in weeks four to twelve, with the
Excel tracker replacement as a separate quick win in weeks two to three since the analysts clearly
need a better tool. Collections summaries follow in month four once we obtain the recordings from
the dialler vendor, which should be straightforward.
