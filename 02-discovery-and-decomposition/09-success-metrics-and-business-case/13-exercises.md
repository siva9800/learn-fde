# 13 · Exercises

> Day 9 · Section 13 of 14 · [Chapter overview](README.md) · Previous: [12 · Interview questions](12-interview-questions.md) · Next: [14 · Further reading](14-further-reading.md)

---

Twelve exercises in three levels, including a predict-the-output, a break-it-then-fix-it and a
"review this AI-written business case". Exercises marked **(tested)** were run on Python 3.14.3
(October 2026) against the chapter's script, and the outputs quoted are real. Learning mode: do the
reasoning and write the code yourself; use an AI assistant as a sceptical CFO or as a tutor on the
statistics, not as the author. Try first, then open the solution.

## Level 1: warm-up (no code)

**1.1 Place it on the ladder.** Business, operational or system? (a) median days from signing to
decision; (b) completeness-check recall; (c) queue age at 10 am; (d) operating cost per file;
(e) share of fields routed to review; (f) files decided with a mandatory document missing; (g) analyst
hours per file.

<details><summary>Solution</summary>

(a) business. (b) system. (c) operational, and leading. (d) business. (e) system. (f) business (risk);
its system partner is completeness recall, measured on the golden set, while (f) is measured on every
decided file. (g) operational. (Section 02.)

</details>

**1.2 Capacity or cash?** For each sentence, say whether it describes capacity or cash, and what would
make it cash. (a) "The system frees 12,600 analyst hours a year." (b) "Godavari hires three analysts
next year instead of seven." (c) "Each analyst handles six more files a week." (d) "Month-end overtime
falls from 400 hours to 150." (e) "We save 57 lakh at 456 rupees an hour."

<details><summary>Solution</summary>

(a) capacity; cash only through (b) or (d). (b) cash: 4.2 hires at 9.13 lakh, about 38 lakh a year.
(c) capacity, spent on speed or on growth. (d) cash, if overtime is paid. (e) capacity times a rate
called a saving (05.4); rewrite it as (b).

</details>

## Level 2: the script

**2.1 Predict the output (tested).** In `OPS_REPORT`, change "analyst hours per file" from 4.5 to 3.5
and rerun. Before running, write down what the hours row of section 3 will print.

<details><summary>Solution</summary>

```text
analyst hours per file              3.5         4.6      4.5 to 4.7   no
```

The hand count does not change (it does not read the report), and 3.5 is now outside the interval, so
the consistency column says `no`. This is also check 6 in section 10.7: if the column had stayed `yes`,
the comparison would be broken.

</details>

**2.2 A smaller sample (tested).** Set `SAMPLE_SIZE = 60` and rerun. (a) Predict what happens to the
interval widths. (b) The run prints hours per file 4.2 (4.0 to 4.5) and a send-back rate of 19 percent
(10 to 28). Because the data is synthetic you can compute the frame's true values: mean hours 4.55,
send-back rate 30.3 percent, median turnaround 9.4. Explain what you see. (c) Why not go below 60?

<details><summary>Solution</summary>

(a) Every interval widens: median 8.0 to 9.3 (was 8.7 to 9.7), hours 4.0 to 4.5 (was 4.5 to 4.7),
send-back 10 to 28 percent (was 21 to 35).

(b) Both intervals miss the true value. A 95 percent interval misses about one time in twenty, and
these two misses are one event: the draw happened to hold few sent-back files, which take an hour
longer, so hours fell with them. Also, 48 of the 60 files are floors of two, and a variance estimated
from two files is unreliable. At 120 every interval contains the true value.

(c) Below 48 the floors alone exceed the sample, and the allocation cannot be proportional at all. If
you must sample fewer files, use fewer strata (product only), not a smaller floor.

</details>

**2.3 Break it, then fix it (tested).** Replace `weighted_median` with a plain median that ignores the
weights: `lambda pairs: statistics.median(v for v, _ in pairs)`. Predict the change in the median
turnaround row, run it, and explain why the damage is small here and when it would be large.

<details><summary>Solution</summary>

```text
median turnaround, days             9.2         9.1      8.7 to 9.6   yes
```

Almost nothing changes: proportional allocation makes every weight close to 700/120. Weights matter
when strata are sampled unevenly (a floor in a tiny stratum, or deliberate over-sampling of phone
photos). Restore them; "the number did not move" is not proof the code is right.

</details>

**2.4 A census of the rare column (tested).** The sample's "decided with a document missing" is 4.1
percent (0.9 to 7.2). Write a few lines that compute it for all 700 frame files using Day 7's
generator, and the recall of today's human check.

<details><summary>Solution</summary>

