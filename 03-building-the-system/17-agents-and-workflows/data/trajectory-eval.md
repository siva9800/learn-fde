# Trajectory eval on Day 14's golden test split

```text
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

  proposed a send-back where the experts sent back:  75 of 75 proposals (100.0%, 95% CI 95 to 100)
  experts' send-backs the workflow proposed:          75 of 92 (81.5%, 95% CI 72 to 88)
  of files with a branch-facing expert reason:        75 of 90 proposed (74 to 90)
  same reasons as the experts, where both sent back:  73 of 75 (91 to 99)

  GF-40038: not proposed (NEEDS_REVIEW) | experts ['MISSING:proof_of_address']
  GF-40130: not proposed (NEEDS_REVIEW) | experts ['MISSING:proof_of_address']
  GF-40438: not proposed (NEEDS_REVIEW) | experts ['MISSING:income_proof']
  GF-40497: not proposed (NEEDS_REVIEW) | experts ['MISSING:pan_card']
  GF-40747: not proposed (NEEDS_REVIEW) | experts ['MISSING:proof_of_address']
  GF-40783: ours ['ADDRESS_NOT_ON_LIST', 'ADDRESS_NOT_OWN_NAME'] | experts ['ADDRESS_NOT_ON_LIST', 'MISSING:pan_card']
  GF-40896: not proposed (NEEDS_REVIEW) | experts ['MISSING:income_proof']
  GF-40903: not proposed (NEEDS_REVIEW) | experts ['MISSING:income_proof']
  ... and 9 more
```
