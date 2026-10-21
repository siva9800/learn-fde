# 08 · Project: The Godavari Stakeholder Map, the Three Scripts, and the Grid From Data

> Day 5 · Section 8 of 12 · [Chapter overview](README.md) · Previous: [07 · 2026 patterns and production concerns](07-2026-patterns-and-production-concerns.md) · Next: [09 · Mistakes and debugging](09-mistakes-and-debugging.md)

---

## 8.1 The brief

It is the end of week 0. Day 4's problem statement is signed. Before the first shadowing session
(Day 6) you owe the engagement folder three things:

1. **The Godavari stakeholder map**: a table with one row per person or group who can fund, use,
   veto, slow, judge or ignore the system, a Mermaid diagram of the same, the constraints list it
   starts, the customer's calendar, and the collisions with a decider each.
2. **Three persona interview scripts** for the mapping conversations: end user, admin and IT,
   executive sponsor. Thirty minutes each, every question tied to the column it fills.
3. **A small standard-library Python script** that reads the map as CSV and prints the
   power-interest grid, who can stop the work and how, whose Tuesday changes, the sponsor's version
   beside the operators', the reviewer's checks, and the collisions. The thinking is in the table;
   the script makes the gaps impossible to ignore.

**Files:**

| Path | What |
|---|---|
| [`worksheet/stakeholder-map-template.md`](worksheet/stakeholder-map-template.md) | the empty map: eleven columns, the roles to check for, constraints, calendar, collisions, readout room, change log |
| [`worksheet/godavari-stakeholder-map.md`](worksheet/godavari-stakeholder-map.md) | the filled Godavari map, week-1 version (the answer to part A) |
| [`worksheet/interview-script-end-user.md`](worksheet/interview-script-end-user.md), [`-admin-it.md`](worksheet/interview-script-admin-it.md), [`-executive-sponsor.md`](worksheet/interview-script-executive-sponsor.md) | the three persona scripts (part B) |
| [`worksheet/ai-draft-stakeholder-map.md`](worksheet/ai-draft-stakeholder-map.md) and `worksheet/ai-draft-stakeholders.csv` | an agent's draft with at least ten problems, for exercise 3.1 |
| [`data/godavari-stakeholders.csv`](data/godavari-stakeholders.csv) | the map as data: one row per stakeholder, fifteen columns |
| [`data/godavari-conflicts.csv`](data/godavari-conflicts.csv) | the six collisions: who, what each wants, where it bites, how handled, who decides, when |
| [`code/stakeholder_grid.py`](code/stakeholder_grid.py) | reads both CSVs, prints the views and the checks, writes `data/godavari-stakeholder-grid.md` |

Run on **Python 3.14.3** (October 2026), standard library only, from the chapter folder:

```bash
python -X utf8 code/stakeholder_grid.py
python -X utf8 code/stakeholder_grid.py worksheet/ai-draft-stakeholders.csv data/none.csv
```

Each run takes well under a second. `-X utf8` keeps Windows consoles happy with the middle dot;
it is harmless elsewhere.

## 8.2 Part A: the map

Copy the template and fill it in this order, because each column makes the next one easier:

1. **Rows first, from the roles list.** Sponsor, operators, blockers, ghost, upstream producer,
   system owner, eval owner, champion, sceptic, your own side. Write a row even when you do not yet
   know the name ("the person who gets the audit letter"). Fewer than eight rows on an enterprise
   problem means someone is missing.
2. **Their version, verbatim.** From Day 0's week, Day 4's meeting, and the mapping conversations.
   If you have not met them, write "not yet met" and the sentence you expect, marked as a guess.
3. **Stops it by, and must change.** The two columns the grid does not have (section 04.2).
4. **Power and interest, 1 to 5.** Score quickly; you will re-score at every checkpoint.
5. **The number they would believe.** In their words. Day 7 formalises it.
6. **Engagement, and when.** A week number for every row that can stop the work; a plan longer
   than a phrase for every row that must change.
7. **Constraints, calendar, collisions, readout room.** The four lists under the table.

The filled map is the chapter's answer. Do not read it until you have drawn your own from Days 0
to 4; then compare row by row. The rows you did not have are the lesson.

