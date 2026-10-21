# Discovery document · Godavari Finance: loan-file intake and completeness

> Engagement folder · Day 10 · Version 1.0, signed at the week-4 checkpoint, Friday 20 November 2026 (M08) · Pre-read version 0.9 sent Wednesday 18 November · Author: the Kaagaz AI FDE · Next version: 1.1 at the week-6 checkpoint, Friday 4 December
> This document assembles Days 4 to 9. It quotes and links the source artifacts rather than restating them; where a number appears here, its method is in the linked source. Every person, date and number at Godavari is invented for the course.
> **How to read it.** The COO: page one. The CISO and the compliance head: section 8, then sections 9 and 10. Srinivas and the Vijayawada team lead: sections 3 and 6. Everyone: section 12 and the sign-off. Text marked **[changed at readout, Cn]** differs from the pre-read; the change log lists all four.

## Page one: what we found, what we will do, what we ask you to sign

**The problem, as signed in week one:** new loan files take a median of nine days from receipt to decision because intake is manual and a third of files are incomplete ([Day 4 memo](../../04-picking-the-problem/worksheet/godavari-problem-selection-memo.md)).

**What we found.**

1. **The nine days are mostly waiting.** The hand count puts the median at 9.1 days (8.7 to 9.7); of each file's time, 6.4 days is waiting in the queue to be opened ([baseline pack](../../09-success-metrics-and-business-case/worksheet/godavari-baseline-pack.md)).
2. **The work that can change is 1.59 of the 4.6 analyst hours a file**: re-keying, completeness checks and chasing branches. 28 percent of files are sent back at least once (the monthly report says 31; both are consistent).
3. **The real workflow has 19 steps, not the SOP's 12.** The Excel tracker is the true state of every file, and one file in five has a page that arrives by WhatsApp and never reaches the file of record ([situational map](../../06-discovery-interviews/worksheet/situational-map.md)).

**What we will do.** Read every new file on the day it arrives, check it against the compliance head's signed rules, tell the branch the same day what is missing, and put the fields in front of an analyst who approves every file. A two-branch pilot (Kukatpally and Guntur) starts on 7 December; all 40 analysts work from the new queue by 22 January 2027 ([90-day plan](../../08-scoping-the-first-90-days/worksheet/godavari-90-day-plan.md)).

**The target.** Median turnaround of 3 to 4 days in the two pilot branches by day 90, with fewer files decided with a missing document than today's 4.1 percent.

**The money, honestly.** At base the system is worth about 15.0 lakh a year net. On analyst hours alone it costs 1.12 crore a year more than it saves; the case rests on faster files keeping customers who walk away today, and breaks even at about 38.8 loans a month kept. The pilot measures that ([business case](../../09-success-metrics-and-business-case/worksheet/godavari-business-case.md)).

**What we will not do** (signed 6 November): build the branch CRM; build collections call summaries; change the core system's data model; send, store or process customer PII outside India.

**Decided at this readout** (section 12): the pilot goes ahead on these terms, subject to the 4 December go or no-go; an analyst decides every file; the branch chatbot is not in these 90 days; nothing leaves the Hyderabad building until the CISO approves in writing.

## 1. The problem statement

> New loan files take a median of nine days from receipt to decision because intake is manual and a third of files are incomplete.

Signed in week one by the COO, Srinivas (credit-ops team lead, Hyderabad) and the credit-ops team lead, Vijayawada; read by Lakshmi ("yes, that is the job"). Unchanged since. The measured numbers inside it (9.1 days, 28 percent) are in section 7; the sentence keeps its round words because the people who signed it would recognise them.

Why this problem and not the other seven: the [Day 4 memo](../../04-picking-the-problem/worksheet/godavari-problem-selection-memo.md), sections 4 to 6. Intake scored 93 of 100 and passed all three gates.

## 2. The people

The full map, with power, interest and each person's version of the problem, is the [Day 5 stakeholder map](../../05-the-stakeholder-map/worksheet/godavari-stakeholder-map.md). This is the part that decides the next 90 days.

