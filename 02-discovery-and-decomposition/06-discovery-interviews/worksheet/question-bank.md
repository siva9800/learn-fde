# Discovery question bank · persona scripts for operators, admins and sponsors

> Day 6 artifact. Three scripts, one per persona, plus the six questions that change the architecture, which are asked of everyone in a form that fits their seat. Every question is open, asks for a specific recent instance, and has a "then" attached: what the answer changes. Questions in the "never ask" list are leading or hypothetical and produce polite answers. Reuse on the capstone (Day 42).

## Rules that apply to every script

- Open with "show me the last one you did", never with "what do you think of AI".
- Specific, recent, concrete. "Walk me through the last time this failed" beats "what usually goes wrong".
- Follow every adjective: "slow" means how many hours or days, measured how, by whom.
- Silence is a question. Count to five before filling it.
- Read the notes back in the last five minutes and let them correct you.
- Write verbatim quotes, not paraphrases; mark your own inferences as inferences.

## Script A · Operators (analysts, team leads, branch staff)

| # | Question | Then: what the answer changes |
|---|---|---|
| A1 | Show me the last file you finished, from the moment it reached you. | the real first step (the tracker, not the system); the tools open at once |
| A2 | What did you open first, and why that one? | which system is the real state |
| A3 | What did you type that someone had already typed somewhere else? | the re-keying count; the extraction scope |
| A4 | What did you wait for, and how did you know you were waiting? | the waits and where they are recorded (the tracker's "waiting on") |
| A5 | What is in the Excel sheet? Show me the columns. | the shadow system's schema; what the tool must read and write |
| A6 | When something is wrong in a file, who finds it, and what happens to them? | who corrects errors; the review queue's owner; the fear |
| A7 | What do you do when you are not sure? | the judgement calls; the unwritten rules; the "unsure" requirement |
| A8 | What is a bad day? What happens on it? | load peaks; what gets skipped under load |
| A9 | What came to you today by a route that is not in the SOP? | the unofficial channels (WhatsApp, phone, courier) |
| A10 | Has anyone tried to automate this before? What did it get wrong? | the sceptic's failure model; the first test cases |
| A11 | If a system did X, where would it have to sit so that you used it? | adoption: the fifth-window rule |
| A12 | If I asked you to mark the correct answer on a hundred real files, would you, and on what condition? | the eval owners; the golden set |
| A13 | What number would make you believe this worked? | the operator's metric |

## Script B · Admins (security, identity, compliance, the system owner)

| # | Question | Then: what the answer changes |
|---|---|---|
| B1 | When a user opens a record, what decides whether they are allowed to? Where does that rule live? | permission-aware retrieval; group source; query-time filtering |
| B2 | Where do the groups come from, how often do they change, and how are exceptions made? | freshness of access; the manual exceptions |
| B3 | Is there a group that means "everything"? Would you create one for a vendor? | whether a service account can ever see all; the answer is usually no |
| B4 | How would you answer "who viewed this file" a year from now? | the view log requirement |
| B5 | Which rules are fixed by regulation, and which are judgement? Who signs a change? | rules as signed code; the alternatives list |
| B6 | What happens when a file is wrong? To whom? | the cost of an error in the regulator's currency |
| B7 | What time do the batches run, and what must not happen during them? | freshness; write windows |
| B8 | What does your system do if I call it twice with the same input? | idempotency |
| B9 | How often is the sandbox refreshed, and what in it should I not trust? | the integration test plan |
| B10 | What did the last vendor who failed here do, in what week? | the week-eight design mistake |
| B11 | Where may my notes, recordings and sample files live, and where may the prototype run? | the data-handling rules for discovery itself |
| B12 | What would make you say no late? | the condition to surface now |

## Script C · Sponsors

| # | Question | Then: what the answer changes |
|---|---|---|
| C1 | Nine days from what event to what event, and is that a median or a mean? | step 1 of Day 7 |
| C2 | Where does that number come from, and who else has a number? | the baseline's source; the operators' metric |
| C3 | What will the board do with the new number? | the business case (Day 9) |
| C4 | When the output is wrong, what happens, and who pays? | the trade-off and its decider |
| C5 | If it were faster but less accurate, is that a success? | makes the sponsor say the trade-off out loud |
| C6 | Is there anything that must never be automated, whatever the accuracy? | the human decision; the governance line |
| C7 | What do you believe the operators do all day? | the sponsor's version, to test against the floor |
| C8 | Were you aware of X (the shadow system)? | whether the sponsor knows the real process |
| C9 | What do you need from me every week, and what do I need from you? | the readout cadence; the asks |
| C10 | Which of your people should I talk to who would tell me this will fail? | the sceptic, named by the sponsor |

## The six questions that change the architecture (ask everyone, in their language)

| Question | Operator form | Admin form | Sponsor form | What it changes |
|---|---|---|---|---|
| Where does the file come from? | "Show me how it reached you." | "Which job moves it, when?" | "Where do the files start?" | input shape, freshness, page order |
| Who corrects errors today? | "When it is wrong, who finds it?" | "Who is accountable for a wrong record?" | "Who pays for a wrong one?" | the review queue; the human in the loop |
| What happens when it is wrong? | "What happened to you last time?" | "What does the regulator do?" | "What does the board do?" | the acceptable error rate and its decider |
| Who sees what? | "Which files can you open?" | "What enforces that, and from where?" | "Should a branch see another branch?" | permission-aware retrieval and identity |
| What time does the batch run? | "What is tomorrow's work?" | "What is the write window?" | "Why can it not be same day?" | freshness bounds; same-hour out of scope |
| What do you do on a bad day? | "Month end: what do you skip?" | "Quarter end: what overruns?" | "Audit month: what stops?" | load, release freezes, what gets skipped |

## Never ask

| Do not ask | Why | Ask instead |
|---|---|---|
| "Would you use a tool that did X?" | hypothetical; everyone says yes | "Show me what you do today; where would X have to sit?" |
| "Do you think AI could help here?" | invites an opinion on a word | "What do you type twice?" |
| "Is the process slow?" | leading; the sponsor already said so | "Show me the last file. Where did the days go?" |
| "Do you follow the SOP?" | the honest answer is embarrassing | "Show me the last one." Count the steps yourself. |
| "What features do you want?" | produces a wish list for the sponsor's demo | "What did you work around this week?" |
| "Is the data clean?" | nobody knows what you mean | "Show me three files that came back." |
