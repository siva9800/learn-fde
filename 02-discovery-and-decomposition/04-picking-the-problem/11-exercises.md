# 11 · Exercises

> Day 4 · Section 11 of 12 · [Chapter overview](README.md) · Previous: [10 · Interview questions](10-interview-questions.md) · Next: [12 · Further reading](12-further-reading.md)

---

Ten exercises in three levels, including one "review this AI-written memo". Solutions are folded
under each one. The exercises marked **(tested)** use the chapter's script, run on Python 3.14.3
(October 2026) from the chapter folder, and the outputs shown are real. Learning mode: do the
scoring and the writing yourself; use an AI assistant as the sceptical reviewer or the sponsor
(section 8.6's prompts), not as the author. Try first, then open.

## Level 1: warm-up

**1.1 Problem or solution?** Each line is a candidate as a customer phrased it. Mark it "problem" or
"solution", and for the solutions rewrite it as the cost it might be hiding.

(a) "An AI assistant for our relationship managers."
(b) "Our field officers re-enter the same visit report into two apps."
(c) "Automate invoice processing with OCR."
(d) "Claims sit for four days waiting for a surveyor's photo."
(e) "A copilot over our HR policies."
(f) "Every dealer order is re-typed from a WhatsApp message into SAP."

<details><summary>Solution</summary>

(a) solution; the cost, if any: "relationship managers spend N hours a week looking up product
terms, and give wrong answers M percent of the time", neither counted. (b) problem: re-key. (c)
solution; the cost: "N invoices a month, each keyed by hand in T minutes, with E percent rejected".
(d) problem: wait. (e) solution; the cost: "employees email HR N questions a month; HR answers in D
days". (f) problem: re-key, and a rework rate if the message is misread. Three of the six are
product categories wearing a problem's clothes. (Sections 03.1, 05.2.)

</details>

**1.2 Which column loses?** For each Godavari candidate, name the single column or gate where it
lost most, without looking at the sheet: (a) title deeds; (b) the branch chatbot; (c) collections
summaries; (d) KYC and re-KYC; (e) the tracker.

<details><summary>Solution</summary>

(a) frequency (120 a month), then all three gates. (b) measurability 1 and the baseline gate. (c)
the data-owner gate (the dialler vendor) and sponsorship 2 (a sponsor, no operator). (d) the
operator gate (branch staff and a compliance head who said not this year), with blast radius 5
behind it. (e) the operator gate: the analysts use it every day and do not want it replaced. (Section
04.6.)

</details>

**1.3 Four parts.** Each is a proposed problem statement. Say which of the four parts (unit of work,
cost as the customer's number, cause as the floor sees it, no solution) it is missing or violating.

(a) "Loan processing is slow and should use AI to get faster."
(b) "New loan files take nine days because the analysts are slow."
(c) "New loan files take a median of nine days from receipt to decision because intake is manual
and a third of files are incomplete, and we will fix it with an extraction model in twelve weeks."
(d) "Branch staff wait for answers to policy questions."

<details><summary>Solution</summary>

(a) no unit, no number, and a solution ("use AI"). (b) has a unit and a number; the cause is the
sponsor's accusation, not the floor's observation; the operators would not sign it. (c) all four
parts and then a solution and a date added; cut the last clause. (d) a unit and a cause of sorts,
no number (nobody counted the waiting), which is why it fails the baseline gate. (Section 06.1.)

</details>

## Level 2: apply

**2.1 Score it yourself (before reading the chapter's CSV).** Copy the catalogue table from section
03.2 into a fresh CSV with the template's columns, score all eight rows against section 04's anchors,
answer the three gates, run the script, and then diff your scores against
`data/godavari-candidates.csv`. For every cell that differs by two or more, write one line saying
which reading of the evidence you now think is right.

<details><summary>What to look for</summary>

The usual differences: C5's frequency (the 2,000 is a guess; 4 is generous, 3 is defensible); C2's
pain (4 on waiting, or 3 on hours); C8's operator gate (yes if you read "use it daily" as "want
it", no if you read Day 0's "fear losing it"); C3's sponsorship (2 because the compliance head is a
blocker here, not a sponsor). If your ranking's winner is not C1 or the winner is not stable, your
anchors drifted toward the demo or the sponsor; re-read 04.2.

</details>

**2.2 Predict the output (tested).** Before running, say what changes and what does not in the
printed ranking when you run `python code/score_candidates.py data/godavari-candidates.csv --rate 450`.

<details><summary>Solution</summary>

Nothing in the scores, ranks, gates, warnings or sensitivity changes; only the rupee column, by a
factor of 1.5. Real output, first three rows:

```text
   1  C1   Loan-file intake and completeness check       93     2,100    9.4 lakh  COO (kickoff)
   2  C2   Income verification from bank statements      67       675    3.0 lakh  COO (kickoff)
   3  C7   Credit-memo drafting                          65       700    3.1 lakh  COO (kickoff)
```

The rate is kept out of the score on purpose: it is a Day 9 number, and a ranking that moved when
it changed would be a ranking built on a placeholder. (Section 04.5.)

</details>

**2.3 Break it, then fix it (tested).** The COO insists the chatbot has a baseline ("the branches
tell me they call all the time") and asks you to mark all three of its gates yes and its
measurability 4. Do it in a copy of the CSV, run the script, and explain the result to him.

<details><summary>Solution</summary>

Real output with C5's gates flipped and measurability set to 4:

```text
== flipped.csv: 8 candidates, 4 pass all three gates ==

rank  code candidate                                  score  hours/mo   rupees/mo  raised by
--------------------------------------------------------------------------------------------
   1  C1   Loan-file intake and completeness check       93     2,100    6.3 lakh  COO (kickoff)
   2  C2   Income verification from bank statements      67       675    2.0 lakh  COO (kickoff)
   3  C7   Credit-memo drafting                          65       700    2.1 lakh  COO (kickoff)
   4  C5   Branch chatbot for policy questions           65       200    0.6 lakh  COO (kickoff)
```

Even with every gate waved through and the measurability doubled, the chatbot ties for third on
score and loses the tie on hours (200 a month against the memo's 700), and intake is still 28 points
clear. The honest sentence to the COO: "even if we take your word for the baseline, it comes
fourth; with a real count it might come second, which is why the count is worth a month." Then
restore the CSV: a gate answered from the sponsor's description is not a gate. (Sections 04.4, 06.5.)

</details>

**2.4 The sensitivity line, forced.** Edit a copy of the CSV so that the winner is no longer stable:
change as few cells as you can until the sensitivity section reports at least one weighting under
which a different candidate wins. Which cells did you change, and what would the memo have to say?

<details><summary>Solution</summary>

It takes more than you expect, because C1 scores at or above C2 in every column, and a candidate
that is dominated column by column cannot win under any weighting. C2 has to overtake C1 somewhere.
The cheapest route is five cells on C2 (income verification): frequency 5, pain 5, measurability 5,
data 5 and blast radius 1 (so safety 5 against C1's 3). Real output with those five changes:

```text
   1  C1   Loan-file intake and completeness check       93     2,100    6.3 lakh  COO (kickoff)
   2  C2   Income verification from bank statements      93       675    2.0 lakh  COO (kickoff)
   3  C7   Credit-memo drafting                          65       700    2.1 lakh  COO (kickoff)

sensitivity: who wins under other weightings?
  equal weights          C2  <-- the winner changes
  ignore frequency       C1
  ...
  ignore sponsorship     C2  <-- the winner changes
  triple data            C2  <-- the winner changes
  triple safety          C2  <-- the winner changes
  ...
  winner C1 is changes under 4 weighting(s): the pick is a judgement call, say so in the memo
```

The two tie at 93 and C1 wins the tie on hours; under four of the thirteen weightings C2 wins.
The memo would then have to say: "under equal weights, or ignoring sponsorship, income verification
wins; we pick intake because the sponsor and the operators both asked for it and because
verification waits on the documents intake catches on day one." Notice what you had to claim to get
there: a wrong income is harmless (blast radius 1) and thirty bank formats are fully available
(data 5). Neither is true. That distance from the evidence is what "stable" was telling you.
(Section 04.3.)

</details>

**2.5 The conversation, out loud (recorded).** Play section 06.5 with another person or with an
agent using section 8.6's sponsor prompt. The COO pushes three times: the board saw it; the
analysts' problem is boring; a competitor has one. For each push, your answer must contain a number,
a reason and an alternative he can act on. Listen to the recording and mark each answer.

<details><summary>What a strong run contains</summary>

Board: "the board saw a demo; by day 90 I want them to see a number, and intake is the candidate
with a number today." Boring: "boring to watch, 2,100 hours a month to do; the analysts asked for
it in their own words, and nobody asked for the chatbot." Competitor: "if their branches count their
calls, they know something we do not; let Kukatpally count for a month and we will know too."
(Sections 06.4, 06.5.)

</details>

## Level 3: stretch

**3.1 Review this AI-written memo and find what is wrong.** Read
[`worksheet/ai-draft-problem-selection-memo.md`](worksheet/ai-draft-problem-selection-memo.md).
It was produced by an agent from the same notes you have, and it reads well. Find at least nine
problems: wrong facts, wrong method, wrong reasoning, missing pieces. Write each as one line with
the section that explains it.

<details><summary>Solution (eleven problems)</summary>

1. **The problem statement is a solution** ("deploy an LLM-powered assistant ...") with a target date
   and a technology; none of the four parts is present as a problem. (06.1, 06.2)
2. **It picks two, then seven in phases**: the assistant in weeks one to six, intake in weeks four to
   twelve, and a twelve-month programme. One problem for the twelve weeks; Day 8 scopes. (01.4)
3. **The chatbot's frequency 5 rests on "an estimated 12,000 policy questions a month"** that nobody
   counted; the COO's own guess was 2,000, and that was a guess. (04.5, 05.2)
4. **Its measurability 4 is "we will instrument the assistant from day one"**: a baseline counted
   after the system exists, by people who want it to look good. The no-baseline trap in new words.
   (05.4)
5. **Data 5 because "the model handles PDFs with 97 percent accuracy as shown in the sales demo"**:
   the demo deck's number is about salary slips (Day 0), not circulars, and data availability is
   about owners and access, not model accuracy. (04.2)
6. **Risk 1 because "the assistant only answers questions"**: a wrong policy answer to a branch is a
   wrong loan; blast radius is the consequence of being wrong, not whether the system writes
   anywhere. (04.2, 08.6)
7. **KYC sponsorship 5 because the compliance head "will be delighted"**: she said not this year;
   the operators are branch staff nobody asked. The sponsorship anchor needs an operator and
   product fit. (04.6)
8. **No gates at all.** Five candidates that fail a gate are scored and ranked as if scoreable; the
   reasons for declining them never appear. (04.4)
9. **The tracker as "a separate quick win in weeks two to three since the analysts clearly need a
   better tool"**: the analysts did not ask for a replacement; forty people keep it alive because it
   is the only true state. Folded into intake as a constraint, or the pick fails in month four.
   (08.4)
10. **The value section prices Indian analyst hours at "USD 85,000 per analyst per year (the 2026
    FDE posting median)"** and then declares OpenAI's tens-of-millions threshold cleared "once the
    twelve-month programme is complete". Wrong rate, wrong currency, wrong role, and a published
    threshold used literally instead of scaled to the vendor. (02.4)
11. **"Obtain the recordings from the dialler vendor, which should be straightforward"**: a data owner
    outside the customer, a contract nobody has read, and open DPDP questions, waved through. The
    owner gate exists for exactly this. (04.4, 05.3)

Two more if you want them: intake "scores higher in total" and is still not picked, with "build
trust with the lower-risk assistant" as the reason (trust is built by moving a number, 07.2); and
there is no "not now, because, and instead" for anything, so the sponsor has nothing to point back
to in week ten (06.4, 07.3).

</details>

**3.2 Your own catalogue.** Take a team or a company you know (your current employer, a family
business, a college office). Write its catalogue of candidate problems, at least six rows, with real
or honestly estimated volumes and hours; answer the three gates from what you actually know; score
against the anchors; run the script; write the memo from the template, including the sentence and
the "not now" lines. Then give the memo to someone who works there and ask whether they would sign
the sentence.

<details><summary>What a strong result contains</summary>

At least one candidate declined on a gate with an "instead" the organisation could do next month; a
pain warning answered in words rather than by changing the hours; a sentence the person who does
the work recognises; and a row that came from watching the work rather than from the person in
charge. If every gate is yes and the winner is the thing the boss mentioned first, go back to the
floor. (Sections 03, 04, 06, 08.)

</details>
