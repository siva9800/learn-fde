# 11 · Exercises

> Day 2 · Section 11 of 12 · [Chapter overview](README.md) · Previous: [10 · Interview questions](10-interview-questions.md) · Next: [12 · Further reading](12-further-reading.md)

---

Nine exercises in three levels, including one "review this AI-filled rubric". Solutions are folded under
each. The exercises marked **(tested)** use the chapter's scripts, run on Python 3.14.3 (October 2026)
from the chapter folder, and the outputs shown are real. Learning mode: do the scoring and the planning
yourself; use an AI assistant as the sceptical hiring manager (section 08.6's prompts), not as the
author. Try first, then open.

## Level 1: warm-up (no code needed)

**1.1 Which bucket?** Tag each block as C (customer-facing), D (deployment code) or I (internal), using
section 03.5's audience test.

(a) Reading the compliance head's KYC checklist alone at your desk.
(b) Filing a VPN request with Godavari's helpdesk.
(c) A call with Lakshmi to label thirty files.
(d) Running extraction on those thirty files.
(e) Writing the Friday status for the COO.
(f) Writing the same facts as a pattern note for Kaagaz product.
(g) The train to Vijayawada.

<details><summary>Solution</summary>

(a) C: the reader of your notes is at the customer. (b) D: environment work. (c) C. (d) D. (e) C. (f) I:
same hour of thinking, different reader. (g) neither; travel is its own line. (Sections 03.5, 04.2.)

</details>

**1.2 Shares or time?** Each statement is a correct reading of the June 2026 analysis or a misreading.
Mark and fix.

(a) "70 percent of an FDE's time is customer-facing."
(b) "Customer-facing skills appear in 70 percent or more of FDE postings."
(c) "95 percent of FDEs are Python developers."
(d) "Postings describe a week of roughly 60 percent customer-facing, 30 deployment code, 10 internal."
(e) "Stack Overflow found that 41 percent of FDEs spend more than 30 percent of their time with
customers."

<details><summary>Solution</summary>

(a) misreading: 70 is the share of postings listing bucket 3; the time figure is 60. (b) correct. (c)
misreading: 95 percent of postings list core engineering, of which Python or TypeScript is one item.
(d) correct, with "consistently describe" as the hedge. (e) misreading twice: the figure is about AI
engineers generally, not FDEs, and it is quoted second-hand; say "as quoted by". (Section 02.)

</details>

**1.3 Read the title.** For each posting title, say which bucket you expect to be over-weighted and one
question you would ask the recruiter.

(a) Forward Deployed Software Engineer, on site, Mumbai.
(b) Applied AI Engineer, named enterprise accounts.
(c) FDE / Solutions Architect, Series A startup.
(d) Deployment Engineer, data platform vendor.

<details><summary>Solution</summary>

(a) bucket 1, heavy coding embedded; ask what goes back to product. (b) bucket 2, evals especially; ask
whether the account is already won and who runs discovery. (c) bucket 3 starting pre-sale; ask whether
any pay is tied to deals closed. (d) bucket 1 on a mature product; ask how much bucket 2 judgement is
left to you. (Section 06.1.)

</details>

## Level 2: apply

**2.1 Score yourself (tested).** Copy `worksheet/skills-rubric-template.md`, fill all twenty rows with
evidence, and run `python -X utf8 code/gap_plan.py worksheet/<your-file>.md`. Fill the "where I will
spend longest" block from the output. Keep the file; you re-score at the start of Parts 2, 3 and 4.

<details><summary>What a good result looks like</summary>

No warnings, or every warning answered by a lower score. No bucket all 3s. The weakest bucket is the
one you would have guessed, and the plan's first three rows are in it. At least one row scored 3 with a
failure story. A backend engineer should expect a shape like Ravi's (2.0 / 1.0 / 0.8); a solutions
engineer should expect bucket 3 highest and a bucket-1 plan starting at Day 16. (Section 08.)

</details>

**2.2 Predict the output (tested).** Before running it, predict what `gap_plan.py` prints for
`worksheet/ai-draft-rubric-priya.md`: how many warnings, which bucket comes out weakest, and which rows
survive as strengths. Then run it.

<details><summary>Solution</summary>

Eighteen warnings (every 2 or 3 with fewer than five words of evidence is downgraded to 1). Core
engineering comes out weakest at a mean of 1.0, tied with customer-facing at 1.0; the script breaks the
tie by bucket order. Two rows survive as strengths because their evidence is five or more words: A1
"Familiar with OpenAI and Anthropic APIs" and A4 "Built a RAG chatbot over company docs". The surprise
is that the weakest bucket is "wrong" (a data engineer's real gap is bucket 3) because the script can
only read evidence length and the CV gave it none. That is the point of exercise 3.1. (Section 08.3.)

</details>

**2.3 Break it, then fix it (tested).** In a copy of `worksheet/godavari-weeks-1-2-calendar.md`, make
two changes. First, change the week-1 Monday SOP block's hours from 3 to 2 without changing its times.
Second, add a block to week-2 Thursday: `| Thu | 06:00 | 09:00 | 3 | D | alone | Rehearse the spike
against the stub |`, so the spike day starts at six. Run `week_hours.py` on the copy. Then fix both and
run again.

<details><summary>Solution</summary>

The script refuses with both problems and prints no split:

```text
problems (fix the calendar before trusting the split):
  - Week 1 Mon 13:00 to 16:00: hours says 2.0, clock says 3
  - Week 2 Thu: 10 hours in one day; a calendar that needs this is not a plan
```

The first catches a hand-edited count; the second catches a plan that only works on paper. The fix is
to make hours and clock agree, and to move the rehearsal into Wednesday or drop it, not to start at six.
A plan that needs ten-hour days is a plan that needs a second engineer. (Sections 05.4, 09.4.)

</details>

**2.4 Your own fortnight (tested).** Take a project you actually worked on and write its first two weeks
as a calendar in the chapter's format, tagged by bucket, with the real people (first names or roles).
Run the script. Then write three lines: the split, the bucket you under-spent, and what it cost you
later.

<details><summary>What to look for</summary>

Most engineers' real fortnights come out near 20/75/5: the discovery that should have happened in week
one happened in month three. Section 07's tables describe the failures. The three lines are a Day 45
behavioural story ("what would you do differently") in draft. (Sections 05, 07.)

</details>

## Level 3: challenging

**3.1 Review this AI-filled rubric and find what the script cannot (tested).** A colleague pasted her CV
into a chat agent and asked it to "fill the Day 2 rubric for me", and got
[`worksheet/ai-draft-rubric-priya.md`](worksheet/ai-draft-rubric-priya.md). Run the script, then read
the rubric yourself. Find at least eight problems the script did not flag, and say which bucket each
belongs to.

<details><summary>Solution</summary>

The script downgrades eighteen rows for thin evidence. The human review, at least nine problems it
cannot see:

1. **A1, "Familiar with OpenAI and Anthropic APIs", passes as a 3.** "Familiar with" is a 1 by the
   definitions; no system, action, result, cost budget or retries. (Bucket 2.)
2. **A4, "Built a RAG chatbot over company docs", passes as a 3.** At most a 2; the row asks for real
   PDFs, hybrid search and permission-aware results, and none is claimed. (Bucket 2.)
3. **E3, "AWS certified", scored 3** for a row about an account you do not own; a certificate is a 1.
   (Bucket 1.)
4. **E5, "REST APIs"**, for a row about SOAP, SFTP, batch jobs and a 2009 system. (Bucket 1.)
5. **E6, "Built Spark pipelines"**, for a row about scanned PDFs and missing pages. (Bucket 1.)
6. **C4, "Agile sprint planning", scored 3** for a row about a customer's problem, a thin slice and a
   "will not do" list the customer signed. (Bucket 3.)
7. **C6, "Excellent communication skills"** and **C1, "Good problem-solving skills"**: adjectives; the
   agent scored the CV, not the engineer. (Bucket 3.)
8. **C7, "Aware of GDPR"**, for a row about a CISO's questionnaire, Indian residency and "does it train
   on our data"; the wrong law and the wrong activity. (Bucket 3.)
9. **"Weakest bucket: none significant; well-rounded profile."** No honestly filled rubric says this; it
   is the agent agreeing with the CV. The real profile (a data engineer at a GCC) is almost certainly
   weakest in bucket 3, which the agent made the second-strongest.
10. **"Strength to lead with: full-stack AI engineering."** Not a story; no system, decision or failure.

The pattern: every score was inferred from a CV adjective, so every bucket looks the same and the one
that matters most is hidden. Section 08.6's first mistake, twenty times over. (Sections 08.3, 08.6.)

</details>

**3.2 The sceptical engineering manager.** Your manager at a product company says: "Sixty percent
customer-facing? So the FDE team is sales with a Git account." Reply in 150 words or fewer, with one
figure, one Godavari example and one published team.

<details><summary>Model reply</summary>

"The 60 percent is what 2026 postings describe, and it is engineering input, not sales. In the first
Godavari fortnight, seven hours beside a credit-ops analyst found that the nine-day turnaround lives in
an Excel tracker and that our model's best document type is not the one the queue waits on; both changed
the architecture before a line was written. The deployment hours that followed were denser for it: a
six-hour sandbox spike found the duplicate-on-retry problem because the week before had been spent with
the core-system owner. Ramp runs its FDEs at five to six customers each, mostly remote, and measures the
team on enterprise revenue over FDE salaries; nobody there is paid on deals. The test is simple: if the
FDEs were sales, there would be no 10 percent going back to product. There is, and it is the part that
pays twice." (Sections 04.3, 04.4, 07.5.)

</details>
