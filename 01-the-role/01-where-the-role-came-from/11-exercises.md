# 11 · Exercises

> Day 1 · Section 11 of 12 · [Chapter overview](README.md) · Previous: [10 · Interview questions](10-interview-questions.md) · Next: [12 · Further reading](12-further-reading.md)

---

Nine exercises in three levels, including the reflective exercise's model answer and one "review this
AI-written lineage". Solutions are folded under each. The exercises marked **(tested)** use the
chapter's script, run on Python 3.14.3 (October 2026) from the chapter folder, and the outputs shown
are real. Learning mode: do the thinking yourself; use an AI assistant as the sceptical CEO or the
interviewer (section 9.7's prompts), not as the author. Try first, then open.

## Level 1: warm-up

**1.1 Name the role.** For each line, say whether it describes a Delta, an Echo or a Dev, and which
source it comes from (Palantir's blog or postings, or the 2015 first-hand account).

(a) "Lead training sessions to ensure that the product is meeting user needs."
(b) Four days a week in Toulouse on the A350 line, negotiating data access.
(c) Rarely visits a customer; turns three hand-built importers into one tool.
(d) "Coding a custom web app"; "speaking with customer executives".
(e) Presents to audiences "ranging from analysts to C-suite executives".
(f) Part of Business Development; "technology-driven value creation" for one customer.

<details><summary>Solution</summary>

(a) Echo; the Deployment Strategist posting. (b) Delta; the 2015 account. (c) Dev; the 2015 account
(Magritte). (d) Delta; the FDSE posting. (e) Echo; the Deployment Strategist posting. (f) Delta;
Palantir's "Dev versus Delta" blog. (Section 02.1.)

</details>

**1.2 Date the claim.** Each claim below is true as stated somewhere in the chapter. Add the date and
the source type (primary, company, vendor, recruiter, press, job board).

(a) OpenAI's FDE practice was two people.
(b) Palantir had more than 100 FDEs.
(c) About 12 weeks to self-sufficient teams.
(d) FDE postings in India up nearly 19 times.
(e) Foundry 50 percent or more of revenue.
(f) The FDE "picks up where the SE left off".

<details><summary>Solution</summary>

(a) start of 2024; company (OpenAI interview via ZenML). (b) by 2014; vendor (Perspective AI, May
2026). (c) 4 October 2026; company (Atlassian). (d) June 2025 to June 2026; press (Analytics India
Magazine, 14 October 2026, citing Indeed). (e) as of October 2024; primary (former FDE's account).
(f) 22 April 2026; recruiter (Paraform). (Section 06.1; `data/fde-timeline.csv`.)

</details>

**1.3 Which edge?** Each posting line below belongs to one of the three jobs the FDE is confused
with. Say which, and which edge gives it away.

(a) "Partner with account executives to deliver proofs of concept that advance opportunities."
(b) "Deliver client engagements against statements of work; track utilisation weekly."
(c) "Own the fine-tuning pipeline and evaluate checkpoints against internal benchmarks."
(d) "Embed with the customer post-sale; own production rollout; feed patterns to the platform team."

<details><summary>Solution</summary>

(a) solutions engineer; pre-sale, the deal is the finish line. (b) consultant; billed hours, no loop.
(c) model trainer; no customer. (d) the FDE: post-sale, outcome, loop. (Section 07.1.)

</details>

## Level 2: apply

**2.1 The lineage map for your own employer.** Take the company you work for now, or the last one.
Fill section 09.2's five parts for it. Where is the loop? Who is the Echo? What would it refuse to
build? If the honest answer to the loop question is "there is none", write what the company's economics
are instead and whether the FDE model would fit.

<details><summary>What to look for</summary>

Most services companies have no loop and should say so; most product companies have a loop with
nobody watching it (section 03.4's first condition). The useful output is one sentence you can say in
an interview: "at my last company the field learned X and the product never absorbed it, which is
why I understand the dark ages from the inside." (Section 04.)

</details>

**2.2 The reply to the COO.** Using the day-one note, write the three-sentence email the CEO should
actually send to Godavari's COO. No number, no technology, one question, one offer.

<details><summary>Model reply</summary>

"Thank you for the introduction. Nine days to three is a clear target, and before we say how, we
would like to understand where the nine days go today, which only your credit-ops team can show us.
Could we place one of our engineers with them in Hyderabad for two weeks, at our cost, and come back to
you with what we found and what we would propose?" (Section 09.4; Day 4 picks the problem; Day 10 is
the document this promises.)

</details>

**2.3 Godavari as a Delta would have described it.** Fill `worksheet/godavari-as-a-delta-template.md`
before opening this.

<details><summary>Model answer (abridged)</summary>

*1. The customer.* "A lender in Hyderabad, 1,200 people, 300 branches. Forty analysts in two cities
turn a pile of fourteen documents into a sanction, and it takes nine days. The executive says the
problem is reading documents. The analysts' problem is waiting: documents that have not arrived, a
credit check that runs as a batch at 6 pm, and a spreadsheet on a shared drive that is the real state
of every file and that nobody mentioned in the meeting."

*2. Where I would sit.* "Beside the analysts in Vijayawada three or four days a week for the first
month, then Hyderabad. I need a desk, a login to the core system's test environment, read access to
the document store, and the spreadsheet. The CISO will say no to the first three for a fortnight. I
will start with the spreadsheet."

*3. The data integration.* "A 2009 core system with a SOAP API that nobody has documented since the
vendor left; a document store of scanned PDFs on a shared drive; the Excel tracker, which has no
timestamps; the HR system's branch groups, which decide who may see which file. Owners: the core
system's one remaining administrator, the IT head, the analysts, HR. Not in any system: why a file
waited, and which of the fourteen documents is the one that usually stalls."

*4. What I would build.* "A screen that replaces the spreadsheet: one row per file, which documents
are present, which are missing, who is waiting on whom, fed by reading the store and the core system
nightly. Hand-built, with the SOAP calls hard-coded and the document checks written as a list the
compliance head signs. It will carry debt. It will also be the first time the executive sees where the
nine days go."

*5. What I would send back.* "A document-completeness checker that takes a signed checklist per
product; an integration layer for an old SOAP core with no idempotency; a work queue that shows
waiting time per file. Every lender has these three problems."

*6. The Echo.* "I need someone to run the training for forty analysts, to hold the weekly readout
with the COO, and to keep the compliance head talking to us. There is no such person. I will do it,
and I will block Friday afternoons for it or it will not happen."

*7. Translation table (six rows).* On site 3 to 4 days a week: same. Pilot time mostly on data
access: same (the CISO's fortnight). The hand-built screen with debt: adapted, it is the Day 20
walking skeleton, thin by design rather than by hurry. Patterns sent to the Devs: same, as the
fortnightly note to Kaagaz's product team. The Echo: does not apply, there is none; you carry it.
Six-to-twelve-month embed: does not apply; twelve weeks to self-sufficiency, then a lighter touch.

*8. Why FDE.* "Because at Godavari the outcome is forty analysts closing a spreadsheet, and I would
rather own that than own a slide that was true."

(Sections 02, 03, 09.5.)

</details>

**2.4 Extend the check (tested).** Add a `refresh_by` column to `data/fde-timeline.csv` (one year
after the source's date, YYYY-MM) and make `code/timeline.py` print every row whose `refresh_by` is
earlier than today. Predict how many rows it prints as of October 2026 before you run it.

<details><summary>Approach and expected result</summary>

Parse the column with the same regex; compare strings against `date.today().strftime("%Y-%m")`
(ISO-style strings compare correctly at month precision). As of October 2026, the rows past refresh
are the ones whose source is dated before October 2025: the October 2024 first-hand account's rows
(one row) and the 2024 OpenAI interview's rows (five rows, if you date the source 2024-12). The 2026
sources are all inside the year. Six rows is the expected count; your count will differ if you dated
the interview differently, which is the point: the source date goes in the CSV, not in your head.

</details>

**2.5 Break it, then fix it (tested).** Change one row's date to `circa 2014` and delete another row's
source, then run the script. Then fix both rows properly: the vague date becomes a year with the
vagueness moved to the source column; the missing source is found or the row is deleted.

<details><summary>Solution</summary>

The real output from exactly this break:

```text
problems (fix the CSV before trusting the table):
  - line 4: date 'circa 2014' is not YYYY, YYYY-MM or YYYY-MM-DD
  - line 16: no source; a dated claim without a source is a rumour
  - line 16: source_type 'blog' not in ['company', 'job board', 'press', 'primary', 'recruiter', 'vendor']
```

Exit code 1 and no table written. The fix for line 4 is `2014` with "approximate, per Perspective AI
(May 2026)" in the source column. The fix for line 16 is to restore the Paraform source and the
`recruiter` type; if you cannot name a source, delete the row. (Sections 08.4, 09.3.)

</details>

## Level 3: challenging

**3.1 Review this AI-written lineage and find what is wrong.** A colleague pasted
[`worksheet/ai-draft-lineage.md`](worksheet/ai-draft-lineage.md) into an onboarding page. Find at
least nine problems, and for each say what the chapter's sources actually support.

<details><summary>Solution</summary>

1. "Invented in 2010 when the company launched Foundry": the vendor source puts the first FDEs at
   2005, and Foundry came out of FDE work later, not the other way round (sections 01.3, 03.1).
2. "FDEs are Echos and product engineers are Deltas": swapped, and the product engineers are Devs
   (section 02.1).
3. "Consultants who spent a week or two gathering requirements, then returned to Palo Alto": Deltas
   were on site three to four days a week for months; the requirements-document pattern is exactly
   what the model replaced (sections 01.4, 02.2).
4. "Shipped to all customers unchanged": the Devs generalised field work; nothing shipped unchanged
   (section 03.1).
5. "Over 1,000 FDEs by 2012": the vendor source says more than 100 by 2014; the 1,000 figure is AIP
   bootcamps by end 2024 (section 06.1).
6. "Never had a period where field and product pulled apart": the dark ages (section 04).
7. "Immediately created a 90-person team" in November 2022: two people at the start of 2024, 90+ by
   2026 (section 05.3).
8. "First customer Klarna in 2021 ... fine-tuned GPT-4 ... 100 percent accuracy": Morgan Stanley was
   the first enterprise GPT-4 customer in 2023; Klarna was 2023 and the work was prompts for 400+
   policies, not fine-tuning; no 100 percent figure exists anywhere (sections 05.3, 03.5).
9. "Take on any customer that will pay": the team declines services work that does not advance
   strategic goals (section 04.3).
10. "Anthropic's FDE role is pre-sales": the posting embeds post-sale, builds production applications
    and feeds patterns to Product (section 06.1).
11. "Self-sufficient in about 12 months": 12 weeks (section 06.1).
12. "Rose 19 percent": nearly 19 times (section 06.3).
13. "1.2 crore": about 12 lakh, Glassdoor January 2026, 28 submissions (section 06.3).
14. "Essentially a solutions engineer": the SE is pre-sale; the FDE picks up where the SE left off
    (section 07.1).
15. "Trains the customer's model and leaves": the role deploys existing models and leaves at
    self-sufficiency, not at accuracy (sections 05.4, 07.1).

The pattern: every sentence has the right shape and the wrong content, and the wrong dates are stated
with the same confidence as the right ones. This is section 09.7's first and second mistakes, done by a
machine. The defence is the timeline CSV: none of these claims has a row.

</details>

**3.2 Argue the other side.** Write the strongest one-page case for the services proposal at
Godavari, as Kaagaz's head of sales would make it (faster revenue, the customer asked for it, a team
can start Monday). Then write the CEO's reply, using only the lineage. Keep both; Day 3 gives the reply
numbers.

<details><summary>What a strong reply contains</summary>

The services case is real: a custom build is faster to quote, the customer understands it, and the
first cheque is bigger. The reply does not deny that. It says what the cheque buys: a codebase only
Godavari uses, an engineer who cannot be moved, a product roadmap held hostage, and the published
failure that turned a product company's field teams into an integrator. It offers the alternative with
a number the head of sales can sell: platform plus a fixed twelve-week deployment fee, scope decided
at the end of week two, and a reference customer at the end. (Sections 04, 09.4; Day 3.)

</details>

**3.3 The lineage for a different vendor.** Write the lineage map's parts 3 and 4 (who plays which
role; what we copy and do not) for a ten-person vertical-AI company selling to district hospitals, with
Krishna District Hospital Network (Day 42) as the first customer. At least two "do not copy" rows must
differ from Godavari's.

<details><summary>What to look for</summary>

Role 3 is harder: at ten people the Dev is also the founder, and the loop runs only if the founder
reads your notes. The "do not copy" rows that change: the twelve-week bar may be too short where
consent and the state medical council are involved; the "will not build" line is different (a
hospital's bed-management screen rather than a lender's CRM); and the Echo's training work is with
junior doctors at 9 pm, which no engineer can also do, so the Echo must be hired before the second
customer. Keep it; Day 42 reuses it. (Sections 02.4, 09.2.)

</details>
