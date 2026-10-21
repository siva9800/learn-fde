# 01 · Why Evals First: The Number Both Sides Accept, and the Work That Is Not Done Without It

> Day 14 · Section 1 of 16 · [Chapter overview](README.md) · Next: [02 · The golden set](02-the-golden-set.md)

---

## 1.1 Two Fridays

Friday 4 December 2026 is the week-6 go or no-go (milestone M12, [Day 8](../../02-discovery-and-decomposition/08-scoping-the-first-90-days/README.md)).
The COO will ask one question, and it is written on the milestone card: "Is accuracy on your analysts' files at the
agreed bar, and are the rules and the security approval signed, so two branches start on Monday?" There are two
ways to answer it.

The first FDE opens a laptop and says: "On the files we tested, extraction is about 97 percent accurate." The COO
asks which files. "A good sample from both cities." The senior analyst from Hyderabad, the sceptic of
[Day 5](../../02-discovery-and-decomposition/05-the-stakeholder-map/README.md), asks who decided what "accurate"
means. "We compared against what the documents say." She asks to see the files it got wrong. There is a pause,
because nobody kept a list. The compliance head asks whether the rules ever missed a mandatory document. "Not that
we saw." The meeting ends with "let us look again next week", which on this calendar means the pilot starts after
the change freeze, which means January.

The second FDE says: "On 150 files your own analysts labelled, Lakshmi and the senior analyst independently, with
Srinivas and the Vijayawada team lead settling every disagreement against the labelling guide, field-level accuracy
is 97.5 percent, with a 95 percent interval of 96.7 to 98.1. Handwritten Telugu fields, which you asked us to
report separately, are 96.0 percent, and 46 percent of them are flagged for review rather than trusted. The signed
rules flagged all 76 incomplete files; zero misses. Seven fields were wrong and not flagged. Here they are, file by
file. Six are one field, the on-road price, misread in a way we can show you, and one is a label we think is
wrong and have sent back to the team leads." Then she hands the senior analyst the list.

Nothing about the model is different between the two meetings. What is different is that the second FDE built the
measuring instrument first, with the customer's experts, and can answer every follow-up question from it. This
chapter is about building that instrument, keeping it honest, and using it to decide every change that follows.

(The numbers in the second answer are this chapter's real output on synthetic files with Day 11's stub model. The
real week-6 report runs the real model on real files inside the Hyderabad building. Section 11 is careful about the
difference; so is the business case.)

## 1.2 What "evals first" means

An **eval** (evaluation) is a repeatable measurement of how well an AI system does its job, on examples where the
right answer is known. A **golden set** is the collection of those examples with their right answers, labelled by
the people whose judgement defines "right". **Evals first** means you build the golden set and the measurement
before serious development, not after the demo.

OpenAI's forward deployed engineering team describes this as **eval-driven development**. In the published summary
of their practice (two interviews in the ZenML LLMOps database; section 16), the team "creates detailed evaluation
sets before significant development begins", works with customer experts to record **trajectories** ("the sequence
of actions an expert would take") and turns them into labelled evaluation sets, and holds a simple standard: "no
LLM-based code is considered done until verification exists." The summary puts the same idea another way:
"LLM-based applications aren't complete without evaluations verifying efficacy." And it names the long-term
benefit: "As models improve, the evaluation framework provides a consistent way to measure progress."

That last sentence is the reason this chapter is called "first". A golden set built in week 2 is not a test you
run at the end. It is:

- **the definition of done** for every extraction, prompt and rule change from now until handoff;
- **the contract** between Kaagaz and Godavari: both sides agreed what is measured, on which files, labelled by whom,
  before anyone knew the score (Day 9 pre-registered the definitions for exactly this reason);
- **the only evidence your product team will accept** when you tell them a customer-specific fix should become a
  product feature ([Day 36](../../06-from-customer-to-product/36-feeding-product-and-research/README.md));
- **the instrument for model choice**: when a new model version arrives, you run the same 150 files and switch only
  if the numbers say so.

## 1.3 Why it matters for your career

Applied AI work (LLM application development, retrieval, evals, agents, guardrails) appears in 80 percent or more of
the 1,000 FDE job postings analysed in 2026 (CURRICULUM.md; the source is the getperspective.ai analysis, a vendor
source). Evals are the part of that bucket that separates engineers who have shipped from engineers who have
demoed. In interviews it shows up in three places:

- the **practical coding** round, where "how would you test this?" about an LLM feature is the follow-up to almost
  every task;
- the **system design** round, where the interviewer listens for whether you put measurement before the model
  ("how will you know it works on their files?");