| Who | Role | The number they would believe | Signs or can stop |
|---|---|---|---|
| the COO | sponsor | median turnaround days, pilot branches | signs |
| the CISO | blocker | security review passed; nothing leaves India | veto |
| the compliance head (speaks for the RBI auditor) | blocker, rule owner | zero completeness misses on the golden set | veto |
| Srinivas and the Vijayawada team lead (champion) | operator leads | files per analyst per day | sign section B of the metric definitions |
| 40 analysts; Lakshmi and the senior analyst as eval owners | operators | analyst hours per file; field accuracy on files they labelled | stop it by ignoring it |
| the core-system owner | system owner | zero duplicate records; every call inside the batch window | slows it |
| corporate IT identity team | blocker (admin) | service account approved, group filtering verified | slows it |
| branch managers (300; Kukatpally and Guntur first) | upstream producers | files accepted first time | input quality |
| Kaagaz's CEO and engagement lead | our side | renewal evidence by month six | funds our side |

The six collisions between these people, each with a decider, are in [the conflicts file](../../05-the-stakeholder-map/data/godavari-conflicts.csv); the two left for this readout are decided in section 12.

## 3. The workflow as it really is

The SOP (2019) has twelve steps. Shadowing and ten interviews found nineteen; the seven in no document are where the days and the workarounds are. The full table and diagram: [situational map](../../06-discovery-interviews/worksheet/situational-map.md), reviewed step by step with Lakshmi, Srinivas and the Vijayawada team lead.

| Where the time goes | Steps | What changes in the pilot |
|---|---|---|
| the file waits to be opened (6.4 days of the 9.1) | 4 to 6 | fields and the completeness result are ready by 9 am the morning after arrival |
| the analyst re-keys 61 fields | 7 | the analyst checks and corrects pre-filled fields instead |
| the junior sends back an unlisted address proof "to be safe" | 9 | the compliance head's signed alternatives list decides, as a rule with a name |
| the analyst phones the branch and writes "waiting on X since" in the tracker | 10, 11 | the branch is told on day one which document is missing and which rule fired |
| the late page arrives by WhatsApp and the core file stays incomplete | 14 | not ingested; the proper route is made as fast: same-day resubmission |
| the 18:00 batch; no writes 17:30 to 20:00 | 17 | unchanged; writes are scheduled around the window |
| a named credit manager sanctions | 19 | unchanged; never automated |

**For the team leads:** the tracker is not replaced. The system reads its state and writes file status back, so there is one file and not two ([finding A2](../../06-discovery-interviews/worksheet/godavari-discovery-synthesis.md)). Assignment stays with you.

## 4. Findings that change the architecture

From the [discovery synthesis](../../06-discovery-interviews/worksheet/godavari-discovery-synthesis.md), section A. Each one, found in month three, would have forced a redesign.

| # | Finding | What it forces |
|---|---|---|
| A1 | branch visibility comes from Active Directory groups synced nightly from HR; no all-branches group | every query filtered by the caller's groups at the moment of the request; the service account starts with none |
| A2 | the Excel tracker is the real state of every file | read the tracker, write status back |
| A3 | one file in five has a WhatsApp page that never reaches the file of record | make resubmission as fast as WhatsApp; do not ingest it |
| A4 | the 18:00 batch and the write window bound every file | three days starts the morning after arrival; same-hour intake is out of scope |
| A5 | CreateApplication has no idempotency; a retry created a duplicate in the test copy | a key from file number and branch code, checked before every create |
| A6 | a named human signs every sanction; the trail must answer "who decided, on what documents" for seven years | an analyst approves every file; decision, approver and documents logged from day one |
| A7 | completeness rules are deterministic code the compliance head signs; the model never overrides them | rules as versioned code with her signature |
| A8 | the system must say "unsure" rather than guess, especially on handwritten Telugu income proofs | uncertain fields go to review; handwritten fields stay manual until proven on the golden set |

## 5. The decomposition and the walking skeleton

