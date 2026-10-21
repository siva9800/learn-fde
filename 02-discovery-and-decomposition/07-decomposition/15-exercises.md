# 15 · Exercises

> Day 7 · Section 15 of 16 · [Chapter overview](README.md) · Previous: [14 · Interview questions](14-interview-questions.md) · Next: [16 · Further reading](16-further-reading.md)

---

Twelve exercises in three levels, including three timed drills and one "review this AI-written
decomposition". Solutions are folded under each one. The exercises marked **(tested)** use the
chapter's scripts, run on Python 3.14.3 (October 2026) from the chapter folder, and the outputs shown
are real. Learning mode: do the thinking yourself; use an AI assistant as the interviewer or the
sceptical reviewer (section 12.7's prompts), not as the author. Try first, then open.

## Level 1: warm-up (no code needed)

**1.1 Spot the anti-pattern.** Each opening sentence below is a candidate's first sentence in the round.
Mark each one as "scoping" or "solution", and for the solution ones say which step was skipped.

(a) "Before anything, what counts as response time here: call to dispatch, or call to arrival?"
(b) "We would fine-tune a model on the historical approvals."
(c) "Who, outside this room, could stop this project?"
(d) "I would put the documents into a vector store so an assistant can answer questions."
(e) "Is the time mostly people working, or mostly files waiting?"
(f) "A dashboard for the dispatchers, plus a recommendation engine."

<details><summary>Solution</summary>

(a) scoping, step 1. (b) solution; skipped steps 1 to 3 (it assumes labelled approvals exist and that
prediction is the lever). (c) scoping, step 2 (the ghost). (d) solution; skipped steps 1 to 2 (no
metric asked for question answering). (e) scoping, step 1 (the assumption that decides the lever).
(f) solution; skipped steps 1 to 4 (a technology list without a trade-off, people, inputs or order).
(Sections 02.2, 09.4.)

</details>

**1.2 Name the trade-off and the decider.** For each goal, write what is being optimised, what is being
traded away, and who sets the acceptable loss: (a) "cut cold-chain spoilage in half"; (b) "answer
insurance pre-authorisation the same day"; (c) "cut the discom's complaint backlog from 40,000 to
5,000"; (d) "reduce failed e-commerce deliveries".

<details><summary>Solution</summary>

(a) share of consignments in temperature range; traded: truck utilisation and route freedom, cost per
trip; decider: the operations head against a customer SLA. (b) hours from discharge to insurer
response; traded: clinical accuracy of the summary and doctor time; decider: the medical
superintendent against the insurer's rejection rate. (c) open complaints; traded: quality of
resolution (closing complaints without fixing them) and field-crew time; decider: the regulator's
consumer-grievance standard and the customer-service head. (d) first-attempt delivery rate; traded:
delivery-window promises and rider earnings per hour; decider: the city operations head against the
customer-rating target. In all four the decider is not the sponsor. (Section 03.2.)

</details>

**1.3 Which column changed the design?** For each Godavari fact, say which of the five input columns
(shape, owner, freshness, access, missing) it belongs to and what it forced: (a) no idempotency on
CreateApplication; (b) the sandbox is refreshed quarterly; (c) the tracker has no timestamps; (d)
branch groups are synced nightly from HR; (e) the checklist does not list acceptable address proofs.

<details><summary>Solution</summary>

(a) missing (a property that is absent): the integration layer owns idempotency. (b) freshness: the
sandbox may be stale, so integration risk is a 5 and a WSDL stub is the fallback. (c) missing: the
baseline must be hand-sampled. (d) access and freshness: group-filtered queries, and a transfer can
lag a day. (e) missing: a week of the compliance head's time, scheduled, before the rules are signed.
(Section 05.3.)

</details>

**1.4 Thin or not?** Each is a proposed walking skeleton. Say whether it is thin, complete, both or
neither, and fix it in one sentence.

(a) "Extraction on all products, tuned to 95 percent field accuracy, demonstrated on a laptop."
(b) "One branch, one product, files in, fields out, an analyst approves, written to the sandbox, timed."
(c) "The full system for the smallest branch, including SSO and the dashboard."
(d) "The live unit map for one district, no recommendation yet, dispatchers decide, logged."

<details><summary>Solution</summary>

(a) neither: one layer, not thin, connected to nothing. Fix: one product, twelve fields, into the rest
of the pipe. (b) both. (c) complete but not thin: SSO and the dashboard are week-eight work, and the
"smallest branch" confuses small customer with thin slice. Fix: one user on a plain page, a CSV for
measurement. (d) both; the Palantir guide's "visibility first" slice; the recommendation is the next
iteration. (Sections 07.3, 07.6.)

</details>

## Level 2: apply

**2.1 Timed drill A (25 minutes, out loud, recorded).** Prompt: "A state discom (electricity
distribution company) has 40,000 open customer complaints, many duplicated across the call centre, an
app and a WhatsApp number. The managing director wants the backlog under 5,000 in 90 days." Run the
protocol in section 9.3 against a timer. Then audit the recording with section 9.7's checklist.

