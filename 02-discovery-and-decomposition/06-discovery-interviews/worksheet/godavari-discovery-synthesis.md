# Godavari discovery synthesis · ten interviews and three days of shadowing

> Day 6 artifact for the engagement folder. Written at the end of discovery week two from the ten coded transcripts in `transcripts/` and the shadowing logs. Every finding carries the code(s) it rests on, in square brackets, so that `code/tally_findings.py` can check that each one is supported by at least one transcript and report how many interviews support it. A finding supported by three or more independent interviews is a **requirement**; one or two is a **hypothesis** to test in the walking skeleton. Reviewed with Lakshmi, Srinivas and the Vijayawada team lead on week 2 Friday before it was filed. All people and numbers are synthetic.

**Customer:** Godavari Finance Ltd · **Vendor:** Kaagaz AI · **Author:** the FDE · **Interviews:** 10 (6 operators and upstream producers, 3 admins and blockers, 1 sponsor) · **Shadowing:** Lakshmi (one full morning), two Hyderabad analysts (one afternoon), Bhavani (one full file)

## A. Findings that change the architecture

These are the findings that, if discovered in month three, would force a redesign. Each one is already a line in Day 7's inputs table.

**A1 · Branch visibility is enforced by Active Directory groups synced nightly from HR, and retrieval must filter by the caller's groups at query time.** [BRANCH_ISOLATION] [ACCESS_VIA_AD_GROUPS] [FRESHNESS_NEXT_DAY]
Five interviews, independently: the CISO (the rule and its source), the core-system owner (the filter lives in the session, not the API), Srinivas (the manual exception and the two-day ticket), the Kukatpally manager (the one-day lag on transfer) and the Guntur manager ("I do not want them to see mine"). There is no "all branches" group and the CISO will not create one for a vendor. Consequence: anything that indexes or retrieves loan files must carry the user's groups into every query, resolved at the moment of the request, and the service account the tool runs under starts with no groups at all. Days 15 and 22 build it; Day 23's questionnaire has to describe it.

**A2 · The Excel tracker is the real state of every file, and the tool must take its place, not sit beside it.** [SHADOW_TRACKER] [TRACKER_LOSS_FEAR]
Five interviews. The analysts open it first; the team leads assign in it; the juniors learned the job from its columns; the senior analyst's test for a review screen is "does it know what I am waiting for". The COO did not know it existed and does not want "a better spreadsheet". Consequence: the first version reads the tracker's state (assignment, waiting-on, colour) and writes its own state back, so that there is one file and not two. Day 16 owns the integration; Day 33 owns the adoption risk.

**A3 · One file in five has a page that arrives by WhatsApp on an analyst's personal phone and never reaches the file of record.** [WHATSAPP_CHANNEL] [PHONE_PHOTO_INPUT]
Six interviews, including the compliance head, who knows and cannot stop it. The channel exists because the official route (re-scan at five, batch at two) costs two days. Consequence: the tool cannot ingest WhatsApp and must not try; it must make the proper route as fast as the improper one, by telling the branch on day one what is missing and accepting a resubmission the same day. The input you cannot use is still an input you plan around.

**A4 · The credit-check batch at 18:00 and the write window bound how fast any file can move.** [BATCH_6PM] [FRESHNESS_NEXT_DAY]
Four interviews. Nothing writes to the core between 17:30 and 20:00; results appear the next morning; a file finished after four is tomorrow's. Consequence: same-hour intake is out of scope; "three days" starts the morning after the file arrives; the integration layer schedules writes around the window. Day 7 step 1 carries it as a constraint; Day 16 implements it.

**A5 · CreateApplication has no idempotency, retries create duplicates, and a lookup operation nobody uses makes a client-side key possible.** [DUPLICATE_ON_RETRY] [IDEMPOTENCY_LOOKUP_EXISTS] [SANDBOX_STALE]
One interview, but the system owner's, and confirmed by the week-2 spike that produced a duplicate in the sandbox (Day 2's Thursday). A single-source finding is a hypothesis by the rule; this one is kept because it was reproduced. Consequence: the integration layer derives a key from file number and branch code and checks GetApplicationByFileNumber before every create; the sandbox's rules are three months stale, so only field validation is trusted there. The owner's condition for production writes is a month of logged, duplicate-free sandbox calls. Day 16.

**A6 · A human, named, signs every sanction, and the trail must answer "who decided, on what documents" for seven years.** [HUMAN_DECISION_REQUIRED] [NEVER_AUTOMATE_DECISION] [VIEW_LOG_REQUIRED]
Four interviews: the COO, the compliance head (speaking for the auditor), the senior analyst, and the CISO's view log. Consequence: the walking skeleton has an analyst approve every file; the decision, the approver and the document set are logged from day one; the CISO's "who viewed this file" is a logging requirement on retrieval, not an afterthought. Days 17, 18 and 20.

**A7 · The completeness rules are deterministic code that the compliance head signs, and the model never overrides them.** [RULES_AS_SIGNED_CODE] [ALTERNATIVES_UNWRITTEN] [CHECKLIST_DRIFT]
The compliance head set the condition and offered a week to write the acceptable-alternatives list that today lives "in my head and in Lakshmi's". Bhavani's send-backs are a third caution, not a missing document, because that list is unwritten. Single-source on the signing condition, so a hypothesis until she signs the first version; the unwritten list is two interviews. Consequence: rules as versioned code with her signature (Day 11); a published checklist version so that branches stop working from last year's.

