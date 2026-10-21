# 01 · Why This Chapter: Three Engineers, Each Sure the Job Is Their Third

> Day 2 · Section 1 of 12 · [Chapter overview](README.md) · Next: [02 · The measured job](02-the-measured-job.md)

---

## 1.1 Three people read the same posting

Kaagaz AI posts a forward deployed engineer role for the Godavari engagement. Three people apply.

**Arjun**, six years of backend at a Bengaluru logistics company, reads "deploy into the customer's AWS
account, integrate with a legacy core system, build pipelines over scanned documents" and thinks: my job
with a commute. He skims "running discovery sessions" as HR filler.

**Meera**, three years as an ML engineer at a Hyderabad GCC, reads "LLM application development,
retrieval, evals, agents" and thinks: finally, a role about the model work. She assumes someone else
does "CI/CD into the customer's environment".

**Farhan**, five years as a solutions engineer at a Chennai SaaS vendor, reads "customer-facing, win
trust, scope the engagement, say no" and thinks: what I do, with a better title. He assumes "production
code in a codebase you did not write" means the demo environment.

Each is right about one third of the job, and each meets the interview round that scores the third they
skipped. Arjun is asked, with no code in front of him, how he would turn "nine days to three" into a
plan a CISO signs. Meera is asked to deploy a container into an account whose IAM she does not control.
Farhan is handed a failing eval and asked which prompt change caused it. None of these is a trick. Each
is the job. This chapter exists so that you know which of the three you are before you apply, and know
the other two well enough to plan the gap.

## 1.2 Why it matters for your career

Two facts from the research behind this course (CURRICULUM.md and the Part 1 plan; sources in section
12), both dated so you can refresh them:

- An analysis of roughly 1,000 FDE postings, published in June 2026 by a recruiting-platform vendor,
  finds **core engineering in 95 percent or more** of postings, **applied AI in 80 percent or more**, and
  **customer-facing discovery in 70 percent or more, rising fastest**. Postings describe the week as
  **roughly 60 percent customer-facing, 30 percent deployment code and 10 percent internal**. Section 02
  gives the method and the caveats.
- Indian FDE postings on Indeed rose **nearly 19 times between June 2025 and June 2026**, as reported by
  Analytics India Magazine. Day 3 prices them; what matters here is that they are written by people who
  read the same playbooks, so the three buckets are what the postings ask for, in almost the same words.

Every round of the interview loop scores one of the buckets (Day 43 maps them). The open-ended
decomposition round, which scores bucket 3, has the lowest pass rate of any stage, and the most common
rejection recorded by the 2026 guides is jumping to a solution before scoping: a bucket-3 failure made by
people who are strong in buckets 1 and 2. The bucket you have not practised is the one the loop will find.

> **Analogy (Telugu audience).** The cricket all-rounder. A specialist batsman is picked for one thing
> and judged on it. The all-rounder bats, bowls and fields at point, and the selectors test all three.
> Nobody is dropped for being an average fielder when the batting and bowling are there. But a batsman
> who cannot field is a liability in the last ten overs, and the last ten overs decide the match. For an
> FDE the last ten overs are the conversations: the CISO's "where does the PDF go?", the COO's "when will
> we be at three days?". That is the bucket most engineers have never fielded in.

## 1.3 Where this sits in the course

[Day 0](../../00-start-here/00-the-engineer-in-the-room/README.md) told the first week as a story and
quoted the three-bucket table once. [Day 1](../01-where-the-role-came-from/README.md) explained where the
role came from and what a Palantir Delta did inside a customer. This chapter takes the job apart:
measured from postings (02, 03), lived as a fortnight (04, 05), read off a title (06), and scored against
you (08). [Day 3](../03-the-economics/README.md) prices it. Then the buckets are taught one chapter at a
time: bucket 3 from Day 4, bucket 2 from Day 11, bucket 1 in the customer's environment from Day 16 and
Day 26. This chapter names each skill once and links; it does not teach any of them.

## 1.4 The hard part, named up front

1. **The figures are soft and you must use them anyway.** Every number in section 02 is recruiter,
   vendor or career-prep content. Quote it exactly, with the date and the source type, and never round
   it up. An engineering manager will ask "where does that 60 percent come from?"; section 02.5 is the
   answer.
2. **Sixty percent customer-facing sounds like a demotion.** It is not. Shadowing Lakshmi for seven
   hours on Wednesday is what made Thursday's SOAP spike the right spike. Section 04.3 makes the case;
   section 05 shows it hour by hour.
3. **Scoring yourself honestly is uncomfortable.** The rubric wants evidence per row, and most people
   find that a CV skill is a 1 ("did a tutorial"), not a 3. The script enforces it: a 2 or 3 without
   evidence counts as 1. The interview enforces it harder.

By the end you will have a calendar for the first two weeks at Godavari, a scored rubric, a gap plan,
and one sentence per bucket that you could say to the three applicants above.
