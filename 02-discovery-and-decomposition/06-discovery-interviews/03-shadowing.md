# 03 · Shadowing: Sit Beside an Operator for a Full Cycle

> Day 6 · Section 3 of 16 · [Chapter overview](README.md) · Previous: [02 · Days one and two](02-access-and-reality.md) · Next: [04 · The interview plan](04-the-interview-plan.md)

---

## 3.1 What shadowing is, and what it is not

Shadowing is sitting beside the person who does the job, for one complete unit of their work, writing down every action, every wait and every workaround, without helping and without asking why until the unit is done. One loan file from "assigned" to "waiting" or "sent to batch". One claim. One ticket. The unit matters: a half-finished file tells you the first eight steps and hides the eleven where the days go.

It is not a demo. When you ask an operator to "show me how the system works", she gives you a tour of the screens, in the order the screens were designed to be used, and skips the spreadsheet, the phone call and the WhatsApp page because they are not "the system". When you say "do your next file as if I were not here, and I will write down what I see", she does the job, and the job is where the nineteen steps are.

It is not an interview either. The interview is the same afternoon (section 04), and it is better for having the shadowing before it, because every question in it starts with "I saw you do X; why?"

## 3.2 How to do it

| Step | What you do | Why |
|---|---|---|
| Ask permission from the person, not only their manager | "May I sit beside you for one file? I will write down what you do, not judge it. You can stop me at any time." | an operator volunteered by her manager performs; one who agreed herself works |
| Get HR told, and say so | "Your team lead has told HR I am here." | the CISO's rule, and it removes the feeling of surveillance |
| Sit where you can see the screen and the desk | the printed checklist, the notebook and the phone are on the desk, not the screen | half the undocumented steps are off-screen |
| Start a log with a time column | the template in `worksheet/shadowing-log-template.md`: time, action, tool, wait, official, workaround, quote | time is how you find the waits; "official" is how you find the SOP gap |
| Write verbs and objects, not conclusions | "opened workbook, found green row" rather than "uses a shadow system" | the conclusion goes in the synthesis with a code; the log is evidence |
| Count the waits | every screen load, every phone call on hold, every "let me find it" | at Godavari, fourteen screen loads in one file, about 8.5 minutes; across forty analysts that is hours a day |
| Do not help | when she scrolls past the PAN on page 19 and goes back, say nothing | your help changes the process you are measuring |
| Note the interruption | the WhatsApp page that arrives for a different file is a step in the process, not noise | the unofficial channel shows up as an interruption, never as a step she describes |
| Stop at the unit's end, then ask | the file reaches "waiting" or "batch"; now ask the three questions the log raised | the questions are better for having been earned |
| Read back the counts | "Four windows, 23 fields typed that were already on the form, 14 screen loads, one call, one WhatsApp, 76 minutes." | she corrects you, and the corrections are the most reliable numbers you will get |

The filled log for Lakshmi's Wednesday is in [`worksheet/shadowing-log-lakshmi-w1-wed.md`](worksheet/shadowing-log-lakshmi-w1-wed.md). Fourteen rows, seven of them official, seven not. Read it once as a model of what the log should look like and once as the evidence for half of section 07's map.

## 3.3 What shadowing finds that interviews do not

| Found by shadowing | Why an interview misses it | At Godavari |
|---|---|---|
| The real first step | people describe the system, not their habit | the tracker, not the core |
| The windows open at once | nobody counts their own windows | four, plus a printed checklist; the "fifth window is a no" rule |
| The waits, in minutes | people round "forty seconds" to "slow" | 14 screen loads, about 8.5 minutes a file |
| The off-screen tools | they are not "the system" | the notebook of branch numbers; the printed 2024 checklist when a 2025 one exists |
| The unofficial channel, as an event | people describe it as rare or do not describe it at all | a Guntur passbook page arriving on WhatsApp mid-file, printed, stapled, "received WA" |
| What gets skipped under load | nobody says "I skip the checklist on a bad day" unprompted | Lakshmi's "on a bad day I check the big ones and hope", said in the interview only because you had watched her check all fourteen on a normal one |
| The judgement calls | they feel like knowledge, not decisions | "an Aadhaar with the old address is not acceptable here", decided in four seconds, written nowhere |

Every row in the right column became a line in Day 7's inputs table or a layer in the walking skeleton. None of them came from a question.

## 3.4 The trust you build by watching

The published playbooks describe discovery as interviews. The hour beside the operator does something the interviews cannot: it changes what she is willing to say. An operator who has watched you write "opened workbook" without a raised eyebrow, who has seen you note the WhatsApp page and not ask "is that allowed?", and who has heard you read back "76 minutes, and the file is not finished" with the same tone you used for everything else, has learned three things about you. You are not the auditor. You are not the vendor who will tell the COO she uses a spreadsheet. And you counted, which means you will not tell the COO she is slow.

That is why the honest sentences come in the afternoon. "On a bad day I check the big ones and hope." "I would not know; that is the honest answer." "Nobody has said no. Nobody has said yes." Those three sentences, from Lakshmi, Bhavani and Lakshmi again, are the ones that put confidence routing, a review queue with a senior's eyes on it, and a resubmission flow into the design. They were given to someone who had watched first.

The same trust is what Day 31 and Day 33 spend later. The operator who lets you count her clicks in week one is the operator who tells you in week nine that the review queue is slower than the tracker, instead of quietly keeping the tracker open.

## 3.5 Who to shadow, and for how long

| Who | How long | Why |
|---|---|---|
| The most experienced operator (Lakshmi) | a full morning, one complete file | she knows every workaround and has stopped seeing them; you have to watch |
| Two ordinary operators in the other city | an afternoon | the process differs by city more than anyone admits; the Hyderabad floor had a different tracker layout |
| The newest operator (Bhavani) | one full file | she still sees the workarounds as workarounds; she learned the job from the tracker and will say so |
| A send-back, specifically | a second pass in week two, only on files that came back | the first pass shows the happy path; the send-back is where the days are |
| The upstream producer at work (the branch's 17:00 scan) | half an hour at the scanner | the page order, the "to follow" note, the tray; nobody describes a scanner |

Three to four sessions, five to six hours, across the two cities and one branch, in the first two weeks. It is roughly a fifth of the customer-facing hours in Day 2's fortnight, and it is where most of the findings in section 12's synthesis were first seen.

## 3.6 Remote shadowing

A screen share with a camera on the desk is weaker than a chair, and still beats an interview alone. Keep the same log; you will miss the notebook and the phone. Never record the screen without the CISO's and HR's agreement: a recording of a loan file is customer PII (Day 24).

## 3.7 Key takeaways

- Shadow one complete unit of work, without helping and without asking until it is done. Log time, action, tool, wait, official, workaround, quote.
- Shadowing finds what interviews miss: the real first step, the windows, the waits, the re-keying, the off-screen tools, the unofficial channel as an event, what is skipped under load, the judgement calls.
- Watching without judging is what makes the afternoon's interview honest, and that honesty is the engagement's most valuable input.
- Three to four sessions across both cities, the newest and the most experienced operator, a send-back and the branch scanner.