<details><summary>What a strong run contains</summary>

Step 1: "open" means what (not closed, or not resolved?); duplicates mean the 40,000 may be 15,000
real; the trade-off is closure speed against resolution quality, and the decider is the regulator's
grievance standard, not the MD. Step 2: MD (backlog count), call-centre agents (handling time,
re-opens), field crews (jobs per day, wasted visits), the regulator (ghost: resolution within
standard), the app vendor (system owner), consumers (re-opened complaints). Step 3: three channels
with three schemas and no shared complaint ID (the join that will fail); free-text categories; field
job records in another system; the data that does not exist is a de-duplicated complaint with a
category. Step 4: de-duplication and a shared ID first (risk 5), the baseline second, visibility (one
queue, categorised) third, routing to crews fourth, adoption with the agents throughout; not now:
predicting outages. Step 5: one division, one channel's backlog, de-duplicated and categorised into
one queue the agents work from, closures logged against the standard; expected failures: categories
wrong (agents correct, feed the rules), crews ignore the routing (routing hidden, queue only), the
regulator counts differently (align the count first).

</details>

**2.2 Timed drill B (25 minutes).** Prompt: "A UPI merchant acquirer has a dispute queue of 9,000 open
chargebacks and a 30-day regulatory deadline per dispute. They have transaction logs, the dispute
tickets, merchant KYC records and a 20-person ops team. Cut the share that breaches the deadline from
18 percent to under 3 percent."

<details><summary>What a strong run contains</summary>

Step 1: the breach is the metric, the trade-off is speed against wrongly decided disputes (which
cost refunds or merchant churn), the decider is the regulator's timeline plus the risk head; the
assumption to revisit is that breaches come from queue ordering, not from evidence collection. Step 2:
ops head (sponsor), ops agents (operators: disputes per day, re-work), merchants (upstream producers
of evidence), the regulator (ghost), the payment switch (system owner), risk and compliance (blockers).
Step 3: tickets with inconsistent timestamps, evidence arriving by email from merchants (the
unofficial channel), logs in a warehouse with a different merchant ID (the failing join), no labelled
"correct decision" set. Step 4: the deadline clock per ticket as deterministic code (risk 3, value 5,
thin version first), the evidence-request flow to merchants (risk 4), the queue ordered by days to
breach (visibility, value 4), evals with the risk head on 200 decided disputes, integration with the
switch, enablement. Step 5: one merchant category, the queue ordered by days to breach with the
evidence status visible, agents decide, every decision logged; prediction of outcomes is "not now".

</details>

**2.3 Timed drill C (25 minutes).** Prompt: "A district hospital network wants discharge summaries
written faster and insurance pre-authorisation answered the same day." This is the capstone's problem
(Day 42). Run it now, before the capstone, and keep the recording to compare later.

<details><summary>What a strong run contains</summary>

Step 1: two goals, pick one or show they share a lever (the summary feeds the pre-auth); the
trade-off is speed against clinical accuracy, decided by the medical superintendent and judged by the
insurer's TPA and the state council; constraints: consent for health data (DPDP), dosage fields never
generated. Step 2: superintendent (sponsor), junior doctors who type at 9 pm (operators), billing staff
(operators), the insurer's TPA (ghost and downstream), the IT head (blocker), the hospital's medical
records officer (system owner). Step 3: dictated notes (audio, 7 pm), typed summaries (9 pm), the
insurer's code lists per policy, the HIS with no API, consent forms on paper; the data that does not
exist is a summary a senior doctor has marked correct. Step 4: the insurer code checklist as rules
(risk 2, value 5), the labelled set with senior doctors (risk 4), HIS integration (risk 5), consent and
residency with the IT head (risk 5), drafting from dictation (value 5, risk 4), enablement with the
junior doctors. Step 5: one ward, one insurer, dictation in, a draft summary with the insurer's
mandatory fields checked, a doctor edits and signs, the pre-auth form filled from the signed summary,
timed; dosage fields are copied from the HIS, never generated.

