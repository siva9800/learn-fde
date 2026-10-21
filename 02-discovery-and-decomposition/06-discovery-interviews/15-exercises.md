# 15 · Exercises

> Day 6 · Section 15 of 16 · [Chapter overview](README.md) · Previous: [14 · Interview questions](14-interview-questions.md) · Next: [16 · Further reading](16-further-reading.md)

---

Eleven exercises in three levels. The ones marked **(tested)** use the chapter's script, run on Python 3.14.3 (October 2026) from the chapter folder, with real output. Learning mode: write the questions, codes and findings yourself; use an assistant as the interviewee in a role-play or as a sceptical reviewer, not as the author. Try first, then open.

## Level 1: warm-up

**1.1 Leading or open?** Mark each and rewrite the leading ones. (a) "Show me the last file that came back." (b) "So the branches are the problem?" (c) "Would a dashboard help you?" (d) "What did you type today that was already typed?" (e) "You must hate the forty-second screen." (f) "Who do you ask when you are not sure?"

<details><summary>Solution</summary>

(a) open. (b) leading; "Where did the days go on the last file that took long?" (c) leading and hypothetical; "What do you look at first in the morning, and why?" (d) open. (e) leading; "What do you do while the screen loads?" (f) open; it finds the rule in someone's head. (Section 06.1.)

</details>

**1.2 Which architecture question?** For each answer, name the question it answers and what it forces: (a) "Nothing writes between five thirty and eight." (b) "The sanction is signed by a person." (c) "A branch user sees only their branch." (d) "Me. Always me." (e) "An audit query with my employee ID."

<details><summary>Solution</summary>

(a) how fresh, what time the batch runs: writes scheduled around the window; same-hour intake out. (b) what must never be automated: a human decision per file. (c) who may see what: query-time group filtering. (d) who corrects errors today: the review queue is for the analyst. (e) what happens when it is wrong: the compliance head sets the error rate; accepted fields record who accepted them. (Section 08.1.)

</details>

**1.3 Requirement or hypothesis?** Using the run in section 12.4: is each a requirement? (a) WHATSAPP_CHANNEL (b) DUPLICATE_ON_RETRY (c) HUMAN_DECISION_REQUIRED (d) FLAG_UNSURE_NOT_GUESS. For the hypotheses, how would you firm them up?

<details><summary>Solution</summary>

(a) requirement, six interviews. (b) hypothesis, one interview, but confirmed by the week-two spike, so it stays in section A labelled single-source. (c) hypothesis by itself, two interviews; combined with NEVER_AUTOMATE_DECISION (three) and the CISO's view log the finding A6 rests on four interviews. (d) requirement, four. Firm up a hypothesis with a test in the skeleton or by asking the question in the next interviews. (Section 10.3.)

</details>

## Level 2: apply

**2.1 Write the admin script for the capstone.** Krishna District Hospital Network (Day 42): discharge summaries and pre-authorisation. Write eight admin questions for the hospital's IT head, each with a "then" column.

<details><summary>What a strong answer contains</summary>

Who may read which patient's record, and what enforces it? Where do roles come from, and how fast do they change when a doctor rotates? Is there a see-everything role; would you create one for a vendor? Who viewed this record? Which fields may never be generated (dosage)? When does the HIS export run? What if a summary reaches the insurer twice? Where may my notes and a prototype live? Each "then" names the design consequence. (Sections 05.3, 05.7.)

</details>

**2.2 Shadow someone (real).** Shadow a colleague or family member through one complete unit of real work for an hour (a GST filing, a ticket, a ration-card renewal), with permission. Use the log template. Count the undocumented steps.

<details><summary>What to look for</summary>

At least one off-screen tool, one wait you would not have guessed, one judgement call made in seconds and written nowhere. If you found none, you helped or you asked too early. (Section 03.)

</details>

**2.3 Code a transcript.** Take transcript 08 (Guntur), delete its coded-notes table, and code it yourself using the existing code list where you can. Compare with the original.

<details><summary>Solution</summary>

The original has ten codes. Common differences: coding the scanner as a new code (it is PHONE_PHOTO_INPUT plus WHATSAPP_CHANNEL); missing WRONG_MEANS_CUSTOMER_AT_BRANCH ("Vijayawada never sees him. I do"); coding "market day" as a new code instead of BAD_DAY_MONTH_END. New codes are allowed; check the list first so that the tally can count them. (Section 10.2.)

</details>

**2.4 Break it, then fix it (tested).** Copy the transcripts to a scratch folder. In the CISO's transcript, change `BRANCH_ISOLATION` to `branch_isolation` and the kind of `SSO_NOT_AVAILABLE` to `blocker`. Predict the count for BRANCH_ISOLATION, then run the script.

<details><summary>Solution</summary>

```text
problems in the coded notes:
  - 04-the-ciso-admin.md: 'branch_isolation' is not UPPER_SNAKE_CASE
  - 04-the-ciso-admin.md: SSO_NOT_AVAILABLE has kind 'blocker', expected one of ['adoption', 'architecture', 'constraint', 'evidence', 'metric', 'scope']
...
BRANCH_ISOLATION                    4  requirement architecture                     admin, operator, operator lead
```

