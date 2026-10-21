# 04 · Milestones, Checkpoints and the Two-Company RACI

> Day 8 · Section 4 of 12 · [Chapter overview](README.md) · Previous: [03 · Sequencing in time](03-sequencing-in-time.md) · Next: [05 · What you will not do](05-what-you-will-not-do.md)

---

## 4.1 A milestone is an event someone outside the team can see

A task is something you do. A milestone is something that is visibly true on a date. "Work on SOAP
integration" is a task. "Approved files are written into the live core system with no duplicates,
after a month of clean test calls" is a milestone: on Tuesday 8 December it is either true or not, and
the COO can ask the core-system owner which.

A milestone a COO can read has five properties. The Godavari milestones file has a column for each,
and the script checks four of them:

| Property | Test | Godavari example (M13) |
|---|---|---|
| **Observable** | someone outside the project team could check it | "six analysts use it every day" (the queue logs who used it) |
| **Dated** | a day, not a week | Monday 7 December |
| **Owned on both sides** | one Kaagaz name and one Godavari name | the Kaagaz FDE; Srinivas and the Vijayawada team lead |
| **Plain** | no word the sponsor would need explained; under 25 words | no "API", "SOAP", "sandbox", "pipeline", "model" |
| **Consequential** | something later depends on it | the pilot results (M17) need it |

The jargon test is mechanical on purpose. "The SOAP CreateApplication call is idempotent" is a
sentence for the core-system owner; the COO's version is "no duplicates". A milestone you cannot
translate into his words is probably a task.
[Day 29](../../05-working-with-the-customer/29-communication-for-engineers/README.md) owns writing for
a COO in general; the milestone line is the smallest unit of it.

Every one of the twenty-two milestones has a Godavari name next to the Kaagaz one, and for nine (the
four gates and the five COO meetings) the Godavari person decides. A milestone with only a vendor owner
is one the customer can watch you miss; one with both is one you hit together.

## 4.2 Gates are milestones someone else decides

The milestones file has three kinds: a **milestone** the team makes true (the skeleton demo, the
rollout waves); a **gate** a customer person decides, without which the next step cannot happen (the
compliance head's signature, the CISO's approvals, the core-system owner's live-write switch); and a
**checkpoint**, a meeting at which the customer answers a question that changes what happens next.
Gates are where plans die quietly, because they look like your milestones on the chart but their date
is someone else's decision. So they are requested early (the CISO is asked in week 1 for a week-6
decision), the decider is the Godavari owner, and any gate with a hard date has a measured buffer.

## 4.3 Checkpoints at weeks 2, 4, 6 and 12

The Part 2 plan puts checkpoints at weeks 2, 4, 6 and 12. Each one exists because the customer has to
answer a question, and the question is written into the plan in advance so that nobody arrives at the
meeting wondering what it is for.

| Week | Date | The question the customer answers | What happens on each answer |
|---|---|---|---|
| 2 | Fri 6 Nov (M04) | "Is this the problem, and is this the plan you will hold us to?" | yes: the COO signs the plan and the "will not do" list; no: the problem statement is reopened, which is cheap in week 2 |
| 4 | Fri 20 Nov (M08) | "Do you commit to a two-branch pilot in December, on these terms and these numbers?" | yes: the discovery document is signed (Day 10) and pilot preparation becomes the main work; no: the plan is versioned with the reason |
| 6 | Fri 4 Dec (M12) | "Is accuracy on your analysts' files at the agreed bar, and are the rules and the security approval signed, so two branches start on Monday?" | yes: the pilot starts on 7 December; no: the pilot waits a week and the slip order applies |
| 12 | Tue 12 Jan (M20) | "Can your team run this without us?" | yes: the last week is Godavari running, Kaagaz watching; no: the handoff gap goes into the day-90 review as the next 90 days' first item |

The week-12 checkpoint was planned for Friday 15 January and the script moved it to Tuesday 12 January,
because 13 to 15 January are the Sankranti holidays. It moved earlier, not later, because a handoff
check that slides into week 13 leaves no time to act on a "no". The milestones file says so with a
`direction` of `earlier` on that row.

