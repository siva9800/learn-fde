# 08 · Project: The Self-Assessment and the Gap Plan

> Day 2 · Section 8 of 12 · [Chapter overview](README.md) · Previous: [07 · Production concerns](07-production-concerns.md) · Next: [09 · Mistakes and debugging](09-mistakes-and-debugging.md)

---

## 8.1 The brief

Day 1 put the first artifact in the engagement folder: the one-page note on what a forward deployed
engagement at Godavari looks like. Day 2 adds two more, and they are about you as much as the customer:

1. the **two-week calendar** (section 05), already written and counted;
2. a **scored skills rubric** against the three buckets, with evidence per row, and the **gap plan** the
   script produces from it, which says where in this course to spend longest.

The second is the project. It belongs in the engagement folder because the engagement plan and the plan
for your own gaps are the same plan: if bucket 3 is your weakest, the Wednesday with Lakshmi is the
block you must not delegate; if bucket 1 is, the Thursday spike is.

**Files:**

| Path | What |
|---|---|
| [`worksheet/skills-rubric-template.md`](worksheet/skills-rubric-template.md) | the empty rubric: twenty rows, three buckets, the scoring definitions, the "where I will spend longest" block |
| [`worksheet/sample-rubric-ravi.md`](worksheet/sample-rubric-ravi.md) | a filled rubric for Ravi Teja, an invented backend engineer with four years at a Hyderabad payments startup |
| [`worksheet/ai-draft-rubric-priya.md`](worksheet/ai-draft-rubric-priya.md) | a rubric an AI filled from a CV; exercise 3.1 |
| [`worksheet/godavari-weeks-1-2-calendar.md`](worksheet/godavari-weeks-1-2-calendar.md) | the calendar from section 05 |
| [`code/gap_plan.py`](code/gap_plan.py) | reads a rubric, checks it, prints the plan, writes `data/<name>-gap-plan.md` |
| [`code/week_hours.py`](code/week_hours.py) | reads a calendar, checks the clock arithmetic, counts hours per bucket |

Everything was run on **Python 3.14.3** (October 2026), standard library only: no packages, no API keys,
no downloads. Run from the chapter folder:

```bash
python -X utf8 code/gap_plan.py worksheet/sample-rubric-ravi.md
python -X utf8 code/week_hours.py worksheet/godavari-weeks-1-2-calendar.md
```

## 8.2 Part A: score yourself

Copy the template, rename it, and score all twenty rows. The scoring definitions are the whole method:

| Score | Means | The test |
|---|---|---|
| **0** | never done it | you could not describe a time you did it |
| **1** | read about it, or did a tutorial or a course exercise | you can describe it; you have not done it on anything that mattered |
| **2** | did it once, or under someone else's ownership | you can name the system and what happened, but the decision or the on-call was someone else's |
| **3** | owned it in production, more than once, and can explain the failures | you can name the system, the result, and the time it went wrong and what you changed |

The rules the template enforces:

- **Evidence for every 2 or 3.** One line: a system, a thing you did, a result. "Strong Python" is not
  evidence; "own the settlement service, 40k lines inherited, typed, on call since 2024" is. The script
  counts a 2 or 3 with fewer than five words of evidence as a 1 and says why.
- **No bucket is all 3s.** Nobody has owned every row of a bucket in production; the script flags it.
- **Score what you have done, not what you could learn fast.** The rubric is for finding gaps; the
  course is where they close.

The twenty rows are the twenty skills the three buckets consist of, each mapped to the chapter that
teaches it (`TEACHES` in the script, following `curriculum/FOLDERS.md`). Read them as a syllabus as
much as a test.

## 8.3 Part B: the gap plan, on Ravi

Ravi Teja is invented: four years of backend at a Hyderabad payments startup, strong in Python and SQL,
an AWS account of his own, one hackathon with an LLM, never run a customer meeting. The script on his
rubric:

```text
== sample-rubric-ravi.md: 20 rows read ==

bucket                    mean  rows at 0/1  rows at 3
core engineering           2.0       2           2
applied AI                 1.0       4           0
customer-facing discovery  0.8       7           0

weakest bucket: customer-facing discovery; spend longest there (Part 2 and Part 5)

the gap plan, in the order to work it (weakest bucket first, lowest score first):
customer-facing discovery (mean 0.8): 7 gap(s)
  C1 score 0  Picking the right problem: frequent, painful, measurable, worth it; refusing the demo-shaped one
      learn it in: Day 4 (picking the right problem)
  C5 score 0  The business case: from "faster" to hours, rupees and risk a COO signs
      learn it in: Day 9 (success metrics and the business case)
  C7 score 0  The security and procurement conversation: the questionnaire, residency, "does it train on our data"
      learn it in: Day 23 (the security review) and Day 24 (data residency)
  C2 score 1  The stakeholder map: sponsor, operators, blockers, and whose version of the problem is true
      learn it in: Day 5 (the stakeholder map)
  C3 score 1  Discovery interviews and shadowing the people who do the work
      learn it in: Day 6 (discovery interviews)
  C4 score 1  Decomposing and scoping: workstreams by risk, a thin first slice, what you will not do
      learn it in: Day 7 (decomposition) and Day 8 (scoping the first 90 days)
  C6 score 1  Writing and speaking for executives: the readout, bad news, pushback, saying no
      learn it in: Day 10, Day 29, Day 30 and Day 32 (the document, the readout, bad news, pushback)
applied AI (mean 1.0): 4 gap(s)
  A3 score 0  Evals: a golden set built with domain experts, a judge, a regression run before every change
      learn it in: Day 14 (evals first)
  A5 score 0  Agents and workflows: tool calling, state machines, human approval on risky actions, guardrails
      learn it in: Day 17 (agents and workflows)
  A2 score 1  Prompts as code: versioned, templated, regression-tested, rolled back
      learn it in: Day 13 (prompts as code)
  A4 score 1  Retrieval over enterprise documents: chunking real PDFs, hybrid search, permission-aware results
      learn it in: Day 15 (retrieval for enterprise documents)
core engineering (mean 2.0): 2 gap(s)
  E3 score 1  A cloud account you do not own: IAM, VPC, deploying into someone else's environment
      learn it in: Day 26 (shipping into infrastructure you do not own)
  E6 score 1  Data pipelines that survive bad input: scanned PDFs, mixed languages, missing pages
      learn it in: Day 15 (chunking real PDFs) and Day 16

strengths to lead with in interviews (a 3 with evidence is a story; Day 45 turns it into one):
  E1  Own the settlement service (FastAPI, 40k lines I inherited); typed, 80 percent test coverage, on call for it since 2024
  E2  Rewrote the reconciliation queries against the bank's mirror schema; found the merchant-ID join that dropped 2 percent of rows

wrote data/sample-rubric-ravi-gap-plan.md
```

Three things to read off it. Ravi is the Arjun of section 01: a 2.0 in bucket 1, and the loop will find
bucket 3 (0.8) first, which is why the plan starts at Day 4 and not Day 11. His two 3s are already
interview stories; the merchant-ID join is a Day 7 step-3 story about a join that fails, and Day 45
makes him tell it with "I". And his bucket-1 gaps are not Python; they are the two rows that only exist
in someone else's environment (E3, E6), which is section 03.1's point.

The script refuses bad input usefully. On the empty template:

```text
E1 has no score: fill every row before running the plan
```

On the AI-filled rubric (exercise 3.1) it downgrades eighteen rows and then, revealingly, lets two
through:

```text
warnings (read these first):
  - E1: scored 3 with thin evidence ('Strong Python skills'); counted as 1 until you can name the system and the result
  - E2: scored 3 with thin evidence ('Advanced SQL'); counted as 1 until you can name the system and the result
  ...
strengths to lead with in interviews (a 3 with evidence is a story; Day 45 turns it into one):
  A1  Familiar with OpenAI and Anthropic APIs
  A4  Built a RAG chatbot over company docs
```

"Familiar with OpenAI and Anthropic APIs" is five words and passes the script's floor. It is not a 3.
The script catches eighteen problems; the human catches the rest, which is the exercise.

## 8.4 Part C: the calendar count

Section 05 showed the output. Build your own: take the Godavari calendar, change it for an engagement
you know (or exercise 2.4), keep the block format, and run `week_hours.py`. It checks that each block's
hours match its times, refuses any day over nine hours, and prints the split per week and overall. A
fortnight far from 60/30/10 is a conversation, not a failure; section 07 says what 90/10/0 or 10/90/0
usually means.

## 8.5 What goes into the engagement folder

| Artefact | Used by |
|---|---|
| `worksheet/<you>-rubric.md` and `data/<you>-rubric-gap-plan.md` | you, re-scored at Day 4, Day 11 and Day 21 (the start of each Part); Day 45 (strengths become stories); Day 46 (the 30/60/90 plan starts from the last re-score) |
| `worksheet/godavari-weeks-1-2-calendar.md` | Day 5 (the people in it become the stakeholder map), Day 8 (the dated plan starts from week 3), Day 29 (the Friday readout hour) |

## 8.6 Build it with AI

An FDE in 2026 would use a chat or coding agent here in two ways: to draft the scripts (routine; the
regex-over-markdown-table pattern is one an agent writes correctly in one pass), and to challenge the
self-assessment. The second is where the value and the danger are.

**Context to provide:** the template with its scoring definitions, your filled rubric, and your CV or a
list of projects with what you personally did on each. State the rule: a 2 or 3 needs a system, an
action and a result.

**A strong prompt (challenge, not fill):**