The malformed row is skipped, so BRANCH_ISOLATION drops from five interviews to four, and the CISO, the person who owns the rule, is no longer behind it. It is still a requirement. The lesson: a typo can quietly remove the most authoritative source; read the problems list before the table. (Section 13.3.)

</details>

**2.5 Predict the output (tested).** Before running it, predict what the script prints in the synthesis check if you delete finding B4 from the synthesis.

<details><summary>Solution</summary>

`MISSED: requirement-level codes not cited in the synthesis:` then `- WRONG_MEANS_AUDIT_FINDING (3 interviews)`, exit 0 (a miss is a warning; only unsupported codes fail). That is exactly what the first run printed before B4 was written. (Section 12.4.)

</details>

## Level 3: challenging

**3.1 Review this AI-written synthesis and find what is wrong (tested).** [`worksheet/ai-draft-findings.md`](worksheet/ai-draft-findings.md) is an assistant's synthesis of the same ten transcripts. Run the script on it, then read it with the transcripts open. Find at least eight problems. The script catches some; say which ones it cannot.

<details><summary>Solution</summary>

The script (exit 1):

```text
UNSUPPORTED: cited in the synthesis but said by no interviewee (invented findings):
  - AUTO_SANCTION_LOW_RISK
  - BUREAU_API_REALTIME
  - CHATBOT_WANTED
  - ENCRYPTED_OFFSHORE_OK
  - MANUAL_ACCURACY_92
  - REST_API_AVAILABLE
  - WHATSAPP_INGEST
MISSED: requirement-level codes not cited in the synthesis:
  - BATCH_6PM (4 interviews)
  - ERROR_CORRECTION_BY_ANALYST (3 interviews)
  - FILE_ORIGIN_SCAN (3 interviews)
  - FLAG_UNSURE_NOT_GUESS (4 interviews)
  - HANDWRITTEN_TELUGU (3 interviews)
  - MISSING_DOC_TOP (4 interviews)
  - NEVER_AUTOMATE_DECISION (3 interviews)
  - PAST_VENDOR_FAILURE (3 interviews)
  - TRACKER_LOSS_FEAR (3 interviews)
  - WAIT_ON_BRANCH (5 interviews)
  - WILLING_TO_LABEL (5 interviews)
  - WRONG_MEANS_AUDIT_FINDING (3 interviews)
```

The human review:

1. **Finding 1, the chatbot,** is invented; nobody asked for one (synthesis section D).
2. **Finding 2 says branch filtering "can be handled at index time".** The code is real; the conclusion is the opposite of the CISO's "at the moment of the query". The script cannot see this.
3. **Findings 3 and 4, a REST API and a real-time bureau API,** are invented. The core is a 2009 SOAP API; the bureau is reached only through the 18:00 batch.
4. **Finding 5 says data entry is the main bottleneck.** The REKEYING code is real but the conclusion launders the sponsor's version; five interviews say the days are waiting (WAIT_ON_BRANCH, missed).
5. **Finding 6 says the tracker can be retired and analysts would be happy to stop using it.** SHADOW_TRACKER is real; the claim is the reverse of TRACKER_LOSS_FEAR ("we needed the spreadsheet"). The script cannot see this.
6. **Finding 7, a 92 percent manual accuracy,** is invented; nobody has ever measured it, which is why the golden set exists.
7. **Finding 8 cites RULES_AS_SIGNED_CODE for the opposite of what it says.** The compliance head: "I do not want a machine deciding that a gas bill is an address proof." The script cannot see this.
8. **Finding 9 turns a tolerated channel into an integration** (WHATSAPP_INGEST is invented; the compliance head wants it to stop).
9. **Finding 10, processing in the vendor's cloud,** contradicts the CISO and the compliance head.
10. **Finding 11, auto-sanction,** contradicts the COO's own "a person signs the sanction".
11. **No requirement or hypothesis labels, no counts, no quotes, no "what was not found", no confirmation.**
12. **The recommendation** names technology, all 300 branches and auto-sanction, none of which any finding supports.

The script catches seven invented codes and twelve misses. It cannot catch findings 2, 5, 6 and 8, where a real code is attached to a false sentence. Those need a person with the transcripts open. (Section 12.5.)

</details>

**3.2 Write the readout paragraph.** In 120 words or fewer, no technology names, write the paragraph the COO reads about finding A1.

<details><summary>Model paragraph</summary>

"Five of your people told us, separately, that branch staff may see only their own branch's files, and your CISO confirmed that this rule comes from your directory, updated each night from HR. Anything we build will follow that rule on every request, at the moment it is made, so a manager who moves branches today cannot see the old branch tomorrow, and every view will be logged for seven years as she asked. We learned this in week two, which means it costs us nothing to build in. Learned in month three, it would have cost a month." (Section 08.)

</details>

**3.3 Role-play the sceptic.** Ask an assistant to play the senior analyst from transcript 09, with her history and her fears, and to answer only what she would plausibly know. Run the operator script for twenty minutes. Then write her failure model in five lines and compare it with the transcript.

<details><summary>What to look for</summary>

If your failure model has the monthly-as-annual error, "say I cannot read this", "not a percentage, the actual files" and "my employee ID on the audit query", you asked well. If the assistant volunteered features or enthusiasm, it broke character; note it, and notice how easily a model offers the sponsor's version. (Sections 06.3, 11.2.)

</details>
