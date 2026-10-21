# Mapping conversation · End user (operator)

> Day 5 · thirty minutes at their desk · run in week 0 or 1, before shadowing (Day 6)
> Purpose: fill this person's row on the stakeholder map and find the next three rows.
> At Godavari: an analyst in Hyderabad or Vijayawada, a team lead, or the senior analyst who expects it to fail.

**Before you sit down:** have the map open with a blank row for them. Know their name, their city, their years on the job. Bring nothing to show. Do not say "AI" before they do.

## Opening (minutes 0 to 2)

> "Thank you for the time. I am here to learn how the work actually runs, not to check how it should run. Nothing you say goes to your manager with your name on it. If I write something down and it is wrong, tell me and I will cross it out in front of you."

Then ask for permission to look at their screen.

## Their version (minutes 2 to 10)

| Ask | Listen for | Fills |
|---|---|---|
| "Show me the last file you finished." | the real sequence, not the SOP; what they open first | their version |
| "What did you wait for on that file?" | the branch, the batch, a colleague, a signature | their version; the upstream producer |
| "What did you type twice?" | re-keying from PDF into the core system; the tracker | their version; the number they would believe (hours) |
| "What is in the spreadsheet?" (there is always a spreadsheet) | the real state: "waiting on bank statement since" | the champion test (do they own a workaround) |

## The waiting and the blame (minutes 10 to 15)

| Ask | Listen for | Fills |
|---|---|---|
| "When a file came back from the branch, what happened?" | who they called, how many times, how long | their version; the branch managers' row |
| "Who gets blamed when a file is late?" | them; the branch; "nobody, and everybody" | the fear; stops it by (ignoring, if blame will follow) |
| "How many files are waiting right now, and on what?" | a number from the tracker, said without looking | the number they would believe |

## Trust and "correct" (minutes 15 to 20)

| Ask | Listen for | Fills |
|---|---|---|
| "If a tool read the documents and filled the fields, what would you check before you trusted it?" | the fields they would never trust unchecked; the salary slip for the wrong month | the eval-owner test: what "correct" means to them |
| "What would make you stop using it after a week?" | an extra step; a wrong field they got blamed for; slower than the spreadsheet | stops it by; must change |
| "Who decides, today, whether a file was done right?" | the team lead, the compliance head, "the auditor, eventually" | the eval owners; the ghost's proxy |

## What was tried before (minutes 20 to 25)

| Ask | Listen for | Fills |
|---|---|---|
| "What has been tried before? What happened to it?" | the 2019 OCR pilot; which documents it failed on; who switched it off | the sceptic's failure model; test cases for Day 14 |
| "What would it have needed to work?" | "to flag what it could not read instead of guessing" | the fear turned into a requirement |

## People (minutes 25 to 30)

| Ask | Listen for | Fills |
|---|---|---|
| "Who knows this work best?" | a name; often not the team lead | the next row; a possible eval owner |
| "Who will hate this?" | a name and a reason | the sceptic's row |
| "Who should I sit with for a full day?" | the person to shadow (Day 6) | the champion test (do they volunteer themselves) |
| "Who else do I need to ask before anything changes here?" | the compliance head, "IT", the branch | blockers and upstream rows the sponsor did not mention |

## Do not ask

- "What are your requirements?" (they will invent some to be helpful)
- "How long does a file take?" (they will quote the SOP; the tracker knows the real number)
- Anything containing "AI", "model", "automation" or "replace" (every answer after it is defensive)

## Within the hour

Fill the row in their words. Add each name they gave as a new row with "not yet met". Note which of section 05.2's signals you saw (the spreadsheet; "we tried that"). Rerun `python -X utf8 code/stakeholder_grid.py`.
