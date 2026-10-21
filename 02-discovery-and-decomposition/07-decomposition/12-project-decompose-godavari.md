# 12 · Project: Decompose Godavari, From Worksheet to Sequenced Plan

> Day 7 · Section 12 of 16 · [Chapter overview](README.md) · Previous: [11 · Production concerns](11-production-concerns.md) · Next: [13 · Mistakes and debugging](13-mistakes-and-debugging.md)

---

## 12.1 The brief

It is the end of discovery week two. You have Day 4's problem statement, Day 5's map and Day 6's
workflow. Before the discovery document (Day 10) and the 90-day plan (Day 8), you owe the engagement
folder three things:

1. a **filled decomposition worksheet** for Godavari, all five steps, in the chapter's template;
2. an **inputs inventory** as data, not prose, so the next person can read it in a table and so the
   two-week sample has something to be counted against;
3. a **sequenced plan**: the six workstreams ordered by risk and value with a reason for every
   position, produced from the worksheet by code so that the order is reproducible and the "why"
   column cannot be skipped.

Code is light in this chapter on purpose. The thinking is in the worksheet; the code checks it and
turns it into something the readout can show.

**Files:**

| Path | What |
|---|---|
| [`worksheet/decomposition-worksheet-template.md`](worksheet/decomposition-worksheet-template.md) | the empty template: five steps, one table each, narration notes |
| [`worksheet/godavari-decomposition.md`](worksheet/godavari-decomposition.md) | the filled Godavari worksheet (the answer to part A) |
| [`worksheet/ai-draft-godavari.md`](worksheet/ai-draft-godavari.md) | an AI-written draft with at least eight mistakes, for exercise 3.1 |
| [`code/inputs_inventory.py`](code/inputs_inventory.py) | writes the step-3 inventory and a 200-file synthetic sample to `data/` and prints the summary |
| [`code/plan_from_worksheet.py`](code/plan_from_worksheet.py) | reads a worksheet's Step 4 table, checks it, sequences it, writes `data/<name>-plan.json` and a week grid |

Everything was run on **Python 3.14.3** (October 2026), standard library only: no packages to install,
no API keys, no downloads. Run from the chapter folder:

```bash
python -X utf8 code/inputs_inventory.py
python -X utf8 code/plan_from_worksheet.py worksheet/godavari-decomposition.md
```

(`-X utf8` keeps Windows consoles from choking on the middle dot in headings; on Linux and macOS it is
harmless.)

## 12.2 Part A: fill the worksheet

Copy the template, rename it, and fill it in order. The rules the template enforces:

- **One line per cell.** If a cell wants a paragraph, the thinking is not finished. The exception is
  the "why this score" column in step 4, which may be a sentence.
- **No technology before step 5.** The template says so at the top; the script does not check it, but
  exercise 3.1 shows what happens when it is ignored.
- **The step 4 table's first cell is W1, W2, ...** so that the script can read it. Value and risk are
  1 to 5; "depends on" lists codes; "weeks" is an estimate; "owner" is a person or pair, not a department.

The filled Godavari worksheet is the chapter's answer; section 08 is its narrative. Do not read it until
you have filled your own, then compare row by row. The differences are the lesson, not the mistakes.

## 12.3 Part B: the inputs inventory as data

`code/inputs_inventory.py` holds step 3 as a dataclass per input (shape, volume, owner, freshness,
access, what is missing, the architecture risk) and writes it to `data/godavari_inputs_inventory.csv`.
It also generates a two-week sample of 200 loan files, seeded, with a channel, a language mix, four
document-presence flags, a turnaround and an hours figure per file, tuned so that the sample reproduces
the engagement's known numbers.