```python
day7 = load_day7()          # the importlib loader from the script
frame = day7.make_loan_files(700, random.Random(day7.SEED))
incomplete = [f for f in frame if not (f.has_pan and f.has_address_proof and f.has_income_proof and f.has_photo)]
slipped = [f for f in incomplete if not f.sent_back]
print(len(slipped), len(slipped) / len(frame), 1 - len(slipped) / len(incomplete))
```

Real output, rounded: 33 files, 4.7 percent, recall 86.5 percent: inside the sample's interval (0.9 to
7.2) and far tighter, for under 60 hours of checking. (Section 04.4.)

</details>

**2.5 Break the queue model (tested).** Run the case with `capture=0.30` and `hires=0` together. What
does the model say, and what does it mean?

<details><summary>Solution</summary>

Utilisation 102 percent, a median of 47 days, net minus 84 lakh. Above 100 percent the queue has no
steady state; the 47 is the capped formula, not a forecast. The meaning is real: low accuracy plus
cancelled hires is worse than today, so decide hires after Day 14's result, and add a guard that
prints "queue unbounded" at utilisation 1.

</details>

## Level 3: judgement

**3.1 Review this AI-written business case.** Read
[`worksheet/ai-draft-business-case.md`](worksheet/ai-draft-business-case.md). Find at least ten
problems and, for each, name the section of this chapter that fixes it.

<details><summary>Solution</summary>

(1) a model accuracy figure in the headline, from no measurement (02.2, 08.5); (2) the ops report as
the baseline, no interval or method (03, 04); (3) a convenience sample of 25 easy SFTP scans from one
branch (03.5, 08.3); (4) withdrawn files excluded (03.4); (5) "baseline after deployment", which is
impossible (03.1); (6) a vendor-study 40 percent uplift (09.2); (7) the 300 salary rate (05.2);
(8) all 4.5 hours automated, when 1.59 are addressable and only a share is captured, and the first two
benefit lines count the same hours twice (05.3); (9) hours times a rate called savings (05.4);
(10) disbursement annualised (06.3); (11) an unsourced 2 crore RBI penalty in the headline (06.1);
(12) no cloud, staff time, learning dip or deployment fee (06.4); (13) point targets and "zero in
production" (07.5); (14) definitions after the pilot (08.1); (15) model names on a COO's page (Day 10).
If you found ten, you have the habit. Raise 9 and 14 with the COO first.

</details>

**3.2 The payback question (tested).** At base, the one-time cost (45 lakh) takes about three years to
recover. What share of walk-aways kept per day of turnaround cut would recover it in one year?

<details><summary>Solution</summary>

You need a net of about 45 lakh a year. From the run: 7.0 percent gives 36.1; 7.4 gives 44.5; 7.5
gives 46.6. So about **7.5 percent per day**, which at 5.5 days cut keeps about 41 percent of today's
walk-aways. Write it as the second line under the break-even: "it pays back in a year if faster
turnaround keeps about four in ten of the customers who leave today."

</details>

**3.3 Pre-register queue age.** Write the full definition of queue age with every field from section
08.2's table, including what happens at the switch-over from the core's timestamp to the review
screen's.

<details><summary>Solution</summary>

Hours from SFTP arrival to first opening; mean and 90th percentile, weekly; every new file from the
pilot branches, resubmissions separate, no exclusions; the core's record-creation time before launch,
the review screen's after, both kept for a fortnight and the difference reported; baseline 6.4 days;
target under 2; a change claimed after four consecutive weeks under 3; guardrail: fields corrected
per file must not rise; signed by both team leads.

</details>

**3.4 Role-play: the CFO cuts the contribution (tested).** The CFO says: "your 24,000 a loan is too
high; our finance team says 12,000." Use the script to answer, and write what you say.

<details><summary>Solution</summary>

At 12,000 the net is **minus 48 lakh** a year and the break-even rises to **77.5 loans a month**, about
57 percent of the would-be-sanctioned customers who walk away today. What you say: "Your number replaces mine. At 12,000 the case needs us to keep more than half of the
customers who leave, which I would not promise. Either we measure walk-aways in the pilot before the
full rollout, or Kaagaz and the COO agree terms that reflect the risk. I will update the case today."
Then version it and tell the COO before the CFO does (07.3; Day 30).

</details>

**3.5 Transfer: the hospital (no solution).** Krishna District Hospital (the Day 42 capstone) wants
insurance pre-authorisation "faster". Write, without any numbers: the customer's clock; the frame and
its source; two strata and why; three metrics on each rung; one guardrail pair; and the one lever you
expect to be unmeasured, with the sentence you would use for its break-even.