## 8.3 Part B: the three scripts

Section 06 explains them; the worksheet files are the ones to print and carry. Run each at least
once out loud with a partner playing the persona before using it on a customer, and time it. The
end-user script in particular runs long the first time, because "show me the last file you did"
produces twenty minutes of material on its own. That is fine on the floor and not fine when the
analyst has a queue; keep the thirty-minute shape and come back for Day 6's full-day shadowing.

## 8.4 Part C: the grid from data

`code/stakeholder_grid.py` reads the stakeholder CSV into a frozen dataclass per row, validates
the scores, and prints six views. The real run, trimmed only where lines repeat:

```text
== godavari-stakeholders.csv: 13 stakeholders, 12 on the customer side ==
  1  blocker
  1  blocker (admin)
  1  blocker and rule owner
  1  eval owners
  1  ghost
  ...

== Power against interest (customer side; high = 4 or 5) ==

[power high, interest low ]  keep satisfied: meet early, ask for conditions in writing, never surprise
    S07  CISO                                                  P5 I2  blocker
    S12  RBI auditor                                           P5 I1  ghost
    S08  Compliance head                                       P4 I3  blocker and rule owner
    S09  Core-system owner (IT, the 2009 core lending system)  P4 I2  system owner

[power high, interest high]  manage closely: in the readout, signs the plan, hears bad news first
    S01  COO                                                   P5 I5  sponsor

[power low , interest low ]  monitor: one named contact, told when their part changes
    S10  Corporate IT identity team (Active Directory, SSO)    P3 I1  blocker (admin)
    S06  Senior analyst, Hyderabad (the sceptic)               P2 I3  operator and sceptic
    S11  Branch managers (300; Kukatpally first)               P2 I2  upstream producer

[power low , interest high]  keep informed and listening: shadow, interview, show the first slice
    S03  Credit-ops team lead, Vijayawada                      P3 I5  operator lead and champion
    S02  Srinivas, credit-ops team lead, Hyderabad             P3 I4  operator lead
    S05  Lakshmi (Vijayawada) and one senior analyst (Hyde...  P2 I5  eval owners
    S04  40 credit-ops analysts (Hyderabad and Vijayawada)     P2 I4  operators

Our side (not on the customer's grid, still on the map):
    S13  Kaagaz CEO and engagement lead (our side)  P4 I4  wants: recurring revenue and patterns for product (Day 3)

== Who can stop the work, and how ==

id   stakeholder                              stops it by    met by week  proxy
S01  COO                                      funding        0            -
S07  CISO                                     veto           1            -
S12  RBI auditor                              finding        never        S08
S08  Compliance head                          veto           1            -
S09  Core-system owner (IT, the 2009 core ... slowing        1            -
S02  Srinivas, credit-ops team lead, Hyder... ignoring       0            -
S03  Credit-ops team lead, Vijayawada         ignoring       0            -
S10  Corporate IT identity team (Active Di... slowing        2            -
S04  40 credit-ops analysts (Hyderabad and... ignoring       1            S03
S05  Lakshmi (Vijayawada) and one senior a... ignoring       1            -
S06  Senior analyst, Hyderabad (the sceptic)  ignoring       1            -
S11  Branch managers (300; Kukatpally first)  input quality  2            S02

== Whose Tuesday changes (must change their behaviour) ==

S03  Credit-ops team lead, Vijayawada         wants: the tracker's job done properly by something that will no...
S05  Lakshmi (Vijayawada) and one senior a... wants: not to be blamed for the model's mistakes; their judgemen...
S02  Srinivas, credit-ops team lead, Hyder... wants: the queue visible, fewer chases, no blame for a wrong field
S04  40 credit-ops analysts (Hyderabad and... wants: less re-keying, fewer chases, a tool that does not add a ...
S06  Senior analyst, Hyderabad (the sceptic)  wants: to be proved right, or shown the failures honestly
S08  Compliance head                          wants: zero audit findings caused by the tool; the rules in writing  (partly)
S09  Core-system owner (IT, the 2009 core ... wants: no duplicate records, no surprise load, a sandbox refresh...
S11  Branch managers (300; Kukatpally first)  wants: fewer send-backs; to be told on day one what is missing

== Sponsor's version against operators' version ==

  COO                                          "the analysts are slow; nine days must become three"
  Srinivas, credit-ops team lead, Hyderabad    "files arrive incomplete and my people spend the week chasing branches"
  Credit-ops team lead, Vijayawada             "the tracker is the real system; the SOP is a story"
  40 credit-ops analysts (Hyderabad and Vij... "we wait three days for the branch to resend a document, then the core batch runs overnight"
  Senior analyst, Hyderabad (the sceptic)      "it will never read handwritten income proofs; the 2019 OCR pilot did not"

== Checks (0 warning(s)) ==

  - none: every role present, every ghost has a proxy, every veto met by week 2

== Conflicts between what stakeholders want (6) ==

1. COO  against  RBI auditor
     COO: auto-approve clean files so turnaround falls
     RBI auditor: a human decision recorded on every file
     collides: the fastest version of the COO's number removes the auditor's condition
     handled:  the skeleton has a human approve every file; the question goes on the readout agenda
     decided by the compliance head on the auditor's behalf; the COO cannot overrule (Day 10 readout)

2. COO  against  Compliance head
     COO: three days
     Compliance head: zero mandatory documents ever skipped
     collides: speed against error rate; the trade-off at the centre of the engagement
     handled:  the compliance head sets the acceptable error rate; the COO's number is measured inside it
     decided by the compliance head (Day 7 step 1 and Day 9 targets)
  ... (four more; section 04.4 has the table)

wrote data/godavari-stakeholder-grid.md
```

