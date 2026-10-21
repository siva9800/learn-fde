# 12 · Exercises

> Day 10 · Section 12 of 13 · [Chapter overview](README.md) · Previous: [11 · Interview questions](11-interview-questions.md) · Next: [13 · Further reading](13-further-reading.md)

---

Nine exercises in three levels, including one "review this AI-written document". Solutions are folded
under each. Exercises marked **(tested)** use the chapter's script, run on Python 3.14.3 (October 2026);
the outputs shown are real. Learning mode: write the document and the answers yourself; use an AI
assistant as the sceptical CISO or the COO (section 9.6's prompt), not as the author.

## Level 1: warm-up (no code)

**1.1 Report or decision document?** For each sentence, say which kind of document it belongs to and
rewrite the report ones. (a) "In week two we interviewed ten people across four roles." (b) "We ask the
COO to commit to a two-branch pilot from 7 December, subject to the 4 December go or no-go." (c) "The
analysts expressed frustration with the core system." (d) "An analyst decides every file; decided by
the compliance head for the auditor, 20 November."

<details><summary>Solution</summary>

(a) report; rewrite as a finding with a consequence: "the nine days are mostly waiting: 6.4 days of
queue (baseline pack)". (b) decision. (c) report; rewrite with the number and what changes: "re-keying
61 fields takes 0.97 hours a file; the pilot pre-fills them for the analyst to check". (d) decision,
in log form. (Section 02.1.)

</details>

**1.2 Which reader?** Place each sentence in the section of the reader who needs it: (a) "logs and
backups are in scope for no PII outside India"; (b) "the system writes file status back to the
tracker"; (c) "minus 1.12 crore on capacity alone"; (d) "the junior sends back an unlisted address
proof to be safe".

<details><summary>Solution</summary>

(a) section 8, the CISO. (b) section 3, the team leads (in bold). (c) page one, the COO, beside the
+15.0 net. (d) section 3, the team leads; it is step 9 of the real workflow. (Section 03.)

</details>

**1.3 Not now, because, and instead.** Write the three-part sentence for: (a) the COO asks to add gold
loans to the pilot; (b) the Guntur branch manager asks the system to read WhatsApp photos; (c) the
core-system owner asks you to skip the idempotency key "because we will be careful".

<details><summary>Solution</summary>

(a) "Not in the pilot, because the compliance head has signed only the two-wheeler rules and gold loans
are first in the slip order; instead, they are the first product added if M10 and M12 hold, and the
first to move to the next 90 days if they do not." (b) "Not now, because a page on a personal phone
never reaches the file of record and the CISO's rules do not allow it; instead, the system tells you on
day one what is missing and accepts a resubmission the same day, so WhatsApp stops being faster."
(c) this is not a "not now" at all: it is the owner's own condition (a month of duplicate-free calls).
Refuse to skip it, gently: "The key is how we keep your condition; it costs one lookup per create."
(Sections 05.1 to 05.3; Day 6, findings A3 and A5.)

</details>

## Level 2: the script

**2.1 Predict the output (tested).** Save this as `mini.md` and, before running the checker on it,
predict: how many required sections it finds, which error it gives on the chatbot row, whether the
problem statement passes E2, and what W2 reports.

```markdown
## Summary

We will cut turnaround from 9.1 days to 3 using an LLM.

## 1. Problem statement

> Files are slow.

## 10. Out of scope

| Item | Because | Agreed by |
|---|---|---|
| CRM | not our product and nobody else would buy it | the COO |
| chatbot | later | |

## Decision log

| Decision | Decided by | Date |
|---|---|---|
| run a pilot | the COO | 20 Nov |
| pick the vendor | Kaagaz | week one |
```

<details><summary>Solution</summary>

```text
== mini.md: 4 of 16 required sections, 2 decisions, 2 will-not-do lines, 0 linked files resolved ==
  ERROR   E1 missing section: the people (no heading matches /people|stakeholder/)
  ... (eleven more E1 lines: workflow, findings, decomposition, 90-day plan, baseline, security, risks,
       open questions, decisions needed, change log, sign-off)
  ERROR   E3 'Decision log': decision pick the vendor has no date ('week one')
  ERROR   E4 'chatbot' has no reason ('because')
  warning W5 'chatbot' does not say who agreed
  warning W1 page one names technology: 'LLM' (the COO signs outcomes, not components)
  warning W2 page-one numbers found in no linked source: 3, 9.1
  ... (six W6 lines, one per earlier Day)
FAIL: 14 errors, 9 warnings
```

Four sections found (summary, problem statement, out of scope, decision log). "later" is in the
checker's list of empty values, so the chatbot has no reason at all. "week one" has no digit, so it is
not a date. "Files are slow." is one sentence, so E2 passes: the checker cannot tell that the sentence
is useless. And "decided by Kaagaz" passes E3, which only a reviewer catches.

</details>

**2.2 Break it, then fix it (tested).** The shipped checker has a real limitation in E2. Run it on a
problem statement that reads "Files from far branches (e.g. Guntur) take nine days because intake is
manual." What does it say, why, and how would you fix it?

<details><summary>Solution</summary>

```text
  ERROR   E2 problem statement is 2 sentences; the signed statement is one
```

The split `(?<=[.!?])\s+` treats the dot in "e.g." as a sentence end. Fix: protect common
abbreviations before splitting, for example
`re.sub(r"\b(e\.g|i\.e|etc|vs|Rs|No|Dr|Mr|Ms)\.", lambda m: m.group(0).replace(".", "<dot>"), quote)`,
which leaves one sentence. Then add the case as a test. The lesson for Day 10: a checker that is wrong
in a way that pushes you to edit the signed sentence is worse than no checker; fix the rule.

</details>

## Level 3: judgement

**3.1 Review this AI-written document.** Open
[`worksheet/ai-draft-discovery-document.md`](worksheet/ai-draft-discovery-document.md). The checker
finds twelve errors (section 9.5). Find at least fourteen problems, including at least eight the
checker does not catch, and say for each which earlier Day's artifact proves it wrong.

<details><summary>Solution</summary>

Caught by the checker: missing open questions and change log; two-sentence problem statement;
decisions with no owner or date; refusals with "deferred", "phase 2" or no reason; two broken links;
technology on page one; invented numbers (67, 12000, 2.4).

Not caught, with the artifact that refutes each:

1. **The problem statement is not the signed one**, and blames "poor document quality" (Day 4 memo:
   the signed sentence).
2. **"Industry benchmark of two days"** has no source and sets a target nobody agreed (Day 9: 3 to 4
   days in two pilot branches by day 90).
3. **Stakeholders: three rows.** No CISO, compliance head, core-system owner, identity team, branch
   managers, auditor (Day 5 map).
4. **The workflow is the SOP's twelve steps.** No tracker, no WhatsApp, no 18:00 batch (Day 6 map).
5. **"50,000 labelled files are available to fine-tune"**: invented. Day 7 found 28,000 files with
   free-text reasons and no field-level ground truth.
6. **Fine-tuning on Godavari's files, "continuous"**: breaks "no model trains on our data" (the CISO,
   Day 5 constraints).
