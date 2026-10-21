# 04 · Tool Design: Narrow, Typed, Labelled by Risk, and Unable to Do the Wrong Thing

> Day 17 · Section 4 of 16 · [Chapter overview](README.md) · Previous: [03 · The state machine](03-the-state-machine.md) · Next: [05 · Human approval as a state](05-human-approval-as-a-state.md)

---

## 4.1 The tool list is the permission list

Day 12 said it in one line: the tool list is the permission list (Day 12, section 4.2). A model cannot do anything a
tool does not let it do. So the question "what may the agent do?" is answered by the registry, not by the prompt. A
prompt that says "never email a customer" is a request. A registry with no tool that can address a customer is a
fact.

This section is about designing that registry for a workflow that touches systems of record. Day 12 covered how a
tool is declared and called; here the questions are which tools exist, what each may touch, and how the arguments are
shaped so that a confused caller cannot cause harm.

## 4.2 Four risk classes

Day 12 named the classes and left them to this chapter. Each tool gets exactly one, in code:

| Class | Meaning | Who may call | Godavari tools |
|---|---|---|---|
| read | no side effect anywhere | the planner and the engine | `get_completeness_result`, `get_branch_contact`, `get_current_checklist`, `search_policy`, `get_file_history` |
| propose | puts something in front of a person; changes nothing outside our store | the planner | `propose_send_back`, `hand_to_analyst` |
| write-reversible | changes a customer system in a way a person can undo | the engine, in one state | `update_tracker` (the "waiting on" row, finding A2) |
| write-irreversible | cannot be taken back | the engine, in one in-flight state, against an approval, keyed | `send_branch_message`; Day 11's `push_to_core` |

The real output of the inventory, from `run_demo.py` part A:

```text
   tools, by risk (the planner sees only read and propose):
     read                 get_completeness_result  none
     read                 get_branch_contact       none
     read                 get_current_checklist    none
     read                 search_policy            none (logged in the view log)
     read                 get_file_history         none
     propose              propose_send_back        creates an approval-queue item
     propose              hand_to_analyst          moves the file to the analyst's review list
     write-reversible     update_tracker           changes the credit-ops tracker row (an analyst can change it back)
     write-irreversible   send_branch_message      emails a branch manager; cannot be unsent
     write-irreversible   push_to_core             creates an application in the 2009 core; we cannot delete it
```

The side-effect column is not decoration. It is the sentence a reviewer reads, the sentence the CISO's questionnaire
asks for (Day 23), and the sentence that makes a wrong classification visible: "read, side effect: emails a branch
manager" is a bug you can see in the table.

Note `search_policy`: a read with a side effect of "logged in the view log". Day 15's retrieval appends a view-log
entry for the CISO's seven-year log on every search. That is a side effect on our own audit store, intended, and
labelling it honestly is the point.

## 4.3 Enforced in one function

`tools.execute(ctx, call, actor)` is the only way a tool runs, and it applies the checks in a fixed order, auditing
every call whatever the outcome:

1. the tool exists (an unknown name returns the names the caller may use, as an error result);
2. if the caller is the planner, the risk class is read or propose (otherwise **refused**);
3. the run is in one of the states the tool may run in (otherwise **refused**);
4. the arguments validate against a strict Pydantic model (`extra="forbid"`; otherwise an error result);
5. the tool's own checks raise `ToolError`, returned as an error result.

A refusal is different from an error. An error ("invalid arguments: file_id: String should match pattern") is the
normal back-and-forth of a model using tools, and the planner may recover from it. A refusal ("send_branch_message is
write-irreversible; a planner may only read and propose") means the planner tried something it was never given. The
engine treats that as a reason to stop the run (section 07): a planner that reaches for a tool outside its list is a
planner whose context you no longer understand.

## 4.4 Least privilege is argument design

An allow-list says which tools exist. The arguments decide what each tool can be pointed at. Four decisions in
`tools.py`, each closing a specific hole:

| Tool | The obvious signature | The one used | The hole it closes |
|---|---|---|---|
| send the email | `send_email(to, subject, body)` | `send_branch_message(approval_id)` | the caller cannot choose the recipient or the text; both come from the approved queue item |
| branch contact | returns the mailbox | returns branch, code and "the branch manager" | the model never sees an address, so it can never write one into a draft or a call |
| completeness result | `get_completeness_result(file_id)` for any file | refuses any file but the run's own | a planner cannot read another branch's file (Day 6's branch-visibility rule, finding A1) |
| propose | `propose(file_id, to, items, body)` | `propose_send_back(items, body, checklist_version, policy_citations)` | no file id to get wrong and no recipient at all; code supplies both |

Anthropic's post has the right name for this: "Poka-yoke your tools. Change the arguments so that it is harder to make
mistakes." Poka-yoke is the Japanese manufacturing term for mistake-proofing: the plug that only fits one way. The SIM
tray that only goes in one way round is poka-yoke. So is a send tool whose only argument is an approval id.

> **Analogy (Telugu audience).** The bank locker. You do not get a key that opens any locker; you get the key to yours,
> and the bank's key turns only together with it. `send_branch_message(approval_id)` is a key that turns only together
> with an analyst's approval.

## 4.5 Narrow and typed

Each argument model is small and strict:

```python
class ApprovalArg(_Strict):
    approval_id: str = Field(pattern=r"^SB-GF-\d{5}-c\d+$")

class TrackerArgs(_Strict):
    file_id: str = Field(pattern=r"^GF-\d{5}$")
    status: Literal["sent back", "with analyst", "keyed"]
    waiting_on: str = Field(max_length=200)
```

`Literal` for the tracker status means the workflow cannot invent a status the team leads' colour scheme does not
know. The pattern on the approval id means a planner cannot pass "the latest one". `extra="forbid"` means a model that
adds `"cc": "..."` to the arguments gets an error, not a silently ignored field.

Narrow also means **one job per tool**. A `manage_file(action, ...)` tool with ten actions is ten tools sharing one
risk class, which is always the highest of the ten. Five reads, two proposes and two writes, each with one sentence of
"when to use it", is what the model chooses well among (Day 12, section 4.3) and what a reviewer can audit.

## 4.6 Results are small, and they are data

Tool results are re-sent to the model every turn, so they cost money (section 07 shows the per-turn rupees rising):
`get_completeness_result` returns the branch-facing findings and a count of review findings, not the forty-field
extraction; `search_policy` returns two citations with a one-line excerpt each. And text that comes from a document
or a tool result is data, never an instruction to a tool; a tool that reads untrusted documents is an injection
surface, and [Day 41](../../07-ai-era-toolkit/41-red-teaming-your-deployment/README.md) owns it.

## 4.7 Where the core write lives

`push_to_core` is in the inventory but not in the callable registry: it is Day 11's function, called by the engine
from PUSHING only, with Day 11's approval and route checks, the key from file number and branch code, and the lookup
before create. A tool wrapper would be a second door to the same room. Day 16's `SafeCoreWriter`, finished in parallel,
adds the write window and the ambiguous-timeout rule behind the same call shape; Day 20 wires it in.
