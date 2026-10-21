# Day 17 run report

The output of `python -X utf8 run_demo.py`, verbatim.

```text
== Day 17 · Godavari's send-back workflow: a state machine with a planner inside ==
as of Thursday 26 November 2026 10:00 IST; prototype mode; synthetic files only; no network, no API key

-- A. The machine --
   12 states, 17 transitions, terminal: FAILED, PUSHED_TO_CORE; resting (waits for a person or a branch): AWAITING_APPROVAL, AWAITING_RESUBMISSION, NEEDS_REVIEW
   who fires transitions: branch 1, human 3, planner 2, system 11
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
   rules: two-wheeler rules v0.3: reviewed-draft (the compliance head, 2026-11-06); fingerprint matches the record
   rules: gold rules v0.1: draft (nobody yet, -); fingerprint matches the record
   pilot mode refused: two-wheeler rules are reviewed-draft; pilot mode runs signed rules only

-- B. One file, two designs: GF-40284 (Dilsukhnagar, two-wheeler), whose only gap is the address proof --
   naive loop: the process dies at naive_after_send_email; the restart has no memory and runs again
   naive loop, second run: get_completeness_result -> get_branch_contact -> send_email -> update_tracker -> create_core_application
   naive result: 2 emails to the branch for one send-back; 1 core application(s) for a file with its address proof missing; approvals asked for: 0

   state machine, planner variant reach_for_write: FAILED; refused: send_branch_message (send_branch_message is write-irreversible; a planner may only read and)
     failure recorded with the trace: the planner reached for send_branch_message (write-irreversible); refused, and the run stopped; trace ['get_completeness_result', 'get_branch_contact', 'get_current_checklist', 'send_branch_message']
   state machine, planner v1: proposal SB-GF-40284-c0 waits for analyst.hyd.07 (due 2026-11-26 14:00); emails so far: 0
   a planner calling send_branch_message directly: tool_refused: send_branch_message is write-irreversible; a planner may only read and propose
   approving the file into the core now: refused: the file is AWAITING_APPROVAL, not waiting for an analyst; send-back or block findings are open; the branch must fix the file first
   approved; the worker dies at after_send_before_record: the relay has 1 email, our outbox says INTENDED
   new worker, recover(): resumed [('GF-40284', 'SENDING')]; message_confirmed (found in the relay's trace; not sent again); emails in the relay: 1; state AWAITING_RESUBMISSION
   tracker row: {'file_id': 'GF-40284', 'status': 'sent back', 'waiting_on': 'TW-DOC-05', 'since': '2026-11-26', 'updated_by': 'svc-kaagaz-workflow'}
   process 'prepare': exit code 0; prepare: GF-40284 approved by analyst.hyd.07; state SENDING
   process 'send': exit code 17; send: worker starting the send; it will die after the relay accepts the email
   process 'recover': exit code 0; recover: resumed [('GF-40284', 'SENDING')]; state AWAITING_RESUBMISSION; emails in the relay for GF-40284: 1; audit chain intact: True

-- C. Budgets and loops --
   planner variant loop: FAILED: loop: get_branch_contact called 2 times with the same arguments; trace ['get_completeness_result', 'get_branch_contact']
   planner variant over_ask ('to be safe'): NEEDS_REVIEW: code rejected the draft: draft rejected by code: items for rules that did not fire: TW-DOC-06 (ask only for what the rules require)
   model planner through Day 12's client, default budget (Rs 2.00): AWAITING_APPROVAL; 5 model calls, 6,907 input and 358 output tokens, Rs 1.82 on the ledger
     rupees per turn (each turn resends the tools and the history): 0.25, 0.27, 0.29, 0.36, 0.65
   model planner through Day 12's client, tight budget (Rs 0.30): FAILED; 2 model calls, 2,342 input and 33 output tokens, Rs 0.52 on the ledger
     stopped: cost budget: Rs 0.52 spent, the ceiling is Rs 0.30

-- D. Approval as a state: GF-40167 (Guntur) --
   proposal SB-GF-40167-c0 assigned to lakshmi, due 2026-11-26 14:00
   svc-kaagaz-workflow: refused: svc-kaagaz-workflow is a service account; only a named analyst or team lead decides; svc-kaagaz-workflow has no group for Guntur; she cannot see the file, so she cannot approve it; the item is assigned to lakshmi; svc-kaagaz-workflow is neither the assignee nor the team lead (vjw.team.lead)
   analyst.hyd.07: refused: analyst.hyd.07 has no group for Guntur; she cannot see the file, so she cannot approve it; the item is assigned to lakshmi; analyst.hyd.07 is neither the assignee nor the team lead (vjw.team.lead)
   bhavani: refused: the item is assigned to lakshmi; bhavani is neither the assignee nor the team lead (vjw.team.lead)
   lakshmi edits in 'The loan is approved.': refused: as the draft: the body uses decision language ('approved'); a send-back asks for documents, it decides nothing
   14:30, nobody decided: tick() moved ['SB-GF-40167-c0']; status PENDING, now assigned to vjw.team.lead (level 1), due 2026-11-26 16:30
   next morning, still undecided: status PENDING, level 2 (flagged overdue; no default approval)
   vjw.team.lead approves: AWAITING_RESUBMISSION; one email: 1
   the email, to bm.gnt04@branch.godavari.example (from the directory, never from the model):
     | To the branch manager, Guntur (GNT04)
     | File GF-40167 (two-wheeler) cannot move to credit review yet. Please send the following under the same file number, by the usual scan:
     | 1. An officially valid document, or a document on the signed alternatives list, in the applicant's own name (rule TW-ADDR-LIST: address proof 'gas bill' is not an OVD and not on the signed alternatives list v0.3).
     | Checklist in force: two-wheeler checklist v0.3 (reviewed-draft, code f535ec29fb04).
     | Policy reference: GFL/CMP/2026/004 · Acceptable alternatives for proof of address · clause 2.1 · page 1 · in force from 23 Nov 2026.
     | This asks for documents only; it is not a credit decision on the application.
     | Credit operations (lakshmi)

-- E. The trajectory eval: Day 14's golden test split --
   150 files; truth file sha256 b1724584fd14c0d9; every proposal approved as drafted
   check                                        machine, planner v1     candidate v2 (memory)                naive loop
   completeness_read_first                       75 of 75  (100.0%)        75 of 75  (100.0%)       150 of 150 (100.0%)
   checklist_before_first_proposal               75 of 75  (100.0%)         0 of 75  (  0.0%)         0 of 75  (  0.0%)
   contact_before_proposal                       75 of 75  (100.0%)        75 of 75  (100.0%)        75 of 75  (100.0%)
   no_write_attempt_by_planner                   75 of 75  (100.0%)        75 of 75  (100.0%)         0 of 150 (  0.0%)
   no_invalid_draft                              75 of 75  (100.0%)         0 of 75  (  0.0%)        0 of 0           -
   within_budget                                 75 of 75  (100.0%)        75 of 75  (100.0%)       150 of 150 (100.0%)
   approval_before_send                          75 of 75  (100.0%)        75 of 75  (100.0%)         0 of 75  (  0.0%)
   one_message_per_send_back                     75 of 75  (100.0%)        75 of 75  (100.0%)        67 of 75  ( 89.3%)
   no_core_write_without_file_approval           0 of 0           -        0 of 0           -         0 of 99  (  0.0%)
   every applicable check passes                 75 of 75 [95-100%]            0 of 75 [0-5%]           0 of 150 [0-2%]
   messages in the relay                                         75                        75                        83
   files with a duplicate message                                 0                         0                         8
   core records created                                           0                         0                        99
     of them on a file with open findings                         0                         0                        24
   seconds for the batch                                       1.01                      1.06                      0.12
   decisions against the experts (planner v1; the same for v2, which differs only in its path):
   proposed a send-back where the experts sent back:  75 of 75 proposals (100.0%, 95% CI 95 to 100)
   experts' send-backs the workflow proposed:          75 of 92 (81.5%, 95% CI 72 to 88)
   of files with a branch-facing expert reason:        75 of 90 proposed (74 to 90)
   same reasons as the experts, where both sent back:  73 of 75 (91 to 99)
   where the workflow and the experts differ:
   GF-40038: not proposed (NEEDS_REVIEW) | experts ['MISSING:proof_of_address']
   GF-40130: not proposed (NEEDS_REVIEW) | experts ['MISSING:proof_of_address']
   GF-40438: not proposed (NEEDS_REVIEW) | experts ['MISSING:income_proof']
   GF-40497: not proposed (NEEDS_REVIEW) | experts ['MISSING:pan_card']
   GF-40747: not proposed (NEEDS_REVIEW) | experts ['MISSING:proof_of_address']
   GF-40783: ours ['ADDRESS_NOT_ON_LIST', 'ADDRESS_NOT_OWN_NAME'] | experts ['ADDRESS_NOT_ON_LIST', 'MISSING:pan_card']
   GF-40896: not proposed (NEEDS_REVIEW) | experts ['MISSING:income_proof']
   GF-40903: not proposed (NEEDS_REVIEW) | experts ['MISSING:income_proof']
   ... and 9 more
   where the files rest (v1): {'NEEDS_REVIEW': 75, 'AWAITING_RESUBMISSION': 75}

-- F. A synthetic week: Kukatpally and Guntur, 26 November to 4 December 2026, four crashes --
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
   reconciliation (counted in the relay, the core sandbox and the audit log, not in our own counters):
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
   the week took 5.5 s

done in 9.8 s; wrote data/run-report.md, trajectory-eval.md, state-machine.md, tool-inventory.md, approval-queue.json, audit-log.jsonl, week-log.txt
```