7. **"Secure, SOC 2 compliant cloud region"**: no India, no stage gates (Day 6 finding B1).
8. **Auto-approval above 0.9 confidence**: removes the human decision on every file (Day 6 finding A6;
   the S01 and S12 collision).
9. **"100 percent accuracy on KYC fields"**: an unverifiable promise; today is 4.1 percent decided
   incomplete (Day 9).
10. **"Saving 2.4 crore a year in analyst cost"**: Day 9 found capacity alone is minus 1.12 crore; it
    is a speed case.
11. **The chatbot as a phase 2 quick win**: it has no baseline (Day 4) and is parked (Day 8).
12. **Security review in weeks 8 to 10, integration in week 9**: Day 7 puts both first, in week one.
13. **All 300 branches live in week 8**: Day 8's plan is two branches in weeks 7 to 10, forty analysts
    by day 90.
14. **"Use RAG architecture, decided by Kaagaz, week 1"**: a vendor deciding before any interview.
15. **"Approved by Godavari leadership"**: no names, no date; nobody can say who signed.
16. **"Hallucination, mitigated by RAG grounding"**: a noun, not a risk with a signal and an owner.

</details>

**3.2 Write your own page one.** Without looking at the Godavari document, write page one from the six
artifacts in under 450 words, then run the checker on a file containing only your page one and a
problem-statement section with links to your sources. Compare with the Godavari version.

<details><summary>Solution</summary>

There is no single answer. Check: the signed sentence verbatim; three findings with numbers that
match their sources to the decimal; what we will do with no model name; 3 to 4 days in two pilot
branches by day 90; both +15.0 lakh and minus 1.12 crore; the four refusals; three or four decisions.
If W2 flags a number, either link its source or remove it.

</details>

**3.3 The readout, out loud.** With a partner (or an agent playing each role in turn), run the 60-minute
agenda of section 4.3 in 15 minutes. The partner raises, in order: the chatbot, on-prem, 100 percent
accuracy, and the CRM. Record it. Score yourself on four things per objection: acknowledged, asked
what would satisfy it, wrote a change or said "not now, because, and instead", read it back with the
decider's name.

<details><summary>Solution</summary>

Compare against sections 05.2 to 05.5. The common failures: arguing with the idea instead of giving a
reason the asker already accepted; giving no alternative; agreeing to the CISO's "never" instead of a
gate; promising 100 percent; and, most often, forgetting the read-back, which is what turns a
conversation into a signed change.

</details>

**3.4 Version it.** It is Friday 4 December, the week-6 checkpoint. The census found 3.4 percent of
the 700 files decided with a document missing; the CISO approved real files in the building on 3
December; the core-system owner reports one duplicate in the month of test calls. Write the change-log
rows for version 1.1 and say which sections change, and whether any change needs the room to sign
again.

<details><summary>Solution</summary>

Three rows. Section 7: the baseline for "decided with a document missing" becomes the census's 3.4
percent (a census has no sampling interval), and the compliance head's target becomes "below 3.4
percent", which she signs (inside scope, minor version, her signature). Section 8: the pilot stage's
gate is marked met, with the date. Section 9 and the plan: R5 has fired; live writes (M14, 8 December)
cannot start until a clean month, so M14 moves and the slip order applies; the COO signs the moved
date. No change touches a signed scope line, so 1.1, not 2.0. (Sections 06.4; Day 8, section 9.)

</details>