Four things to read off the run:

- **The "keep satisfied" quadrant holds every veto.** Four people, all high power, all low interest
  in week 0, and the engagement cannot ship without any of them. That quadrant is where week 1's
  meetings go, and it is the quadrant a sponsor-led introduction tour never visits.
- **"Who can stop it" is twelve rows long; "who must change" is eight; the overlap is small.** The
  COO, the CISO and the auditor can stop the work and change nothing about their day. The analysts
  and the branch managers change everything about their day and could only stop the work by
  ignoring it. Your week is shaped by the second list; your plan is shaped by the first.
- **The sponsor's sentence and the operators' sentences do not overlap in a single word.** That is
  what a real map looks like. The AI draft's five identical sentences (below) are what a map drawn
  from one interview looks like.
- **Four of six collisions have the COO on one side.** Normal, and the reason the readout (Day 10)
  has an agenda.

**The checks** the script runs are the reviewer's checks from section 8.7, as code: every role
present (sponsor, operator, blocker, ghost, upstream, system owner, eval); every ghost has a proxy
that is a row; everyone who can stop the work is met by week 2 (except the ghost, who is never
met); every must-change row has an engagement plan longer than a phrase; high-power low-interest
rows are met in week 0 or 1 (the quiet veto); every version is at least four words; no sponsor's
version is word for word an operator's. The week-0 draft of the Godavari map failed three of them
(the compliance head met in week 2, the branch managers in week 3, the identity team's version as
"raise a ticket"); fixing them is what the week-1 version of the map is.

On the AI-written draft the script says:

```text
== Checks (9 warning(s)) ==

  - no stakeholder in category 'ghost': the map is probably missing someone
  - no stakeholder in category 'upstream': the map is probably missing someone
  - no stakeholder in category 'system owner': the map is probably missing someone
  - no stakeholder in category 'eval': the map is probably missing someone
  - A02 Users (loan officers and analysts): their behaviour must change but the engagement plan is 'training session at launch'
  - A06 IT helpdesk: 'their version of the problem' is not in their words yet
  - A01 and A02: the sponsor's version and an operator's version are word for word the same: you have only interviewed one of them
  - A01 and A03: the sponsor's version and an operator's version are word for word the same: you have only interviewed one of them
  - A01 and A07: the sponsor's version and an operator's version are word for word the same: you have only interviewed one of them

== Conflicts between what stakeholders want (0) ==

none listed: on an enterprise problem that means they have not been looked for
```

Nine warnings a script can raise. The draft has at least ten problems; the rest need a human, which
is exercise 3.1.

