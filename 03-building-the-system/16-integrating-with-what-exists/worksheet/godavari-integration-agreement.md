# Godavari integration agreement · the core lending system, the 02:00 batch, the trackers, the reporting copy

> Day 16 artifact for the engagement folder. One page the core-system owner, the CISO's team and Kaagaz sign before any call leaves the machine in the Hyderabad building. Version 0.3, agreed in the week-3 review on Tuesday 10 November 2026; the owner's sign-off on the mapping (1.3.0) is recorded in `code/godavari_integration/mapping/mapping_signoff.json`. Synthetic: Godavari, its systems and every value here are invented.

**Parties:** the core-system owner (writes and the mapping), the CISO (connections and accounts), the compliance head (what may be copied, data classes), Srinivas and the Vijayawada team lead (the tracker mapping), Kaagaz FDE (the integration layer). Godavari's application-support engineer joins as co-owner from the day IT names him (Day 8; open question Q4 in the discovery document).

## 1. What we call, and what we never call

| Operation | Direction | When | Why |
|---|---|---|---|
| GetApplicationByFileNumber | read | any time, paced | the lookup before every create; the reconciliation; the analyst's on-demand view |
| CreateApplication | write | 08:00 to 17:30 and after the batch ends (20:00; 23:00 in the last three days of a month) | one application per approved file, never more |
| GetApplication | read | any time, paced | on-demand identifiers for one file, for one analyst; the reconciliation's field check |
| UpdateKYCStatus | write | as CreateApplication | after the analyst confirms the checklist (Day 17 wires it behind the approval gate) |
| The other ten operations in the WSDL | none | never | not needed for intake; each would need its own line in this table first |

## 2. How a write is made safe on a system with no idempotency key

1. Day 11's key: SHA-256 of file number and branch code, first 20 characters, stamped in `EXT_REF` (agreed as the only spare field long enough).
2. Intent recorded in Kaagaz's journal before the call; outcome after it. The journal holds no customer identifiers.
3. Lookup before create (`GetApplicationByFileNumber`, the owner's suggestion). A shell means create; one application means stop; two means stop and tell a person.
4. A call that gets no reply is never retried. It waits 90 seconds (longer than the core's 60-second transaction ceiling, confirmed with the owner), then the lookup decides.
5. No call between 17:30 and the end of the batch. If the batch overruns, the core answers CL-E017 and the write waits.
6. Paced at four calls a second. The core answers CL-E099 above five in a second; nobody had written that down.

## 3. Files and the 02:00 batch

Read-only SFTP account to the region folders; pinned host key. We process only what the manifest lists, only after the `.done` marker, only when size and SHA-256 match. Partial files wait for the next poll; files not in the manifest wait for the next night's manifest; nothing on Godavari's side is moved or deleted by us. A re-scan under the same file number is a new version of the documents, never a new application.

## 4. The trackers

Read nightly from the shared drive with the team leads' mapping (`godavari_tracker_mapping.toml`, version 0.4.0). Rows the reader cannot parse go to the team lead, never to a guess. From the week the pilot starts, the system writes one column it owns, "Queue status (auto)", and only when the workbook is not open in Excel.

## 5. The reporting copy

Account `RPT_KAAGAZ_RO`, read-only, on the tables and columns in `reporting_signoff.json`. The customer's name, date of birth, PAN, mobile and address are not on that list. Every query states its purpose, is logged, returns at most 5,000 rows and is aborted if it runs away. We never write to it, and we never write to the core's database directly.

## 6. What the owner receives

The reconciliation report every morning by 09:00, generated at 06:00 from his system: our writes looked up live, our call log against his access log, the batch, the trackers against production, codes the mapping does not know, and what the report could not check. One line per night in the history file. **His condition for live writes (M14, Tuesday 8 December 2026): a month of these reports, every call logged, no duplicates, nothing in the batch window.**

## 7. Change notice

| Change | Who tells whom | Notice | What happens on our side |
|---|---|---|---|
| a core release (fields, codes, rules) | the owner to Kaagaz | two weeks | re-record the sandbox; mapping version bumped and reviewed; known-drift list updated |
| the quarterly sandbox refresh | the owner to Kaagaz | one week | re-record; expire or renew each known-drift entry |
| a new tracker column or colour | team leads to Kaagaz | before use | tracker mapping version bumped |
| a new query on the reporting copy | Kaagaz to the owner | before use | a line in the sign-off, or it is denied |
| maintenance (Sunday 06:00 to 09:00) | the owner to Kaagaz | standing | writes wait; the maintenance page is not a failure |

## Sign-off

| Name | For | Date |
|---|---|---|
| the core-system owner | writes, the mapping, the reporting columns | 10 Nov 2026 |
| the CISO's team | the service account, the SFTP account, network path | pending (the staged approval, Day 10 section 8) |
| the compliance head | data classes and what may be copied | 11 Nov 2026 |
| Srinivas, the Vijayawada team lead | the tracker mapping | 11 Nov 2026 |
| Kaagaz FDE | the integration layer and the morning report | 10 Nov 2026 |
