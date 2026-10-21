# 09 · Advanced and 2026 Patterns, and What Is Hype

> Day 11 · Section 9 of 16 · [Chapter overview](README.md) · Previous: [08 · Godavari's architecture](08-godavari-architecture.md) · Next: [10 · Production concerns](10-production-concerns.md)

---

The split between deterministic code and the model is stable. The tools around it change every few months.
This section names the patterns practitioners use as of October 2026, what each is good for, and the claims
to treat with care. Library and API names here will date; Day 12 owns the current API shapes.

## 9.1 Structured outputs: necessary, not sufficient

As of October 2026 every major model vendor offers structured outputs: you send a JSON schema, and the model's
decoding is constrained so the response parses against it. Anthropic's documentation describes this as
constrained decoding that guarantees schema compliance "in most cases", with listed exceptions, and with some
JSON Schema features (numeric constraints such as `minimum`, recursive schemas) not supported. The optional
adapter in this chapter uses it (`output_config.format` with `llm_adapter.SCHEMA`), and the test
`test_schema_objects_are_closed` checks that every object in the schema is closed.

What structured outputs remove: the whole class of "the JSON did not parse", "the field was called `PAN_No`
this time", "the model wrote a paragraph instead of an object". That used to be a third of the envelope's work.

What they do not remove: anything about truth. A schema-valid response can claim a PAN card on a blank page,
copy a misread date with confidence 0.94, or give `"complete": true` for a file with a gas bill as address
proof. The envelope's checks 2 to 8 are unchanged by structured outputs. Note too that numeric range checks
(amount between Rs 20,000 and Rs 3,00,000) cannot go in the schema; they belong in code anyway.

## 9.2 Tools that are deterministic code

Tool use lets the model call functions you declare. It is the natural way to give the model access to the
deterministic world: a `gold_rate_on(date)` lookup, an `ltv_cap(amount)` function, a `check_file()` that runs
the signed rules. The pattern is sound, with one condition: **the tool's result is authoritative, and the
decision does not route through the model's interpretation of it.**

| Use | Good | Dangerous |
|---|---|---|
| the model calls `gold_rate_on()` to explain an eligibility figure to an analyst | yes; the model narrates code's number | |
| the model calls `check_ltv()` and then decides whether to route the file | | the model can misread, ignore or "reconsider" the result; route from code's result directly |
| the model calls a simulator to explore loan structures (seam 4) | yes; constraints still checked in code on the chosen option | |
| the model calls `create_application()` | | only behind a named human's approval and an idempotency key (Day 17) |

The general rule from section 05 applies: the model may propose, explore and explain with tools; code disposes.

## 9.3 The model as a rule drafter, not a rule

One of the most productive 2026 uses of a model in this area is upstream of the system: drafting the rules.
Give a model Godavari's Word checklist, the RBI Master Direction's list of officially valid documents and the
compliance head's notes from the week she spent on the alternatives list, and ask it to draft `rules_kyc.py`
and the boundary tests. It does a good first draft quickly. Then the FDE reviews it, the tests run, the sheet
is generated, and the compliance head reviews and signs. The model's output becomes code that no longer
depends on the model.

This is the same move as the automotive example: the model works where its language ability adds value
(reading a Word document full of exceptions), and the result is frozen into something deterministic. Section
12 covers the specific mistakes a coding agent makes when it drafts rules.

## 9.4 Policy engines and decision tables

When a customer has hundreds of rules, owned by several teams and changed often, plain Python functions stop
scaling, and a policy engine earns its place: a decision-table standard such as DMN (Decision Model and
Notation), a business-rules engine, or a general policy language such as Open Policy Agent's Rego for
authorisation decisions. Their advantage is that rule owners can read and sometimes edit the rules directly,
with versioning and testing built in.

For Godavari, with two products and a few dozen rules in the first 90 days, plain code with generated sheets
is simpler and easier to hand over (Godavari's application-support engineer must release a rule change
without help by M21; Day 28). The decision to adopt an engine is a Day 35 question: when the same pattern
appears across customers, it may become a product feature.

## 9.5 Guardrail frameworks and LLM judges

Guardrail libraries bundle input and output checks (PII detection, topic filters, schema validation, some
grounding checks) around model calls. They are useful for generic checks and say nothing about your
customer's rules; the address-proof list is not in any library. Use them for the generic layer if they fit the
customer's environment, and keep the customer's rules in your own signed code.

An LLM judge (a second model grading the first) is valuable for open-ended outputs such as the analyst note's
tone or a summary's faithfulness, once it is calibrated against human labels (Day 14). It is not a substitute
for a deterministic check where one exists: never ask a judge model whether the LTV is within the cap.

## 9.6 Agents

Day 17 builds the workflow as a state machine with a model inside, and applies this chapter's split to
every transition and tool result; Day 41 attacks it.

## 9.7 What is hype

- **"Models are good enough now to just follow the rules."** Instruction-following has improved a great deal,
  and you should use that: a better model reads more pages correctly. It does not change the kind of promise
  a model makes (section 3.2). A regulator does not accept "it follows instructions very well" as a control.
- **"The prompt is the new code."** Half true. Prompts deserve versioning, review and tests (Day 13). But a
  prompt is not a rule its owner can sign, because the same text can behave differently on a new model.
- **"Put everything in one agent and let it figure out the workflow."** For open-ended research, perhaps. For
  a regulated intake process with known steps, a fixed workflow with a model in specific boxes is cheaper,
  faster, auditable and easier to hand over.
- **"Confidence scores solve review."** Uncalibrated scores route by accident. Calibrated thresholds from a
  golden set route by evidence (Days 14 and 18), and even then they do not see errors upstream of the model.
- **"Deterministic code is legacy thinking."** The teams that invented the FDE role keep hard constraints in
  code that is checked every time. That is not legacy; it is what lets them put a model in front of a regulator.

## 9.8 Key takeaways

- Structured outputs fix shape, not truth; the envelope is still needed.
- Give the model deterministic tools to explain and explore, but route decisions from code's results directly.
- A model is an excellent drafter of rules; the signed rule is code that no longer depends on it.
- Policy engines pay off at scale and across customers; plain code is simpler for the first 90 days.
- Treat "just let the model follow the rules" as the claim to argue with in every design review.
