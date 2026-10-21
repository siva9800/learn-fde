# 02 · The Five Steps: One Method, Three Sources, No Technology Until the End

> Day 7 · Section 2 of 16 · [Chapter overview](README.md) · Previous: [01 · Why decomposition](01-why-decomposition.md) · Next: [03 · Step 1: clarify the goal and the trade-off](03-step-1-clarify.md)

---

## 2.1 The steps and what each one produces

The method in this course is the one the published interview guides describe (the Harvard FAS 2026
guide lists exactly these five, and the Palantir-focused guide at fdeinterviews.com folds them into
four), aligned with what the FDE playbooks say the job does in the first weeks. Each step has a
question, an output you can write down, and a failure that shows up if you skip it.

| Step | The question | The output (one table in the worksheet) | What goes wrong if you skip it |
|---|---|---|---|
| 1 · Clarify | What exactly is the goal, and what is being traded for it? | the goal as a number with a date; the trade-off and who decides it; the constraint that cannot move; your assumptions | you optimise the wrong thing (speed when the auditor wanted accuracy), or the right thing in the wrong unit |
| 2 · Stakeholders and metrics | Who decides whether this worked, and what number would each accept? | one row per stakeholder: role, want, metric, fear | the sponsor is happy and the operators ignore it; or the blocker you never met vetoes it in week ten |
| 3 · Map the inputs | What data exists, in what shape, owned by whom, how fresh, how reachable, and what is missing? | one row per input, plus the list of data that does not exist yet | you discover in month three that the tracker is the real state, or that branch managers may not see each other's files |
| 4 · Decompose and sequence | What are the independent pieces of work, and which unknown must be retired first? | workstreams with value, risk, dependencies, owner, and an order | the security review starts in week ten; integration is "plumbing" left for the end |
| 5 · Walking skeleton | What is the thinnest end-to-end slice that proves the whole path works? | one row per layer: what is thin, what is stubbed, what it proves | a polished component that cannot be connected; integration risk surfaces last |

The order matters. Step 2 needs step 1's goal to attach metrics to. Step 3 needs step 2's people to
name owners. Step 4 needs step 3's gaps to score risk. Step 5 needs step 4's workstreams to take a thin
slice of each. Skip a step and the ones after it rest on a guess.

## 2.2 The rule that makes it work: no solution before step five

Here is the rule in one line: **you may not name a model, a database, a framework or an architecture
until step five, and when you do, it must be the thinnest thing that could possibly work.**

This is not a stylistic preference. It is what the round scores and what the job rewards, for one
reason: a solution named early anchors everything after it. Once "an LLM with RAG" is on the table, the
stakeholder list becomes "who will use the chatbot", the inputs become "documents to index", and the
workstreams become "ingestion, embeddings, retrieval, UI". The real inputs (a SOAP API with no
idempotency, an Excel tracker that is the true state, AD groups that decide who sees what) never get
written down, because nothing in the chatbot story needed them.

The published guides describe the anti-pattern in almost the same words: "jumping to a technical
proposal in the first minute" (Harvard), "designing before scoping" and "reaching for a model first"
(fdeinterviews.com), "a solution looking for a problem" (Day 4's chatbot trap). It is the single most
common reason candidates are rejected and, on the job, the single most common reason a prototype is
built for the sponsor's version of the problem.

> **The "LLM with RAG" test.** If your first sentence about a problem contains the words LLM, RAG,
> agent, vector, fine-tune, OCR, or the name of a cloud service, you have failed the round in the
> interviewer's notes before you finished the sentence. Not because those things are wrong (Godavari's
> skeleton uses extraction and will later use retrieval), but because you chose them before you knew
> the trade-off, the people, or the data. The fix is mechanical: say the five step names out loud and
> start with step one.

## 2.3 How the three sources line up

You will see the method described slightly differently in different places. They are the same method;
it helps to see the mapping so none of them confuses you in an interview.

