# 11 · Interview Questions

> Day 18 · Section 11 of 13 · [Chapter overview](README.md) · Previous: [10 · Mistakes and debugging](10-mistakes-and-debugging.md) · Next: [12 · Exercises](12-exercises.md)

---

Twelve questions in the forms FDE loops ask them: the system-design round ("how would the operator know it is
wrong?"), the hiring-manager screen, and the client simulation. Answer out loud first, then compare.

**Q1. Your extraction model is 97 percent accurate. Why not just show the values with a confidence score?**

Because the 3 percent is not spread evenly and the score does not find it. On our golden set the wrong values that no
check flagged had confidences of 0.88 to 0.97, above most correct values in the same field; a threshold cannot
separate them. Every one was obvious in the source line: a capital "I" for a "1" in a price. So the screen puts the
source next to every value, labels the score as one signal, and routes on deterministic checks plus a confidence
band fitted per field. (Sections 02.3, 03.)

**Q2. How do you set confidence thresholds?**

From the customer's golden set, per field and per kind of source page, fitted on the development split and confirmed
on the test split. Fit: the lowest threshold with enough development fields above it, all correct, never below the
lowest confidence development showed correct. Confirm: any wrong auto-accepted value on test withdraws that cell; a
failed confirmation never moves a threshold, because that would be tuning on test. Then price it in analyst minutes
and in wrong values per band. (03.2 to 03.4.)

**Q3. The pooled error in your auto-accept band is 1.07 percent, under your 1.5 percent bar. Ship it?**

No. Six of the nine errors were one field, the on-road price, and that field feeds the margin rule and the core-system
record. The bar applies per cell with zero tolerance on the test split; pooled numbers are where a failing field
hides. Where does 1.5 percent come from? The senior analyst's own keying error on the golden set: an accepted field
must be no worse than a careful person typing it. (03.3.)

**Q4. What is the difference between auto-accept and auto-approve?**

Auto-accept is per field: no action needed on that field. Auto-approve is per file: no human decision. At Godavari the
compliance head decided, for the auditor, that a named analyst decides every file in the first 90 days, so there is no
auto-approve at all; auto-accepted fields are spot-checked after approval. (03.1.)

**Q5. How do you stop reviewers from rubber-stamping?**

Design and measurement. Design: information rather than verdicts, highlights that mean something, one forced look per
file at the riskiest field with approval disabled until it is done, the analyst's name on the record. Measurement:
time on field and on the forced field per session, approval bursts, override rates over weeks, and random blind spot
checks of the accepted fields. Two signals before a session is "suspected", because experts are fast. (04.)

**Q6. How do you choose the forced-look field?**

Impact times risk. Impact is agreed with the eval owners: a value that feeds an eligibility rule or the record of
money or identity scores highest. Risk is the upper bound on that cell's error rate, from development data only. Cells
that failed test confirmation go on a standing list and win. The trade-off: the same field every time becomes
routine, so the standing list is temporary until the underlying check is fixed. (04.2.)

**Q7. How many spot checks are enough?**

Enough to see the error rate you care about. To see at least one error at a true 1 percent rate with 95 percent
probability you need about 299 fields, n = ln(0.05) / ln(0.99). At the pilot's rate that is about six weeks, so you
start on day one, report an upper bound rather than "zero errors", and never stop. (04.3.)

**Q8. The sceptic on the floor says "it will never read handwritten Telugu". What do you do with that?**

Write it into the policy as a test. Handwritten Telugu cells are never auto-accepted until their own test fields bound
the error at or below the agreed bar; with zero errors that needs 253 fields, which the golden set reaches as it grows.
She gets a date and a number, not a promise, and she is one of the two people who label the set. (03.3; Day 14.)

**Q9. A rule fired. What does the operator need to see?**

The rule's id and kind (regulatory, policy, or an engineering check), its version and sign-off status, the field it
concerns, and the clause of the customer's own policy it rests on, quoted from the register and in force on the
decision date. Never a citation found by similarity, because the worst citation is a superseded one quoted perfectly.
(02.4.)

**Q10. Explain the same decision to a branch manager and to an RBI auditor.**

The branch manager wants what to fix, why, and the clause, the same day, in two lines. The auditor wants who decided,
when, on which exact pages, under which rules version, what the machine did and what the person did, and whether the
person looked. Both come from the same decision record; neither needs model prose. (06.3, 06.4.)

**Q11. What happens to an analyst's correction?**

It is captured with both values, a reason from a fixed list, who and when, and the model, rules and bands versions.
Content corrections and "unsure" answers go to the development split as single-labeller candidates for adjudication;
never to test. Every correction, format-only ones included, goes to the dashboards. (06.1, 06.2.)

**Q12. Client simulation. The COO: "Every field reviewed costs 68 hours a month. Your bands cost 43. The old
thresholds cost 30. Why not the cheapest?"**

"The old thresholds leave about 65 wrong values a month that nobody is told to check, at your volume of 1,400 files.
The bands cost about 12 more analyst hours a month, roughly 5,500 rupees, and on your analysts' 150 files they left
none. One wrong price sanctioned and found by the auditor in March costs more than a year of that. As the pilot timer
replaces my assumptions and the spot checks bound the accepted band, I will bring you the same table with measured
numbers, and if a field earns automation back, the cost comes down." (03.4.)
