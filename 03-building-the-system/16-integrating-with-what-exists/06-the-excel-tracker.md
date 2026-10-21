# 06 · The Excel Tracker: Reading It Without Trusting It, and Moving It Into the Review Queue

> Day 16 · Section 6 of 18 · [Chapter overview](README.md) · Previous: [05 · Files and the nightly batch](05-files-and-the-nightly-batch.md) · Next: [07 · SQL, read-only](07-sql-read-only.md)

---

## 6.1 Why the tracker is an integration, not a nuisance

Finding A2 (five interviews): the Excel tracker is the real state of every file, and the tool must take
its place, not sit beside it. The analysts open it first; the team leads assign in it; Bhavani learned the
job from its columns ("The tracker's columns are the steps. 'Received', 'keyed', 'docs checked', 'waiting
on', 'verified', 'batch', 'memo'. Seven columns and three colours.", transcript 10). Risk R4 in the
discovery document is that analysts keep it open beside the queue, and its mitigation is "the system writes
the tracker". So the tracker is read on day one and, from the pilot, written in one place.

It is also forty workbooks kept by forty people for years. It has no schema, no timestamps and no
validation, and every irregularity in it means something to someone.

## 6.2 What the chapter's workbooks contain

`synth_sources.build_trackers()` writes three Hyderabad workbooks for the night's files, kept the way
people keep them. Every irregularity is listed in the module's docstring so the reader's findings can be
checked against the list:

| Workbook | What a person did |
|---|---|
| `Tracker_GF-AN-1142_Nov26.xlsx` | a merged title row above the header; `gf-25040 ` in lower case with a space; one received date typed as an Excel serial number and one as text; GF-25147 ticked "keyed" though production holds only its shell; a hidden October row; a total row with a formula |
| `Tracker_GF-AN-1157_Nov26.xlsx` | header names spelled differently ("File No.", "Recd", "Pending with", "Verfied"); the branch written "KPHB"; GF-25115 pasted twice; "12-Nov" with no year; GF-25037 coloured green though production sent it back; "bank stmt (WA recd)"; a Telugu remark |
| `Tracker_GF-AN-1163_Nov26.xlsx` | header on row 2 under a note; an extra "Priority" column that shifts every position; "GF-2503", a digit lost; GF-25001 also claimed by GF-AN-1142; GF-25057 green with a "waiting on" note; ageing as a formula saved without a cached value |

## 6.3 The reader, assumption by assumption

`tracker.read_workbook()` (openpyxl 3.1.5) assumes nothing:

- **The header is found, not assumed.** It scores the first ten rows by how many cells match a known alias
  and takes the best; the night's three workbooks have their headers on rows 3, 1 and 2. Reading by
  column position, the AI-draft habit (`pandas.read_excel` and `df.iloc[:, 1]`), breaks the moment someone
  inserts a "Priority" column.
- **Headers go through the team leads' aliases.** `godavari_tracker_mapping.toml` maps "File No.", "file#"
  and "fileno" to `file_number`, and "Pending with" to `waiting_on`. The team leads own that file; a new
  spelling is a one-line change they review.
- **Every cell is parsed into a value and a problem.** `parse_file_no("gf-25040 ")` normalises to
  `GF-25040` and records that it did; `parse_file_no("GF-2503")` refuses. `parse_date` accepts real dates,
  Excel serial numbers (46338 is 12 November 2026), and day-first text, because these machines run en-IN
  and 05/11/2026 is 5 November; "11/25/2026" is refused as not day-first, and "12-Nov" takes its year from
  a title above the header or, failing that, from the workbook's name, and says which.
- **Colour is data.** The fill of the file-number cell is read as ARGB and translated through the mapping:
  red is waiting on the branch, yellow is a query with a senior, green is ready for the batch. When colour
  and text disagree (green, but "waiting on: addr proof"), the item carries a note: ask the analyst.
- **Hidden rows are kept and marked; total rows are skipped.** A hidden row is often a closed file someone
  did not want to delete; a total row is not a file.
- **A formula is not a value.** openpyxl never calculates. `load_workbook(data_only=True)` returns the
  value Excel cached at the last save, and a workbook saved by a program, not by Excel, has no cached
  value at all. The reader notes the formula and recomputes ageing from the received date instead.

## 6.4 Migration into the review queue

`tracker.migrate()` turns rows into review-queue items keyed by file number: assignee, state (received,
keyed, docs checked, waiting on branch, query with senior, verified, in credit batch, memo written),
the documents being waited on (from free text, via the mapping's phrases: "bank stmt" is
`bank_statement`, "addr" is `proof_of_address`), the received date, and the source rows. The night run:

```text
trackers: 3 workbooks, 40 rows -> 37 queue items; 1 for a person, 1 conflict, 1 duplicate row merged
```

- **Unreadable rows go to a person.** "GF-2503" is not a file number; the item is not created, and the team
  lead sees the row reference. The migration never guesses which file a typo meant.
- **Two workbooks claiming one file is a conflict.** GF-25001 is in GF-AN-1142's and GF-AN-1163's
  workbooks. The queue holds it as "conflict" until the team lead decides; picking one would silently take
  a file away from an analyst.
- **The same row pasted twice in one workbook is merged**, and the merge is reported.
- **"WA recd" becomes a note**: a page came by WhatsApp and is not in the file of record (finding A3).
- **Some columns do not travel.** The customer's name stays in the workbook; the queue shows it on demand
  from the core (section 09). The analysts' branch phone column, more current than the core's two-year-old
  list, is offered to the team leads as its own list, not hidden in the queue. Both rules are written in
  the mapping's `[not_migrated]` table so that nobody re-adds them later "because the column was there".

## 6.5 Not trusting it, and still using it

The reconciliation (section 11) compares the migrated tracker with production's reporting copy and lists
the disagreements for the team leads, not as failures:

```text
| GF-25037 | verified | Q | tracker says verified, the core says query to branch |
| GF-25147 | keyed | S | tracker says keyed, the core says shell |
```

Both are what trackers do: a tick before the work, a colour after the state changed. Showing the team
leads their own discrepancies, by file, is also how the queue earns the right to replace the tracker. Day
33 owns that adoption problem.

## 6.6 Writing back without breaking anything

From the pilot, the system writes the queue's status into the tracker so analysts see one truth.
`tracker.write_back()`:

1. refuses while Excel has the workbook open: Excel creates `~$Tracker_GF-AN-1142_Nov26.xlsx` beside it,
   and writing then either fails or silently loses someone's edits;
2. writes only one column it owns, "Queue status (auto)", appended after the last column, never in a
   column a person uses;
3. loads the workbook *without* `data_only=True`. Loading with cached values and saving replaces every
   formula with its last value, a destructive change nobody would notice for a week;
4. saves to a temporary file in the same folder and replaces the original atomically.

The test `test_write_back_touches_only_its_own_column` snapshots every cell's value and fill, writes two
statuses, and requires everything else, including the hidden row and the merged title, to be unchanged.
openpyxl does not keep everything a workbook can hold (charts and some extensions are dropped on save), so
the team leads agree to the write-back on their workbooks before it is turned on, and a copy is kept.
