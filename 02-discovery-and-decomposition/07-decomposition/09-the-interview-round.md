# 09 · The Interview Round: Running the Method Out Loud in 25 Minutes

> Day 7 · Section 9 of 16 · [Chapter overview](README.md) · Previous: [08 · Godavari: nine days to three](08-godavari-nine-days-to-three.md) · Next: [10 · Two more problems](10-two-more-problems.md)

---

## 9.1 What the round is

The decomposition round (Palantir's "decomp", the "open-ended problem" at the AI labs, the "case" at
vertical-AI companies) gives you an ambiguous operational problem and asks you to turn it into a plan.
Published guides agree on the shape:

| Aspect | What the 2026 guides say |
|---|---|
| Length | 45 to 60 minutes; Palantir's runs the full hour; the first 10 to 15 minutes are expected to be questions |
| The prompt | one or two sentences, deliberately under-specified: "A city wants to reduce 911 response times. You have call data, traffic data and ambulance GPS. You have 60 minutes. Go." |
| What is scored | not the answer: "how you think through a problem you've never seen before" |
| The strongest single signal | whether you clarified before you proposed anything |
| The most common rejection | jumping to a solution before scoping |
| The second most common | silence: "silence reads as being stuck"; "the out-loud part is not optional" |

Day 43 covers the full loop and Day 44 gives ten timed drills with worked answers. This section
teaches the one skill the round scores, with a clock.

## 9.2 The scoring behaviours

The Harvard FAS 2026 guide lists seven behaviours the interviewer is watching for. Each maps to a step
of the method, and the table is worth memorising because it is also the self-audit the guide
recommends after every practice run.

| Scored behaviour | Which step | What it sounds like | What failing it sounds like |
|---|---|---|---|
| clarifies before solving | 1 | "Nine days from what to what, and is the time analysis or waiting?" | "So we would build a pipeline that..." (in minute one) |
| surfaces missing data, stakeholders and metrics | 2, 3 | "Has anyone recorded the correct value of each field? Who upstream produces the incomplete files?" | takes the data as described; stakeholders are "users" |
| states assumptions and revisits them | all | "I will assume the time is mostly waiting, and I will come back to that" | assumptions are invisible, or stated once and never revisited |
| decomposes and sequences by risk and value | 4 | "Integration first, because a duplicate on retry forces a redesign and I want to know in week two" | a list of components in build order |
| proposes a thin first version, then iterates | 5 | "One product, one branch, end to end, three weeks, then widen" | a complete architecture, or a model demo |
| names failure modes | 2, 5 | "The analysts may keep their spreadsheet; the sandbox may be stale" | failure modes only when asked, or "it should work" |
| keeps talking | all | thinking out loud, labelled by step | long silences; "let me think" followed by nothing |

The Palantir-focused guide adds two: **raises adoption without being asked** (the people who must
change their behaviour) and **handles pushback** by stating the trade-off, asking what constraint was
missed, and updating when warranted (section 9.6).

## 9.3 The 25-minute protocol

Real rounds are 45 to 60 minutes. The guides recommend practising in 25, out loud, against a timer,
because a compressed run forces the steps to be crisp and leaves time for the interviewer's pushback in
the real thing. This is the protocol to drill until it is automatic. The minute marks are targets, not
walls; the labels ("Step 2: stakeholders") are said out loud so the interviewer can follow.

| Minutes | Step | What you do | What you must have said by the end |
|---|---|---|---|
| 0 to 1 | Restate | repeat the problem in one sentence; say "I will go through five steps: clarify, stakeholders and metrics, inputs, workstreams, a thin first slice" | the interviewer knows your structure |
| 1 to 5 | 1 · Clarify | ask the unit, the baseline, the trade-off, the constraint; state three assumptions, flag the one that would change everything | the goal as a number; the trade-off; who sets the acceptable loss; one assumption to revisit |
| 5 to 9 | 2 · Stakeholders and metrics | name sponsor, operators, blockers, the ghost, the upstream producer, the owner of the system you write to; a metric each; two fears as failure modes | at least six stakeholders, one metric each, one conflict between them |
| 9 to 14 | 3 · Inputs | for each input: shape, owner, freshness, access, what is missing; name the data that does not exist and who creates it | one architecture risk per input; the missing ground truth and baseline |
| 14 to 20 | 4 · Workstreams | five to seven workstreams; value and risk for each; the order and a one-sentence reason per position; what you will not do | the riskiest two start first; the value one is close behind; adoption is a workstream |
| 20 to 24 | 5 · Skeleton | one product, one site, one path; a row per layer, thin and stubbed; what it proves by week three; three expected failures and what each changes | the first time you describe a system |
| 24 to 25 | Close | one sentence: the trade-off, the first slice, the biggest risk, what you would want to know next | the interviewer has something to push on |