```text
== Step 3: the inputs inventory ==
7 input sources written to godavari_inputs_inventory.csv
input                                                 kind         owner
Loan application PDFs                                 document     branch operations (collected by the bran
Core lending system (2009) SOAP API                   api          the core-system owner (one engineer, 14
File status Excel tracker                             spreadsheet  the credit-ops team lead in Vijayawada
Active Directory groups                               directory    corporate IT (identity team)
WhatsApp photos from branch staff                     chat         nobody; it is an unofficial channel
RBI KYC document rules                                document     the compliance head
Historical decisions (approved, sent back, rejected)  file         credit-ops (data), the core-system owner

Architecture risks surfaced by the inventory (one per source):
  - page order and document type are not labelled, so classification is a workstream, not a detail
  - duplicate records on retry means the integration layer must own idempotency before any automation
  - the tracker is the real workflow state; the tool must read and write it or it will be ignored
  - branch managers must not see other branches' files: every query must filter by the caller's groups
  - an input that cannot be used is still an input you must plan around: the tool must make resubmission easy
  - the completeness rules must be deterministic code the compliance head signs, not model behaviour
  - no labelled ground truth means the eval set is a workstream with customer experts, not a download

== Two-week sample: 200 loan files written to godavari_loan_file_sample.csv ==
files by channel:        mixed 54, phone_photo 31, sftp_scan 115
files by language mix:   english 68, mixed 91, telugu 41
sent back at least once: 63 of 200 (32%)
median turnaround:       9.2 days
mean analyst hours/file: 4.6 h

what is missing, by document (share of files without it):
  has_pan                10%
  has_address_proof      18%
  has_income_proof       14%
  has_photo               4%

send-back rate by channel (why the walking skeleton starts with SFTP scans):
  mixed          44%  (n=54)
  phone_photo    55%  (n=31)
  sftp_scan      19%  (n=115)

send-back rate by product (why the skeleton starts with one product):
  two-wheeler       32%  (n=81)
  gold              24%  (n=49)
  small-business    30%  (n=44)
  personal          46%  (n=26)
```

Three things to take from the run. The "architecture risks" list is the sentence per input you say in
step 3 of the interview; the code makes you write one per row. The sample's numbers (32 percent, 9.2
days, 4.6 hours) are close to the engagement's known baseline (31 percent, 9.2 days, 4.5 hours), which
is what a synthetic sample is for and nothing more; Day 9 measures the real one. And the two breakdowns
at the end are the data behind step 5's "one product, one path" choice: clean SFTP scans are sent back a
third as often as phone photos, and two-wheeler loans are the largest group.

The generator is deliberately simple (a seeded `random.Random`, one dataclass per row, `csv.DictWriter`).
Read it once; the point is that step 3 can be data from day one.

## 12.4 Part C: the sequenced plan from the worksheet

`code/plan_from_worksheet.py` does four things: finds the `## Step 4` section in the worksheet, parses
every row that starts with a `W` code, runs the checks a reviewer would run, and sequences.

**The checks** (the script refuses to sequence until they pass):

- value and risk are 1 to 5; weeks is at least 1; every dependency names a row in the table;
- the "why this score" cell has at least four words (so the order can be defended in a readout);
- some workstream mentions evals, integration, security and enablement. This last check is crude, and
  it exists because those four are the workstreams an architecture-first decomposition leaves out.

