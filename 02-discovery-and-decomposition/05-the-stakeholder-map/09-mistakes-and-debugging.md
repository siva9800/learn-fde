# 09 · Common Mistakes and Debugging

> Day 5 · Section 9 of 12 · [Chapter overview](README.md) · Previous: [08 · Project: the Godavari stakeholder map](08-project-godavari-stakeholder-map.md) · Next: [10 · Interview questions](10-interview-questions.md)

---

Each row is **symptom, cause, fix**, with the section that explains it. The first table is the
engagement, the second is the interview, the third is the map and the script.

## 9.1 On the engagement

| Symptom | Likely cause | Fix |
|---|---|---|
| The prototype works and the analysts keep the tracker open beside it | built for the sponsor's version; the operators' version never recorded; "must change" rows had no plan | both versions verbatim; the lever that moves both; an engagement plan per must-change row (03.2, 04.2) |
| The CISO refuses the deployment in week ten | met in week ten; conditions never asked for | the blocker in week 1, conditions verbatim, the questionnaire in week 2 (05.3) |
| The compliance head finds the tool in month three and stops the pilot | "who gets the audit letter" never asked; the ghost had no proxy | the eleven signals; a proxy row for every ghost (05.2, 03.4) |
| The core-system owner takes six weeks to refresh the sandbox | mapped as "IT", not as a person with a memory of three failed vendors | the system-owner row; the admin script's "what did the last vendor get wrong" (02.2, 06.3) |
| 31 percent send-backs do not move after go-live | branch managers treated as a cause, not a stakeholder | the upstream-producer row with a number they would believe (02.2, 04.4) |
| The golden set is labelled against the demo's 97 percent, and the first audit finding is yours | the sponsor defined "correct" | the eval-owner rows; "you decide fast, they decide right" said to the COO in week 0 (03.3) |
| The champion is promoted away in month three and usage halves | one champion, no second | a named second for every must-change row; re-score at checkpoints (07.3) |
| The integration spike lands in a release freeze | the customer's calendar never asked for | the calendar row from week 0 (05.5) |
| A row of the map is quoted back to you by the person in it, angrily | character words in the map | their words, roles not character, nothing they would be surprised to read (07.4) |
| Your own CEO pulls the FDE in month four | own side not on the map; the second-customer test never revisited | the own-side row, reviewed in the internal weekly (02.4) |

## 9.2 In the interview

| Symptom | Likely cause | Fix |
|---|---|---|
| You listed "users, IT, management" as stakeholders | roles by title, not by what they can do to the work | sponsor, operators, blockers, ghost, upstream producer, system owner, eval owner; say the three everyone forgets (02.1, 02.2) |
| The interviewer asks "who could stop this?" and you had not said | the veto list not separated from the sign list | who signs, who vetoes, who opens the tool: three lists, unprompted (04.3) |
| You said "the regulator" and could not say what they would ask | the ghost named but their version not written | one sentence in the ghost's voice ("show me the decision, who made it, and the documents") (03.4) |
| You resolved the sponsor-operator disagreement by picking a side | treating two true versions as a contradiction | both true from where each sits; the lever; the sentence both sign (03.1, 03.2) |
| You said the sponsor decides whether outputs are correct | the eval-customer split missed | the eval owner is a senior IC, not the sponsor; say who labels (03.3) |
| You proposed training users at launch as the adoption plan | operators' power (ignoring) invisible on the grid | "stops it by: ignoring"; the champion and the sceptic; shadowing before code (04.2, 05.4) |

## 9.3 The map and the script

| Symptom | Likely cause | Fix |
|---|---|---|
| `needs integer power and interest` | a blank or a word in a score cell | 1 to 5 in both columns; "unknown" is a 3 with a note in the engagement column |
| `a ghost with nobody named to speak for them` | the proxy column empty for a ghost row | the proxy is a row id (S08), not a name |
| `proxy 'compliance head' is not a row in the map` | a name where an id was expected | use the id; the script joins on it |
| `can stop the work (veto) but first contact is week 8` | the blocker met at UAT | move the meeting; if you truly cannot meet them earlier, write why in the engagement column and raise it in the readout |
| `the sponsor's version and an operator's version are word for word the same` | one interview copied into several rows | interview the other; or mark the copied cell as a guess until you have |
| Zero warnings on a map that feels thin | the checks are a floor; a row per category satisfies them | the review checklist (08.7), especially "would surprise the person" and "at least one collision with the sponsor" |
| The quadrant chart puts the operators in "monitor" | interest scored from how often they attend meetings | interest is how much their day depends on it; forty analysts are a 4 or 5 |
| The generated grid file lists your own side in the customer's quadrants | the `side` column not set to `kaagaz`, or the row's name does not say "(our side)" | set the column and keep "(our side)" in the name; the printed grid filters own-side rows out, the Markdown writer keeps them with that label |

## 9.4 A routine for a map that feels wrong

When the map is filled, the script is clean, and something still feels off, run these five in
order:

1. Read the "their version" column aloud. Any sentence you would not hear the person say is yours,
   not theirs. Replace it or mark it as a guess.
2. Cover the names and read the "stops it by" column. If nobody can stop the work except the
   sponsor, you have mapped the sponsor's friends.
3. For every row with "must change: yes", say what they do on the first Tuesday after go-live
   that they did not do before. If you cannot, the engagement column is a phrase.
4. Ask "who gets the letter" for every regulator, insurer, auditor or court that touches this
   workflow. Each answer is a ghost and a proxy.
5. Ask the sceptic, by name, what the map is missing. They will tell you.