In a 60-minute round, the same shape stretches: 10 to 15 minutes of questions (steps 1 to 3 with the
interviewer's answers), the thin slice by minute 30 (the Palantir guide's target), and the second half
for pushback, deeper design and operational constraints.

### What to do with the interviewer's answers

In the real round, steps 1 to 3 are a conversation. The interviewer answers some questions and
deflects others ("assume whatever you like"). Both are information:

- An answer is data. Repeat it back and say what it changes: "A nightly batch. Then same-hour intake is
  off the table and the three days start the morning after arrival."
- A deflection means the interviewer wants to see you commit. State the assumption and move on: "Then I
  will assume no field-level ground truth exists, and building it with the customer's experts is the
  first workstream."

Never ask a question you would not know what to do with the answer to. Every question in the protocol
above has a "then" attached.

## 9.4 Good and bad openings, side by side

The first three minutes decide the interviewer's frame for the rest of the hour. Here are two openings
to the same prompt. Read both out loud and time them.

**Prompt:** "A regional lender wants to cut loan turnaround from nine days to three. They have scanned
loan files, a legacy core system and a team of credit analysts. Go."

| BAD opening (about 2 minutes) | GOOD opening (about 2 minutes) |
|---|---|
| "Okay, so this is a document-processing problem. I would start with an OCR layer, probably a cloud document-AI service, to extract the fields from the scanned files. Then I would put the documents into a vector database so we can do retrieval, and use an LLM to answer questions and summarise each file for the analysts. We could fine-tune on their historical approvals to predict which loans to approve. The output goes into the core system through its API. For the UI, a chatbot the analysts can ask about any file. I think we could have a prototype in two to three weeks and then iterate on accuracy. We would need to think about hallucination, so RAG helps there, and about PII, so we would mask it. Does that sound like the right direction?" | "Let me restate: nine days to three, scanned files, a legacy core, analysts. I will go through five steps and I will not propose a system until the last one. Step one, clarify. Nine days measured from what event to what, median or mean? I will assume median, receipt to decision. Is it analysis time or waiting time? I will assume waiting, because a nine-day median for a loan file usually means files sitting for a missing document or a batch job, and that assumption decides everything, so I will revisit it. The trade-off: speed against the error rate the regulator sees; if three days doubled the error rate that would not be a success, so I am optimising speed under a fixed error ceiling, and I need to know who sets the ceiling, probably compliance. Constraints: for a lender I will assume customer data stays in the country and the core system's data model is not ours to change. Step two, who decides whether this worked..." |

What the interviewer writes down after the bad opening: "solution in minute one; vector DB and
fine-tuning without knowing the data; no stakeholders; no trade-off; 'does that sound right' is asking
me to do the scoping." What they write after the good one: "clarified; assumptions stated and flagged;
trade-off named with a decider; constraints guessed; structure announced." The bad opening is not
stupid; most of its components may appear in the final design. It is simply unscoped, and it has spent
the candidate's best two minutes on the least valuable thing.

A second pair, shorter, for the city emergency-response prompt (section 10 runs it in full):

| BAD | GOOD |
|---|---|
| "We would train a model on the historical calls to predict where the next call will come from and pre-position ambulances. The traffic data gives us ETAs, and the GPS tells us where units are. A dashboard for dispatchers, maybe a recommendation engine." | "Response time from which event to which: call received, dispatched, or arrival? Is the target the median or the long tail, because the two need different tools. Where does the time go today: call handling, dispatch decision, or driving? I would guess dispatch and driving, and I will come back to that. The trade-off: faster average response against coverage of outer areas and dispatcher autonomy. Who sets the acceptable risk: an EMS chief under a public-safety standard, probably..." |

## 9.5 Narration patterns that keep you talking