</details>

**2.4 Fill the worksheet for the trucking firm (tested).** Take section 10.2 and fill
`worksheet/decomposition-worksheet-template.md` for Rayalaseema Roadways. Run the script. Compare the
order with section 10.2's table.

<details><summary>Solution (tested with the section's scores)</summary>

With the six workstreams scored as in 10.2 (baseline 3/5, three-way match 5/4, POD capture 4/4,
challan reading 4/4 depending on the labelled set from the baseline work, AP rules 3/2, invoicing 4/3
depending on the match) the script ranks: baseline (prio 13), three-way match (13, tie broken by
risk: equal, then by code), POD capture (12), challan reading (12), invoicing (10), AP rules (7). The
baseline and the match start in week 1; POD capture and challan reading in weeks 1 to 2 subject to the
three-FDE-workstream cap; invoicing after the match starts; AP rules thin in the skeleton and full
effort last. Where your table differs, the "why" cells decide, not the script.

</details>

**2.5 Predict the output (tested).** Change `RISK_WEIGHT` to 1.0 and `VALUE_WEIGHT` to 2.0 in
`code/plan_from_worksheet.py` and predict the new order for the Godavari worksheet before running it.
Then run it and explain the one surprising thing.

<details><summary>Solution</summary>

Priorities become W1 extraction 14 (4 + 10), W4 integration 13, W2 completeness 10, W5 security 9,
W3 evals 10, W6 enablement 9. But W1 depends on W3, so the first pick from the ready set is W4 (13),
then W2 and W3 tie at 10 and the riskier W3 goes first, then W1 is ready (14) and goes next, then W2,
then W5 and W6 tie at 9 and the riskier W5 goes first. The surprise is that the security review falls
to fifth and starts in week 1 anyway, because it is not FDE-owned and so is not held back by the
capacity rule; the order is "wrong" but the start week is not. Which is the point: the order matters
when capacity is scarce, and the weights are a convention you must be able to defend. (Section 06.3.)

</details>

**2.6 Break it, then fix it (tested).** In `worksheet/godavari-decomposition.md`, make W3 (evals)
depend on W1 (extraction) as well as the other way round, and run the script. Then decide which
dependency is real, remove the other, and say in one sentence why the thin version resolves it.

<details><summary>Solution</summary>

The script reports `dependency cycle among W1, W3` (with the others listed, since nothing can be
scheduled). The real dependency is extraction on evals: you cannot judge extraction without labelled
files. Evals do not depend on extraction; labelling is done by analysts on the raw files. The thin
version resolves the apparent cycle: the first fifty labelled files are enough to start extraction,
and the extraction's early errors feed the labelling guidelines, which is overlap, not a cycle.
(Section 06.3.)

</details>

## Level 3: challenging

**3.1 Review this AI-written decomposition and find what it skipped (tested).** A colleague asked a
coding agent to "decompose: an NBFC wants loan turnaround from 9 days to 3; fill the Day 7 worksheet"
and got [`worksheet/ai-draft-godavari.md`](worksheet/ai-draft-godavari.md). It reads well. Run the
script on it, then read it yourself. Find at least eight problems and say which step each belongs to.
The script catches two.

<details><summary>Solution</summary>

The script:

```text
== ai-draft-godavari.md: 5 workstreams read from the Step 4 table ==
problems (fix the worksheet before trusting the order):
  - no workstream mentions 'security': the decomposition is probably missing one
  - no workstream mentions 'enable': the decomposition is probably missing one
```

The human review, at least ten problems:

1. **Step 1: the sponsor is wrong** (CTO, not COO) and the goal is "all loans within 6 weeks", with
   no unit, no population and a date nobody agreed.
2. **Step 1: no trade-off.** "Nothing significant; the LLM will improve both" is the anti-pattern in
   one line, and "the RAG chatbot deployed to 300 branches" is a technology as the definition of done.
3. **Step 1: the constraint is "budget".** No PII residency, no RBI rules, no core-system condition.
4. **Step 2: three stakeholders**, none of them a blocker who can stop the project: no CISO, no
   compliance head, no core-system owner, no auditor, no branch managers; "IT team: minimal integration
   work" is not a metric.
5. **Step 3: invented data.** "A PostgreSQL table with 50,000 historical applications and approval
   labels", "PDFs in an S3 bucket", "a credit bureau API", all "real time" with "none" missing. The
   discovery notes have scanned PDFs on nightly SFTP, a 2009 SOAP API, an Excel tracker, AD groups and
   no ground truth. Not one row traces to evidence.
6. **Step 3: "data that does not exist: none."** The ground truth and the baseline are both missing.
7. **Step 4: four workstreams an architecture-first plan always drops.** No evals with experts (the
   "evaluation on held-out approvals" is a one-week afterthought on invented labels), integration as
   one week of "plumbing" after the UI, no security review, no enablement. The script caught two.
8. **Step 4: risk scored as difficulty**, and backwards: the RAG pipeline is risk 2, integration with
   a 2009 system is risk 2, fine-tuning on invented labels is the core workstream.
9. **Step 4: "out of scope: none."** No "not now" list; the chatbot is in scope with no metric.
10. **Step 5: the skeleton is neither thin nor complete.** "All products, all branches, in week 2";
    "the LLM checks completeness" (the deterministic layer handed to the model); "human in the loop:
    not needed after week 2" (the auditor's constraint violated); measurement is "a satisfaction
    survey"; the failure mode is "hallucination, mitigated by RAG", which maps to no plan change.
11. **Fine-tuning on historical approvals** would also train on the analysts' past errors and, for a
    lender, is a model-governance question the compliance head would have to answer; it appears with
    no stakeholder attached.

The pattern: the draft is confident, well formatted, and built entirely on the sponsor's version of
the problem plus invented data. Every one of section 12.7's typical mistakes is present. (Sections
12.7, 12.8.)

