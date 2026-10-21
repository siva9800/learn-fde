# 06 · The One-Sentence Problem Statement, and Declining on Day 4 Without Losing the Sponsor

> Day 4 · Section 6 of 12 · [Chapter overview](README.md) · Previous: [05 · The traps](05-the-traps.md) · Next: [07 · 2026 patterns and production concerns](07-2026-patterns-and-production-concerns.md)

---

## 6.1 What the sentence is for

The output of Day 4 is one sentence that the sponsor and the operators both sign. Not a scope, not
a plan, not an architecture: a statement of the problem that both the COO and the analysts would
read and say "yes, that is it". [Day 7](../07-decomposition/README.md)'s step 1 starts from this
sentence; Day 9's baseline measures the numbers in it; Day 10's discovery document opens with it.
If it is wrong, everything downstream is built on the wrong thing, which is why it is written on
Day 4 and signed before any interview on Day 6.

The sentence has four parts, and leaving any out is the usual mistake:

| Part | What it carries | Godavari |
|---|---|---|
| **The unit of work** | what one instance of the problem is, so that frequency means something | a new loan file |
| **The cost, as a number the customer already has** | the baseline, in the customer's own measure, so that measurability is real | a median of nine days from receipt to decision |
| **The cause, as the floor sees it** | where the waiting, re-keying or rework is, so that the operators recognise it | intake is manual and a third of files are incomplete |
| **No solution** | not a model, not a tool, not a product category, so that Day 7 can do its work | (nothing) |

Godavari's, as signed:

> New loan files take a median of nine days from receipt to decision because intake is manual and
> a third of files are incomplete.

Read it against the COO's version ("the analysts are slow; I want three days") and the analysts'
version ("we wait three days for the branch to resend a document, then the batch runs overnight").
It contains neither accusation and both facts. [Day 5](../05-the-stakeholder-map/README.md) will
show that the two versions are both true from where each person sits; the sentence is the first
place they meet.

## 6.2 What is deliberately not in it

- **"Three days."** The target is the COO's, and it is real, but it is not the problem. Day 9 turns
  it into "three to four days in the pilot branches by day 90", a range with a method. A target in
  the problem statement becomes a promise before the baseline is measured.
- **"Using AI" or any technology.** The sentence must survive the Day 7 test: no model, database or
  framework word before step five. Day 11 decides what the model does and what deterministic code
  does; that decision cannot be made on Day 4 and should not be pre-empted by a word.
- **The tracker, the batch, the SOAP API.** These are causes at a finer grain, and Day 6 will map
  them. The sentence names the cause at the grain the operators use ("intake is manual"; "files are
  incomplete"), not the grain the architecture will use.

## 6.3 Who signs, and what signing means

Three signatures on Day 4: the COO as sponsor, and the two credit-ops team leads (Srinivas in
Hyderabad and his counterpart in Vijayawada) for the operators. Lakshmi, who showed you the
tracker, is asked to read it and say whether the analysts would recognise it; she is not a
signatory yet (Day 5 decides who the champion is).

Signing means: "this is the problem we are spending the first twelve weeks on, and the other seven
are on the list with a reason each." It does not mean a scope (Day 8), a number (Day 9) or a
contract change. Keep it that light, or nobody will sign it on a Friday.

## 6.4 Declining the other seven on Day 4

The COO brought seven. You are picking one. The other six, plus the tracker, need a sentence each
by Friday, and the shape of that sentence is the one Day 10 drills: **not now, because, and
instead**. On Day 4 the "because" is the gate or the column the candidate lost on, and the
"instead" is what would make it scoreable next cycle.

| Candidate | Not now, because | And instead |
|---|---|---|
| C2 income verification | it waits on intake: a third of the statements have not arrived when the file is opened | second in the ranking; the natural next slice once intake runs (Day 8 decides whether it is in the 90 days) |
| C7 credit memo | its inputs are the fields intake would extract; building it first means building intake twice | third in the ranking; revisit after the skeleton (Day 20) |
| C8 the tracker | the analysts do not want it replaced; they want to stop running two systems | a constraint on intake: read the tracker before replacing it, write status back (Day 7's step 3) |
| C3 KYC and re-KYC | the compliance head owns it and has said not this year; the operators are branch staff we have not met | the completeness check in intake enforces the RBI document list; re-KYC is a second-cycle candidate with her as sponsor |
| C6 collections summaries | a different team, recordings held by the dialler vendor, DPDP questions open | the collections head in the room for the next cycle; the contract with the dialler vendor read first |
| C5 branch chatbot | no baseline: nobody has counted the calls | one branch counts policy calls for a month; score it next cycle |
| C4 title deeds | 120 a month, reviewed by lawyers outside the company, no owner of the data | a question for the legal head; likely never ours |

Say the sentences in the order of the ranking, so that the COO hears "second" and "third" before he
hears "no". A sponsor who hears that his list has an order is a sponsor who has been listened to. A
sponsor who hears six noes has been told his list was wrong.

The "and instead" column is what keeps the relationship. It is also honest: four of the seven are
real problems that will be scoreable once something changes, and the memo says what. Day 8 turns
three of these lines into the formal "will not do" list and Day 10 defends them in the readout; the
sentence the COO hears there about the chatbot is the one written here.

## 6.5 The conversation, rehearsed

Interviewers run this as a client-simulation prompt ("the COO wants the chatbot; you want
intake; go"), and Day 34 drills six of them. One pass of the Day 4 version:

**COO:** "I like the completeness idea. But the chatbot is what the board saw. Can we do both?"

**You:** "We can do both over the year. In the first twelve weeks, doing both means neither is in
daily use by day 90, and the twelve weeks is the test of whether this is worth renewing. Intake is
1,400 files a month, 2,100 analyst hours, a third of files reworked, and you already report the
numbers it would move. The chatbot has no count yet. If Kukatpally branch logs its policy calls for
the next month, we will know whether it is the second thing or the fifth."

**COO:** "And if the count is high?"

**You:** "Then it goes to the top of the next cycle with a baseline, which is more than it has
today. I would rather show the board a chatbot with a number than a chatbot with a demo."

Three things in that exchange are the scored behaviours: the number instead of the adjective, the
reason instead of the refusal, and the alternative that costs the customer something small (a
month of counting) and gives them something real (a baseline).

## 6.6 Key takeaways

- The sentence has four parts: unit of work, cost as a number the customer already has, cause as
  the floor sees it, no solution. Godavari's is signed by the COO and the two team leads.
- The target, the technology and the fine-grained causes are deliberately not in it.
- The other seven get "not now, because, and instead", said in ranking order. The "instead" is
  what makes each scoreable next cycle.
- The chatbot sentence written here is the one Day 10 says in the readout.