**A8 · The system must say "unsure" rather than guess, especially on handwritten Telugu income proofs, and the analyst is the person who corrects errors today.** [FLAG_UNSURE_NOT_GUESS] [HANDWRITTEN_TELUGU] [ERROR_CORRECTION_BY_ANALYST] [PAST_VENDOR_FAILURE] [REVIEW_WILL_NOT_CATCH_ALL]
Four interviews asked for "unsure" in their own words. The 2019 OCR pilot guessed, read a monthly figure as annual on a handwritten Telugu declaration, and was switched off in six weeks. Bhavani's honest answer, "I would not know", shows that review by a busy analyst does not catch confident wrong figures. Consequence: confidence routing to a review queue (Day 18); handwritten fields stay manual until proven on the golden set; the per-document accuracy report the senior analyst asked for ("the actual files, not a percentage") is Day 14's output format.

## B. Constraints that cannot move

**B1 · No customer PII leaves India; nothing leaves the building before the CISO's review; no model trains on Godavari's data.** [NO_PII_OUTSIDE_INDIA] [NO_TRAINING_ON_DATA] [PROTOTYPE_ON_PREM_MASKED] [SECURITY_REVIEW_LONG]
The CISO and the compliance head, independently, and the same sentence the compliance head said in week one (Day 5). The review is eight weeks if the answers are complete; the COO has ordered it started in week two. The prototype runs on a machine in the building on fifty masked files the compliance head approves. Days 21, 23, 24.

**B2 · No vendor SSO this year; service accounts through the CISO personally; shadowing notes live on Godavari's SharePoint, not on the FDE's laptop.** [SSO_NOT_AVAILABLE] [NOTES_STAY_ON_SITE]
Day 22 designs around the read-only domain controller inside the VPC. The notes rule applies to this document.

**B3 · Nothing new in front of the analysts in March (RBI audit), and expect three times the volume in the last three days of every month.** [BAD_DAY_MONTH_END]
Seven of ten interviews described a bad day, and the bad days line up: month end, quarter end, the day after a holiday, market day in Guntur, March. Consequence: the 90-day plan's pilot avoids March and the load model plans for month-end peaks (Days 8 and 27).

**B4 · A wrong record costs Godavari an audit observation, and the person who carries it is the analyst, not the vendor.** [WRONG_MEANS_AUDIT_FINDING]
Three interviews, in three seats: the COO ("the RBI observation is worse than the loss"), the compliance head ("repeated, it is a finding") and the senior analyst ("an audit query, with my employee ID on it"). Consequence: the acceptable error rate is set by the compliance head, not the sponsor (Day 7 step 1), and every field the tool fills records who accepted it. Added after the first run of the tally script flagged it as a requirement the synthesis had missed.

## C. Findings that change the scope and the metrics

**C1 · The nine days are mostly waiting, not analysis.** [WAIT_ON_BRANCH] [REKEYING] [TURNAROUND_NUMBER]
A clean file takes a day and a half, batch included; an incomplete file takes eight or nine; a third arrive incomplete. The COO "had assumed the days were in Hyderabad". Srinivas's number is files per analyst per day, not turnaround. Both numbers go into Day 9's baseline.

**C2 · The top missing documents are address proof, then bank statement, then income proof in the far branches, and half of send-backs are the address-proof judgement call.** [MISSING_DOC_TOP] [SENDBACK_CAUTION] [SENDBACK_FREE_TEXT]
The send-back reason in the core is free text and cannot be counted; the tracker's "waiting on" column can. Consequence: the walking skeleton's completeness check starts with address proof and the signed alternatives list; the send-back reason becomes a coded rule the branch can read.

**C3 · Both sides want day-one feedback with the rule that fired, and both sides are offering their worst files for testing.** [DAY_ONE_FEEDBACK_WANTED] [BLAME_BETWEEN_SIDES] [WRONG_MEANS_CUSTOMER_AT_BRANCH] [WILLING_TO_LABEL]
Kukatpally: "thirty"; Guntur: "take the whole month"; Lakshmi and the senior analyst: "if my answers are the standard". Consequence: the golden set (Day 14) is seeded now with 100 to 200 real files drawn from send-backs and far-branch phone photos, not from clean files, labelled by Lakshmi and the senior analyst, with the compliance head signing the completeness labels.

**C4 · Files arrive as 30 to 40 page scans in whatever order the papers were in, and the far branches' files are phone photographs of handwritten Telugu documents.** [FILE_ORIGIN_SCAN] [PAGE_ORDER_UNLABELLED] [PHONE_PHOTO_INPUT]
Consequence: page classification is a workstream before extraction; the skeleton starts with SFTP scans from one branch and treats phone photos as the second slice.

**C5 · The SOP has twelve steps; the floor has nineteen.** [SOP_VS_REALITY] [SHADOW_NOTEBOOK]
Nobody on the floor has read the SOP since 2019. The tracker's seven columns and three colours, the personal phone lists of branch numbers, and the WhatsApp channel are the steps the SOP does not have. The situational map in `situational-map.md` is the week-one deliverable, reviewed with the people who gave it.

## D. What was not found, and should not be written

- Nobody asked for a chatbot. The word did not come up in any operator interview.
- Nobody described a REST API, a data warehouse or a credit bureau feed the tool could call directly; the bureau is reached only through the 18:00 batch.
- No interviewee gave a field-level accuracy figure for today's process; "correct" has never been measured per field, which is why the golden set is a workstream.
- The RBI auditor was not interviewed. The compliance head speaks for him, and every sentence attributed to him in this document is hers.

## E. Confirmation

Reviewed on week 2 Friday with Lakshmi, Srinivas and the Vijayawada team lead, who corrected three things: the two-wheeler clean-file time includes checking; gold loans have nine documents; the Guntur phone-photo share is "one in four normally, most of them this month". The nineteen-step map was walked through step by step and signed off by all three. The COO has seen section A and section C1.