The round penalises silence, and the method gives you a sentence for every moment you would otherwise
go quiet:

- **Labelling:** "That is step one. Step two: who decides whether this worked."
- **Assuming:** "I do not know X, so I will assume Y, and here is what changes if I am wrong."
- **Reasoning between steps:** "Because the time is waiting rather than analysis, the metrics that
  matter are the waiting ones, which means..."
- **Parking:** "That is a real question; I will put it on the list for the readout and keep going."
- **Committing:** "If I had to choose now, I would start with integration, because..."

Thinking silently for twenty seconds is fine if you announce it: "Give me a moment to order these by
risk." Thirty seconds of unexplained silence is scored.

## 9.6 When the interviewer pushes: "Just tell me the architecture"

Some interviewers push on purpose, at minute five, to see whether you fold. Common pushes and what to
say:

| Push | What it is testing | What to say |
|---|---|---|
| "Skip the questions. Just tell me the architecture." | whether you can commit without abandoning the method | "Happy to. Here is the shape I expect, and I will flag the two things that would change it." Then give the skeleton in four sentences, name the two unknowns (the write interface, the ground truth), and say: "If either of those is different from my assumption, the order of the first month changes, which is why I asked." You have committed and kept the method. |
| "Assume the data is clean and available." | whether you will accept a convenient fiction | "I will, for this exercise. In the real engagement the first week is usually finding out that it is not, so I would keep a one-week spike to confirm." Then continue. |
| "Why not just use an LLM with RAG?" | whether you can say what RAG would and would not do here | "Retrieval answers questions over documents. The metric here is days to decision, and the lever is completeness and re-keying, not question answering. Retrieval may be useful later for the analysts' lookups; it does not move the number first." |
| "Your first slice is too small. The customer wants all branches." | whether you can defend thinness | "The slice is small so that the joints are tested in week three: the write into the core system, the access rules, whether the analysts use a queue. Widening to all branches is mostly configuration once the pipe works; widening before the pipe works multiplies every integration failure by three hundred." |
| "You have been talking for ten minutes and have not designed anything." | whether you can see your own clock | "Correct, and I am about to. One more minute on inputs, because the write interface decides the first workstream." Then move. If you really have overrun, say so and jump to step four. |
| "What would you do differently if the error rate did not matter?" | whether your trade-off was real | "Then the completeness rules could be advisory and clean files could be auto-approved, which cuts the median most. For a lender the error rate always matters, which is why I put a human decision in the skeleton." |

The pattern the Palantir guide describes for every push: **state your trade-off, ask what constraint you
missed, update if warranted.** Folding ("okay, here is the architecture") and refusing ("I really need
to ask more questions") both score badly. Committing while naming what would change the commitment
scores well.

## 9.7 Self-audit after a practice run

The guides recommend recording yourself and auditing against the scored behaviours. The checklist,
from section 9.2:

- [ ] Did I restate the problem and announce the five steps in the first minute?
- [ ] Did I ask about the unit, the baseline and the trade-off before saying any technology?
- [ ] Did I name at least six stakeholders, a metric each, including the upstream producer and the ghost?
- [ ] Did I state assumptions out loud, and revisit at least one?
- [ ] Did I name data that does not exist and who would create it?
- [ ] Did I give a reason for every position in the workstream order?
- [ ] Was my first slice one product, one site, one path, with every layer present and a stubbed list?
- [ ] Did I name failure modes without being asked?
- [ ] Did I raise adoption without being asked?
- [ ] Was there any silence over fifteen seconds that I did not announce?
- [ ] When pushed, did I commit while naming what would change my answer?

Most people fail items 2 and 8 on the first three runs, and the recording shows it more clearly than
memory does. The guides say the same: candidates are "surprised by how often they jump to solutions".
That is why section 15 has three timed drills.

## 9.8 Key takeaways

- The round scores behaviours, not answers: clarify first, surface missing data and stakeholders,
  state and revisit assumptions, sequence by risk and value, thin first slice, failure modes, keep talking.
- Drill the 25-minute protocol with the step labels said out loud; the real round is the same shape
  stretched to 60.
- A bad opening spends the best two minutes on technology; a good one spends them on the unit, the
  trade-off and the assumptions.
- When pushed, commit while naming what would change your answer. Never fold, never refuse.
