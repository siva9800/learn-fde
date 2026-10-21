# 10 · Common Mistakes and Debugging

> Day 10 · Section 10 of 13 · [Chapter overview](README.md) · Previous: [09 · Project: the Godavari discovery document](09-project-the-godavari-discovery-document.md) · Next: [11 · Interview questions](11-interview-questions.md)

---

Each row is **symptom, likely cause, fix**, with the section that explains it.

## 10.1 The document

| Symptom | Likely cause | Fix |
|---|---|---|
| The COO says "this is very thorough" and asks for a summary | written as a report, organised by what you did | page one carries the decision; sections answer readers' questions (02.1, 03.2) |
| Thirty pages, and the CISO has not read her part | restated every artifact | one conclusion and a link per source; section 8 on one page (02.5) |
| The CFO finds a negative number on page nine | the honest money left off page one | put the floor and the net side by side on page one (03.2) |
| The team leads go quiet when section 3 is shown | the SOP's twelve steps, or the new system's flow | Day 6's nineteen steps in their words; the tracker's fate in bold (03.4) |
| "Which region, approved by whom?" | a condition written as an adjective | the condition in its owner's words, plus the stage table with gates (03.3) |
| The problem statement was "improved" and the COO no longer recognises it | rewriting a signed sentence | quote it verbatim; measured numbers go in section 7 (02.3) |
| Two numbers for the same thing in different sections | one source updated, the other quoted from memory | quote from the source each time; the review checklist traces page one (09.7) |

## 10.2 The readout

| Symptom | Likely cause | Fix |
|---|---|---|
| The CISO raises a new condition in front of the COO and the meeting stalls | no one-to-one pre-read with the blockers | fifteen minutes each on Monday: "what is wrong with your section?" (04.2) |
| Every decision is answered by the COO | questions put to "everyone" | name the decider for each: "this one is the compliance head's" (04.3) |
| The meeting ends with "let us take this offline" | objections not turned into written changes | acknowledge, ask what would satisfy it, write the change, read it back (04.4) |
| A request is agreed in the room and costs three weeks later | scope reopened on enthusiasm | cost in dates, what comes off, the checkpoint; then section 12 with a date (04.5) |
| Nobody is sure what was signed | no read-back, no version sent after | read the changes aloud; version 1.0 out within two hours (04.6, 04.7) |

## 10.3 Saying no

| Symptom | Likely cause | Fix |
|---|---|---|
| The COO defends the chatbot harder after your "no" | the refusal judged the idea | "not now", with a reason he can repeat to the board, and an alternative he controls (05.2) |
| The refused item comes back every week | no written reason, or a reason that changes | a row with reason, alternative and names; the same reason every time (05.5, 05.6) |
| You promised 100 percent and cannot measure it | an absolute accepted as stated | split into tested (the rules, on the golden set) and compared (production, against today) (05.4) |
| A blocker's "no" became the plan's "never" | the request for control heard as a change of plan | answer with a gate the blocker owns (05.3) |

## 10.4 The log, versions and the script

| Symptom | Likely cause | Fix |
|---|---|---|
| "Why do analysts approve every file?" three months later, and nobody knows | the decision not logged with its reason | ID, date, decision, decider, why, source (06.2) |
| The document has been rewritten twice and the old commitments are gone | edited instead of versioned | minor versions inside scope, major for scope; mark changes; supersede decisions (06.4) |
| The checker passes a document you know is wrong | the script checks form, not meaning | the review checklist is the real test; the script only guarantees nothing is missing (09.5) |
| W2 flags small numbers like 2 or 7 | integers appear everywhere and rarely nowhere | read W2 for the large, specific numbers; a flagged "67" or "12000" is the finding |
| E3 fires on a table that is not about decisions | the heading contains "decision" | rename the heading, or move the table; do not weaken the check |
| E5 fires after a colleague renamed a source file | sources changed under you | fix the link in the next version and note it in the change log (06.5) |
