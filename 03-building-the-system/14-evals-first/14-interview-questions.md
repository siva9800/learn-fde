# 14 · Interview Questions

> Day 14 · Section 14 of 16 · [Chapter overview](README.md) · Previous: [13 · Mistakes and debugging](13-mistakes-and-debugging.md) · Next: [15 · Exercises](15-exercises.md)

---

Twelve questions in the forms they take in FDE loops: some are asked directly in the technical or hiring-manager
screen ("how do you evaluate an LLM feature?"), many arrive as follow-ups in system design ("how will you know it
works on their files?") or in client simulation ("we need 100 percent accuracy"). Answer out loud first, then compare.
Section numbers point to the full explanation.

## The method

**Q1. A customer wants you to automate extraction from their loan documents. When do you build the evaluation?**

Before serious development, in the first two weeks, in parallel with discovery and the first slice. I find the
people who do the work and are trusted to be right, write a labelling guide with them, and have two of them label
100 to 200 real files drawn deliberately from the hard cases, with a written adjudication rule. That set is the
definition of done for every change after it: OpenAI's FDE team calls it eval-driven development and treats LLM work
without verification as unfinished. Building it first is also the only way to fit trust-building into a 90-day
engagement; in the published Morgan Stanley case, the pipeline took 6 to 8 weeks and the evaluation and trust work
about four more months. (Sections 01.2, 01.4.)

**Q2. How big should a golden set be?**

Sized by the smallest stratum I must decide about, not by the total. 100 to 200 examples is typical; each slice a
decision depends on (a pilot branch, a language, a product) needs at least about 20 examples so its interval is
narrower than the differences I care about. Bigger is limited by the experts' time: on the course's engagement, 200
files labelled twice took about 300 analyst hours. What the set cannot see because it is too small, production
monitoring and a growing set must. (Sections 02.2, 05.8.)

**Q3. Walk me through how you would label it.**

A guide first, written with the experts, with rules for the cases that cause disagreement (where each field is read
from, what to do when a document is missing, "cannot read it, do not guess"). Two experts label every file
independently, recording fields, documents, the decision with reasons, and their steps with page numbers and time.
I measure agreement before adjudicating: raw agreement for values after a registered normaliser, Cohen's kappa for
decisions. Disagreements go to named people by a written rule: field readings to two team leads, rule questions to
the rule owner. Nobody from the vendor adjudicates. Then the first thirty files usually change the guide.
(Section 03.)

**Q4. What is inter-annotator agreement, and what is kappa for?**

How often two independent labellers give the same answer. It is the ceiling on any claim about the system: if two
experts agree on 92 percent of a field, "99 percent accurate" on that field means nothing yet. Kappa is for
categorical decisions, where raw agreement misleads: if 95 percent of files are complete, two people agree a lot by
both saying "complete". Kappa subtracts the agreement expected by chance from people with those habits. (Section 03.5.)

## What to measure

**Q5. What metrics would you report for an extraction system?**

Field-level accuracy over all mandatory fields with a registered normaliser, exact beside it; the confidently wrong
rate (wrong and not flagged), also as unflagged precision and as a file-by-file list; the flag rate; page
classification and document detection as diagnostics; completeness recall and precision against the rule owner's
labels; cost and latency per file. Every one with its count and a 95 percent interval, for every stratum that varies
or decides something. (Section 04.)

**Q6. Which metric matters most, and why?**

For a lender: the rate of confidently wrong answers. A wrong-but-flagged field costs a minute of review; a wrong
field that looks exactly like a right one reaches the core system, because busy reviewers check what they are told
to check. It is also what the analysts' trust rests on: they stop re-typing a field only when unflagged values are
almost always right. Accuracy without this number can rise while the system gets more dangerous, for example when a
prompt change makes the model more confident and no more correct. (Sections 04.3, 07.5.)

## Judges and statistics

**Q7. When is LLM-as-judge acceptable?**

For open-ended outputs, on criteria code cannot check, at a volume people cannot read, and only after it has been
calibrated against the experts on held-out examples and passes a written bar, with recalibration on every change to
the judge model, its prompt, the rubric or the writer. First I move every criterion code can check into code; in an
extraction system that is most of them. On the course's branch notes, code checks coverage, citations, invented
documents and PII, and the judge answers only "is this plain enough for a branch clerk". (Sections 06.1, 06.2, 06.5.)

**Q8. How do you calibrate a judge?**

Binary rubric written with the experts; a calibration set and a held-out set labelled by them with critiques; tune
the judge on calibration only; report on held-out: agreement, kappa, the share of failures it catches and of passes it
passes, separately, plus bias probes (own-family against other writers; order swapped for pairwise). Write the bar
before looking; a judge below it is advisory. In the course's run, a holistic 1-to-10 judge agreed with people 79
percent of the time but caught only 35 percent of the notes they failed; the rubric judge caught all of them.
(Section 06.6.)

**Q9. Your new prompt scores 97.7 percent and the old one 97.5. Is it better?**

Probably not, and I would not decide from those two numbers. Both runs are on the same files, so I compare cell by
cell: only fields that changed carry information. If five went right-to-wrong and eight wrong-to-right, a fair coin
explains it. I would also look at every stratum and at confidently wrong fields, because a 0.2-point overall gain can
hide a ten-point loss on one field. (Section 05.6.)

## The gate and the set over time

**Q10. Design a CI regression gate for prompt changes.**

On every pull request that can change what the system reads or decides: run the candidate on the golden test split,
compare with main's stored baseline cell by cell. Fail on the business case's accuracy floor, on any completeness
miss, on a one-directional paired regression in any stratum (exact test on the changed cells, with a minimum net
count), and on a rise in confidently wrong fields. Refuse to compare different file sets or truth versions.
Thresholds in a versioned policy agreed with the experts, set above the noise floor of the unchanged model re-run on
the development split. Measure the gate's own false-alarm and miss rates, and keep a known-bad candidate in CI that it
must fail. In the course's run, an average-only gate let a trimmed prompt through ten times in ten; the stratified gate
caught it every time with no false alarms in 30 reruns. (Section 07.)

**Q11. How do you keep the golden set from leaking into the system?**

Few-shot examples, threshold tuning and noise floors come only from a development split. A mechanical check scans
every prompt template, example file and retrieval or training corpus for the test split's identifiers before scoring,
and refuses to run if it finds one; names are weak matches because real people share names. Develop on development,
run the test split when a change is ready, count the looks, and keep a sealed slice for milestones. (Section 08.1, 08.2.)

**Q12. A new model version is released. How do you decide whether to switch?**

Same files, same truth-file version, same normaliser, same policy; run both models inside the same envelope and
rules; read the field and stratum comparison, cost and latency, not the headline; the experts decide any trade in
writing; then refit the confidence thresholds and recalibrate any judge whose model changed. The eval set is what
turns "should we switch?" into a one-page report. (Section 08.4.)

## Quick-fire

- What are the four outcomes for a field? Correct; correct but flagged; wrong but flagged; confidently wrong.
- Wilson or the school formula near 100 percent? Wilson.
- Why a file-level bootstrap? Fields in one file share their errors.
- Who adjudicates a rule question? The rule owner, against the signed rules; never the vendor.
- What should a gate that has never failed make you think? That it cannot fail.
- Where do few-shot examples come from? The development split only.
- What does the eval export to the vendor contain? Scores and masked rows; no identifiers.
- Two experts agreed and were both wrong: how would you find out? A double-keyed audit; reading confidently-wrong rows label first.
