# 05 · What You Will Not Do, and Why Writing It Down Protects the Engagement

> Day 8 · Section 5 of 12 · [Chapter overview](README.md) · Previous: [04 · Milestones, checkpoints and the RACI](04-milestones-checkpoints-and-the-raci.md) · Next: [06 · Buffers, slips and re-planning](06-buffers-slips-and-re-planning.md)

---

## 5.1 The most important page of the plan

The Part 2 plan's second Short says it in one line: the most important page of the plan is the list of
what you will not build. That sounds like a slogan until you watch an engagement without one.

Week 5: the COO, pleased with the skeleton demo, mentions that branch managers would love to track
customer follow-ups "in the same screen". Nobody says no. Week 9: the FDE spends three days on a
prototype "just to show it". Week 11: the Vijayawada rollout slips, because those three days were the
buffer. Week 13: the day-90 review spends twenty minutes on the follow-up screen and four on
turnaround.

Day 3 ran the numbers on that request. The branch CRM keeps an FDE on site full time for 36 months and
drops revenue over FDE cost to 2.2x, below Kaagaz's floor. It fails the second-customer test: no other
lender wants Godavari's CRM. Day 3 also wrote the sentence that refused it. What Day 3 could not do is
make the refusal stick. A refusal said once in a meeting is forgotten by the next sprint. A refusal
written on a page the COO signed is a fact both sides can point to.

## 5.2 Three lists, not one

People put three different things under "out of scope", and mixing them weakens all three. Keep them
apart:

| List | What it holds | Who signs | Can it change? |
|---|---|---|---|
| **Will not do** | work this engagement will not take on at all, usually something someone asked for | the sponsor and your own side | only by a new agreement, in writing, at a checkpoint |
| **Not in these 90 days** | real candidates parked, each with a reason and a revisit date | the sponsor | yes, at the revisit date |
| **Constraints** | conditions the work must meet (Day 5's list, Day 7's step 1) | the blocker who set them | no; they are not scope at all |

At Godavari the "will not do" list has four lines, as the Part 2 plan specifies. Two are refusals of
things the sponsor's side asked for. Two are blockers' conditions restated as scope, because they are
the kind of thing a well-meaning engineer could otherwise drift into.

| # | We will not | Because | Agreed by |
|---|---|---|---|
| 1 | build the branch CRM (customer follow-ups for branch managers) | it is not Kaagaz's product, no other lender would buy Godavari's version, and it would keep an FDE on site for a year doing work Godavari's IT or a CRM vendor does better (Day 3). Instead: the file status is exposed so that a CRM, or the tracker, can read it | the COO; the Kaagaz CEO and engagement lead |
| 2 | build collections call summaries | a different team of forty agents, Telugu recordings held by the dialler vendor, and DPDP consent questions open; the collections head was never in the room (Day 4). Instead: a candidate for a later cycle with the collections head as sponsor | the COO |
| 3 | change the core lending system's data model, or ask for a change to it | the core-system owner's condition; three vendors have broken his system before; every field we write already exists in CreateApplication (Day 6) | the core-system owner; the COO |
| 4 | send, store or process customer PII outside India, in any environment, including tests and logs | the compliance head's first sentence in week 1, and the CISO's condition; the law and RBI guidance behind it are Day 24's | the compliance head; the CISO; the COO |

Each line has a reason a stranger could follow, an "instead" where there is one, and the name of the
person who agreed. Without the name, the line is the vendor's preference. With it, the line is the
customer's decision.

## 5.3 The parked list

The "not in these 90 days" list comes mostly from Day 4's "not now, because, and instead" table, so
that nothing good is lost and the sponsor knows when he will hear about it again. At Godavari it holds
the branch chatbot (no baseline; Kukatpally logs its policy calls for a month and it is scored at the
day-90 review), income verification (the first candidate for the next 90 days), credit-memo drafting,
KYC and re-KYC (the compliance head's "not this year"), title deeds and vendor SSO, each with a revisit
date in section 7 of the [plan page](worksheet/godavari-90-day-plan.md). The Excel tracker is not on
it: the plan does not replace the tracker, it writes status back to it, and that is a constraint.

## 5.4 Why the written list protects the engagement

1. **The schedule.** Every unplanned yes is paid for out of the buffer, and Godavari's buffers are six
   and seven working days (section 06). One "small" request uses either.
2. **The sponsor.** The COO can say no to his own branch managers by pointing at a page he signed. He
   is defending his decision, not a vendor's refusal.
3. **The relationship.** The refusal happens once, in week 2, calmly, with reasons and an alternative,
   instead of every Friday with less patience each time.
4. **Your own company.** Line 1 is Kaagaz's economics as much as Godavari's scope; the engagement
   lead's signature stops your own sales team promising the CRM at renewal.

## 5.5 Writing a line that holds

Most bad "will not do" lists fail in one of five ways:

| Weak line | Why it fails | Strong version |
|---|---|---|
| "We will not build a mobile app" | nobody asked; it refuses nothing (Day 3's warning) | refuse something someone actually wants: the branch CRM |
| "Out of scope: integrations" | too broad; the core-system integration is the whole point | name the thing: "no change to the core system's data model" |
| "No CRM" | no reason, so it will be reopened | the reason and the second-customer test, in one sentence |
| "CRM deferred" | no date and no owner, so it is a promise in disguise | either "will not do" with a signature, or parked with a revisit date |
| a list of twenty items | nobody reads it; the important refusals are hidden | four to six lines; the rest goes to the parked list |

And one rule about timing: the list is signed at the **week-2 checkpoint**, before the skeleton demo.
After a good demo every request feels affordable, and every refusal feels ungracious. Sign it while
the plan is still a plan.

## 5.6 When someone pushes on the list

They will. The list changes the conversation from "can you also..." to "do we want to change what we
signed?", and the answer has three parts: what the change costs in dates (run the slip), what comes off
the plan to pay for it (the slip order), and the checkpoint at which it could be agreed.
[Day 10](../10-the-discovery-document/README.md) rehearses the COO asking for the chatbot in the
readout; [Day 32](../../05-working-with-the-customer/32-scope-pushback-and-governance/README.md) owns
the harder case where a request crosses a governance line.

## 5.7 Key takeaways

- A refusal said in a meeting is forgotten; one on a signed page is a fact both sides use.
- Keep three lists: will not do (signed), not in these 90 days (revisit dates), constraints (not scope).
- A strong line refuses something someone wants, names it precisely, gives the reason and the agreer,
  and is signed in week 2, before the demo makes everything feel affordable.
