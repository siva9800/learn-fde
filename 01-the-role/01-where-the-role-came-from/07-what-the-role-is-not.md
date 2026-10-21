# 07 · What the Role Is Not: Three Older Jobs, the Hype, and the Test

> Day 1 · Section 7 of 12 · [Chapter overview](README.md) · Previous: [06 · The 2026 adopters](06-the-2026-adopters.md) · Next: [08 · Production concerns, mistakes and debugging](08-mistakes-and-debugging.md)

---

## 7.1 Three jobs wearing the title

Day 0 gave you the one-table version. Here it is with the lineage behind it, because the confusion is
not random: each of the three is a real job that shares one edge with the FDE and lacks the rest.

| The job | Shares with the FDE | Lacks | How to spot it in a posting |
|---|---|---|---|
| **Solutions engineer (pre-sales)** | customer-facing; technical; builds things for a specific customer | the timing and the finish line: the SE "lives in the pre-sales cycle" and the FDE "picks up where the SE left off" (Paraform, April 2026); SE pay leans on variable compensation "tied to deals closed"; the SE's build is a demo, never production | "support the sales team", "proof of concept", "OTE", quota language, "hand off to delivery" |
| **Consultant or systems integrator** | on site; the customer's data and rules; production work | the loop: the consultant's work ends in the customer's codebase and is paid for once; nothing goes back to a product; every project starts from zero (Day 3) | "billable", "statement of work", "client deliverables", "practice", no product named, "any technology the client uses" |
| **ML engineer or model trainer** | applied AI; evals; data | the customer: the trainer improves the model in the lab; the FDE deploys the model that exists into a business that exists; "not training models" is explicit in the course's reading of 80 percent or more of 2026 postings | "pre-training", "fine-tuning pipelines", "GPU", "research", no customer named |

The Delta's edges from section 02 are the same three. A Delta did not sell, did not deliver a report
and leave, and did not build the core platform. The AI-era FDE does not sell, does not leave a
codebase and go, and does not train the model. Twenty years, same edges.

## 7.2 The test

If you could do the job without ever seeing the customer's data, their systems or their people, it is
not the FDE job. Add the lineage's second clause: if nothing from the engagement will ever improve the
vendor's product, it is not the FDE job either. The first clause rules out the lab. The second rules
out the integrator. The solutions engineer fails both: a demo on sample data, and nothing to send back
because nothing was built.

## 7.3 The 2026 patterns, and what is hype

Three things practitioners are actually doing in 2026, and three things the market says that are
not true.

**Real:**

- **One person, both halves.** The Delta plus the Echo in one engineer (section 02.4). This is why
  Part 2 of this course exists and why customer-facing discovery is the fastest-rising bucket in
  postings (Day 2).
- **The time box.** Twelve weeks to a self-sufficient team (Atlassian, October 2026) rather than a
  year-long embed. The engineer's job is to leave.
- **Coding agents moving the split.** The 2026 panel reports that models which handle long-horizon
  coding tasks have shifted FDE time toward the customer's problem and away from the build, and that
  roughly 80 percent of about 50 products OpenAI's team expected to need later became possible as
  extensions of its coding tool. Part 7 of this course is about working that way on customer code.

**Hype, or at least unsupported:**

- **"Every company needs FDEs."** The model is expensive and is justified only where the gap between
  product and outcome is wide (section 05.1). A vendor whose product installs cleanly does not need
  them and should not be hiring them; a posting for one at such a vendor is usually a solutions
  engineer or an integrator role.
- **"FDE is the new consulting, and it pays better."** It pays better where the loop runs (Day 3's
  revenue-per-FDE logic). Where it does not, it is consulting at consulting economics with a product
  company's expectations. Some of the Indian postings at 5 to 10 lakh (Day 3) are this.
- **"The role will disappear when models get good enough."** The published teams report the opposite
  so far: better models widened what could be attempted and raised demand about ten times in a year
  (section 05.5). What may shrink is the build; the gap stays.

## 7.4 What to ask in the interview to tell them apart

Four questions, each of which checks one edge. Ask them of the hiring manager; the answers are the
chapter's content in reverse.

1. "When does an FDE join an engagement, and when do they leave?" (After the deal and at
   self-sufficiency is the FDE answer. Before the deal is an SE. Never is an integrator.)
2. "What came from the field into the product in the last year?" (A list is the loop running.
   Silence is the dark ages, or a consultancy.)
3. "What do you measure the team on?" (Revenue per FDE, adoption, time to self-sufficiency are FDE
   answers. Utilisation and billable hours are not.)
4. "What will I not be allowed to build?" (A real answer shows the refusal in section 04.3 exists.
   "Whatever the customer needs" is the dark ages scheduled.)

## 7.5 Key takeaways

- Three older jobs share one edge each with the FDE: the SE is pre-sale and paid on the deal; the
  consultant has no loop; the model trainer has no customer.
- Two-clause test: could you do it without their data, systems and people? Will anything go back to
  the product?
- Real in 2026: one person carrying Delta and Echo, a twelve-week time box, coding agents shifting
  time toward the customer. Hype: everyone needs FDEs, it is consulting with better pay, it will vanish
  when models improve.
- Four interview questions check the four edges.
