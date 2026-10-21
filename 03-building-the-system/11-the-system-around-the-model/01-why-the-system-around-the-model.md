# 01 · Why the System Around the Model Decides Whether Anyone Trusts It

> Day 11 · Section 1 of 16 · [Chapter overview](README.md) · Next: [02 · The eight boxes](02-the-eight-boxes.md)

---

## 1.1 Two pipelines, one Tuesday

It is week three at Godavari Finance. The walking skeleton from Day 7 is half built: one product
(two-wheeler loans), one branch (Kukatpally), one path (SFTP scans). You have a model that reads the
scanned pages well. Now you have to decide what happens after it reads them.

There are two ways to finish the pipeline, and both can be demonstrated by Friday.

**Pipeline A** sends each 30-page file to the model with a long prompt: "Here is Godavari's two-wheeler
checklist. Extract the twelve mandatory fields, tell me which of the fourteen documents are present,
check that the address proof is acceptable, that the Aadhaar copy is masked, that the amount is within
90 percent of the on-road price, and say whether the file is complete." The model answers in neat JSON
with a `complete: true` at the bottom. On the ten files you try, it is right nine times. It is fast to
build, it demos beautifully, and the COO likes it.

**Pipeline B** asks the model to do only the reading: classify each page, copy each field with the line
it came from, list the documents it found with a quote from each. Then ordinary Python takes over. It
checks that every quote is really on the page the model cited. It checks the PAN's format and compares
the PAN card with the application form. It looks the address proof up in the list the compliance head
signed. It scans every page for an unmasked Aadhaar number. It does the margin arithmetic in integer
rupees. It sends the file to the right queue, and the model's last job is to write the note that
explains to the analyst, in plain words, what the code decided.

Pipeline B takes longer to build, and on a demo it looks the same as A. The difference shows up on the
day the RBI auditor samples files in March, when the compliance head is asked "why was this file
accepted with a gas bill in the applicant's father's name?" With pipeline A, the honest answer is "the
model thought it was fine". With pipeline B, the answer is "it was not accepted: rule TW-ADDR-LIST,
version 0.3, which you signed, sent it back to the branch on the day it arrived, and here is the log".

This chapter is about building pipeline B, and about knowing, for every rule and every judgement in a
customer's process, which side of the line it belongs on.

## 1.2 The failure you have already heard about

You met this failure in Day 6, from three people who had lived through it. In 2019 Godavari ran an OCR
pilot. It guessed instead of saying "unsure", read a monthly income figure on a handwritten Telugu
declaration as an annual one, and was switched off in six weeks
([finding A8](../../02-discovery-and-decomposition/06-discovery-interviews/worksheet/godavari-discovery-synthesis.md)).
The senior analyst in Hyderabad still tells the story. Bhavani, the junior analyst in Vijayawada, told
you honestly that she would not have caught it: review by a busy analyst does not catch a confident wrong
figure (code `REVIEW_WILL_NOT_CATCH_ALL`).

The compliance head set the condition that this chapter turns into code. "I sign it, and if it changes,
I sign the change. I do not want a machine deciding that a gas bill is an address proof because it saw
one accepted last year" (code `RULES_AS_SIGNED_CODE`). And she named the cost of being wrong: "A missing
KYC document is an observation. Repeated, it is a finding," with her name on the response (code
`WRONG_MEANS_AUDIT_FINDING`).

Put those three findings together and the architecture follows:

- The completeness checks cannot live in a prompt. The compliance head cannot read a prompt as a rule,
  cannot sign it, and cannot be sure that the behaviour she signed is the behaviour that ran.
- The checks cannot rely on review to catch what the model gets wrong, because review will not catch
  everything.
- The model still has a real job: reading scanned, stamped, hand-annotated, half-Telugu pages is exactly
  the kind of work deterministic code cannot do well. The model earns its place in extraction.

## 1.3 What "the system around the model" means

An enterprise AI system is not a model with a user interface on it. It is a pipeline of components, and
the model is one of them. Day 7 said it in one line: "The model is one box. The skeleton proves the pipe."
Section 02 draws the eight boxes: ingestion, retrieval, model, rules, verification, interface,
integration and observability. Seven of them are ordinary software. They decide whether the eighth is
trusted.

