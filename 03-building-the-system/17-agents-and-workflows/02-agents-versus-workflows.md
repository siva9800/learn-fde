# 02 · Agents Versus Workflows: Who Chooses the Next Step

> Day 17 · Section 2 of 16 · [Chapter overview](README.md) · Previous: [01 · Why agents and workflows](01-why-agents-and-workflows.md) · Next: [03 · The state machine](03-the-state-machine.md)

---

## 2.1 The distinction, in Anthropic's words

Anthropic's engineering post "Building effective agents" (Erik S. and Barry Zhang, 19 December 2024; fetched for this
chapter on 21 October 2026) draws the line most practitioners now use:

> "Workflows are systems where LLMs and tools are orchestrated through predefined code paths. Agents, on the other
> hand, are systems where LLMs dynamically direct their own processes and tool usage."

Read it as a question about one thing: **who chooses the next step?** In a workflow, your code does. The model may do
a lot of work inside a step (read a page, write a paragraph, classify a document), but the order of steps, and what is
allowed after what, is written down in code you can read. In an agent, the model does: it decides which tool to call,
with what arguments, and when it is finished.

The same post gives the advice that this chapter applies to Godavari: "we recommend finding the simplest solution
possible, and only increasing complexity when needed", and agents "can be used for open-ended problems where it's
difficult or impossible to predict the required number of steps". It names five workflow patterns: prompt chaining,
routing, parallelization, orchestrator-workers and evaluator-optimizer. Each is a predefined code path with model
calls inside.

> **Analogy (Telugu audience).** The wedding event manager with a checklist (the Part 3 plan's picture). The checklist
> is the workflow: haldi, then mehendi, then the muhurtham, then the meal, in that order, and nobody serves lunch before
> the priest is done. Inside each item the event manager uses judgement (which caterer, where the guests sit). He does
> not get to decide that today the muhurtham is skipped. That judgement-inside-a-fixed-order is a workflow with a
> model inside.

## 2.2 A spectrum, not a switch

In practice there are four positions, and most enterprise systems sit in the middle two.

| Position | Who picks the next step | Example at Godavari | When it is right |
|---|---|---|---|
| plain code | code; no model | the 18:00 batch; the branch-visibility check | the steps and the decisions are both known |
| workflow with model steps | code; the model works inside steps | Day 11's pipeline: model reads the pages, code checks the rules, code routes | the steps are known, some judgements are not |
| workflow with a bounded agent inside one state | code picks the state; inside one state the model picks among a few safe tools until it proposes | this chapter: DRAFTING lets the planner choose which read tools to call before proposing a draft | one step is genuinely open-ended, and its outputs can be checked by code before anything happens |
| agent | the model, for the whole task | an analyst's open question to an assistant ("why did the Guntur files slow down this week?") | the number and kind of steps cannot be predicted, and every action is safe to take or is gated |

The naive design in section 01 is the last row applied to a task that belongs in the third. The send-back has a known
shape (check, draft, approve, send, wait, re-check), irreversible actions in the middle of it, and a regulator at the
end of it. The open-ended part is small: which facts to gather for this file (does it need the policy clause? is this
the second request?) and how to word the draft.

## 2.3 How to decide: five questions

Ask these about the task, in this order. Any "no" to the first three pushes you toward a workflow.

1. **Can you write the steps down?** If an analyst can describe the job as a sequence with branches (Day 6's nineteen
   steps), it is a workflow. Day 14's expert trajectories are the evidence: Lakshmi's steps on a file are the same
   handful of actions every time.
2. **Is every action the model could take safe to take without a person?** Reading is. Proposing is. Emailing a
   branch manager and creating an application in the core are not. If some actions are irreversible, the model must
   not be the one choosing to take them; that leaves the model choosing only among safe actions.
3. **Can code check the result before it matters?** A draft send-back can be checked against the rule findings
   before anyone sees it (section 04 and `drafts.py`). If the output can be checked, the model can be given room; if
   not, give it less.
4. **Does the order of steps change from case to case in ways you cannot enumerate?** For the send-back, barely: the
   second request needs the history, an address-proof finding needs the policy clause. That is two branches, and a
   workflow can hold them. A planner holds them too, cheaply, and that is why DRAFTING has one.
5. **What does a wrong step cost, and who notices?** A wasted read costs a few paise and nobody notices. A duplicate
   email costs the branch manager's trust in the system on day one, and the branch manager is the upstream producer
   whose cooperation the whole send-back loop depends on (Day 7, step 2).

## 2.4 What the published advice says, and what it means for an FDE

The post also recommends sandboxed testing with guardrails, stopping conditions "such as a maximum number of
iterations", and pausing "for human feedback at checkpoints". In this chapter those are the synthetic week (11),
the risk classes (04), the budgets (07) and the approval state (05).

The FDE reading of it is blunter. **Most enterprise value in 2026 is workflows with a model inside.** The customer's
processes already exist; they are written in SOPs and lived in trackers. What a model adds is reading the unreadable
page and writing the sentence nobody had time to write, inside a sequence the customer's people recognise. The
recognisability is not cosmetic: the compliance head can sign a state diagram; she cannot sign "the model decides".
Day 11's split applies here unchanged: hard constraints in code, judgement to the model, behind review. A
multi-step system only adds the question "and who decides the order?", and for anything touching a system of record
the answer is code.

## 2.5 Godavari's decision, written down

| Part of the send-back | Who decides | Why |
|---|---|---|
| whether the file is complete | code (Day 11's signed rules) | regulatory and policy rules, signed by the compliance head |
| whether to draft a send-back at all | code (the route, and the cycle cap) | a send-back for a review-only finding is the "to be safe" habit automated |
| which facts to gather for the draft | the planner, among read tools only | genuinely varies per file; reading is safe; bounded by budgets |
| the wording | the planner | judgement and explanation: the model's job in Day 11's split |
| whether the draft is acceptable | code (`drafts.problems`) | the items must equal the fired rules; the checklist version must be the one in force |
| whether it is sent | a named analyst | irreversible; decision D07; the analyst owns the branch relationship |
| who receives it | code (the branch directory) | a recipient chosen by a model is how a customer gets an email |
| sending, tracker update, core write | code, from states only a person's approval reaches | irreversible or shared; keyed and recorded |

That table is the architecture. Section 03 turns it into states.

## 2.6 When the agent is the right answer

Picture an assistant for the team leads' open questions ("which branches sent back most this month, and for what?"),
a thought experiment, not in the signed scope. The steps cannot be predicted, every tool is a read, and the answer goes
to the person who asked. That is a reasonable agent, with a tool list that is read-only by construction and the same
budgets as section 07.