The script also writes `data/godavari-stakeholder-grid.md`: the grid, the veto table and the
collisions as Markdown tables, which go into the discovery document (Day 10) without retyping.

## 8.5 What goes into the engagement folder

| Artefact | Used by |
|---|---|
| `worksheet/godavari-stakeholder-map.md` (your version, with the change log) | Day 6 (whom to shadow), Day 7 step 2 (the metric column), Day 10 (the stakeholder section and the readout room) |
| the constraints list | Day 7 step 1, Day 8's "will not do" list, Days 21 to 24 |
| the customer's calendar | Day 8's sequencing, Day 9's baseline sample |
| `data/godavari-conflicts.csv` | Day 10's readout agenda |
| `data/godavari-stakeholder-grid.md` | Day 10, pasted |
| the three scripts, annotated after use | Day 6's interview plan; Day 42's capstone (same scripts, a hospital) |

## 8.6 Build it with AI

An FDE in 2026 would use a coding agent for the script (routine; it writes something like
`stakeholder_grid.py` correctly in one pass) and a chat agent for two harder things: drafting rows
from your own notes, and interrogating the map for who is missing. The second is where the value
is and where the agent fails in ways that look like competence.

**Context to provide:** your own notes from Day 0's week and Day 4's meeting (never the customer's
email, Slack or documents; the CISO has not allowed it and the map is about people); the roles list
from section 02 with the three everyone forgets; the empty template; the rule that every "their
version" cell is verbatim or marked as a guess; the rule that nothing in the map may be something
the person would be surprised to read.

**A strong prompt (interrogate, not draft):**

> Here is my stakeholder map for a lender's loan-intake engagement and the notes it was drawn from.
> Do not rewrite it. Review it as a sceptical FDE lead would: (1) which roles are missing, checking
> specifically for the upstream producer of the main input, the owner of the system we write into,
> the person whose judgement defines a correct output, a regulator or auditor who is never in the
> room, a sceptic, and our own side; (2) which "their version" cells are my paraphrase rather than
> their words, and which rows I have not actually met; (3) which rows could stop the work and have
> a first contact later than week 2; (4) which rows must change their behaviour and have an
> engagement plan that is only a phrase; (5) which collisions between what rows want I have not
> listed, and for each, who would decide it. For every point cite the line in my notes that supports
> it or say explicitly that it is a guess. Do not invent any person, team or system that is not in
> the notes.

**A second prompt (the persona, for rehearsal):**

> Play the owner of a 2009 core lending system at a mid-sized Indian NBFC. Three vendors have
> integrated with your SOAP API in the last six years and one of them created duplicate records
> on retry that you cleaned up at 2 am. You run a credit-check batch at 6 pm that must not be
> disturbed. You are polite, tired of vendors, and answer only what is asked. I will run a
> thirty-minute mapping conversation; at the end, tell me which of your conditions I failed to ask
> for and whether you would have told me about the batch window if I had not asked.

**What the agent typically gets right:** the structure (it knows the grid and the four quadrants);
the generic roles (sponsor, users, IT, security); the script; plausible conditions for a CISO; a
convincing persona for rehearsal.

**What it typically gets wrong for this concept (check each):**