The deeper idea is a split of responsibility:

| | Deterministic code | The model |
|---|---|---|
| Does | rules, arithmetic, lookups, formats, permissions, writes to systems of record | reading messy documents, classifying free text, summarising, explaining, drafting |
| Promise | the same answer for the same input, every time, testable at the boundaries | the most likely good answer for inputs nobody could enumerate in advance |
| When it fails | loudly: a test fails, an exception is raised, a rule fires | quietly: a fluent, confident, wrong answer |
| Who can sign it | the rule owner, from a table generated from the code | nobody, as a rule; it is measured instead (Day 14) |

The phrase this course uses for the split is **the model proposes, code disposes**. The model may say
"page 7 is the address proof, it is a gas bill, in the name of the applicant's father". Code decides what
that means for the file.

## 1.4 Why it matters for your career

The teams that invented the forward deployed role say the same thing in their own words. OpenAI's FDE
team, in the interviews summarised in the ZenML LLMOps database (section 16), describes keeping hard
business constraints in deterministic code that is "checked 100% of the time" rather than trusting the
model, and states the rule plainly: "Critical business rules, mathematical constraints, and verification
steps should be deterministic code, not LLM outputs." Their automotive supply-chain example, "always
maintaining at least two suppliers for critical components like tires", is the cleanest picture of the
idea you will find, and section 03 takes it apart.

Applied AI work appears in 80 percent or more of the 1,000 FDE postings analysed in 2026 (CURRICULUM.md;
the source is a vendor's analysis, dated 2026). What separates the engineer who gets the offer from the
one who does not, in the system-design round and on the job, is rarely "can you call a model". It is
"where does the model stop, and what stops it". An interviewer who asks you to design a claims system,
a KYC pipeline or a contract reviewer is listening for the moment you say which parts are rules in code,
who owns them, and what happens when the model is unsure. Day 44 drills it; this chapter is where the
judgement is built.

On the job the stakes are concrete. A rule left to a prompt is the commonest cause of the production
incident that ends an engagement: the system that worked in the demo and then did something no one can
explain to a regulator. The FDE who draws the line well ships a system the CISO and the compliance head
can sign. The one who draws it badly ships a demo.

> **Analogy (Telugu audience).** DRS in cricket. Ball-tracking is deterministic: the same delivery gives
> the same projection, everyone in the ground can see the three red lights, and nobody argues with it.
> The on-field umpire's soft signal handles the nuance the cameras cannot: did the fielder's fingers stay
> under the ball? The system is trusted not because either part is perfect, but because everyone knows
> which part decides which question. Godavari's system needs the same clarity: ball-tracking for the
> fourteen documents and the LTV cap, the umpire's judgement for "which of these three bank statements is
> the salary account".

## 1.5 What you will build

A working, offline prototype of pipeline B for two loan products, run over the same 200 synthetic
files Day 7 generated, which prints what the rules caught that the model alone would have shipped
(section 11). It needs no network and no API key, and that is deliberate: the CISO allows the prototype
only "on a machine in this building, on masked files ... with no internet" (Day 6). The offline stub is
not a convenience; it is the only model the customer's rules allow at this stage.

## 1.6 The hard parts, named up front

Three things make this harder than it sounds. Knowing them in advance saves a week.

1. **The model can do most of it, most of the time.** That is the trap. Pipeline A really does get nine
   files in ten right. The argument for code is not that the model is bad; it is that 90 or even 99
   percent is the wrong kind of number for a rule. Section 03 does the arithmetic.
2. **The customer's rules are not written down.** The acceptable-alternatives list for address proofs
   lived "in my head and in Lakshmi's" (the compliance head, Day 6). You cannot code a rule nobody has
   written. Part of the FDE's job is to get it written, in a form a program can apply, and signed.
   Section 04 shows how.
3. **The line is fuzzy exactly where it matters.** "Is this a salary account?" is a judgement. "Does this
   statement have three monthly credits from the employer named on the salary slip?" is a rule. The
   craft is in the seams between the model's judgement and code's check. Section 06 is about nothing else.

This feels like a lot of plumbing for a chapter about AI. That is normal, and it is the point. The
plumbing is what the customer is buying.
