# Decomposition worksheet · Godavari Finance: nine days to three

> Filled by the FDE at the end of discovery week two, after the Day 4 scoring, the Day 5 stakeholder
> map and the Day 6 shadowing in Vijayawada. Every number is from the course's synthetic engagement.
> Run `python code/plan_from_worksheet.py worksheet/godavari-decomposition.md` from the chapter folder.

**Customer:** Godavari Finance Ltd, Hyderabad · **Sponsor:** the COO · **Date:** discovery week 2 · **Author:** Kaagaz AI FDE

## Step 1 · Clarify the goal and the trade-off

| Question | Answer |
|---|---|
| The goal in the sponsor's words | "Loan turnaround from nine days to three." |
| The goal rewritten as an outcome with a number and a date | Median turnaround for new loan files in the pilot branches from 9.2 days to 3 to 4 days by day 90, without raising the error rate the RBI auditor sees. |
| What is being optimised | Speed: days from file received to decision, and analyst hours per file. |
| What is being traded away, and who decides how much | Error rate at the field level and completeness misses; the compliance head decides the acceptable rate, the auditor judges it once a year. |
| The constraint that cannot move | No customer PII leaves India; mandatory KYC documents per RBI rules; no change to the core system's data model. |
| What the sponsor would accept as "done" | Pilot branches at 3 to 4 days median, measured the way the operators agree, with no new audit findings. |
| Assumptions I am making (to revisit) | The 9 days are mostly waiting, not analysis; intake and completeness are the biggest share of the wait; analysts will accept a review queue. |

## Step 2 · Stakeholders and the metric each accepts

| Stakeholder | Role | What they want | The metric they would accept | What they fear |
|---|---|---|---|---|
| COO | sponsor | a number the board recognises | median turnaround days, pilot branches | a demo that never reaches production |
| 40 credit-ops analysts | operators | less re-keying, fewer chases to branches | analyst hours per file; send-back rate | a tool that adds a step, or blame when it is wrong |
| Credit-ops team lead (Vijayawada) | operator and champion | the tracker's job done properly | files per analyst per day | losing the tracker before the tool works |
| CISO | blocker | nothing leaves India, no vendor with production credentials | passed security review; VPC in AWS Mumbai | a data incident with her name on it |
| Compliance head | blocker | mandatory documents never skipped | field-level accuracy on KYC fields; zero completeness misses | an audit finding caused by a model |
| Core-system owner | blocker turned partner | no duplicate records, no surprise load | zero duplicates; calls within batch window | the fourth vendor to break his system |
| RBI auditor | ghost | documented, reviewable decisions | an audit trail per file | automation without a human decision |
| Branch managers | operator (upstream) | fewer send-backs from credit-ops | files accepted first time | being blamed for incomplete files |

## Step 3 · Map the inputs

| Input | Shape | Owner | Freshness | Access today | What is missing or untrustworthy | Architecture risk |
|---|---|---|---|---|---|---|
| Loan application PDFs | scanned PDF, 8 to 40 pages, English and Telugu, some phone photos | branch ops / credit-ops | nightly SFTP batch | SFTP on-prem, service account via IT ticket | no page index; 31 percent lack a mandatory document | document classification is a workstream |
| Core lending system SOAP API | 14 operations, CreateApplication with 61 fields | core-system owner | visible after nightly batch | quarterly-refreshed sandbox; prod write needs CISO | no idempotency on create | integration must own idempotency |
| Excel file tracker | 40 workbooks, 19 columns, free text, colour coding | team lead | minutes | shared drive, no API | no timestamps | the tool must read and write the real state |
| Active Directory groups | group per branch and role, synced from HR | corporate IT | nightly | LDAP after security review | no cross-branch group | filter every query by caller's groups |
| WhatsApp photos | JPEG pages to personal numbers | nobody | same day | not allowed | pages not in the file of record | make resubmission easy instead |
| RBI KYC rules and internal checklist | Master Direction plus a Word checklist per product | compliance head | changes by notification | public plus compliance drive | acceptable alternatives not listed | rules in signed deterministic code |
| Historical decisions | 28,000 files, free-text send-back reasons | credit-ops, core owner | historical | report on request | no field-level ground truth | the golden set must be labelled by experts |

