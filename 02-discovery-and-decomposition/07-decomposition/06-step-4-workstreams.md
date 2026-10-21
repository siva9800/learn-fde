# 06 · Step 4: Decompose Into Workstreams, Sequenced by Risk and Value

> Day 7 · Section 6 of 16 · [Chapter overview](README.md) · Previous: [05 · Step 3: map the inputs](05-step-3-map-the-inputs.md) · Next: [07 · Step 5: the walking skeleton](07-step-5-walking-skeleton.md)

---

## 6.1 What a workstream is

A workstream is a piece of the work that can be owned by one person or pair, progressed independently
for weeks, and judged on its own. "Build the system" is not a workstream. "Extraction: classify pages
and pull the mandatory fields from scanned PDFs, judged on field-level accuracy against the golden set"
is one.

Workstreams come from steps 1 to 3, not from an architecture diagram. Each row of the inputs table that
carried an architecture risk, each metric in step 2 that needs a thing built to measure it, and each
constraint in step 1 that needs a thing built to respect it, is a candidate. On Godavari, that process
produces six:

| Workstream | Where it came from |
|---|---|
| **Extraction** | the goal (step 1): fields out of scanned PDFs is the core of the value |
| **Completeness checks** | the 31 percent send-backs (step 1's assumption), the compliance head's metric (step 2), the RBI rules row (step 3) |
| **Evals and the golden set** | "no field-level ground truth" (step 3); the compliance head's accuracy metric (step 2) |
| **Integration** | the SOAP row, the SFTP row and the tracker row (step 3); the core-system owner's zero-duplicates metric (step 2) |
| **Security review and the VPC path** | the CISO's metric (step 2); the AD-groups and access columns (step 3); the "nothing leaves India" constraint (step 1) |
| **Enablement** | the analysts' fear (step 2): a tool that adds a step is abandoned; the tracker migration (step 3) |

Notice that four of the six are not "AI work". Evals, integration, security and enablement are where
engagements die, and they are exactly the workstreams an architecture-first decomposition leaves out
(the AI-written draft in section 15 omits two of them).

## 6.2 Scoring value and risk

Each workstream gets two scores from 1 to 5. The definitions matter, because people argue about them.

- **Value**: how much of the step-1 goal this workstream delivers on its own. Extraction is a 5: without
  it there is no speed gain. The security review is a 2: it delivers nothing to the metric directly, but
  nothing ships without it.
- **Risk**: how likely it is that what you learn doing this workstream **changes the plan**. Not "how
  hard is it", and not "how likely is it to fail". The security review is a 5 because an eight-week
  process outside your control, started late, is the usual way engagements die, and its outcome (VPC or
  on-prem, which model endpoints are allowed) changes everything downstream. The completeness rules are
  a 2 because the rules are knowable and the compliance head can sign them in a week.

| Workstream | Value | Risk | Why |
|---|---|---|---|
| Extraction | 5 | 4 | the value; Telugu forms and phone photos make accuracy the big unknown |
| Completeness checks | 4 | 2 | catches the send-backs on day one; the rules are knowable |
| Evals and golden set | 3 | 4 | no ground truth exists; until it does, nobody can say extraction works |
| Integration | 4 | 5 | no idempotency, a quarterly sandbox, a tracker with no API: the biggest technical unknowns |
| Security review and VPC path | 2 | 5 | long, outside our control, changes what is allowed |
| Enablement | 3 | 3 | analysts keep the tracker if the tool adds a step |

## 6.3 Sequencing: risk first, value second, dependencies always

The sequencing rule the guides describe ("sequence the pieces by risk and value") has a precise form:

1. **Risk first.** The workstream most likely to change the plan starts first, because an unknown
   discovered in week two costs a conversation and the same unknown discovered in week ten costs a
   rewrite. This is why integration and the security review start in week one at Godavari even though
   neither produces a visible result for weeks.
2. **Value breaks ties.** Among workstreams of similar risk, the one that moves the metric most goes first.
3. **Dependencies are respected, loosely.** Extraction cannot be judged until the golden set exists, so
   it starts after evals start, but not after evals finish: the first fifty labelled files are enough
   to begin. Overlap on purpose ([Day 8](../08-scoping-the-first-90-days/README.md) makes this the shape
   of the whole 90 days).
4. **Low-risk, high-value work is not last; it is thin and early.** Completeness checks score low on risk
   and so rank low in the full-effort order, but a thin version (one product's rules) is in the walking
   skeleton in week one. The rank says where the full effort goes, not when the first slice appears.

The chapter's script (section 12) applies the rule as `priority = 2 x risk + 1 x value`, respects
dependencies, and limits how many FDE-owned workstreams run at once. On Godavari it produces:

```text
rank  code workstream                                     risk value  prio weeks start  end  owner
   1  W4   Integration: SFTP, tracker, SOAP create with i    5     4  14.0     5     1    5  Kaagaz FDE with core-system owner
   2  W5   Security review and VPC path                      5     2  12.0     8     1    8  Kaagaz security lead with CISO
   3  W3   Evals: golden set of 100 to 200 labelled files    4     3  11.0     4     1    4  Kaagaz FDE with two senior analysts
   4  W1   Extraction: pages and fields from scanned PDFs    4     5  13.0     6     2    7  Kaagaz FDE
   5  W2   Completeness checks: deterministic rules per p    2     4   8.0     3     5    7  Kaagaz FDE with compliance head
   6  W6   Enablement: review queue, tracker migration, r    3     3   9.0     4     6    9  credit-ops team lead with FDE
```

Read the "start" column against the risk column. The three riskiest workstreams all start in week one.
Extraction, the most valuable, starts in week two, one week behind the evals it depends on. The
completeness rules, lowest risk, get their full effort in week five, but their thin version is in the
skeleton from week one. Enablement starts in week six, before the pilot, not after it.

The exact weights are a convention, not a law. What matters is that **the order is explainable**: every
row has a "why this score" cell that you can defend in a readout, and the script prints it. An
interviewer, or a COO, who asks "why is security before extraction?" gets a one-sentence answer, not a
shrug.

## 6.4 The two sequencing mistakes

| Mistake | How it looks | What it costs |
|---|---|---|
| **Value first, risk last** | extraction demo in week two, security questionnaire "once we have something to show" | the review takes eight weeks; the demo sits in a Kaagaz sandbox until week twelve; the sponsor's confidence runs out at week ten |
| **Dependencies as a straight line** | "we cannot start extraction until the golden set is complete, and we cannot start the golden set until the analysts are free" | nothing starts; the first result is in week eight; the engagement looks stalled |

Both come from the same root: treating the plan as a sequence of finished things instead of a set of
overlapping workstreams that each retire a risk. Day 8 owns the dated plan, the checkpoints and the
"will not do" list; step 4 only has to produce an order you can defend and the reason for each position.

## 6.5 What is not a workstream

Three things people put in the table that do not belong:

- **A technology.** "Vector database" is not a workstream; "retrieval over loan documents for the
  analyst's questions" might be one, if a step-2 metric needs it. At Godavari it does not, which is why
  the COO's chatbot is on the "not now" list (Day 10).
- **A phase.** "Discovery", "build", "pilot" are phases of the 90 days (Day 8), not workstreams. Every
  workstream passes through all of them.
- **The skeleton itself.** The walking skeleton is not a seventh workstream. It is a thin slice through
  all six, which is section 07's whole point.

## 6.6 What step 4 sounds like in the interview

> "I would split this into six pieces and order them by what could change the plan. First, integration
> with the core system, because a retry that creates a duplicate record is the kind of thing that
> forces a redesign and I want to know in week two. Second, the security review, because it is long and
> not in my control, and if it comes back 'on-prem only' my model choices change. Third, a labelled set
> with the senior analysts, because without ground truth I cannot claim extraction works. Then
> extraction itself, which is where the value is, one week behind the labelled set. Completeness rules
> are high value but low risk, so a thin version goes in the first slice and the full set follows. And
> enablement, which I would plan from week one even though the work happens later, because the
> analysts will keep their spreadsheet if the tool adds a step."

Six workstreams, an order, a reason for each position, two failure modes (duplicates, on-prem) named
unprompted, and adoption raised without being asked. Still no technology.

## 6.7 Key takeaways

- Workstreams come from steps 1 to 3, not from a diagram; four of Godavari's six are not AI work.
- Score value (how much of the goal) and risk (how likely to change the plan), 1 to 5, with a reason.
- Risk first, value second, dependencies respected loosely, overlap on purpose.
- Low-risk, high-value work is thin and early, not last.
- Every position in the order must have a one-sentence defence.
