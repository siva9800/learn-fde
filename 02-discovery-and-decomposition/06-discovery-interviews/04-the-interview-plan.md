# 04 · The Interview Plan: 8 to 10 End Users Before Any Production Code

> Day 6 · Section 4 of 16 · [Chapter overview](README.md) · Previous: [03 · Shadowing](03-shadowing.md) · Next: [05 · The question bank](05-the-question-bank.md)

---

## 4.1 The number, and where it comes from

The 2026 discovery playbooks that this course cites converge on a number: **interview at least 8 to 10 end users, not just the executive sponsor, before writing production code.** One of them (getperspective.ai's discovery playbook, July 2026) states it as the exit criterion of its interview phase and gives the reason: sponsors and operators describe the problem differently, and a requirement should appear in at least three independent interviews before it enters the spec; a pain mentioned once is a hypothesis. The same vendor's earlier article (May 2026) says "interview at least 10 end users before writing production code" and argues for more, run asynchronously, because "variance matters more than volume". Both are vendor content, and the vendor sells interview tooling; the number is quoted as published, and it matches what the published FDE accounts describe.

Why that many? Three reasons that you can see in Godavari's ten:

- **The three-interview rule needs a denominator.** With four interviews, nothing reaches three independent sources except the things everybody says. With ten, the branch-isolation rule appears in five, the tracker in five, the WhatsApp channel in six, and the chatbot in none. The tally in section 12 is only meaningful because there are enough interviews to tally.
- **Roles disagree, and the disagreement is the finding.** The COO's version ("the analysts are slow") and Srinivas's ("my people spend the week chasing branches") are both in the pack. The branch manager's ("credit-ops sends files back for no reason") and the analysts' ("they send rubbish") are both there too. Day 5 taught you that both versions are true; the plan has to include enough seats to hear every version.
- **The sceptic and the newest person say things nobody else will.** The senior analyst's "it typed four lakh eighty thousand as monthly" and Bhavani's "I would not know; that is the honest answer" are two of the eight architecture-changing findings. Neither would have been in a plan built from the sponsor's introductions.

## 4.2 From the stakeholder map to a roster

The plan is [Day 5](../05-the-stakeholder-map/README.md)'s map with dates and a reason per row. The Godavari roster is in [`worksheet/interview-plan.md`](worksheet/interview-plan.md); here is how it was built.

| Map category | How many to interview | Who at Godavari | Why that person |
|---|---|---|---|
| Operators | 4 to 6, both cities, senior and junior | Lakshmi; the senior analyst in Hyderabad; Bhavani; Srinivas as the operator lead | the most experienced, the sceptic, the newest, the person who runs the queue |
| Upstream producers | 2, near and far | the Kukatpally manager; the Guntur manager | the pilot branch and the branch with the most phone photos |
| Admins and blockers | all of them | the CISO; the compliance head; the core-system owner | each can stop the engagement; each owns a rule that becomes architecture |
| The sponsor | 1 | the COO | the number, and what must never be automated |
| The ghost | 0, by design | the RBI auditor | the compliance head speaks for him; write down that every auditor sentence is hers |
| The champion | daily, not an interview | the Vijayawada team lead | sat in on Lakshmi's interview and the Friday review |

Ten transcripts: six operators and upstream producers, three admins, one sponsor. The playbooks' number is about end users, and the admins and the sponsor are on top of it: six end users have full transcripts, and the two Hyderabad analysts shadowed on Tuesday of week one were questioned on the floor without a full transcript, which makes eight end users heard before any production code.

## 4.3 Persona-specific scripts

The three personas ask for different scripts because the same question lands differently in each seat. "What happens when it is wrong?" to an operator is "what happened to you last time?"; to an admin it is "what does the regulator do?"; to the sponsor it is "what does the board do?". Operators are asked to show; admins are asked where rules live and who signs them; the sponsor is asked for the number, the trade-off and the governance line in his own words. [`worksheet/question-bank.md`](worksheet/question-bank.md) has the full scripts and section 05 walks through them.

Day 5 gave three first-conversation scripts for the week-0 meeting with each role. These are the full banks for the discovery interview that follows, and they assume the shadowing has happened.

## 4.4 Sequencing

The order matters as much as the roster. The Godavari plan used six rules:

1. **Shadow before interviewing an operator, and interview the same day.** The questions come from the log; the memory is fresh on both sides.
2. **Operators before the sponsor.** You want to walk into the COO's office with "the analysts told me the files wait three days for a branch" and watch him say "I had assumed the days were in Hyderabad". Interview him first and you will carry his version into every operator interview as a leading question.
3. **Blockers in week one or two.** Day 5's rule: the blocker met early writes conditions; the blocker met late writes a refusal. The CISO's interview produced the group-filtering requirement, the seven-year view log and the on-prem prototype rule; all three are cheap in week two and a rewrite in week ten.
4. **The system owner before the WSDL in anger.** An hour with him on Thursday of week one meant the WSDL reading that afternoon had a purpose (CreateApplication, retries, the lookup nobody uses), and the week-two spike had a question to answer.
5. **Synthesise after every three or four interviews.** The playbooks say so and the reason is practical: after Lakshmi, the senior analyst and the core-system owner, "unsure, not a guess" had already appeared twice and the question went into every later script. Synthesis at the end alone would have found it; synthesis every three interviews made the later interviews better.
6. **Read back at the end of every interview; file the same day.** Section 06.

## 4.5 "Before any production code"

The phrase is in the Part 2 plan and in every playbook, and it is worth being precise about what it forbids. It does not forbid code. Day 2's week two has a SOAP spike, an extraction run on twenty files and thirty labelled files with Lakshmi; all of that is discovery code, written to answer a question (does the API tolerate retries? what does the model read today?) and thrown away or kept as a stub. What it forbids is building the thing: the pipeline, the review screen, the index. Build those before the ten interviews and you will build them for the sponsor's version of the problem, with an index that has no groups in it and a screen that sits beside the tracker.

A test: if an interview answer in week two would make you delete it, it is production code and it is too early.

## 4.6 When you cannot get ten

Sometimes the customer offers three people and a week. Make them the sceptic, the most experienced operator and the admin who owns access; those three produce the most architecture per hour. Shadow harder: one full cycle beside the experienced operator is worth more than two short interviews. Write the plan anyway, with the empty rows, and put them in the readout as a risk; a customer who sees the empty rows usually fills them. And never substitute the sponsor's description of an operator for the operator: "the analysts would say X" is a hypothesis whose one source has the least view of the floor.

## 4.7 Key takeaways

- 8 to 10 end users, across roles and locations, before any production code; the playbooks' number, quoted from vendor content, and the denominator the three-interview rule needs.
- The roster is Day 5's map with a reason per row: senior and junior, near and far, every blocker, the sponsor once, the ghost never.
- Three persona scripts, because the same question lands differently in each seat.
- Sequence: shadow then interview, operators before the sponsor, blockers early, the system owner before the WSDL, synthesise every three interviews, read back and file the same day.
- Discovery code is fine; building the thing is not. If an answer would make you delete it, it is too early.