The goal, rewritten in [Day 7's step 1](../../07-decomposition/worksheet/godavari-decomposition.md): "median turnaround for new loan files in the pilot branches from 9.2 days to 3 to 4 days by day 90, without raising the error rate the RBI auditor sees" (9.2 was the ops report; the hand count since measured 9.1). The trade-off is speed against error rate, and the compliance head, not the sponsor, sets the acceptable rate.

Six workstreams, ordered risk first ([sequenced plan](../../07-decomposition/data/godavari-decomposition-plan.md)):

| # | Workstream | Why it sits where it does |
|---|---|---|
| W4 | Integration: SFTP, tracker, SOAP create with idempotency | duplicates on retry and a stale test copy are the biggest technical unknowns |
| W5 | Security review and VPC path | long and outside our control; starting late is how engagements die |
| W3 | Evals: golden set of 100 to 200 labelled files | no ground truth exists; without it nobody can say extraction works |
| W1 | Extraction: pages and fields from scanned PDFs | the core of the value; Telugu forms and phone photos make accuracy the unknown |
| W2 | Completeness checks: deterministic rules per product | catches send-backs on day one; the rules are knowable, so low risk |
| W6 | Enablement: review queue, tracker migration, resubmission | analysts keep the tracker if the tool adds a step |

**The walking skeleton** (M07, week 3): one product (two-wheeler), one branch (Kukatpally), one path (SFTP scans). A PDF goes in; pages are classified and 12 mandatory fields extracted; the completeness rules run as code; an analyst corrects and approves on a plain review page; a record lands in the core system's test copy with an idempotency key; every step is timed. Its measured results are reported at the week-6 checkpoint.

## 6. The 90-day plan

Dated in the [90-day plan](../../08-scoping-the-first-90-days/worksheet/godavari-90-day-plan.md) (signed 6 November). Day 1 was Monday 26 October 2026; the day-90 review is Friday 22 January 2027.

| Phase | Dates | Exit decision |
|---|---|---|
| Discovery | 26 Oct to 20 Nov | this readout: commit to the pilot |
| Prototype | 9 Nov to 4 Dec | week-6 go or no-go (M12) |
| Pilot: Kukatpally and Guntur, six analysts | 7 Dec to 1 Jan | pilot results (M17, 4 Jan) |
| Rollout and handoff | 4 Jan to 22 Jan | handoff check (M20) and the day-90 review (M22) |

The milestones the next two weeks turn on: the compliance head signs the two-wheeler rules (M10, 2 December); the CISO approves real files from two branches on the machine in the building (M11, 3 December); go or no-go (M12, 4 December). Two dates we do not control: the core-system release freeze from 17 December, and the RBI inspection from about February.

**[changed at readout, C4]** The week-6 checkpoint pack includes the per-file failure list from the golden set: the actual files the system got wrong, not only a percentage, as the senior analyst asked.

## 7. The baseline and the business case

Measured in the [baseline pack](../../09-success-metrics-and-business-case/worksheet/godavari-baseline-pack.md) (120 stratified files, a fortnight with no month end or festival, 95 percent intervals, a second counter on 12 files). Definitions are pre-registered and signed alongside this document in the [metric definitions](../../09-success-metrics-and-business-case/worksheet/godavari-metric-definitions.md).

| Metric | Ops report | Hand count | 95% interval |
|---|---|---|---|
| median turnaround, days | 9.2 | 9.1 | 8.7 to 9.7 |
| analyst hours per file | 4.5 | 4.6 | 4.5 to 4.7 |
| send-back rate | 31% | 28% | 21% to 35% |
| addressable hours per file | - | 1.59 | 1.52 to 1.66 |
| decided with a mandatory document missing | - | 4.1% | 0.9% to 7.2% |
| withdrawn by the customer | - | 10.1% | 5.2% to 14.9% |

**The case** ([one page](../../09-success-metrics-and-business-case/worksheet/godavari-business-case.md); [generated summary](../../09-success-metrics-and-business-case/data/godavari-baseline-and-case.md)): net +15.0 lakh a year at base; minus 1.12 crore on capacity alone; break-even at 38.8 loans a month kept; the median falls to about 3.6 days in the model. It is a speed case, not a cost case. What decides it: field accuracy of at least 90 to 95 percent on the golden set's mandatory fields; the pilot's withdrawal rate against 10.1 percent, weekly; the contribution per loan confirmed by finance; who pays for serving (section 12).

**Promised, as ranges:** the COO, 3 to 4 days in the pilot branches by day 90; the team leads, addressable hours 0.5 to 0.9 a file and queue age under 2 days; the compliance head, no mandatory document missed by the rules on the golden set and fewer than 4.1 percent decided incomplete in production, monthly; branch managers, a missing-document notice the day the file arrives.

**[changed at readout, C3]** Before the go or no-go, Bhavani and the FDE count every file in the 700-file baseline frame for "decided with a mandatory document missing", because an interval of 0.9 to 7.2 percent is too wide to judge a "below today" promise against.

## 8. Data and security (for the CISO and the compliance head)

The conditions below were said in week one and have not moved ([constraints list](../../05-the-stakeholder-map/worksheet/godavari-stakeholder-map.md); [finding B1](../../06-discovery-interviews/worksheet/godavari-discovery-synthesis.md)). The security questionnaire answers have been with the CISO since 3 November (M03).

| Condition | Said by | How the plan meets it |
|---|---|---|
| no customer PII leaves India, in any environment, including tests, logs and backups | the compliance head; the CISO | will-not-do line 4; production only in Godavari's VPC in AWS Mumbai |
| no model trains on Godavari's data | the CISO | a contract term, reviewed in the security questionnaire |
| no vendor holds production credentials | the CISO | service accounts issued through the CISO, held in Godavari's account |
| branch managers do not see other branches' files | the CISO; confirmed in shadowing | group filtering at query time from the first query (finding A1) |
| "who viewed this file" is logged for seven years | the CISO | view logging on every retrieval, not added later (finding A6) |
| shadowing notes and files stay on Godavari's SharePoint | the CISO | applies to this document |

**Where files are processed, stage by stage.** **[changed at readout, C2]** The CISO asked that nothing run outside the building before a prototype has been reviewed. We agreed the stages below, each with her written approval as the gate.

| Stage | Dates | Where | Which files | Gate (the CISO, in writing) |
|---|---|---|---|---|
| skeleton and prototype | 26 Oct to 4 Dec | a machine inside the Hyderabad building | masked files approved by the compliance head; the golden set | in place since week one |
| pilot | from 7 Dec | the same machine | real files from Kukatpally and Guntur | M11, 3 December |
| production | from 4 Jan | Godavari's VPC in AWS Mumbai | all files | M15 (review passed, 16 December) and a separate approval of the cutover (M16) |

If M15 slips, the pilot stays in the building and the cutover moves; the slip order is in the [90-day plan](../../08-scoping-the-first-90-days/worksheet/godavari-90-day-plan.md), section 9. The deployment-model argument in full is for the week-6 checkpoint.

## 9. Risks

| # | Risk | Early signal | Response | Owner |
|---|---|---|---|---|
| R1 | handwritten Telugu fields too inaccurate to pre-fill | golden-set accuracy on those fields at week 6 | those fields stay manual; a Telugu workstream is scoped for the next 90 days | the FDE with the eval owners |
| R2 | field accuracy below 90 percent, so the case is below break-even before the pilot | the week-6 accuracy report | narrow the pre-filled fields; go or no-go decides | the FDE; the COO decides |
| R3 | faster files do not keep customers, and the case is negative | pilot withdrawals, weekly, against 10.1 percent | renewal and price terms for the engagement lead and the COO | Kaagaz engagement lead |
| R4 | analysts keep the tracker open beside the queue | files opened in the tool below 90 percent | the system writes the tracker; enablement moves first | the two team leads |
| R5 | duplicates in the live core system | any duplicate in the month of logged test calls | no live writes (M14) until a clean month | the core-system owner |
| R6 | the security review misses 16 December and the freeze | open questionnaire items on 4 December | pilot stays in the building; cutover moves | the CISO with the Kaagaz security lead |
| R7 | the RBI inspection takes the compliance head away before rules for a second product are signed | inspection dates confirmed | gold loans move to the next 90 days (slip order, step 1) | the compliance head |

## 10. What we will not do

### 10.1 We will not do these

Signed by the COO and Kaagaz's engagement lead on 6 November ([90-day plan](../../08-scoping-the-first-90-days/worksheet/godavari-90-day-plan.md), section 6); read out and reaffirmed at this readout.

| # | We will not | Because | And instead | Agreed by |
|---|---|---|---|---|
| 1 | build the branch CRM | not Kaagaz's product; no other lender would buy Godavari's; it would keep an FDE on site for a year doing work Godavari's IT or a CRM vendor does better | file status and the missing-document list are exposed so a CRM or the tracker can read them | the COO; the Kaagaz CEO and engagement lead |
| 2 | build collections call summaries | a different team, vendor-held Telugu recordings, DPDP consent open, the collections head not in the room | a later-cycle candidate with the collections head as sponsor | the COO |
| 3 | change the core system's data model, or ask for a change | the core-system owner's condition; every field we write already exists | write only through the existing operations | the core-system owner; the COO |
| 4 | send, store or process customer PII outside India, in any environment, including tests and logs | the compliance head's and the CISO's condition | production in Godavari's VPC in AWS Mumbai (section 8) | the compliance head; the CISO; the COO |

### 10.2 Not in these 90 days

| Candidate | Not now, because | Revisit |
|---|---|---|
| branch chatbot for policy questions | no baseline: nobody counts the calls | Kukatpally logs policy calls from 9 November **[changed at readout, C1]** and Guntur from 23 November; scored at the day-90 review |
| income verification from bank statements | it waits on intake | first candidate for the next 90 days |
| credit-memo drafting | it needs intake's fields | after intake is in daily use |
| KYC and periodic re-KYC | the compliance head: not this year | second cycle, with her as sponsor |
| auto-approval of clean files | the auditor's condition: a human decision on every file (decision D07) | not before the 2027 inspection closes |

## 11. Open questions

| # | Question | Why it matters | Owner | Due |
|---|---|---|---|---|
| Q1 | what is the contribution per loan, in writing from finance? | the second-largest swing in the case | the COO, through finance | 27 Nov |
| Q2 | who pays for serving: Godavari's AWS bill or Kaagaz's subscription? | the same 26 lakh is counted on both sides | Kaagaz engagement lead with the COO | 4 Dec |
| Q3 | when does the RBI inspection start on site? | the Vijayawada wave must finish before it | the compliance head | 4 Dec |
| Q4 | has IT named the application-support engineer? | handoff (M21) needs him from week 2 | IT, through the COO | 27 Nov |
| Q5 | how many withdrawals does a faster file prevent? | the case rests on it | the FDE with the team leads | 4 Jan (M17) |

## 12. Decisions needed, and who makes them

### 12.1 Decided at this readout

| # | Decision | Decided by | Date |
|---|---|---|---|
| D05 | commit to the two-branch pilot from 7 December on these terms, subject to M12 | the COO | 20 Nov 2026 |
| D06 | the branch chatbot is not in these 90 days; Guntur joins the call count | the COO | 20 Nov 2026 |
| D07 | an analyst decides every file; no auto-approval in these 90 days | the compliance head, for the auditor | 20 Nov 2026 |
| D08 | processing stays in the building until each written gate in section 8 | the CISO | 20 Nov 2026 |
| D09 | the compliance target as written in section 7, with the census before M12 | the compliance head | 20 Nov 2026 |
| D10 | the branch CRM stays on the will-not-do list | the COO; Kaagaz engagement lead | 20 Nov 2026 |

### 12.2 Still to decide

| # | Decision | Who decides | By |
|---|---|---|---|
| N1 | the two-wheeler completeness rules, signed (M10) | the compliance head | 2 Dec 2026 |
| N2 | real files from two branches approved in the building (M11) | the CISO | 3 Dec 2026 |
| N3 | go or no-go for the pilot (M12) | the COO | 4 Dec 2026 |
| N4 | who pays for serving (Q2) | Kaagaz engagement lead with the COO | 4 Dec 2026 |

## Decision log

Every decision on this engagement, newest last. A decision is never edited; a later one supersedes it and says so.

| ID | Date | Decision | Decided by | Why | Source |
|---|---|---|---|---|---|
| D01 | 30 Oct 2026 | the engagement attacks loan-file intake and completeness | the COO; Srinivas; the Vijayawada team lead | scored 93 of 100; passed all three gates | [Day 4 memo](../../04-picking-the-problem/worksheet/godavari-problem-selection-memo.md) |
| D02 | 6 Nov 2026 | the acceptable error rate is set by the compliance head; the COO's number is measured inside it | the compliance head | the S01 and S08 collision | [conflicts](../../05-the-stakeholder-map/data/godavari-conflicts.csv) |
| D03 | 6 Nov 2026 | the 90-day plan, the will-not-do list and the parked list | the COO; Kaagaz engagement lead | week-2 checkpoint | [90-day plan](../../08-scoping-the-first-90-days/worksheet/godavari-90-day-plan.md) |
| D04 | 18 Nov 2026 | an address proof is present only if it is in the file of record, legible and on the signed list | the compliance head | the second count found the disagreement | [baseline pack](../../09-success-metrics-and-business-case/worksheet/godavari-baseline-pack.md) |
| D05 | 20 Nov 2026 | commit to the two-branch pilot, subject to M12 | the COO | the week-4 checkpoint question | this document |
| D06 | 20 Nov 2026 | chatbot not now; Guntur joins the call count | the COO | no baseline; one more branch makes the count credible | section 10.2 |
| D07 | 20 Nov 2026 | a human decision on every file; no auto-approval | the compliance head, for the auditor | the S01 and S12 collision; the COO cannot overrule | [conflicts](../../05-the-stakeholder-map/data/godavari-conflicts.csv) |
| D08 | 20 Nov 2026 | staged processing with the CISO's written gates | the CISO | her request at the readout | section 8 |
| D09 | 20 Nov 2026 | the compliance target and the 700-file census | the compliance head | the interval is too wide to judge "below today" | section 7 |
| D10 | 20 Nov 2026 | the branch CRM stays out | the COO; Kaagaz engagement lead | raised again for branch follow-ups; the reason has not changed | section 10.1 |

## Change log

| Version | Date | What changed | Why |
|---|---|---|---|
| 0.9 | Wed 18 Nov 2026 | pre-read to everyone in the room, with the baseline pack | two days to read before the readout |
| 1.0 | Fri 20 Nov 2026 | C1: Guntur added to the policy-call count (10.2) | the COO asked for the chatbot; the count is the "instead" |
| 1.0 | Fri 20 Nov 2026 | C2: the stage-by-stage gates written into section 8 | the CISO asked for on-prem before any prototype |
| 1.0 | Fri 20 Nov 2026 | C3: the 700-file census before M12 (section 7) | the compliance head would not accept "below 4.1 percent" on a 0.9 to 7.2 interval |
| 1.0 | Fri 20 Nov 2026 | C4: the per-file failure list in the week-6 pack (section 6) | the senior analyst's condition for trusting the accuracy number |

## Sign-off

Signing means: this is the problem, these are the numbers and their methods, this is the plan we will be held to, and these are the things we will not do. It does not change the contract.

| Role | Signed | Date |
|---|---|---|
| the COO, Godavari Finance (sponsor) | signed | 20 Nov 2026 |
| the CISO | signed, with the gates in section 8 | 20 Nov 2026 |
| the compliance head | signed, with the target in section 7 | 20 Nov 2026 |
| Srinivas, credit-ops team lead, Hyderabad | signed | 20 Nov 2026 |
| the credit-ops team lead, Vijayawada | signed | 20 Nov 2026 |
| Kaagaz AI engagement lead | signed | 20 Nov 2026 |
| the Kaagaz AI FDE (author) | signed | 20 Nov 2026 |
