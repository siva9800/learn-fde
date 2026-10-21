# Integration reconciliation · Friday 13 November 2026

**For:** the core-system owner. **Overall:** CLEAN.

- job reconcile 0.6.0; mapping 1.3.0 (fingerprint 0b12e0a77d41)
- sources: sandbox core (live lookups, read-only); your access log export; our journal and call log; SFTP manifests; three tracker workbooks; reporting copy refreshed 13 Nov 2026 05:00

## 1. Our writes to the sandbox, checked against the core · ok

- journal: confirmed 9, exists_not_ours 1, failed 2
- looked up live: 10 files; exactly one application each: 10
- duplicates: 0
- journal says written, core disagrees: 0
- GF-25010: already keyed by someone else (AP0000000001, no Kaagaz EXT_REF); we did not create a second one
- GF-25148: failed: mapping: INC_PRF_CD (Income proof submitted) is mandatory and income_proof_kind is empty
- GF-25183: failed: mapping: INC_PRF_CD (Income proof submitted) is mandatory and income_proof_kind is empty

## 2. Fields changed in the core after our write · ok

- none

## 3. Our call log against your access log for SVC_KAAGAZ_SBX · ok

- calls: ours 23, yours 23; 2 we logged as no-reply, which your log records as OK (the core did the work; we did not hear back)
- write calls between 17:30 and the end of the batch: 0
- files with more than one successful CreateApplication in your log: 0
- CL-E099 busy faults: 0

| operation | outcome | our log | your log | difference |
|---|---|---|---|---|
| CreateApplication | AMBIGUOUS | 2 | 0 | 2 |
| CreateApplication | OK | 7 | 9 | -2 |
| GetApplication | OK | 1 | 1 | 0 |
| GetApplicationByFileNumber | OK | 13 | 13 | 0 |

## 4. The 02:00 SFTP batch · ok

- GF-25040: rescan: version 2 of GF-25040: same application, new documents

| poll | manifest rows | picked | re-scan | already picked | partial | late | missing | corrupt |
|---|---|---|---|---|---|---|---|---|
| 1: HYD 12 Nov | 27 | 26 | 0 | 0 | 1 | 1 | 0 | 0 |
| 2: HYD 12 Nov | 27 | 1 | 0 | 26 | 0 | 1 | 0 | 0 |
| 3: HYD 12 Nov | 27 | 0 | 0 | 27 | 0 | 1 | 0 | 0 |
| 4: HYD 13 Nov | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |

## 5. The analysts' trackers against production (reporting copy) · ok

- tracker rows read: 40; queue items: 37; rows for a person: 1; conflicts: 1; duplicate rows merged: 1
- for a person: Tracker_GF-AN-1163_Nov26.xlsx:4: not a file number: 'GF-2503'
- conflict: GF-25001: Tracker_GF-AN-1142_Nov26.xlsx:4 says GF-AN-1142/received, Tracker_GF-AN-1163_Nov26.xlsx:12 says GF-AN-1163/received; the team lead decides
- tracker and core disagree: 2

| file | tracker | core | what to check |
|---|---|---|---|
| GF-25037 | verified | Q | tracker says verified, the core says query to branch |
| GF-25147 | keyed | S | tracker says keyed, the core says shell |

## 6. Codes in your CODE_MST that the mapping does not know · ok

- APPLSTAT H 'ON HOLD - FRAUD CHECK': not in mapping 1.3.0; anything reading it fails closed until the owner reviews the meaning

## 7. The month of logged calls

- consecutive clean nights in the history file: 1 (your condition: a month, before live writes on 8 December, M14)

## 8. What this report could not check

- production writes: there are none yet; live writes start 8 December (M14) if this history is clean
- credit-check results in the sandbox: computed on July's rules, so ignored (finding A5)
- applications carrying our EXT_REF on files we never journaled: needs a query on the sandbox's own tables, which only you can run; requested for Monday
- the WhatsApp pages (finding A3): they never reach any system this report can read

## Appendix: the queries this job ran on the reporting copy

- tracker reconciliation: core status per registered file: `SELECT r.FILE_NO, a.APPL_STAT FROM FILE_REG r LEFT JOIN APPL_MST a ON a.FILE_NO = r.FILE_NO` (38 rows)
- mapping drift: active codes: `SELECT CODE_TYP, CODE_VAL, CODE_DESC FROM CODE_MST WHERE ACTIVE_FLG = 'Y'` (33 rows)
- freshness of the copy: `SELECT MAX(REFRESH_TS) AS ts FROM RPT_REFRESH_LOG` (1 row)
