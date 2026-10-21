# 01 · Why Picking the Problem: Seven Candidates, Twelve Weeks, One Choice

> Day 4 · Section 1 of 12 · [Chapter overview](README.md) · Next: [02 · The two filters](02-the-two-filters.md)

---

## 1.1 Monday, the list

The glass room on the fourth floor of Godavari Finance, the one from Day 0. The COO has said
"nine days to three" and then, because he has been thinking about this for months, he keeps going.
He has a list. He has seen what the model does with a salary slip, and he can see it everywhere:

1. KYC document checks, and the periodic re-KYC the RBI requires.
2. Income verification from bank statements.
3. Title-deed review for the secured loans.
4. A chatbot for the branches, so they stop phoning Hyderabad about policy.
5. Summaries of collections calls.
6. Drafting the credit memo.
7. Loan-file completeness: "the files keep coming back".

Seven problems, one sponsor, twelve weeks on site, and a platform that could plausibly touch all
seven. Everyone in the room is looking at you.

There are two ways to spend the next minute. The first is to say "yes, the platform can do all of
that", which is true and is also the beginning of the services trap from
[Day 3](../../01-the-role/03-the-economics/README.md): seven half-built things, none of them in daily
use by day 90, and an engineer who cannot leave. The second is to say "it can touch all seven; the
question is which one is worth the first twelve weeks, and I would like a week to answer that with
numbers rather than a guess." Then you spend the week the way Day 0 described it: on the floor with
Srinivas in Hyderabad, on the train to Vijayawada to sit beside Lakshmi, counting.

This chapter is that week. It teaches how to choose the one problem an engagement should attack when
the customer arrives with seven, and why "what can the model do" is the wrong first question.

## 1.2 Why it matters for your career

Three reasons, from the research behind this course (CURRICULUM.md and the Part 2 plan; sources in
section 12):

- **It is the first thing the job gets wrong.** The Part 2 plan names the failure on the job in one
  line: a prototype built for the sponsor's version of the problem that the operators never use. That
  failure is decided in week one, when the problem is picked, not in week ten when the demo is shown.
  Customer-facing discovery, the bucket this chapter opens, appears in 70 percent or more of the
  1,000 FDE postings analysed in 2026 and is the fastest-rising of the three (Day 2).
- **The teams that invented the role say it the same way.** Atlassian's playbook: pick problems that
  are frequent, painful and measurable, then work backwards to the AI. OpenAI's team: problems worth
  tens of millions to the customer, at the core of the business rather than at its edges, and
  qualified as FDE-shaped with a path to recurring revenue. Interviewers who have read those
  playbooks ask "how would you choose?" in hiring-manager screens, and they are listening for a
  method rather than enthusiasm.
- **It is step zero of the decomposition round.** [Day 7](../07-decomposition/README.md) owns the
  five-step method and the interview that scores it. That method starts from a one-sentence problem
  statement. This chapter is where that sentence comes from, and a candidate who can say why this
  problem and not those six has already shown the behaviour the round scores: scoping before
  solving.

> **Analogy (Telugu audience).** Exam preparation. You have a week before the exam and twelve
> chapters. You do not revise the chapter you enjoy. You revise the chapter that carries the most
> marks and that you keep failing in the mock tests. Marks are frequency and pain. The mock-test
> score is the baseline. The chapter you enjoy is the demo that impressed the board. This chapter is
> the marking scheme.

## 1.3 Where this sits in the course

Day 4 opens Part 2 and the engagement proper. It consumes Days 2 and 3 and feeds the rest of Part 2.

| Day | What it gave you | How Day 4 uses it |
|---|---|---|
| [Day 2](../../01-the-role/02-the-three-buckets/README.md) | bucket 3, customer-facing discovery, as the fastest-rising skill; the two-week calendar | this is the first week of that calendar, told as a decision |
| [Day 3](../../01-the-role/03-the-economics/README.md) | "is this FDE-shaped?"; the second-customer test; the branch CRM already declined | the sponsorship column asks whether Kaagaz's product can absorb the fix; the CRM is not even in the catalogue |
| [Day 0](../../00-start-here/00-the-engineer-in-the-room/README.md) | the week on the floor: the tracker, the 6 pm batch, fourteen documents, Lakshmi | the eighth candidate (the tracker) and the evidence behind the scores |

And it sets up: [Day 5](../05-the-stakeholder-map/README.md) maps who owns the chosen problem;
[Day 7](../07-decomposition/README.md) decomposes the signed sentence; [Day 9](../09-success-metrics-and-business-case/README.md)
turns the baseline this chapter insists on into a business case; [Day 10](../10-the-discovery-document/README.md)
uses the "not now, because" lines you write here when the COO asks for the chatbot in the readout;
Day 42 repeats the whole step on a hospital.

## 1.4 The hard parts, named up front

Three things make this harder than a scoring sheet suggests:

1. **The sponsor is in the room and the operators are not.** The COO's list is ordered by what
   excites him. The analysts' list, if anyone asked, would be ordered by what wastes their Tuesday.
   Scoring the sponsor's list honestly in front of the sponsor takes a sentence you need to have
   ready (section 06).
2. **The impressive candidate and the valuable candidate are different rows.** The chatbot is the
   demo the board liked. Intake is forty people re-keying forms. Every instinct that got you into
   engineering pulls toward the first row. The scoring sheet exists to make the second row win on
   paper before the first wins in the room.
3. **You will want to pick two.** Intake and the credit memo; intake and income verification. Both
   pairs are sensible, and both halve the chance that either is in daily use by day 90. The chapter
   gives you a way to keep the second one visible without starting it: the ranked list and the
   "next slice" line in the memo.

By the end of the chapter you will have scored Godavari's eight candidates with a rubric, seen the
script confirm that the winner survives every reasonable change of weights, written the one-sentence
problem statement that the COO and the team leads both sign, and written the "not now, because" line
for each of the other seven. That memo is the first page of the engagement folder.
