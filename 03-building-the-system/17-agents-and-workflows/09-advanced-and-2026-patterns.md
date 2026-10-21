# 09 · Advanced and 2026 Patterns: Frameworks, Durable Execution, MCP, and What Is Hype

> Day 17 · Section 9 of 16 · [Chapter overview](README.md) · Previous: [08 · Evaluating on trajectories](08-evaluating-on-trajectories.md) · Next: [10 · Production concerns](10-production-concerns.md)

---

Library names and APIs below are as read on 21 October 2026 and will date; the ideas under them will not.

## 9.1 Agent frameworks: useful for the loop, never a substitute for the state machine

By October 2026 every major vendor ships an agent toolkit (OpenAI's Agents SDK, Anthropic's Claude Agent SDK, Google's
Agent Development Kit), and graph frameworks such as LangGraph are in wide use. They are good at what Day 12 built by
hand: the tool loop, schemas from typed functions, hand-offs, tracing. What none of them decides is **which states your
customer's process has, who may move a file between them, what is irreversible, and what must be true after a crash**.
A framework that lets a model call `create_application` is as dangerous as the naive loop, however good its tracing.

When a team proposes a framework, ask where, in their design, five things live: the states and who may move between
them; which tools are irreversible and why the model cannot call them; each side effect's key and its lookup; where the
approval is stored, bound to what, assigned to whom, due when; and what happens to a run that was mid-way when the
process died. "The framework handles it" is not an answer until they show how.

## 9.2 Human-in-the-loop in graph frameworks: interrupts and checkpointers

LangGraph's documentation describes its interrupts in exactly this chapter's terms (read on 21 October 2026):
"Interrupts allow you to pause graph execution at specific points and wait for external input before continuing." It
lists the requirement first: "A checkpointer to persist the graph state (use a durable checkpointer in production)",
resuming with a `Command` carrying the resume value, on "the same thread ID", which the docs call "effectively your
persistent cursor".

It also carries the warning that maps onto section 06: because interrupts work "by re-running the nodes they were
called from", code before the interrupt runs again on resume, and side effects there should be idempotent; the
guidance is to put non-idempotent work after the interrupt or in a separate node. That is the outbox pattern in
another vocabulary. If you use LangGraph, your SENDING node is a separate node after the approval interrupt, with the
lookup-before-send inside it.

## 9.3 Durable execution engines

Temporal (and similar engines: AWS Step Functions, Azure Durable Functions, Restate, DBOS) take durability out of your
code and into a runtime. Temporal's documentation explains that after a failure it "will automatically recreate its
pre-failure state", that it "replays the Event History step by step" to rebuild the workflow's state, that workflow
code "has to make the same decisions when given the same history", and that "Activities handle everything that
interacts with the outside world", with their results recorded so that "Activities aren't executed again during
replay".

That is this chapter's design with the bookkeeping done for you: the event history is the audit table, activities are
the side-effecting tools, replay is `recover()`. Two cautions carry over unchanged:

- An activity that **fails ambiguously** (it sent the email, then the reply was lost) will be retried by the engine.
  The engine does not know the relay's semantics. The activity still needs its key and its lookup.
- The determinism rule means the **model call belongs in an activity**, never in workflow code: a model is the least
  deterministic function you will ever call.

When is an engine worth it at a customer? When there are many long-running workflows, timers measured in days (the
five-day resubmission wait), and a platform team to run it. At Godavari, in week 5, on a machine in the Hyderabad
building, a SQLite store and forty lines of recovery are the right size. The design should make moving to an engine a
port, not a rewrite, which is another reason the state table is data.

## 9.4 MCP: tools as servers

The Model Context Protocol (specification version 2025-06-18, read on 21 October 2026) lets a system expose tools to
any compliant model client. Two lines in the specification matter for this chapter. On interaction: "For trust & safety
and security, there **SHOULD** always be a human in the loop with the ability to deny tool invocations." On metadata:
tools may carry annotations describing their behaviour, and "clients **MUST** consider tool annotations to be untrusted
unless they come from trusted servers". Its security list asks servers to validate inputs, implement access controls
and rate-limit, and clients to confirm sensitive operations and "log tool usage for audit purposes".

For an FDE this is the risk-class question again, across a process boundary. If Godavari ever exposes the tracker or
the core lookup as MCP servers for other assistants, the risk class and the side-effect sentence must be enforced by
the **server**, because a client's view of "this tool is read-only" is a hint the server sent it. The send tool's
signature (an approval id, nothing else) works the same over MCP as in-process; that is what poka-yoke buys.

## 9.5 Multi-agent designs and screen agents

Orchestrator-worker and multi-agent patterns suit research-style tasks. For a system-of-record workflow each extra agent
is another loop to bound and another place a write could be attempted; if a design needs two agents, ask whether it
needs two **states**. Godavari's reading (EXTRACTED) and drafting (DRAFTING) are two states, not two agents talking.
Computer-use agents that key the 61 fields into the 2009 screens are the naive loop with a mouse: no key, no lookup, no
structured reply to check afterwards. Day 16's integration exists so that writes go through an interface whose outcome
can be checked.

## 9.6 What is hype, in October 2026

| Claim | What is true |
|---|---|
| "Autonomous agents will run the back office end to end" | the published guidance (Anthropic's post among it) is to start with the simplest system and add autonomy only where steps cannot be predicted; regulated processes keep humans at irreversible steps by rule (decision D07), not by preference |
| "The framework handles reliability" | frameworks handle retries of calls; idempotency of side effects depends on the target system, which the framework does not know |
| "Human in the loop slows everything down" | at Godavari it costs about two minutes of analyst time per send-back, against a phone call and a tracker edit today (section 05.7) |
| "Better models will remove the need for guardrails" | the duplicate email in section 01 is made by a perfect model too; it is a property of the loop |
| "Agents remember" | agent memory features store conversation history; they are not a transactional record of what was done in someone else's system |