**The sequencing rule** is section 06's: `priority = 2 x risk + 1 x value`; ties go to the riskier
one; a workstream cannot start before the week after each dependency starts (overlap on purpose, Day
8); and at most three FDE-owned workstreams run in any week (the customer's own workstreams, such as
the security review, do not consume the FDE's hours).

```text
== godavari-decomposition.md: 6 workstreams read from the Step 4 table ==

rank  code workstream                                     risk value  prio weeks start  end  owner
   1  W4   Integration: SFTP, tracker, SOAP create with i    5     4  14.0     5     1    5  Kaagaz FDE with core-system owner
   2  W5   Security review and VPC path                      5     2  12.0     8     1    8  Kaagaz security lead with CISO
   3  W3   Evals: golden set of 100 to 200 labelled files    4     3  11.0     4     1    4  Kaagaz FDE with two senior analysts
   4  W1   Extraction: pages and fields from scanned PDFs    4     5  13.0     6     2    7  Kaagaz FDE
   5  W2   Completeness checks: deterministic rules per p    2     4   8.0     3     5    7  Kaagaz FDE with compliance head
   6  W6   Enablement: review queue, tracker migration, r    3     3   9.0     4     6    9  credit-ops team lead with FDE

why each one sits where it does:
  1. W4 Integration: SFTP, tracker, SOAP create with idempotency: duplicate records on retry and a quarterly sandbox are the biggest technical unknowns (after nothing)
  2. W5 Security review and VPC path: long and outside our control; starting late is the usual way engagements die (after nothing)
  3. W3 Evals: golden set of 100 to 200 labelled files: no ground truth exists; without it nobody can say extraction works (after nothing)
  4. W1 Extraction: pages and fields from scanned PDFs: the core of the value; Telugu forms and phone photos make accuracy the big unknown (after W3)
  5. W2 Completeness checks: deterministic rules per product: catches the 31 percent send-backs on day one; rules are knowable, so low risk (after nothing)
  6. W6 Enablement: review queue, tracker migration, resubmission: adoption risk: analysts keep the tracker if the tool adds a step (after W2, W4)

weeks 1 to 3, the window in which the walking skeleton is built from a thin slice of every workstream:
  running: W4 Integration: SFTP, tracker, SOAP create with idempotency (weeks 1 to 5)
  running: W5 Security review and VPC path (weeks 1 to 8)
  running: W3 Evals: golden set of 100 to 200 labelled files (weeks 1 to 4)
  running: W1 Extraction: pages and fields from scanned PDFs (weeks 2 to 7)
how to read: priority = 2 x risk + 1 x value; ties go to the riskier one; at most 3 FDE-owned workstreams run in any week
wrote data/godavari-decomposition-plan.json and data/godavari-decomposition-plan.md
```

The week grid it writes, which goes straight into the discovery document:

| # | Workstream | w1 | w2 | w3 | w4 | w5 | w6 | w7 | w8 | w9 |
|---|---|---|---|---|---|---|---|---|---|---|
| W4 | Integration: SFTP, tracker, SOAP create with idempotency | ## | ## | ## | ## | ## |  |  |  |  |
| W5 | Security review and VPC path | ## | ## | ## | ## | ## | ## | ## | ## |  |
| W3 | Evals: golden set of 100 to 200 labelled files | ## | ## | ## | ## |  |  |  |  |  |
| W1 | Extraction: pages and fields from scanned PDFs |  | ## | ## | ## | ## | ## | ## |  |  |
| W2 | Completeness checks: deterministic rules per product |  |  |  |  | ## | ## | ## |  |  |
| W6 | Enablement: review queue, tracker migration, resubmission |  |  |  |  |  | ## | ## | ## | ## |

Read it against Day 8's published shape (discovery weeks 1 to 4, prototype weeks 3 to 6, pilot weeks 7
to 10): the three riskiest workstreams fill weeks 1 to 3, the skeleton is built from thin slices of
all of them in that window, and enablement runs into the pilot. The grid is a suggestion for Day 8 to
date, not a schedule.

The script also refuses bad input usefully. On the empty template:

```text
Step 4 table has no filled rows (W1, W2, ... with a workstream name): fill the worksheet first
```

And on the AI-written draft (section 15, exercise 3.1):

```text
== ai-draft-godavari.md: 5 workstreams read from the Step 4 table ==
problems (fix the worksheet before trusting the order):
  - no workstream mentions 'security': the decomposition is probably missing one
  - no workstream mentions 'enable': the decomposition is probably missing one
```

Those two are the mistakes a script can catch. The other six in that draft need a human, which is
the exercise.

## 12.5 Part D: the narration notes

The last block of the worksheet is five lines, one per time window of the 25-minute protocol (section
09). Fill them after the tables, not before: each line is the one thing you must have said by the end
of that window. Then run the protocol out loud against a timer, record it, and audit against section
9.7's checklist. That is the project's real deliverable; the files are its evidence.

## 12.6 What goes into the engagement folder

| Artefact | Used by |
|---|---|
| `worksheet/godavari-decomposition.md` (your version) | Day 8 (the dated plan), Day 10 (the decomposition section of the discovery document) |
| `data/godavari_inputs_inventory.csv` | Day 16 (the integration surface), Day 15 and 22 (the access rules) |
| `data/godavari_loan_file_sample.csv` | Day 9 (the shape of the baseline sample; the real one is hand-counted) |
| `data/godavari-decomposition-plan.md` (the week grid) | Day 8, Day 10 |
| the recording of your 25-minute run | Day 44 (compare against the drills), Day 46 (the defence runs on the same clock) |