| This course (Day 7) | Harvard FAS 2026 guide | fdeinterviews.com (Palantir) | The FDE discovery playbooks |
|---|---|---|---|
| 1 · Clarify the goal and trade-off | "Clarify the problem: confirm the actual goal and what is being optimized" | "Gather context and frame the scope: the user, the current metric and target" | Scope: the operational pain, who feels it, "the specific human whose day gets better" |
| 2 · Stakeholders and metrics | "Identify stakeholders and success metrics: who would count the project as a success" | part of framing: the user and the metric | Interview 8 to 10 stakeholders; "how would you know it worked" |
| 3 · Map the inputs | "Map the inputs: what data exists, its shape, its owner, and its freshness" | "the state of the data"; "data as it actually is, including likely join failures" | "Inspect the data path": which systems generate inputs, which schemas conflict, where fields are incomplete |
| 4 · Decompose and sequence by risk and value | "Decompose into subproblems: workstreams sequenced by risk" | "Propose a layered architecture: ingestion, then visibility, then optimisation, so you can discuss sequencing" | phase gates with exit criteria; eval co-design by week three |
| 5 · Walking skeleton | "Propose a walking-skeleton MVP, then iterate: the thinnest end-to-end version first" | "Cut a thin slice and justify it: the smallest deployment that delivers value on its own" | a narrow "first release" with a decision point and a safety boundary |

Two things the Palantir guide adds that this course folds into steps 4 and 5: **address operational
constraints out loud** (outages, stale data, access control, what happens when operators ignore the
tool) and **raise adoption without being asked**. On Godavari, both land in the enablement workstream
and in the skeleton's human-in-the-loop row.

## 2.4 The method on one page

Before the detail, here is the whole thing applied to Godavari in the shortest form it can take. Section
08 expands every cell; this is what you should be able to say in two minutes.

| Step | Godavari, in one line each |
|---|---|
| 1 · Clarify | Median turnaround 9.2 days to 3 to 4 in pilot branches by day 90; the trade-off is speed against the field-level error rate the RBI auditor accepts; PII stays in India; the core system's data model does not change. |
| 2 · Stakeholders | COO (turnaround days), 40 analysts (hours per file, send-backs), team lead (files per analyst per day), CISO (passed review, VPC in Mumbai), compliance head (field accuracy, zero completeness misses), core-system owner (zero duplicates), RBI auditor (an audit trail), branch managers (files accepted first time). |
| 3 · Inputs | Scanned PDFs on nightly SFTP (no page index, 31 percent incomplete); the 2009 SOAP API (no idempotency, quarterly sandbox); the Excel tracker (the real state, no timestamps); AD groups (branch isolation); WhatsApp photos (not allowed); RBI KYC rules (deterministic); historical decisions (no field-level ground truth). |
| 4 · Workstreams | Integration and the security review first (slow, outside our control, highest risk); evals with senior analysts from week one; extraction as the value; completeness rules as low-risk, high-value deterministic code; enablement last but planned from the start. |
| 5 · Skeleton | Two-wheeler loans, Kukatpally branch, SFTP scans only: PDF in, 12 fields and a completeness result out, an analyst approves on a plain page, a record lands in the core-system sandbox with an idempotency key, every step measured. Week three. |

Notice what is absent: no model name, no database, no cloud service. All of those are decisions that
step five's skeleton will force in week one of building (Day 11 onwards), and by then every one of them
is constrained by something in rows 1 to 3.

## 2.5 The two habits that run through every step

**State assumptions and revisit them.** Every step produces assumptions ("the nine days are mostly
waiting", "the analysts will accept a queue"). Write them down, say them out loud, and come back to them
when a later step produces evidence. The guides list "state assumptions aloud and revisit them" as a
scored behaviour, and on the job the assumption you did not write down is the one that costs a rewrite.

**Narrate.** In the interview, the method is spoken, not written; the interviewer scores the thinking
they can hear. On the job, the method is written, in the worksheet (section 12) and then the discovery
document (Day 10), because the people who must sign it were not in your head. Section 09 is the spoken
version; section 12 is the written one. Practise both.

## 2.6 Key takeaways

- Five steps, each with a question and a written output: clarify, stakeholders and metrics, map the
  inputs, decompose and sequence, walking skeleton.
- No technology until step five. The anti-pattern has a name in every guide and it is the most common
  rejection.
- The steps are ordered because each one feeds the next; skipping one leaves the rest resting on a guess.
- State assumptions, revisit them, and narrate. The interview scores what it can hear; the customer
  signs what it can read.