- the **client simulation**, where a VP says "we need 100 percent accuracy" (Day 34 drills it) and the only good
  answer is a measured number, a definition, and a routing rule for the cases that are not certain.

On the job it is simpler. An FDE who cannot say how accurate the system is, on whose files, by whose definition,
will be outranked in every meeting by the customer's sceptic, and should be.

## 1.4 Morgan Stanley: the pipeline was the easy part

The case the course keeps returning to (Day 18 and Day 31 use it too) is OpenAI's work with Morgan Stanley's wealth
management division in 2023, the first enterprise deployment of GPT-4. As the ZenML summary of OpenAI's account
describes it: the technical pipeline (retrieval, guardrails, basic evaluation) took **6 to 8 weeks**; building
trust took roughly **4 more months** of pilots, user feedback collection and evaluation refinement; the FDE team
"worked closely with advisors to label data, verify outputs" and to build verification tools where confidence was
lower; the result was **98 percent adoption** among advisors. (OpenAI's own customer page for the story refused our
fetch on 21 October 2026, so the figures here are as summarised by ZenML and as cited in the Part 3 plan.)

Read the proportions: two months of building, four months of evaluating. The four months were not wasted on a
system that did not work. They were spent turning "it works" into "the advisors agree it works on their questions",
which is a different and harder claim. Godavari's calendar does not have four spare months; the pilot starts
7 December. The only way to fit is to start the evaluating in week 2, in parallel with the building, which is what
Day 8's plan did (the golden set reaches 30 files at M05 on 6 November, 100 at M09 on 20 November, 200 by M12).

## 1.5 Where this sits in the course

This chapter consumes what Part 2 and the first three Part 3 chapters produced, without re-teaching them:
[Day 6](../../02-discovery-and-decomposition/06-discovery-interviews/README.md)'s labellers, their conditions and the
180-file manifest from the hard cases; [Day 9](../../02-discovery-and-decomposition/09-success-metrics-and-business-case/README.md)'s
pre-registered definitions and the 90 to 95 percent bar the case depends on; [Day 10](../../02-discovery-and-decomposition/10-the-discovery-document/README.md)'s
risks R1 and R2, change C4 and decision D08; [Day 11](../11-the-system-around-the-model/README.md)'s intake package,
imported by path; [Day 12](../12-llm-apis-for-production/README.md)'s cost per file; and
[Day 13](../13-prompts-as-code/README.md)'s prompt releases, each of which now needs a score.

It sets up [Day 18](../18-verification-and-trust/README.md) (thresholds from this harness),
[Day 19](../19-observability-for-ai-systems/README.md) (the same metrics on a production stream),
[Day 27](../../04-deploying-into-their-world/27-reliability-in-their-production/README.md) (the golden set as a
production check) and [Day 36](../../06-from-customer-to-product/36-feeding-product-and-research/README.md) (the eval
set as the currency between field and product). **This chapter owns evals and golden sets for the course.**

## 1.6 The hard parts, named up front

Four things make evals harder than they look. Knowing them in advance is most of the defence.

1. **"Correct" is a decision, not a fact.** Is "Rs 1,25,000" the same as "125000"? Is the PAN on the form good
   enough when the PAN card is missing? Two careful analysts will disagree on a few percent of fields, and the
   disagreements are where the labelling guide is unfinished. Section 03 makes this concrete: before
   normalisation, Lakshmi and the senior analyst agree on 79.8 percent of field cells; after, 97.8 percent; the
   remaining 2.2 percent is the real work.
2. **Averages lie politely.** A prompt change that loses ten points on one field can move the overall number by half
   a point. Section 07 shows a gate that checks only the average letting exactly that change through, ten times in
   ten. Slicing by stratum is not optional.
3. **Small numbers wobble.** 150 files sounds like a lot until you slice it by branch and get 20 files each. A
   number without its interval and its count is a rumour. Section 05 gives you the two intervals you need and when
   each one lies.
4. **The thing measuring the model can be wrong too.** Labels have errors (one of the seven confidently-wrong
   fields in this chapter's baseline run is a label error, and the trimmed-prompt run surfaces a second). Judges have biases (the holistic judge in section 06 agrees
   with people 79 percent of the time, which sounds fine until you see it catches only 35 percent of the notes
   people failed). An eval you have not checked is a second unverified system.

This feels like a lot of statistics for an engineering chapter. It is less than it looks: two intervals, one
agreement score and one paired test, all in under a hundred lines of standard-library Python, and each is explained in
plain words before it is used. The judgement (what to measure, who decides "right", what to do when the number is
inconvenient) is the larger part, and it is the part that transfers to every customer you will work with.
