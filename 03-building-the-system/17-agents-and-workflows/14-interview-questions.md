# 14 · Interview Questions: Agents and Workflows

> Day 17 · Section 14 of 16 · [Chapter overview](README.md) · Previous: [13 · Mistakes and debugging](13-mistakes-and-debugging.md) · Next: [15 · Exercises](15-exercises.md)

---

These come up in the enterprise system-design round and the practical round (Day 43 maps the loop). The model answers
are short on purpose: say the decision, the reason, and the failure it prevents.

**1. What is the difference between a workflow and an agent?**
Who chooses the next step. In a workflow, code does: LLM calls sit inside predefined code paths (Anthropic's
definition). In an agent, the model directs its own process and tool use. Most enterprise value is workflows with a
model inside, because the steps are known and some actions are irreversible.

**2. A customer wants "an agent that handles incomplete loan files end to end". What do you build?**
A state machine for the file with the model inside one or two states: the model reads the documents and drafts the
send-back; code checks completeness against signed rules, decides whether to send back, and owns every write. A named
analyst approves before any email leaves. I would show them the state diagram before any code, because the compliance
head can sign a diagram, not "the model decides".

**3. Why model the workflow as an explicit state machine rather than a loop?**
Three reasons: it constrains the model (it may act only in the state that allows it), it survives crashes (the state is
a row on disk, so a new process knows where to resume), and it explains itself to people who must approve it. A loop
keeps its position in memory, so a restart starts over.

**4. How do you decide which states you need?**
A state earns its place if it changes who owns the file, what may happen next, or what a crash leaves behind. Waiting
for an analyst and waiting for a branch are different states (different owners and deadlines). An in-flight state for
each irreversible side effect is needed so that "about to send" and "sent" are distinguishable after a crash. A step
that changes none of the three is a step inside a state.

**5. What is an idempotency key, and how do you derive one?**
A value that identifies one intended effect, so repeated attempts can be recognised as the same intent. Derive it from
durable business facts, so any process can recompute it: file number and branch code for the core create; file,
send-back cycle and approved-text hash for the email. Never a uuid per attempt or a timestamp. And never something that
changes when the intent does not: a key that includes the bundle hash makes a resubmission look like a new loan.

**6. The target system has no idempotency support. What do you do?**
Keep the memory on your side and the truth on theirs: write an outbox row before the call, close it after, and before
any repeat look the effect up in the target (the core's lookup by file number, the relay's message trace by a header
you set). If the target cannot be searched, ask for that before you write to it; otherwise you cannot make the write
safe to repeat.

**7. Walk me through the crash windows of sending an email.**
Before the approval commits: nothing happened. After the commit, before the send: outbox INTENDED, relay empty; resume
sends. After the relay accepted, before the outbox closes: the dangerous one; resume looks up the key, finds the email,
closes the outbox, does not send. After the outbox closes: resume finds it closed and moves on. I test the dangerous one
with a real process kill.

**8. Why not just put a confirmation dialog in front of risky actions?**
A dialog has no durable owner, no deadline, no record of exactly what was approved, and no authority check beyond
whoever is at the screen. Approval should be a state of the work item with an assigned approver checked at decision
time, a hash of what is approved, a deadline that escalates, and an audit event committed with the transition.

**9. What should happen when an approval times out?**
Escalate to the next person and flag it. Never approve by default; that turns every absent approver into a yes. The
deadline should be in working hours.

**10. How do you stop an agent from looping or overspending?**
Budgets checked by code before every call: steps, money (from the same ledger finance sees), wall time, and a stop on
an identical repeated call. Plus limits at the workflow level, such as a cap on send-back cycles. Hitting one ends the
run in a failed state with its trace for a person, not a silent retry.

**11. How do you design tools for an agent that touches a system of record?**
Narrow, typed, one job each, with a risk class and a side-effect sentence. The planner gets read and propose tools
only. Least privilege through argument design: the send tool takes an approval id, so nobody can choose the recipient
or the text; the contact tool returns a role, never an address; read tools act only on the run's own file.

**12. How do you evaluate an agent?**
On outcomes and on trajectories. Outcomes against the experts' decisions on a golden set (precision, recall,
same-reason agreement, with intervals). Trajectories against fixed checks per file: read the rules first, read the
checklist before proposing, never attempt a write, approval before every send, one email per send-back. A change can
keep the outcomes and break the path; only the trajectory eval catches it.

**13. What goes in the audit trail, and what stays out?**
Every transition, tool call with risk class, proposal by hash, decision with who and whether edited, refusal,
escalation, send, write and recovery, append-only and hash-chained. Message bodies stay in the approval queue and are
recorded in the log by hash and length; customer identifiers stay out entirely, and a test scans for them.

**14. The compliance head asks: "Can your system take an action in our core without a human?" How do you answer?**
"No, and here is how to check." Show the tool inventory (two irreversible actions), the state table (each reachable
only through a human transition), and the test that refuses a planner's write. Then offer the reconciliation report
that counts core records against analysts' approvals every night.

## Quick-fire

| Question | Answer |
|---|---|
| Who may fire the transition into SENDING? | a named human, with authority checked then |
| What does FAILED mean? | automation stops; a person reads the reason and the trace |
| Key for a model call? | file, page, page hash, stage, prompt version, schema version, model (Day 12) |
| Key for the core create? | file number and branch code (Day 11) |
| Why an outbox? | so a resumed process knows a side effect was intended |
| Why look up before a repeat? | because the effect may have happened after you last heard |
| Does a hash chain prevent tampering? | no; it makes it detectable to anyone holding a later hash |
| Approve on timeout? | never |
| Should a planner that tries a write continue? | no; stop the run and alert |
