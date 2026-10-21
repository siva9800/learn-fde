# 05 · Saying No in Writing: Not Now, Because, and Instead

> Day 10 · Section 5 of 13 · [Chapter overview](README.md) · Previous: [04 · The readout](04-the-readout.md) · Next: [06 · The decision log and versioning](06-the-decision-log-and-versioning.md)

---

## 5.1 The three parts

Day 4 wrote the sentence and Day 8 put four of them on a signed page. Day 10 says them out loud, to
the person who pays, in front of his peers, and writes down what happened.

| Part | What it does | Without it |
|---|---|---|
| **Not now** | refuses for this cycle, not forever | "no" sounds like a judgement on the idea, and the sponsor defends the idea |
| **Because** | gives the reason in terms the asker already accepted (a gate, a condition, a number) | the refusal is your opinion, and opinions get overruled by seniority |
| **And instead** | offers the thing that would make it possible, or the part of it you can do | the conversation ends with a loss, and the asker looks for a way round you |

The "because" should point to something already signed. At Godavari, every refusal's reason is in an
earlier artifact: the chatbot has no baseline (Day 4's gate), the CRM fails the second-customer test
(Day 3), auto-approval breaks the auditor's condition (Day 5's collision), PII outside India breaks
the compliance head's first sentence. You are not inventing a reason in the room; you are reminding
the room of one it agreed to.

## 5.2 The COO who wants the chatbot

**COO:** "The board saw a chatbot at the conference. The branches would love it. Can we add it to
the pilot? It is the same documents."

**FDE:** "You are right that branches phone Hyderabad about policy, and the board will ask. Not in
this pilot, because nobody has counted those calls yet, so we could not show the board it worked.
Kukatpally has been logging its policy calls since 9 November. If Guntur logs them too from Monday,
at the day-90 review you will have a month of real numbers from two branches, and if the calls cost
what you think, it is the first thing we score for the next 90 days."

**COO:** "Fine. Add Guntur."

What made it land: the acknowledgement (the board will ask), a reason he could repeat to the board
(no count, so no proof), an alternative that costs him nothing and that he controls (Guntur logs
calls), and a date. The written result is change C1 and decision D06. The chatbot line in section 10.2
now reads "Kukatpally logs policy calls from 9 November and Guntur from 23 November; scored at the
day-90 review."

Notice what the FDE did not say: "a chatbot is a solution looking for a problem". Day 4 taught you to
think it. Saying it to a COO about his board's idea is how you lose the sponsor.

## 5.3 The CISO who wants on-prem before any prototype

**CISO:** "I am not comfortable with anything running in AWS before I have seen it. Keep it on-prem
until I say otherwise."

**FDE:** "That is fair: nothing has been reviewed yet. Today the skeleton and the prototype run on a
machine inside this building on masked files the compliance head approved, and nothing else is
planned until you approve it. Can I write it as three stages, each with your written approval as the
gate? The building with masked files, which is where we are. The building with real files from two
branches, from 7 December, with your approval on 3 December. Godavari's own VPC in AWS Mumbai, with no
PII leaving India, only after your review passes and you approve the cutover. Your questionnaire
answers have been with you since 3 November."

**CISO:** "And logs and backups are in scope for 'nothing leaves India'."

**FDE:** "Written into section 8 now."

This is not a "no" at all. It is the commonest kind of objection: a condition that sounds like a
change of plan and is really a request for control. The commitment is the Part file's: a VPC in AWS
Mumbai with no PII leaving India, the security questionnaire started in week two. The new part is the
gate at each stage, which is change C2 and decision D08. The full deployment-model argument (SaaS,
VPC, on-prem, air-gapped) is Day 21's; the document records the decision for these 90 days.

## 5.4 The VP who wants 100 percent accuracy

In interviews this is the "VP" scenario; at Godavari it came from the compliance head as "can you
promise zero misses?". The shape is the same.

**Compliance head:** "If the system ever marks a file complete when a mandatory document is missing,
that is my audit finding. I need 100 percent."

**FDE:** "You should have it where it can be tested. The rules are code you sign, so on the golden set
they must miss no mandatory document, and they will not run until they do. In production I cannot
promise zero, because today's process is not zero: the hand count found 4.1 percent of files decided
with a document missing, and your analysts' own check catches 87 percent. What I can promise is
better than today, measured every month by your definition, with you re-drawing one month in three."

**Compliance head:** "Then measure today properly. 0.9 to 7.2 percent is not a baseline."

**FDE:** "Agreed. Bhavani and I will count all 700 files in the frame before the go or no-go."

Change C3, decision D09. The pattern: split the absolute into the part that can be tested (the rules,
on the golden set) and the part that can only be compared (production, against today). Never promise
an absolute nobody can verify; Day 9 section 7.5 explains why, and Day 32 owns the harder case where
the demand crosses a governance line.

## 5.5 The CRM, again

The branch CRM was declined in Day 3, before the contract. At the readout it came back in a new shape:
the Kukatpally manager's conditions mentioned "follow-ups", and the COO asked whether "a small screen
for branch follow-ups" could ride along.

**FDE:** "Not in this engagement, because it is not our product, no other lender would buy Godavari's,
and it would keep an engineer here for a year on work your IT team or a CRM vendor does better. What we
will do instead is what the branches actually asked for: the missing-document notice on the day the
file arrives, and the file status and missing-document list exposed so any CRM, or the tracker, can
read them."

Decision D10: the line stays. A request that returns in a new shape is answered with the same reason;
a reason that changes each time it is asked is not a reason.

## 5.6 The written form

A refusal in a meeting is forgotten by Monday. In the document it is a table row with five cells.

| We will not | Because | And instead | Agreed by |
|---|---|---|---|
| build the branch CRM | not Kaagaz's product; no other lender would buy Godavari's; it would keep an FDE on site for a year | file status and the missing-document list exposed so a CRM or the tracker can read them | the COO; the Kaagaz CEO and engagement lead |

Rules for the row, each checked by the script in section 09 or by the review checklist:

- the "because" is a reason of four words or more, not a label ("phase 2", "deferred");
- the "agreed by" names people, not "leadership";
- a "not now" line has a revisit point (a date, a checkpoint, or an event like "after intake is in
  daily use");
- the list stays short: Godavari has four will-not-do lines and five parked ones. Twenty lines hide
  the four that matter.