**Data that does not exist yet (and who will create it):** field-level ground truth for 100 to 200 files (two senior analysts, with the compliance head signing the completeness rules); timestamps for the baseline (a two-week hand-counted sample).

## Step 4 · Workstreams, sequenced by risk and value

| # | Workstream | Value (1 to 5) | Risk (1 to 5) | Depends on | Weeks | Owner | Why this score |
|---|---|---|---|---|---|---|---|
| W1 | Extraction: pages and fields from scanned PDFs | 5 | 4 | W3 | 6 | Kaagaz FDE | the core of the value; Telugu forms and phone photos make accuracy the big unknown |
| W2 | Completeness checks: deterministic rules per product | 4 | 2 | | 3 | Kaagaz FDE with compliance head | catches the 31 percent send-backs on day one; rules are knowable, so low risk |
| W3 | Evals: golden set of 100 to 200 labelled files | 3 | 4 | | 4 | Kaagaz FDE with two senior analysts | no ground truth exists; without it nobody can say extraction works |
| W4 | Integration: SFTP, tracker, SOAP create with idempotency | 4 | 5 | | 5 | Kaagaz FDE with core-system owner | duplicate records on retry and a quarterly sandbox are the biggest technical unknowns |
| W5 | Security review and VPC path | 2 | 5 | | 8 | Kaagaz security lead with CISO | long and outside our control; starting late is the usual way engagements die |
| W6 | Enablement: review queue, tracker migration, resubmission | 3 | 3 | W2 W4 | 4 | credit-ops team lead with FDE | adoption risk: analysts keep the tracker if the tool adds a step |

**Out of scope for now (each with a reason):** the branch chatbot (no baseline, Day 4); collections call summaries (different operators); any change to the core system's data model (the owner's condition); any processing outside India (the compliance head's condition).

## Step 5 · The walking skeleton

| Layer | What the thin version does | What is stubbed or manual | What it proves |
|---|---|---|---|
| Input | picks up one branch's two-wheeler loan PDFs from a sandbox SFTP folder | files copied by hand from the real SFTP, masked | we can read what the branch sends |
| Processing | classifies pages and extracts 12 mandatory fields | only two-wheeler forms; Telugu fields may be flagged "unsure" | the extraction path works on real scans |
| Checks | runs the two-wheeler completeness checklist as code | one product's rules only | the deterministic layer catches missing documents |
| Human in the loop | an analyst sees fields and flags, corrects, approves | a plain review page, no SSO, one user | analysts will use a queue |
| Output / system of record | CreateApplication in the core-system sandbox with an idempotency key | sandbox only; status not written back to the tracker | the integration path works end to end, no duplicates |
| Measurement | per-file time, fields corrected, completeness flags, logged | a CSV, not a dashboard | the metrics from Step 2 can be measured at all |

**Scope of the skeleton (one product, one site, one path):** two-wheeler loans, Kukatpally branch, SFTP scans only.

**What the skeleton must prove by the end of week 3:** a PDF goes in, fields and a completeness result come out, an analyst approves, a record lands in the sandbox, and the whole path is measured on ten files the analysts choose.

**Failure modes I expect, and what each would change:** Telugu field accuracy too low (add a Telugu-specific extraction workstream, keep those fields manual); SOAP sandbox unusable (build a stub with the owner's WSDL and move integration risk to week 5); analysts bypass the queue (enablement becomes the first workstream, not the last).

## Narration notes (for the out-loud run)

- Minute 0 to 5: restate the goal as a number; ask what "three days" means and what error rate the auditor accepts; name the assumption that the time is waiting, not analysis.
- Minute 5 to 10: the eight stakeholders and the metric each accepts; the compliance head and the core-system owner are where the plan can die.
- Minute 10 to 15: seven inputs, one per line; say which two do not exist yet (ground truth, timestamps) and who creates them.
- Minute 15 to 22: six workstreams; security review and integration start in week 2 because they are slow and outside my control; extraction is the value; evals before any model claim.
- Minute 22 to 25: the skeleton: one product, one branch, PDF in, fields and completeness out, analyst approves, record in the sandbox, measured. Then the failure modes.
