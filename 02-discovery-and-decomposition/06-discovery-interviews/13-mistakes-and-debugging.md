# 13 · Common Mistakes and Debugging

> Day 6 · Section 13 of 16 · [Chapter overview](README.md) · Previous: [12 · Project: the discovery pack](12-project-the-discovery-pack.md) · Next: [14 · Interview questions](14-interview-questions.md)

---

Each row is **symptom, cause, fix**, with the section that explains it.

## 13.1 In the room

| Symptom | Likely cause | Fix |
|---|---|---|
| Every operator agreed with your hypothesis | you said it aloud as a question | ask about the last instance; echo, do not interpret (06.1, 06.2) |
| The interview produced a feature list | "what would you like it to do?" | "what did you work around this week?" (05.6) |
| Short, polite answers | no shadowing first; the interviewee does not know you | shadow the same morning; read back what you saw (03.4) |
| You never heard about the spreadsheet | you asked "do you use spreadsheets?" | "what is in the Excel sheet?"; look at the desk (09.2) |
| The sceptic argued and you defended the product | you tried to convert her | ask what it got wrong, in detail, and what would have to be true (06.3) |
| A number in your notes was wrong at the readout | an adjective not followed, or no read-back | follow "slow" to hours; read back facts and quotes (06.2, 06.5) |

## 13.2 On the job

| Symptom | Likely cause | Fix |
|---|---|---|
| Week 8: the CISO asks how a transferred manager loses access, and the answer is "at re-index" | "who may see what, and where does the rule live" never asked | the six architecture questions to everyone in week one (08.1 to 08.3) |
| The analysts use the tool for a day and go back to the tracker | the tracker was treated as a workaround | read it before replacing it; write state back (09.3) |
| The sponsor quotes a finding the operators deny | the synthesis was not reviewed with the operators first | review with operators, then the sponsor (10.5) |
| The readout cites a finding nobody said | an assistant's synthesis was filed without checking | the script, both directions, plus reading uncoded sentences (12.5) |
| The interview plan was the sponsor's introductions | the sample is the sponsor's version | add the sceptic, the newest operator, the far branch (04.1, 11.3) |
| A finding came from one loud interview and drove the design | no threshold | three independent interviews, or a test (10.3) |
| Discovery notes with customer names on a laptop | data rules not settled before the first note | ask where notes live on day one; file numbers only (02.5) |
| The golden set was all clean files | examples chosen for convenience | draw from send-backs and far branches; named edge cases (09.4) |

## 13.3 The script

| Symptom | Likely cause | Fix |
|---|---|---|
| `no coded notes found: code the transcripts first` | no `## Coded notes` heading, or the folder is wrong | add the section; point at the transcripts folder |
| `'branch_isolation' is not UPPER_SNAKE_CASE` | lower case or spaces in a code | rename; check the code list |
| `X has kind 'blocker', expected one of [...]` | a role used as a kind | use one of the six kinds |
| `UNSUPPORTED: ...` and exit 1 | the synthesis cites a code no transcript has | delete the finding, or find the quote and code it in the transcript |
| `MISSED: ...` | a requirement-level code is not in the synthesis | add a finding, or write in section D why it does not belong |
| A code's count is lower than you expected | a typo created a second code (BRANCH_ISOLATON) | sort the CSV by code and look for near-duplicates |

## 13.4 Key takeaways

- In the room, the mistakes are leading, asking for features, skipping the shadowing, converting the sceptic, keeping adjectives and skipping the read-back.
- On the job, each one has a month-later symptom: a re-index, an abandoned tool, a denied finding, an invented finding at the readout.
- The script catches malformed codes, invented codes and missed requirements; it cannot catch a real code attached to a false sentence.