There is a fifth meeting, the day-90 review on Friday 22 January (M22), with the question "What do the
next 90 days buy you?". It is not one of the four checkpoints; it is the end of this plan and the start
of the next one, and Day 9's business case is what makes that question answerable.

Three rules make checkpoints work: the question has a yes and a no and the plan says what each does
("review progress" is not a question); the person who can answer is in the room; and a "no" is a
legitimate outcome. If week-6 accuracy is below the bar, saying so and waiting a week is the plan
working. [Day 30](../../05-working-with-the-customer/30-delivering-bad-news/README.md) owns how to say it.

## 4.4 The two-company RACI

RACI is the familiar grid: **R**esponsible (does the work), **A**ccountable (one person who answers for
the outcome and can say it is done), **C**onsulted (asked before), **I**nformed (told after). Inside
one company it is a formality. Across two companies it is the document that settles arguments in week
ten about whose job something was.

Godavari's grid is in `data/godavari-raci.csv` and on the [plan page](worksheet/godavari-90-day-plan.md)
(section 8). Three rows show its logic (K: Kaagaz, G: Godavari):

| Row | Accountable | Responsible | Consulted |
|---|---|---|---|
| W2 Completeness rules | G: compliance head | K: FDE | G: team leads, eval owners |
| W5 Security review | G: CISO | K: security lead, G: IT identity team | K: FDE, G: compliance head |
| RUN (after day 90) | G: application-support engineer | G: application-support engineer | K: FDE, G: CISO, core-system owner |

Four rules the script enforces or the review checklist asks for:

1. **Exactly one A per row.** Two accountable people means none. The script refuses a row with two
   (exercise 2.3 shows the message).
2. **The A sits where the decision sits.** The compliance head is accountable for the completeness
   rules because she signs them; the CISO for the security review because she decides it; the eval
   owners for the golden set because their judgement defines "correct" (Day 5's eval-customer split).
   Kaagaz is accountable only for what Kaagaz builds and owns: extraction and integration.
3. **Anything that runs past week 10 has a Godavari R.** Otherwise, on day 91, it has nobody. The
   script checks this, and on its first run it caught a real gap: the PLAN row had no Godavari R, which
   meant that after the FDE left, nobody at Godavari kept the plan, the calendar or the checkpoint
   dates. The fix was to make the team leads responsible with the COO accountable.
4. **No row is "Godavari" or "Kaagaz".** A company cannot be accountable; a named role can.

## 4.5 What the customer's engineers own from day one

The last row, RUN, is the reason the RACI exists. Handoff ([Day 28](../../04-deploying-into-their-world/28-handoff-and-self-sufficiency/README.md))
is not an event in week 13; it is a sequence of things the customer's engineers own from the start, so
that by week 13 there is nothing left to hand over:

| From | Godavari owns | Why then |
|---|---|---|
| week 1 | the access tickets and the service account (IT identity team) | the account is theirs; Kaagaz never holds production credentials (the CISO's condition) |
| week 2 | the test-copy refresh and the live-write switch (core-system owner) | his system, his switch; the month of clean calls is measured on his logs |
| week 2 | the golden set (eval owners) | correctness is their judgement |
| week 6 | the signed rules (compliance head) | a rule change is a compliance decision, not a code change |
| week 8 | deployments, alongside the FDE (the application-support engineer IT assigns in week 2) | he deploys to the Mumbai environment with the FDE, then without |
| week 12 | a release on his own (M21, 12 January) and a week of running with Kaagaz watching (M20) | the 12-week bar, tested rather than asserted |

The application-support engineer is the person most plans forget, because he was in no discovery
meeting. Ask IT for him in week 2; if nobody can be spared, that goes on the week-4 readout agenda.

## 4.6 Key takeaways

- A milestone is observable, dated, owned on both sides, plain and consequential; the COO line is
  under 25 words with no jargon.
- Gates are milestones a customer person decides; request them early and measure their buffers.
- Checkpoints at weeks 2, 4, 6 and 12 each carry a yes-or-no question and what each answer does.
- The two-company RACI has one A per row, the A where the decision sits, and a Godavari R on anything
  that runs past week 10.
- Handoff is a sequence of things the customer owns from week 1, not an event in week 13.
