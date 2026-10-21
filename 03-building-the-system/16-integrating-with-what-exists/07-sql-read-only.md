# 07 · SQL, Read-Only: The Reporting Database, the Sign-Off per Column, and Why You Never Write

> Day 16 · Section 7 of 18 · [Chapter overview](README.md) · Previous: [06 · The Excel tracker](06-the-excel-tracker.md) · Next: [08 · The metadata translation layer](08-the-metadata-translation-layer.md)

---

## 7.1 What the reporting database is

Godavari's monthly ops report "comes from the core's received and sanction dates" (Day 6, section 02, access and reality),
and the historical decisions are "a report the core-system owner runs on request" (Day 7's inventory).
Behind both is the reporting copy: a nightly copy of the core's tables, refreshed at 05:00, on-prem, SQL.
At Godavari it is a reporting replica reached with a read-only account; in this chapter it is a SQLite
file built by `synth_sources.build_reporting_db()` with the tables a 2009 core would have: `APPL_MST`
(applications, including the customer's name, date of birth, PAN, mobile and first address line),
`APPL_STAT_HIST`, `FILE_REG` (the 02:00 job's shells), `BRANCH_MST`, `CODE_MST` and `RPT_REFRESH_LOG`.

It is the right place for questions across many files: how many are sent back, which codes exist, which
files the tracker and the core disagree about. It is the wrong place for two things, and the chapter's
code makes both impossible.

## 7.2 Never write to it, and never write to their production database at all

Even if the account allowed it. A write straight into a core's tables skips everything the core does on
the way in: its validation, its sequence numbers (the owner: "Writes during the batch have corrupted the
sequence twice"), its audit trail, its triggers, the batch's assumptions. A reporting copy written to is
also no longer a copy: tomorrow's 05:00 refresh overwrites it, or worse, does not. Writes go through the
core's own API, where the owner can see them in his access log, or they do not happen. That sentence goes
in the agreement, and the AI-draft plan in `worksheet/ai-draft-integration-plan.md` asks for a read-write
account so that you can practise refusing it.

## 7.3 Never use it to decide whether to write

The reporting copy is up to a day old. A lookup against it at 16:10 cannot see an application created at
16:09, so using it as the "does this exist?" check before a create is the duplicate bug again, with a
24-hour window instead of a one-second one. The idempotency lookup goes to the system of record, live
(section 04). This is a general rule: **check for existence where the write lands, never in a replica.**

## 7.4 Four locks, each enough on a good day

`reporting.ReportingReader` opens the copy with four independent protections:

```python
self.conn = sqlite3.connect(f"file:{Path(db_path).as_posix()}?mode=ro", uri=True)    # 1. read-only open
self.conn.execute("PRAGMA query_only = ON")
self.conn.set_authorizer(self._authorize)                                            # 2. signed-off columns
...
cur = self.conn.execute(sql, params)
rows = cur.fetchmany(self.row_cap + 1)                                               # 3. row cap
self.conn.set_progress_handler(progress, 1000)                                       # 3. work budget
self.log.entries.append((purpose, " ".join(sql.split()), len(rows)))                 # 4. purpose, logged
```

1. **Read-only at the connection.** `mode=ro` is SQLite's URI flag; the Python documentation's own example
   shows a write failing with "attempt to write a readonly database" (read 21 October 2026). At Godavari
   the equivalent is the database account's grants, set by the owner, not by us.
2. **An authorizer allows only the signed-off columns.** SQLite calls the authorizer for every column a
   statement touches; returning `SQLITE_DENY` aborts the statement. The allowed list is
   `reporting_signoff.json`, signed by the core-system owner, with the compliance head agreeing the PII
   exclusion. `APPL_NM`, `PAN_NO`, `MOB_NO`, `APPL_DOB` and `ADDR_LN1` are not on it, so
   `SELECT APPL_NM ...` and even `SELECT * FROM APPL_MST` fail, whoever wrote the query, including a model
   writing SQL. Postgres and Oracle give you the same with column-level grants and views; the point is that
   the rule lives below the application, where a bug in the application cannot skip it.
3. **Bounded queries.** At most 5,000 rows (the reader fetches one more than the cap and refuses rather
   than truncating silently) and a work budget that interrupts a runaway join. The SQLite progress handler
   stands in for a statement timeout; on a real replica you also ask for one on the account.
4. **Every query states its purpose and is logged.** The morning report prints the SQL it ran, so the
   owner can run the same queries himself.

```text
reporting copy refused: SELECT APPL_NM, PAN_NO FROM APPL_MST -> access to APPL_MST.APPL_NM is prohibited
reporting copy refused: UPDATE APPL_MST SET APPL_STAT = 'K' -> not authorized
```

## 7.5 The sign-off per table

The Part plan asks for "the data owner's sign-off per table". In practice it is per column, written down,
and versioned like code:

| Table | Columns we may read | Why we need them |
|---|---|---|
| APPL_MST | application ID, file number, branch, product, status, KYC status, amount, EXT_REF, maker, timestamps | the reconciliation; status across files |
| APPL_STAT_HIST | all | when a status changed and who changed it |
| FILE_REG | file number, branch, registered time, page count | which files the 02:00 job saw |
| BRANCH_MST | code, name, region, state | the state code in the mapping comes from here |
| CODE_MST | all | mapping drift (section 08) |
| RPT_REFRESH_LOG | all | how fresh the copy is; printed in every report |

A new query that needs a new column is a request to the owner first, a line in the sign-off second, and
code third. That order is slower by a day and saves the conversation where he finds a query he never
agreed to.

## 7.6 Freshness, said out loud

Every report says "reporting copy refreshed 13 Nov 2026 05:00". A file the analysts keyed at 05:30 is not
in it, and the report's tracker comparison could flag a correct tracker row as a disagreement. State the
freshness, compare only like with like, and let the person reading decide; never let a stale source
silently win an argument with a live one.
