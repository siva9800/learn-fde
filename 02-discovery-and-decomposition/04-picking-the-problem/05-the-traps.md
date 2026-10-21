# 05 · The Traps: The Demo, the Chatbot, the Pet Project, the Missing Baseline and the Edge Case

> Day 4 · Section 5 of 12 · [Chapter overview](README.md) · Previous: [04 · The scoring sheet](04-the-scoring-sheet.md) · Next: [06 · The problem statement and declining](06-the-problem-statement-and-declining.md)

---

Every trap in this section is a problem that looks good in the room and scores badly on the sheet.
Each has a tell you can hear in the first meeting, a column where it loses, and a sentence for
declining it. They are worth learning as a list because interviewers ask for them by name ("what is
the demo trap?") and because you will meet all five at every customer.

## 5.1 The demo trap: impressive, and it happens twice a month

The tell: "we showed this to the board and they loved it." The problem is real, the model does
something visibly clever with it, and the unit of work happens rarely. Title-deed review at
Godavari is the clean example: a model reading a scanned Telugu registered deed and listing the
encumbrances is a remarkable demo, and there are about 120 of them a month, reviewed by lawyers
who are not Godavari's staff.

Where it loses: frequency 2, and usually measurability and data as well, because rare work is
rarely timed and often outsourced. The sheet's frequency anchor exists for this row.

The sentence: "It is the best demo on the list and it happens 120 times a month to people outside
the company. Intake happens 1,400 times a month to forty of your analysts. I would rather show you
the impressive one after the valuable one is in daily use."

## 5.2 The chatbot trap: a solution wearing a problem's clothes

The tell: the candidate is named after a product category, not after a cost. "A chatbot for the
branches" is not a problem. The problem, if there is one, is "branch staff phone Hyderabad about
policy and wait", and nobody at Godavari has counted the calls, the waiting or the wrong answers
given over the phone.

Where it loses: measurability 1 and all three gates. There is no baseline because there is no
count; there is no data owner because the forty circulars live in email with unclear versions and
nobody owns them; there is no operator who asked, because no branch manager was in the room.

The sentence, which [Day 10](../10-the-discovery-document/README.md) says in the readout: "Not now,
because there is no baseline. If a branch counts its policy calls for a month and we find they
cost what you think, it goes to the top of the next cycle." Day 7's method calls the same thing the
"LLM with RAG in minute one" anti-pattern: a technology chosen before the trade-off, the people or
the data were known. The chatbot trap is that anti-pattern arriving from the customer's side of the
table instead of yours.

A retrieval assistant over Godavari's documents may well be right later; Days 15 and 22 build
permission-aware retrieval for the loan files themselves. The trap is not the technology. It is
scoring a technology as if it were a problem.

## 5.3 The sponsor's pet project

The tell: the sponsor raises it in the second call, not the first, and with more energy than the
rest. At Godavari it was the branch CRM, declined on [Day 3](../../01-the-role/03-the-economics/README.md)
with the second-customer test, and collections call summaries, raised the same way.

Where it loses: sponsorship, counter-intuitively. The column asks for three things (a sponsor, an
operator who wants it, and product fit), and the pet project has only the first. Collections has a
sponsor who is not the operator's boss (the collections head reports elsewhere), no agent who was
asked, and a data owner outside the company. It also fails the owner and operator gates.

The sentence: "I can see why it appeals; it is a large volume and the model is good at it. The
people whose day it would change report to someone we have not met, and the recordings are held by
your dialler vendor under a contract I have not read. If the collections head wants it, let us put
it on the list for the second cycle with her in the room."

The pet project is dangerous for a reason the demo trap is not: it comes with budget. Saying yes
is easy, pays this quarter, and is scenario B1 in Day 3's model, the engineer who cannot leave.

## 5.4 The problem with no baseline

The tell: "everyone knows it is slow." Nobody has a number. The pain may be real; the proof will
never exist. At Godavari the chatbot and the title deeds both fail here; so would a candidate like
"improve the quality of the credit memos", where quality has no count.

Where it loses: the baseline gate, and measurability. The sheet does not let a candidate without a
baseline be scored this cycle, whatever its pain, because [Day 9](../09-success-metrics-and-business-case/README.md)
needs a number to start from and Day 37 needs one to measure against, and because a baseline
counted after the system exists is counted by people who want the system to look good.

The sentence: "Before we build anything for this, someone has to count it for two weeks the way
the operators agree. If the count says what you think, it is a strong candidate. If we skip the
count, we will never be able to show you it worked."

## 5.5 The edge case at the edge of the business

The tell: "nobody will object to this one." It is easy to get permission for because nobody
important depends on it, and for the same reason nobody will use it. OpenAI's interview names the
pattern from the other side: the deployments that worked were high-stakes use cases at the core of
the business rather than edge cases.

Where it loses: pain and sponsorship, and usually frequency. At Godavari the clean example is a
candidate nobody raised but that an engineer might offer to avoid the compliance head: "let us start
with something safe, like summarising the internal audit reports." Twelve a year, read by three
people.

The sentence, to yourself as much as to the sponsor: the blast radius column is handled by design
(a human decision per file, Day 18's review queue), not by choosing problems that do not matter.
Intake's completeness check carries a blast radius of 3 because a missed KYC document is an audit
finding. That is a reason to keep the rules deterministic and signed (Day 11), not a reason to go
and summarise audit reports instead.

## 5.6 The traps on one sheet

| Trap | Tell | Loses on | Godavari row |
|---|---|---|---|
| The demo | "the board loved it" | frequency | C4 title deeds |
| The chatbot | named after a product category | measurability; all three gates | C5 branch chatbot |
| The pet project | raised in the second call, comes with budget | sponsorship (no operator, no product fit); owner gate | C6 collections; the CRM on Day 3 |
| No baseline | "everyone knows it is slow" | the baseline gate | C5 again; C4 |
| The edge case | "nobody will object" | pain, sponsorship | the audit-report summariser nobody asked for |

And the one that is not a trap but looks like one: the tracker (C8). It scores 80, fails the
operator gate, and is neither picked nor dropped. Section 08 explains.

## 5.7 Key takeaways

- Five traps, each with a tell, a column it loses on, and a sentence for declining it with a reason
  and an alternative.
- The chatbot trap is Day 7's "LLM with RAG" anti-pattern arriving from the customer's side.
- The pet project is the dangerous one because it comes with budget; Day 3's model shows what the
  yes costs.
- Blast radius is handled by design, not by choosing problems that do not matter.
