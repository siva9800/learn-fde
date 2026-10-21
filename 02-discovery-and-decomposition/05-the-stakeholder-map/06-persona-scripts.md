# 06 · The Three Persona Scripts: End User, Admin and IT, Executive Sponsor

> Day 5 · Section 6 of 12 · [Chapter overview](README.md) · Previous: [05 · Reading the org](05-reading-the-org.md) · Next: [07 · 2026 patterns and production concerns](07-2026-patterns-and-production-concerns.md)

---

## 6.1 Why one script does not fit

The first conversation with each person on the map has one purpose: **fill their row**. Their
version of the problem, what they want, the number they would believe, how they could stop the
work, whether their day changes, and who else they think you should meet. That purpose is the same
for everyone; the questions that get there are not. The 2026 discovery playbooks are explicit that
scripts differ by persona and pair each audience with questions to ask and questions to avoid. Ask
a COO to walk you through the workflow and you get the SOP from memory and a wasted half hour. Ask
an analyst about strategic outcomes and you get silence.

These are **mapping conversations**, thirty minutes each, run in week 0 and week 1. They are not
Day 6's shadowing sessions, which take a full cycle beside an operator and use a different, longer
question bank; the mapping conversation is how you decide whom to shadow. The full scripts, with
timing and the column each question fills, are in `worksheet/`; this section is the shape and the
reasoning.

| Persona | Script | At Godavari | Fills |
|---|---|---|---|
| End user (operator) | [`worksheet/interview-script-end-user.md`](worksheet/interview-script-end-user.md) | an analyst in Hyderabad or Vijayawada; a team lead; the sceptic | their version, what they want, stops it by (ignoring), must change, the champion and sceptic tests |
| Admin and IT | [`worksheet/interview-script-admin-it.md`](worksheet/interview-script-admin-it.md) | the core-system owner; the identity team; the CISO's office for the first conditions | stops it by (veto, slowing), conditions, the calendar, the system owner's memory |
| Executive sponsor | [`worksheet/interview-script-executive-sponsor.md`](worksheet/interview-script-executive-sponsor.md) | the COO | their version, the number, who else is invested, who can stop it, what was promised upward |

## 6.2 The end-user script: "show me the last one you did"

Thirty minutes at their desk, not in a meeting room. The order matters: start concrete, end with
people.

| Minutes | Question | Why, and what it fills |
|---|---|---|
| 0 to 2 | "I am here to learn how the work actually runs, not to check it. Nothing you say goes to your manager with your name on it." | the sentence that makes the next twenty-eight minutes honest; without it you get the SOP |
| 2 to 10 | "Show me the last file you finished. What did you open first? What did you wait for? What did you type twice?" | their version, in their words and on their screen; the tracker appears here |
| 10 to 15 | "When a file comes back from the branch, what happened? Who did you call? How long did it take?" | the waiting; the upstream producer; the number they would believe (chases, hours) |
| 15 to 20 | "If a tool read the documents and filled the fields, what would you check before you trusted it? What would make you stop using it?" | stops it by (ignoring); the fear; the eval-owner test (what "correct" means to them) |
| 20 to 25 | "What have you tried before? What happened to it?" | the sceptic's failure model; the 2019 OCR pilot; test cases for Day 14 |
| 25 to 30 | "Who else should I sit with? Who knows this best? Who will hate this?" | the next three rows of the map; the champion and the sceptic by name |

Do not ask: "what are your requirements" (they will invent some), "how long does a file take"
(they will quote the SOP), or anything with the word "AI" in it (it changes every answer that
follows). Do ask to see the spreadsheet. There is always a spreadsheet.

## 6.3 The admin and IT script: "under what conditions"

Thirty minutes, and bring nothing to demo. The person across the table has seen vendors arrive with
slides; the one who arrives with questions about their batch window is new to them.

| Minutes | Question | Why, and what it fills |
|---|---|---|
| 0 to 3 | "I have nothing to show you and I would rather not build something you will have to refuse. I am here for the conditions." | turns a blocker into a partner (section 05.3) |
| 3 to 10 | "Which systems would a tool like this have to read from and write to? Who owns each one, by name? When does each run its batch, backup or refresh?" | the system owner; the calendar; the inputs Day 7's step 3 will map |
| 10 to 17 | "What happened with the last vendor who integrated here? What did they get wrong, in your words?" | the memory; the three failed vendors; the fear ("the fourth vendor to break his system") |
| 17 to 24 | "Under what conditions may a vendor's system touch a loan file? Where may it run? Who may hold credentials? What must never leave the building, and what must never be trained on?" | the CISO's and compliance head's conditions, verbatim, into the constraints list |
| 24 to 28 | "How is access granted here: who approves a service account, how long does it take, and what breaks if it is done wrong?" | the identity team; the ticket in week 2; Day 22's design inputs |
| 28 to 30 | "Who else signs before anything goes live? Who gets the audit letter?" | the ghost's proxy; the readout room |

Do not ask them about the workflow, the analysts or the business case; they do not know and it tells
them you have not understood their job. Do not promise anything about the architecture. Write every
condition down in their words and read it back before you leave; the row is theirs.

## 6.4 The executive sponsor script: "who else is invested"

Thirty minutes, usually less. The sponsor has given you the problem already (Day 4); this
conversation fills the rest of his row and finds the rows he has not mentioned.

| Minutes | Question | Why, and what it fills |
|---|---|---|
| 0 to 5 | "When this works, what will you say to the board, in one sentence? What number will be on the slide?" | the number they would believe; what was promised upward and by when |
| 5 to 10 | "What does three days get Godavari that nine does not? Loans, customers, capital, audit?" | the value behind the number (Day 9's business case starts here) |
| 10 to 15 | "Who else has a stake in this: who benefits, who pays in time or budget, who has said no to something like it before?" | the rows the sponsor knows and did not mention; the blockers by name |
| 15 to 20 | "Who could stop this, inside or outside the company? What happens if the RBI asks about it?" | the veto list; the ghost; whether the sponsor has thought about the auditor |
| 20 to 25 | "Who would you trust to say whether a file was processed correctly? If they and the number disagree, who wins?" | the eval-owner split made explicit; the first collision on the record |
| 25 to 30 | "What is fixed in your calendar for the next six months: audit, year end, freezes, board dates?" | the calendar; the date the number must exist by |

Do not ask the sponsor to describe the workflow in detail, to estimate how long steps take, or to
name the champion. Do not show the demo deck again. Do ask, before leaving, for introductions to
every person he named, in his words ("the COO asked me to meet you" opens doors that "the vendor
wants a meeting" does not).

## 6.5 After the thirty minutes

Within the hour, before the next conversation: fill the row, verbatim where you can; add every name
they gave you as a new row with "not yet met" in the engagement column; note which of the eleven
signals (section 05.2) you saw. Then run the script (section 08) and read the warnings. A map that
grows by three rows per conversation in week 0 is normal; one that does not grow means you are
asking the wrong persona the wrong questions.

## 6.6 Key takeaways

- One purpose (fill the row), three scripts, because a COO and an analyst answer different questions
  honestly.
- End users: start at their screen, end with names; never say "AI". Admin and IT: bring nothing,
  ask for conditions, write them verbatim. Sponsor: the board sentence, the value, who else, who
  could stop it, who judges correctness, the calendar.
- Every conversation should add rows. Fill the row within the hour and rerun the checks.
