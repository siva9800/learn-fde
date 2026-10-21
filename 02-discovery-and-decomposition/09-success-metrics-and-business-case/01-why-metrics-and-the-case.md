# 01 · Why Success Metrics and the Business Case

> Day 9 · Section 1 of 14 · [Chapter overview](README.md) · Next: [02 · The metric ladder](02-the-metric-ladder.md)

---

## 1.1 The sentence that does not renew a contract

Picture Godavari in month seven. The system has run in every branch for four months. The COO's
board pack is due. Someone asks the question every renewal turns on: "what did it do for us?" The
analysts say it feels faster. Srinivas says his team chases branches less. The ops report says
turnaround is 4.8 days. Then the CFO asks three questions: 4.8 days compared with what, measured how?
Is the change from the system or from the two analysts hired in March? And what is 4.8 days worth in
rupees, set against the 1.2 crore a year?

If the FDE's answer starts with "we think", the renewal is now a negotiation about feelings, and
Kaagaz's Day 3 model (scenario B, the renewal) is a coin toss. If the answer starts with "the baseline
we measured in week three, by the method the COO and the compliance head signed, was 9.1 days with an
interval of 8.7 to 9.7", the conversation is about a number that both sides agreed to before anybody
had a reason to bend it.

This chapter is about the second answer. The work happens in discovery weeks two to four, months
before anyone asks.

## 1.2 Why this matters for your career

- **The teams that invented the role say so.** Atlassian: frequent, painful, *measurable*; OpenAI:
  agree how success is measured with the customer's experts before choosing a model (Part 2's
  sources). Without a measured change, an engagement is a demo with a delay (Day 4).
- **The interview asks for it.** "How would you know it worked?" follows step 2 of every
  decomposition ([Day 7](../07-decomposition/README.md)). "Accuracy" answers a different question;
  "median days from signing to sanction, baselined on a stratified sample, with field accuracy
  underneath" sounds like someone who has done it.
- **It is the FDE's commercial lever.** Kaagaz's economics depend on renewal (Day 3), and renewal
  depends on the customer's case being true. The FDE is the one person who sees both ledgers.

## 1.3 What the chapter does

It turns the COO's adjective into numbers: the metric ladder (02), the baseline by hand with
intervals (03, 04), rupees counted honestly on both sides of the ledger (05, 06), a one-page case with a
sensitivity table (07), and definitions signed before the pilot (08). The project (10) builds the
baseline pack and the case for the engagement folder, with a script that draws the sample from Day 7's
synthetic data.

## 1.4 What it does not do

It does not measure the result. That is [Day 37](../../06-from-customer-to-product/37-measuring-value-honestly/README.md),
which owns measured value in production: attribution, counterfactuals, the full catalogue of gamed
numbers, and the renewal conversation. Day 9 builds what Day 37 needs: a baseline with a method, a
definition signed before anyone had a reason to bend it, and a case that says in advance which
number will decide it. It also does not build the golden set ([Day 14](../../03-building-the-system/14-evals-first/README.md))
or the quality dashboard ([Day 19](../../03-building-the-system/19-observability-for-ai-systems/README.md)).
It decides what they must report.

## 1.5 The hard parts, named early

- **The result is less flattering than the pitch.** Godavari's honest case is thinner than "nine days
  to three pays for itself". Section 07 shows what to do: say so, compute the break-even on the lever
  not yet measured, and make it the pilot's question. It feels like losing; it is how you keep the
  COO's trust when the CFO checks.
- **Statistics anxiety.** Three ideas are enough (a frame, a stratified draw, an interval) plus the
  habit of writing the method beside every number. The script does the arithmetic.
- **Hours are not rupees.** Freed hours are capacity; they become cash only through hires not made,
  and they can be spent only once (section 05).

## 1.6 The picture to carry

UPI is the Telugu-audience analogy for the whole chapter. Nobody funded "convenient payments". NPCI
and the banks tracked transactions per day, the failure rate and the seconds per payment, and those
numbers are what moved and what got reported. "Faster loans" is the same kind of adjective. Day 9's
job is to find the transactions-per-day of loan intake, measure it before anything changes, and
agree in writing what it means.