## 12.7 Build it with AI

An FDE in 2026 would use a coding or chat agent in two ways here: to pressure-test the decomposition,
and to draft the code. The second is routine (both scripts are the kind of thing an agent writes
correctly in one pass). The first is where the value and the danger are.

**Context to provide:** the Day 4 problem statement, the Day 5 stakeholder map, the Day 6 workflow map
(the 19 steps, the tracker, the WhatsApp channel, the AD-group rule), the empty worksheet template, and
the rule that no technology may be named before step 5. Give it the real constraints in writing: "no
PII leaves India", "the core system's data model does not change", "the RBI auditor must see a human
decision per file".

**A strong prompt (pressure-test, not draft):**

> Here is my filled decomposition worksheet for a lender's loan-intake problem, and the discovery
> notes it was built from. Do not rewrite it. Review it as a sceptical FDE lead would, step by step:
> (1) which stakeholders are missing, especially upstream producers of the inputs, owners of systems we
> write to, and regulators or auditors who are not in any meeting; (2) which inputs I have described
> with a shape, owner, freshness or access that the discovery notes do not support; (3) which assumptions
> in step 1 are unstated; (4) which workstream has a risk score you would challenge, and why; (5) which
> layer of the walking skeleton is missing or not thin; (6) which failure modes I have not listed.
> For every point, cite the line in the discovery notes that supports it, or say explicitly that it is
> a guess. Do not invent any data source, system, team or number that is not in the notes.

**A second prompt (the interviewer):**

