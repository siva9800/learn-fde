# 11 · Project: Godavari's Send-Back Workflow, Offline, End to End

> Day 17 · Section 11 of 16 · [Chapter overview](README.md) · Previous: [10 · Production concerns](10-production-concerns.md) · Next: [12 · Build it with AI, and how you know it is right](12-build-with-ai-and-verification.md)

---

## 11.1 The brief

Week 5, Thursday 26 November 2026. The prototype checks files; the send-back is still a phone call. Before the pilot
starts on 7 December in Kukatpally and Guntur, the engagement folder needs:

1. a **working send-back workflow**: a typed state machine, a tool registry with read and write tools labelled by risk,
   a planner inside one state (a deterministic stub with no API key, and Day 12's client as the optional model path),
   an approval queue on disk, crash-and-resume with no duplicate messages, step and cost budgets, a full audit log;
2. **evidence** that it is safe: the naive design's failures reproduced on the same file, a trajectory evaluation on
   Day 14's golden set, and a synthetic week with crashes that reconciles to zero duplicates;
3. a **design note** the compliance head and the team leads can sign, with the open questions listed.

Everything runs offline on synthetic data, in prototype mode (pilot mode refuses, because the compliance head signs
the rules on 2 December, milestone M10).

## 11.2 The package

| Module | What it holds |
|---|---|
| `states.py` | the 12 states, 17 transitions, actors, `check_transition`, and the Mermaid generator |
| `store.py` | SQLite: runs, staging, approvals, outbox, hash-chained events; every transition in one transaction |
| `engine.py` | one handler per state; `receive`, `advance`, `run_until_rest`, `decide_send`, `approve_file`, `tick`, `recover` |
| `tools.py` | the registry: risk classes, side-effect labels, strict arguments, `execute` with its checks; the idempotent send |
| `planner.py` | `StubPlanner` and its variants; `ProviderPlanner` through Day 12's `LLMClient`; `ScriptedPlannerProvider` |
| `drafts.py` | the typed draft and `problems()`: what code rejects, and the proposal hash |
| `approvals.py` | people, authority checks, working-hour deadlines, escalation that never approves |
| `budgets.py` | the four meters and the loop signature |
| `systems.py` | stand-ins on disk: branch directory, mail relay (no dedupe, searchable by header), tracker, core sandbox; crash injection |
| `naive.py` | the naive model-directed loop, kept to be shown and tested |
| `trajectory.py` | trajectory checks, decision checks against the experts, the report |
| `simulate.py` | the synthetic week: analysts, branches, four crashes, the reconciliation |
| `worker.py` | a separate process for the hard-kill demo |
| `day11.py`, `day12.py`, `day14.py`, `day15.py` | the earlier chapters' packages, imported by path, never copied |

About 3,000 lines of code with the demo, and 600 of tests.

## 11.3 How to run it

pytest is not on the global Python. Create a virtual environment for the chapter's pinned requirements (the same pins
as Day 12, so one environment runs Days 11 to 17):

```bash
cd 03-building-the-system/17-agents-and-workflows/code
python -m venv .venv
# Windows: .venv\Scripts\activate    Linux and macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
python -X utf8 run_demo.py          # about 40 seconds
python -X utf8 -m pytest            # 51 tests, about 40 seconds
```

Days 11, 12, 14 and 15 must be at their FOLDERS.md paths; the package imports them from there and writes no bytecode
into their folders. No network after the install, no API key. The optional real-provider path is Day 12's
`AnthropicProvider` passed to `LLMClient` in place of `ScriptedPlannerProvider`; it needs `requirements-real-provider.txt`
from Day 12, a key and `KAAGAZ_SYNTHETIC_ONLY=yes`, and it was not run for this chapter.

## 11.4 The run, part by part

Shown outputs are from the run on 21 October 2026 (Python 3.14.3, Windows 11). The full text is `data/run-report.md`.

**A. The machine.** The inventory and the gate:

```text
   12 states, 17 transitions, terminal: FAILED, PUSHED_TO_CORE; resting (waits for a person or a branch): AWAITING_APPROVAL, AWAITING_RESUBMISSION, NEEDS_REVIEW
   who fires transitions: branch 1, human 3, planner 2, system 11
   rules: two-wheeler rules v0.3: reviewed-draft (the compliance head, 2026-11-06); fingerprint matches the record
   rules: gold rules v0.1: draft (nobody yet, -); fingerprint matches the record
   pilot mode refused: two-wheeler rules are reviewed-draft; pilot mode runs signed rules only
```

