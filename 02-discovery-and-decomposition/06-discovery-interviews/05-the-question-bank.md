# 05 · The Question Bank: "Show Me the Last One You Did"

> Day 6 · Section 5 of 16 · [Chapter overview](README.md) · Previous: [04 · The interview plan](04-the-interview-plan.md) · Next: [06 · Interviewing without leading](06-interviewing-without-leading.md)

---

## 5.1 Three questions that do most of the work

If you remember nothing else from the bank, remember these three, because between them they produce the real workflow, the error path and the shadow system:

| Question | What it produces | Why it works |
|---|---|---|
| **"Show me the last one you did."** | the real steps, in the order they happen, with the tools that are actually open | it asks for a specific, recent, concrete instance; people cannot describe a process they do not follow, but they can always show the last file |
| **"What do you do when it is wrong?"** | who corrects errors today, what happens to them, what they fear, and what they want the system to do instead of guessing | "wrong" is the moment the process shows its real owner; the person who answers "me, always me" is the person your review queue is for |
| **"What is in the Excel sheet?"** | the shadow system's columns, its colours, who writes it and who reads it | every operation has one; asking for it by name, without judgement, is permission to show it |

The playbooks say the same thing in their own words: "walk me through the last time you did X; specific, recent, concrete, never hypothetical"; "ask about the last time the process failed rather than about abstract requirements"; "what's the part of this you'd pay someone to do for you?"

## 5.2 The operator script

The full script is in [`worksheet/question-bank.md`](worksheet/question-bank.md), script A, thirteen questions, each with a "then" column saying what the answer changes. A forty-minute operator interview, after a morning of shadowing, runs in four movements: the real steps and the re-keying (show me the last one; what did you open first; what did you type that was already typed), about ten minutes; the waits, the shadow systems and the unofficial channels (what did you wait for; what is in the Excel sheet; what came by a route that is not in the SOP), about eight; the error path, the judgement calls and the failure model (when it is wrong, who finds it; what do you do when you are not sure; what did the last vendor get wrong), about ten; then the bad day, where a tool would have to sit, the hundred labelled files, the number they would believe, and the read-back.

Lakshmi's transcript ([`worksheet/transcripts/01-lakshmi-analyst-vijayawada.md`](worksheet/transcripts/01-lakshmi-analyst-vijayawada.md)) follows this shape almost exactly, and you can see where each question lands: "show me the last one" produces the tracker in the first answer; "when it is wrong" produces "me, always me" and then "tell me when it is not sure; do not guess"; "what is a bad day" produces "I check the big ones and hope".

## 5.3 The admin script

Admins (security, identity, compliance, the system owner) are not asked to show you their last file. They are asked where rules live. Script B, twelve questions; the ones that matter most:

| Question | At Godavari, the answer | What it changed |
|---|---|---|
| B1 "When a user opens a record, what decides whether they are allowed to? Where does that rule live?" | AD groups per branch, region and role; the core reads them at login; the filter is in the session, not the API | permission-aware retrieval, resolved at query time (Days 15, 22) |
| B4 "How would you answer 'who viewed this file' a year from now?" | "for seven years" | a view log on retrieval, from day one |
| B5 "Which rules are fixed by regulation, which are judgement, who signs a change?" | the RBI KYC Master Direction fixes the documents; acceptable alternatives are judgement, unwritten; she signs | rules as signed deterministic code (Day 11); a week of her time for the list |
| B7 "What time do the batches run, and what must not happen during them?" | 02:00 transfer, 18:00 credit check, no writes 17:30 to 20:00 | freshness bound; same-hour intake out of scope |
| B8 "What does your system do if I call it twice with the same input?" | "it creates two applications" | the idempotency key (Day 16) |
| B12 "What would make you say no late?" | "finding something in week ten I was not told in week two" | the whole reason the interview happens in week two |

Notice that none of these is a technical question about the vendor's product. Admins are interviewed about their rules and their fears, and the architecture falls out.

## 5.4 The sponsor script

The sponsor interview is short because the sponsor's time is short, and it has one job besides the number: to get the trade-off and the governance line said out loud by the person who will later be tempted to forget them. Script C, ten questions:

| Question | The COO's answer | What it is for |
|---|---|---|
| C1 "Nine days from what event to what, median or mean?" | application signed at the branch to sanction letter; a median; 9.2 last quarter | Day 7 step 1; Day 9's baseline definition |
| C2 "Where does that number come from, and who else has a number?" | the core's dates, the monthly ops report; "the analysts, in whatever they keep" | the baseline's source; a hint that he does not know about the tracker |
| C4 and C5 "When it is wrong, what happens? If it were faster but less accurate, is that a success?" | "a credit loss or an audit observation; the observation is worse"; "(pause) No." | the trade-off, in his words, to quote back in month two |
| C6 "Is there anything that must never be automated?" | "the sanction; a person signs; the RBI expects a name, and so do I" | the governance line (Day 32), set by the sponsor himself |
| C7 "What do you believe the operators do all day?" | asked in his own form, "is the branches' wait in your nine days?": "I had assumed the days were in Hyderabad, not the branches" | the sponsor's version, tested against the floor |
| C8 "Were you aware of the tracker?" | "What tracker? No. Do not build me a better spreadsheet." | whether the sponsor knows the real process; the adoption condition said the wrong way round |
| C10 "Who would tell me this will fail?" | "Talk to Kukatpally." | the sponsor names his own sceptic |

## 5.5 The six questions that change the architecture

Six questions are asked of everyone, in whatever form fits the seat: where does the file come from, who corrects errors today, what happens when it is wrong, who sees what, what time does the batch run, and what do you do on a bad day. Their answers decide the design. Section 08 takes them one by one; the bank has them with the operator, admin and sponsor forms side by side.

## 5.6 Never ask

A short list, because each of these produces an answer that looks like data and is not:

| Do not ask | Why | Ask instead |
|---|---|---|
| "Would you use a tool that did X?" | hypothetical; the answer is yes in every language | "Where would X have to sit so that you used it?" |
| "Do you think AI could help here?" | an opinion about a word | "What do you type twice?" |
| "Is the process slow?" | leading; the sponsor already said so | "Show me the last file. Where did the days go?" |
| "Do you follow the SOP?" | the honest answer is embarrassing, so you will not get it | "Show me the last one." Count the steps yourself. |
| "What features do you want?" | a wish list for the sponsor's demo | "What did you work around this week?" |
| "Is the data clean?" | nobody knows what you mean by clean | "Show me three files that came back." |

## 5.7 Adapting the bank to a new customer

The questions transfer because they are about process, errors, rules and load, not loans. At the capstone hospital (Day 42), "show me the last one you did" becomes "show me the last discharge summary you wrote"; "who sees what" becomes "which doctor may read which patient's record, and what enforces it"; "what must never be automated" becomes "which fields may never be generated". Rewrite the nouns; keep the verbs.

## 5.8 Key takeaways

- Three questions do most of the work: show me the last one, what do you do when it is wrong, what is in the Excel sheet.
- Operators are asked to show; admins are asked where rules live and who signs; sponsors are asked for the number, the trade-off and the governance line in their own words.
- Six questions are asked of everyone because their answers change the architecture.
- Never ask hypotheticals, opinions about AI, or leading questions; every one of them produces polite noise.