> Act as the interviewer for a 25-minute decomposition round. Give me the prompt "a city wants to cut
> emergency response times using call, traffic and ambulance GPS data" and nothing else. Answer my
> clarifying questions only with facts a real city dispatch centre would plausibly have, and say "assume
> what you like" to one in three. At minute five, push me with "just tell me the architecture". At the
> end, score me against these seven behaviours [paste section 9.2's list] with one sentence of
> evidence for each.

**What the agent typically gets right:** the structure (it knows the five steps and the vocabulary of
the guides); the checklist of generic stakeholders; plausible failure modes for a document pipeline;
the code for both scripts; playing the interviewer with a timer.

**What it typically gets wrong for this concept (check each):**

| Mistake | How it shows | Fix |
|---|---|---|
| **invents data that does not exist** | "the 50,000 historical applications with approval labels in PostgreSQL" (the AI draft in `worksheet/ai-draft-godavari.md`); a "credit bureau API"; "real-time" freshness for a nightly batch | every input it names must trace to a line in the discovery notes; the prompt demands the citation; anything without one is deleted |
| **skips stakeholders**, especially blockers and ghosts | a three-row table: sponsor, "loan officers", IT; no compliance head, no CISO, no core-system owner, no auditor, no branch managers | compare against Day 5's four roles plus the upstream producer and the system owner; the draft's sponsor is even the wrong person (CTO, not COO) |
| **names the technology in step 1** | "the LLM will improve both"; "the RAG chatbot deployed to 300 branches" as the definition of done | the rule is mechanical: no model, database or framework word before step 5; search the draft for them |
| **scores risk as difficulty** | RAG pipeline risk 2, evaluation risk 1, integration risk 2 | risk is "how likely to change the plan"; integration against a 2009 SOAP API with no idempotency is a 5 |
| **drops the non-AI workstreams** | no security review, no enablement, "integration" as one week of plumbing after the UI | the script's crude check catches two of these; the human check is "which four workstreams does an architecture-first plan always omit" |
| **the skeleton is not thin and not complete** | "all products, all branches, in week 2"; "human in the loop: not needed after week 2"; no measurement layer | one product, one site, one path; every layer present; the stubbed column filled |
| **states no assumptions, or states them as facts** | "loan data is available in a structured database" written as an assumption and then used as a fact in step 3 | each assumption gets a "what changes if wrong" and is revisited after step 3 |
| **agrees with you** | asked to review your worksheet, it praises it and suggests two cosmetic changes | ask it to argue the opposite order; ask "what would a CISO object to"; give it the scored behaviours as the rubric, not "is this good" |
| **writes the "why this score" cell as a label** | "core feature", "plumbing", "standard ML practice" | the script's four-word check is a floor; the real test is whether a COO would accept the sentence as a reason |

The two mistakes to watch most are the first two. An agent will produce a confident, well-formatted
inputs table containing systems the customer does not have, and a stakeholder list that omits exactly
the people who can stop the project. Both read as competence. Both are the interview's two most
common rejections, done by a machine.

## 12.8 How do you know it's right?

Whether a human or an agent wrote the decomposition, the checks are the same:

1. **Trace every input to evidence.** Each row of step 3 should point to a Day 6 interview, a document,
   or a system you were shown. A row with no source is an assumption; move it to step 1's assumptions
   list or delete it.
2. **Count the roles.** Step 2 has at least one sponsor, operators, two or more blockers, a ghost, the
   upstream producer of the main input, and the owner of the system you write to. Fewer than six rows
   on an enterprise problem is almost always missing someone.
3. **Search for technology words before step 5.** `grep -n -i "llm\|rag\|vector\|model\|fine-tune\|ocr\|database"`
   over steps 1 to 4 of your worksheet should return nothing, or only "the core lending system".
4. **Every metric is measurable from the skeleton, or has a stand-in that is** (section 4.3's table).
5. **Every position in the order has a sentence a COO would accept.** Run the script; read the "why"
   lines out loud; if one is a label ("plumbing"), it is not a reason.
6. **The riskiest two workstreams start in week one or two.** If the script's warning fires ("risk 5
   but starts in week 4"), say why in the readout or fix the table.
7. **The skeleton has every layer and a stubbed column.** A row with an empty "stubbed" cell is either
   not thin or not honest.
8. **Each expected failure maps to a plan change.** "Hallucination, mitigated by RAG" is not a failure
   mode; "Telugu accuracy too low, so those fields stay manual and a Telugu workstream is added" is.
9. **The sample numbers reconcile.** The synthetic sample's 32 percent, 9.2 days and 4.6 hours are near
   the engagement's 31, 9.2 and 4.5; if you change the generator and the numbers drift, the text that
   quotes them is wrong.
10. **The out-loud run passes the self-audit** (section 9.7), on a recording, not from memory.

**Review checklist:**

- [ ] goal rewritten with a number, unit, date, population, and the trade-off named with its decider
- [ ] constraints that cannot move written in step 1; assumptions listed with "what changes if wrong"
- [ ] six or more stakeholders, a metric each, the upstream producer and the ghost included, one conflict named
- [ ] every input row traceable to evidence; shape, owner, freshness, access, missing, architecture risk all filled
- [ ] data that does not exist named, with who creates it
- [ ] no technology words before step 5
- [ ] five to seven workstreams including evals, integration, security and enablement; value and risk 1 to 5 with a reason
- [ ] script runs clean; riskiest two start in week 1 or 2; the order is explainable line by line
- [ ] skeleton: one product, one site, one path; every layer present; stubbed column filled; what it proves by week three; three expected failures with plan changes
- [ ] the 25-minute run recorded and audited

## 12.9 Extend it

- Fill the worksheet for the trucking firm (section 10.2) and run the script. Does the order match the
  section's table? Where it differs, which is right, and why?
- Add a column `must_start_by` to the step 4 table and make the script warn when the sequencing pushes
  a workstream past it (the security review has a hard deadline: the VPC by week 8).
- Change `RISK_WEIGHT` to 1 and `VALUE_WEIGHT` to 2 and rerun. Extraction moves to the top. Write the
  paragraph you would need in the readout to defend that order, and notice how much harder it is.
- Extend the generator with a `branch` effect (Guntur sends more phone photos) and check whether the
  "one site" choice in step 5 would change.
- Write the Day 10 decomposition section from the worksheet: one page, no model names, numbers with
  their methods.