**B. One file, two designs.** GF-40284 from the golden set, whose only gap is the address proof. The naive loop sends
twice after a crash and writes an incomplete file to the core with no approval (section 01). The state machine, on the
same file: a planner that reaches for the send tool is refused and stopped; the v1 planner's proposal waits for its
analyst; a direct planner call to the send tool is refused; approving the file into the core is refused while the
send-back is open; the crash after the email leaves is recovered with one email; and the same crash as a real process
kill, three processes, one email:

```text
   state machine, planner variant reach_for_write: FAILED; refused: send_branch_message (send_branch_message is write-irreversible; a planner may only read and)
   state machine, planner v1: proposal SB-GF-40284-c0 waits for analyst.hyd.07 (due 2026-11-26 14:00); emails so far: 0
   a planner calling send_branch_message directly: tool_refused: send_branch_message is write-irreversible; a planner may only read and propose
   approving the file into the core now: refused: the file is AWAITING_APPROVAL, not waiting for an analyst; send-back or block findings are open; the branch must fix the file first
   approved; the worker dies at after_send_before_record: the relay has 1 email, our outbox says INTENDED
   new worker, recover(): resumed [('GF-40284', 'SENDING')]; message_confirmed (found in the relay's trace; not sent again); emails in the relay: 1; state AWAITING_RESUBMISSION
   tracker row: {'file_id': 'GF-40284', 'status': 'sent back', 'waiting_on': 'TW-DOC-05', 'since': '2026-11-26', 'updated_by': 'svc-kaagaz-workflow'}
   process 'prepare': exit code 0; prepare: GF-40284 approved by analyst.hyd.07; state SENDING
   process 'send': exit code 17; send: worker starting the send; it will die after the relay accepts the email
   process 'recover': exit code 0; recover: resumed [('GF-40284', 'SENDING')]; state AWAITING_RESUBMISSION; emails in the relay for GF-40284: 1; audit chain intact: True
```

**C. Budgets and loops.** The loop stopped at its second identical call; the "to be safe" over-ask rejected by code and
handed to the analyst; the model planner through Day 12's client at Rs 1.82 under the default budget, and stopped at
Rs 0.52 under a 0.30 ceiling (section 07 explains the overshoot).

**D. Approval as a state.** Three people refused for three different reasons, an edit that says "The loan is approved."
refused, a missed deadline escalating to the Vijayawada team lead and then flagged overdue without approving, and the
email that finally went (section 05). The email's recipient came from the directory; its policy line came from Day 15's
search run as Lakshmi:

```text
     | To the branch manager, Guntur (GNT04)
     | File GF-40167 (two-wheeler) cannot move to credit review yet. Please send the following under the same file number, by the usual scan:
     | 1. An officially valid document, or a document on the signed alternatives list, in the applicant's own name (rule TW-ADDR-LIST: address proof 'gas bill' is not an OVD and not on the signed alternatives list v0.3).
     | Checklist in force: two-wheeler checklist v0.3 (reviewed-draft, code f535ec29fb04).
     | Policy reference: GFL/CMP/2026/004 · Acceptable alternatives for proof of address · clause 2.1 · page 1 · in force from 23 Nov 2026.
     | This asks for documents only; it is not a credit decision on the application.
     | Credit operations (lakshmi)
```

Two things in that email are the engagement's earlier findings, turned into text. "A gas bill" is the address proof
juniors send back "to be safe" (Day 6); here a signed rule sends it back, and says which list it is not on. "Checklist in
force: v0.3, code f535ec29fb04" is CHECKLIST_DRIFT's answer: the branch can see which version it is being held to.

**E. The trajectory eval.** Section 08's table: v1 passes every check on all 75 files it drafted for; v2, with the
same outcomes, fails two checks on all 75; the naive loop fails approval on every send and writes 99 core records.

**F. A synthetic week.** 45 Kukatpally and Guntur files from Day 7's sample, Thursday 26 November to Friday 4 December,
with the four crashes and the people and branches of `simulate.py`:

```text
   Thu 26 Nov 09:00  45 files from Kukatpally and Guntur received
   Thu 26 Nov 09:00  CRASH at mid_drafting; a new worker opens the same store and recovers
   Thu 26 Nov 09:00    resumed 37 unfinished run(s); mid-step: GF-25047 from DRAFTING; the other 36 had not started their step
   Thu 26 Nov 10:00  lakshmi's edit of SB-GF-25074-c0 refused: the body carries an email address or phone number; recipients and contacts come from the directory
   Thu 26 Nov 10:00  CRASH at after_send_before_record; a new worker opens the same store and recovers
   Thu 26 Nov 10:00    resumed 1 unfinished run(s); mid-step: GF-25175 from SENDING; the other 0 had not started their step
   Thu 26 Nov 10:30  CRASH at after_tracker_before_transition; a new worker opens the same store and recovers
   Thu 26 Nov 10:30    resumed 5 unfinished run(s); mid-step: GF-25060 from SENDING, GF-25073 from SENDING, GF-25109 from SENDING, GF-25139 from SENDING, GF-25177 from SENDING; the other 0 had not started their step
   Thu 26 Nov 11:30  CRASH at after_core_write_before_record; a new worker opens the same store and recovers
   Thu 26 Nov 11:30    resumed 23 unfinished run(s); mid-step: GF-25003 from PUSHING, GF-25079 from SENDING; the other 21 had not started their step
   Fri 27 Nov 09:30  GF-25058: the same resubmission uploaded twice; second upload: duplicate
   people and branches: {'approved': 18, 'approved_after_escalation': 5, 'approved_edited': 3, 'edit_refused': 1, 'escalations': 5, 'files_approved': 43, 'rejected': 2, 'resubmissions': 21}
```

and the reconciliation, counted in the relay, the sandbox and the audit log:

```text
     approved_send_backs                21
     messages                           21
     duplicate_messages                 0
     messages_to_non_branch_addresses   0
     messages_without_an_approval       0
     core_records                       43
     pushed_runs                        43
     duplicate_core_records             0
     audit_events                       824
     audit_chain_ok                     True
     audit_chain_break                  None
     states                             {'NEEDS_REVIEW': 2, 'PUSHED_TO_CORE': 43}
```

The two files in NEEDS_REVIEW are Lakshmi's rejections: she is phoning those branches herself. Every other file of
the 45 reached the core exactly once, 21 of them after a send-back and a resubmission.

Notice the 10:30 crash: five runs were mid-SENDING at once, because the analysts approved several items in the same
half hour and the crash came during the drain. All five resumed by looking their keys up in the relay. That is the
design working on a case nobody scripted.

## 11.5 The tests

51 tests in four files, about 40 seconds (the synthetic week and the subprocess kill are most of it):

| File | Tests | What they pin down |
|---|---|---|
| `test_states_and_tools.py` | 12 | reachability, terminal states, only humans approve, the planner's two exits, the generated diagram, planner tools read and propose only, refusals audited, reads scoped to the run's file, no address in a result |
| `test_drafts_and_approvals.py` | 18 | over- and under-asking, decision words, phone numbers, PAN, email, a remembered checklist and an invented citation rejected; three people refused for three reasons; edits re-checked and sent as edited; the approval bound to its text; escalation never approves; working hours; rejection and the resubmission timeout |
| `test_idempotency_and_recovery.py` | 8 | sending twice sends once; crashes after the email, after the tracker, mid-draft and after the core create each leave one effect; duplicate uploads, resubmission cycles and the cycle cap; a killed process |
| `test_budgets_audit_and_eval.py` | 13 | loop, step, time and rupee budgets; a reach for a write stops the run; the model planner matches the stub; pilot mode and changed rules refused; audit completeness and tamper detection; the naive loop's failures; the trajectory eval; the week's reconciliation with no PII in the log |

## 11.6 What goes into the engagement folder

| Artefact | Who uses it |
|---|---|
| `worksheet/godavari-send-back-design.md` | the compliance head, the team leads, the CISO: what it does, never does, approvals, deadlines; questions SB1 to SB6 |
| `data/state-machine.md`, `data/tool-inventory.md` | the CISO's questionnaire (Day 23); the design review |
| `data/trajectory-eval.md` | the gate for every planner, tool or prompt change; the week-6 checkpoint pack |
| `data/run-report.md`, `data/week-log.txt` | the evidence for the go or no-go on 4 December (M12) |
| `data/approval-queue.json`, `data/audit-log.jsonl` | the shape of what Day 18's queue screen shows and Day 19's traces join to |
| `worksheet/agent-review-checklist.md` | every pull request on the workflow |

`data/state/` holds the week's SQLite files and the sandbox records, regenerated on every run; they are there to be
opened, not kept.

## 11.7 Extend it

- Add a `correction` proposal kind: after a send, an analyst can propose a correction email, which goes through the
  same approval and send states with its own key (section 06.6).
- Replace the core sandbox with Day 16's `SafeCoreWriter` behind PUSHING, and add a crash test for Day 16's
  "stall then commit" case.
- Add a `claimed_by` lease to runs and run two workers on the week concurrently; prove the reconciliation still reads
  zero.
- Give the planner a template mode in which the model writes only each item's "issue" sentence, and compare cost and
  approval edit rate against the full draft on the golden set.