> Here is my filled skills rubric for the three buckets of a forward deployed engineer role, with the
> scoring definitions at the top, and a list of my projects with what I personally did on each. Do not
> fill or rewrite the rubric. Challenge it, row by row: (1) for every 2 or 3, say whether the evidence
> names a system, an action I took and a result, and if not, what score the evidence supports; (2) for
> every 0 or 1, check my project list for something I forgot that would raise it, and quote the project;
> (3) tell me which bucket an FDE interview loop would find weakest in me and which round would find
> it; (4) for my three strongest rows, write the one-sentence first-person version I could say in a
> behavioural round. Do not invent projects or results that are not in the list.

**A second prompt (the sceptical hiring manager):**

> Act as a hiring manager for a forward deployed engineer role at an AI vendor. Read my rubric and my
> project list. Ask me five questions, one at a time, that test whether my 3s are real. After each
> answer, say whether you would still score it a 3 and why.

**What the agent typically gets right:** the structure of the rubric and the scripts; spotting evidence
that is an adjective rather than an action; finding a forgotten project; turning a 3 into a
first-person sentence; playing the hiring manager.

**What it typically gets wrong for this concept (check each):**

| Mistake | How it shows | Fix |
|---|---|---|
| **inflates scores from CV adjectives** | "Strong Python skills" becomes a 3; "excellent communication" becomes a 2 in C6 (the Priya draft) | system, action, result; the script's five-word floor catches the worst, you catch "familiar with" |
| **treats every bucket as equally learnable from reading** | the plan is "read Days 4 to 10, then 11 to 19"; no out-loud work, no customer | bucket 3 is practised out loud (Day 7's 25-minute protocol, Day 34's drills); a plan without recordings and role-plays is not a bucket-3 plan |
| **scores bucket 1 from a product-team frame** | "AWS certified" is a 3 for E3, though E3 is about an account you do not own | the row's wording matters: "someone else's environment", "a pipeline that belongs to the customer" |
| **confuses bucket 2 with model knowledge** | a transformers course raises A3 (evals); "LangChain agents" raises A5 | the rows are about evals with experts, human approval, guardrails; a tutorial agent with no approval step is a 1 |
| **agrees with you** | asked to challenge, it praises the rubric and suggests cosmetic changes | give it the definitions as the rubric and ask it to argue each 3 down; ask "which round would find me out" |
| **fills the calendar backwards from 60/30/10** | asked for a calendar, it writes blocks that sum to exactly 60/30/10 with generic names ("stakeholder meeting") | plan the work, then count (05.1); every block names a person and a thing; the weeks should differ |

The first two are the ones to watch. An agent reading a CV scores it the way a CV wants to be scored,
and an agent writing a plan writes a reading list, because reading is what it can see. Bucket 3 is the
bucket neither helps with, and it is the one rising fastest.

## 8.7 How do you know it's right?

Whether a human or an agent filled the rubric, the checks are the same:

1. **Every 2 or 3 names a system, an action and a result.** Read the evidence aloud; if it would not
   survive "tell me more about that" from a hiring manager, lower the score.
2. **The script runs clean**, or every warning has been answered by a lower score or better evidence,
   not by adding words.
3. **No bucket is all 3s, and the weakest bucket is the one you would have guessed.** If not, one of
   the two is wrong; find out which.
4. **Each gap maps to a chapter and an artifact** for the engagement folder, with a re-score date (start
   of Parts 2, 3 and 4).
5. **The bucket-3 plan contains practice:** at least one recorded out-loud drill (Day 7) and one
   role-play (Day 34) per gap.
6. **The calendar's blocks each name a person or a thing, the weeks differ, and the count came from the
   script.**
7. **The two strengths are stories**, each with a system, a decision and a failure. A 3 with no failure
   story is probably a 2.

**Review checklist:**

- [ ] twenty rows scored; evidence for every 2 or 3 names a system, an action and a result
- [ ] script runs with no warnings, or every warning answered honestly
- [ ] no bucket all 3s; the weakest bucket matches your prior guess, or the mismatch is explained
- [ ] gap plan: weakest bucket first; each gap mapped to a chapter and an artifact; re-score dates set
- [ ] bucket-3 plan includes recorded drills and role-plays, not only chapters
- [ ] calendar: every block named; weeks differ; count from the script; no day over nine hours
- [ ] two strengths written as first-person stories with a failure each
- [ ] rubric, gap plan and calendar saved in the engagement folder beside Day 1's one-page note

## 8.8 Extend it

- Add a `Target by` column (the Day by which a row should be a 2) and make the script print rows whose
  target has passed without a re-score.
- Give `week_hours.py` a `--compare` flag that reads two calendars (weeks 1 to 2 and weeks 9 to 10) and
  prints how the split moved; section 07.5 says it should.
- Re-score the rubric as Meera and as Farhan from section 01 and run the plan; the three gap plans
  should start in three different Parts (Day 4, Day 4 with bucket-1 rows close behind, Day 11).