</details>

**3.2 Write the readout paragraph.** Take the script's Godavari order and write the paragraph (120
words or fewer, no model names) that the COO reads in the discovery document explaining why the
security review and the integration start before the extraction that she is paying for.

<details><summary>Model paragraph</summary>

"The work is ordered by what could change the plan, not by what is most visible. The security review
takes about eight weeks and is run by your team; if it starts in week two, the system can run in your
AWS Mumbai account by week eight, which is when the pilot branches need it. The integration with the
core lending system is where the last three vendors failed; we test it in week one with one record in
the sandbox so that any surprise costs a conversation, not a rebuild. Extraction, which is where the
speed comes from, starts in week two against a set of files your senior analysts have labelled, so
that by week three we can show you a measured result rather than a demo." (Section 06.3; Day 10.)

</details>

**3.3 Add a hard deadline to the script (tested, extension).** Add an optional ninth column
`Must start by` to the step 4 table and make the script warn when the sequencing pushes a workstream's
start past it. Give W5 a `must start by` of week 1 and W6 of week 5. Run it.

<details><summary>Approach</summary>

Parse the ninth cell if present (`int` or blank), store it as `must_start_by: int | None` on the
dataclass, and after `sequence()` append a warning to any row with `start_week > must_start_by`. The
Godavari run should produce no warnings (W5 starts week 1, W6 week 6 is after 5, so one warning: W6).
That warning is correct and is the kind of thing Day 8 resolves by moving enablement's first task (the
tracker read) into the skeleton. Keep the capacity rule; deadlines do not create hours.

</details>

**3.4 The method on your own work.** Take a project you have actually worked on. Write the five steps
as they should have been written on day one, in the worksheet. Then write the list of what the project
discovered in month three that step 3 or step 4 would have found in week two. Keep this; it is a
behavioural-round story (Day 45).

<details><summary>What to look for</summary>

Almost every real project has at least one row in section 11.1's table. The exercise is not to feel
bad about it; it is to be able to say, in an interview, "on project X we discovered the write
interface could not handle retries in month three; here is how I would sequence it now, and here is
the question I would ask in week one." That sentence is worth more than any architecture.

</details>