| Mistake | How it shows | Fix |
|---|---|---|
| **invents stakeholders** | a "Head of AI" or a "CTO" as sponsor when the notes say COO (the draft in `worksheet/ai-draft-stakeholder-map.md`); a "Head of Digital Transformation" | every row traces to a line in your notes; the prompt demands the citation; rows without one are deleted |
| **lumps the operators** | one row called "Users" with one view; no team leads, no eval owners, no sceptic | a group shares a row only until someone in it says something different; the notes already have three different sentences |
| **misses the ghost and the upstream producer** | no auditor; branch staff as "end users" who need "app downloads" | the script's category check catches the absence; the human check is "who is never in the room" and "who makes the input" |
| **writes one version for everyone** | "loan processing is slow and needs AI" in five rows | verbatim or marked as a guess; the script flags sponsor-equals-operator; the human reads for paraphrase |
| **scores power from the org chart** | the CISO at power 2 because she is not in the steering committee; Lakshmi at power 5 because she is "the champion" | power is what they can do to the work (veto, fund, ignore); the CISO is a 5 on any map with customer data on it |
| **appoints the champion** | "Lakshmi, appointed by the CTO to lead adoption" | a champion is found by the three tests (section 05.4); an appointed one is a liaison |
| **meets the blockers at the end** | "security sign-off at UAT in week 8"; "inform IT at launch" | everyone who can veto is met by week 2; the script warns on a later first contact |
| **finds no conflicts** | "everyone agrees loan processing is slow"; "the CTO decides all disputes" | a map with no collisions has interviewed one person; and a sponsor cannot overrule a regulator's condition |
| **turns views into character** | "obstructive CISO", "resistant users" | their words, roles not character, nothing they would be surprised to read (section 07.4) |
| **reads the customer's data to draw the map** | offers to "analyse the Slack export for key influencers" | the map is drawn from your notes; the customer's data is behind the CISO's conditions and Day 39's rules |

The first three are the ones to watch. An agent will produce a confident register with a sponsor
who does not exist, one row for forty people and no auditor, and it will read as thorough because
it is formatted. Those are exactly the stakeholder mistakes the decomposition round rejects, done
by a machine in four seconds.

## 8.7 How do you know it's right?

Whether a human or an agent drew the map, the checks are the same:

1. **Every row traces to a conversation or a document.** A row with "not yet met" is allowed; a
   row with a confident version and no source is a guess dressed as a fact.
2. **Count the roles.** Sponsor, operators (split as soon as they say different things), two or
   more blockers, a ghost with a proxy, the upstream producer, the system owner, the eval owner,
   a champion found, a sceptic, your own side. Fewer than eight rows on an enterprise problem is
   almost always missing someone. The script's category check is the floor.
3. **The sponsor's version and the operators' version differ.** If they match, you have heard one
   of them through the other.
4. **Every veto is met by week 2, with a week number in the engagement column.** The script warns
   on anything later.
5. **Every must-change row has an engagement plan you could do on a Tuesday**, not "training at
   launch".
6. **There is at least one collision with the sponsor on one side**, with a decider who is not the
   sponsor.
7. **The constraints list has started**, with a name and a date beside every line, before any
   architecture exists.
8. **The calendar has at least three fixed dates** the sponsor did not volunteer.
9. **Nothing in the map would surprise the person it describes.** Read each row as if they were
   reading it; rewrite the ones that fail.
10. **The map has a change log**, and the week-0 version is kept beside the current one.

**Review checklist:**

- [ ] eight or more rows; every one of the ten roles considered; groups split where they disagree
- [ ] "their version" verbatim or marked as a guess; sponsor's and operators' differ
- [ ] power and interest 1 to 5; "stops it by" and "must change" filled for every row
- [ ] every veto met by week 2; every ghost has a proxy who is a row; quiet-veto rows met in week 0 or 1
- [ ] every must-change row has a plan longer than a phrase, with a Day reference
- [ ] the number each would believe, in their words
- [ ] six or more collisions on an enterprise problem, each with a decider and a date; at least one with the sponsor
- [ ] constraints list started with names and dates; calendar with three or more fixed dates
- [ ] readout room listed; own side on the map
- [ ] script runs clean; the generated grid pasted into the discovery document; change log kept

## 8.8 Extend it

- Add a `second` column (the named backup for every must-change row) and make the script warn when
  a champion or eval owner has none. Section 07.3 is the reason.
- Add `interest_week4` and `interest_week8` columns, re-score, and print how each row moved. The
  CISO should rise; see whether your plan rose with her.
- Draw the map for the Day 42 capstone customer (Krishna District Hospital) from its brief alone,
  before reading Day 42's answer. The ghost changes (the insurer's TPA and the state medical
  council); the method does not.
- Make the grid's thresholds (`HIGH`) and the veto deadline (`LATE_FOR_A_VETO`) command-line
  arguments, and argue in one paragraph why week 2 is the right default for an eight-week security
  review.
- Write the Day 10 stakeholder section from the map: half a page, no character words, the
  collisions as the readout agenda.
