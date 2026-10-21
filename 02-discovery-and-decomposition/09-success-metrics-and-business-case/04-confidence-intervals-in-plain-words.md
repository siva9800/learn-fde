# 04 · Confidence Intervals in Plain Words

> Day 9 · Section 4 of 14 · [Chapter overview](README.md) · Previous: [03 · Measuring the baseline](03-measuring-the-baseline.md) · Next: [05 · Hours into rupees](05-hours-into-rupees.md)

---

## 4.1 Why 9.2 is not a number yet

"9.2 days" from one quarterly report is a measurement with three things missing: a definition (whose
clock, section 03.2), a population (which files), and a sense of how much it would move if you
measured again. Without the third, you cannot tell a real change from noise. If the pilot branches
show 8.6 days next month, did anything happen? You cannot say unless you know how much 9.2 wobbles on
its own.

A **confidence interval** is the honest way to write that wobble down. In plain words: *if we drew
many samples like this one, by the same method, and computed an interval from each, about 95 in 100
of those intervals would contain the true value for the whole frame.* You will usually say it more
loosely to a COO: "our best estimate is 9.1 days, and the true figure for that fortnight's files is
very likely between 8.7 and 9.7". That loose version is fine in a readout. Do not say "there is a 95
percent chance the true value is in this interval" in front of a statistician, who will correct you;
do not let the correction stop you writing intervals.

What an interval does not cover: a wrong definition, a frame that dropped files, or a counter who
judged "present" differently. Those are **bias**, and no amount of sample size fixes them. The interval
is only about the luck of the draw. That is why section 03 spent so long on the frame and the form.

## 4.2 The three intervals the pack uses

You need three, and the script computes all of them with the standard library.

| Quantity | Example | Interval method | In one sentence |
|---|---|---|---|
| a mean | analyst hours per file | normal approximation: estimate plus or minus 1.96 standard errors, combined across strata by their weights, with the finite population correction | the spread of the hours, divided by the square root of the sample size, tells you how far the average can wander |
| a proportion | send-back rate | the same, with the spread of a yes-or-no variable | a rate is the mean of a column of ones and zeros |
| a median | turnaround | **bootstrap**: resample the sampled files with replacement inside each stratum 2,000 times, take the median each time, and keep the middle 95 percent of those medians | if the sample is a fair miniature of the frame, re-drawing from it mimics re-drawing from the frame |

Why the median for turnaround and not the mean? Turnaround has a long right tail (files sent back
twice, a branch that never answers). One file of 30 days moves the mean and barely moves the median.
The board already reads a median, so the baseline matches it. Report the mean as well, in the
appendix, because the CFO's arithmetic (days saved times loans) uses means.

The **finite population correction**, (1 minus n/N) per stratum, accounts for having seen a real
share of each stratum; with 120 from 700 it narrows the intervals by about 9 percent. Leave it in.

## 4.3 What sample size buys you

The script shows the effect directly on Godavari's frame:

```text
Why one number is not a baseline yet:
  20 files picked at random            median 8.6 days, interval 8.0 to 11.4
  120 files, stratified                median 9.1 days, interval 8.7 to 9.7
```

Twenty files, a team lead's "quick check", give an interval more than three days wide: a pilot at
8.0 days could not be told from no change. 120 stratified files give one day. The 20-file interval is
also lopsided (8.0 below, 11.4 above), which the bootstrap shows honestly for a skewed quantity.

## 4.4 Reading intervals against each other

Three rules cover almost every conversation you will have.

1. **The report's number inside the hand count's interval** means the report is consistent with what
   you counted. All three of Godavari's are inside (9.2 in 8.7 to 9.7; 4.5 in 4.5 to 4.7; 31 percent
   in 21 to 35). Do not "correct" the report to 28 percent; say "consistent, with the definition
   caveats".
2. **A rare event has a wide interval.** 4.1 percent decided with a document missing, interval 0.9 to
   7.2. Five files in 120 is not enough to pin a rate that small. If the compliance head needs a tight
   number (she will), count that one column for all 700 files: checking four documents is about five
   minutes a file, under 60 hours, and turns an estimate into a census.
3. **Before and after**: a pilot interval of 3.2 to 4.1 against a baseline of 8.7 to 9.7 is a result;
   8.2 to 9.4 is not, however the slide is coloured. Day 37 owns the full comparison; the overlap
   check is the first sanity test.

## 4.5 Subgroups

Personal loans from Guntur are 2 of the 120 files; a number for that cell alone is close to
meaningless. Report by product (17 to 47 files) or cluster (17 to 23) with intervals, never by cell.
If the Guntur branch manager needs Guntur, count Guntur completely; it is small.

## 4.6 The words for a COO

> "The report's 9.2 days holds up. We counted 120 files, drawn at random across every branch cluster
> and product, from a fortnight with no month-end and no festival. Our estimate is 9.1 days, and the
> true figure for those files is very likely between 8.7 and 9.7. Anything the pilot shows below
> about 8.5 is a real change; anything above it, we will not claim. The count also found that six of
> the nine days are files waiting to be opened, which is where the plan aims."

Four sentences: the number, the method, the interval in plain words, and what the interval means for
the claim we will make later. The last sentence is the one that earns trust: you have told him in
advance what you will not claim.

## 4.7 Key takeaways

- An interval writes down the luck of the draw; it says nothing about a wrong definition or frame.
- Three intervals cover the pack: normal for means and rates, a stratified bootstrap for the median.
- Twenty files give a three-day-wide interval at Godavari; 120 stratified give one day.
- Rare events need a census of the one column that matters, not a bigger sample of everything.
- Tell the sponsor in advance what change you will not claim.
