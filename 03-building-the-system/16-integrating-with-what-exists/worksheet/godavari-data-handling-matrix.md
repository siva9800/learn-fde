# Godavari data-handling matrix · what may be copied, cached, logged or shown, per source

> Day 16 artifact for the engagement folder. The engineering half of "no customer PII leaves India" and "nothing leaves the building before the CISO's review" (finding B1, decision D08). The contract terms (DPA, retention, subprocessors) are Day 23's; the law (DPDP Act 2023 and its rules, RBI outsourcing and KYC directions, residency) is Day 24's. This page records what the integration layer does today, so that those chapters have something concrete to review. Synthetic.

## 1. Data classes (from the mapping file, owned by the compliance head with the CISO)

| Class | Examples | Copied out of Godavari's systems | Stored in Kaagaz components | Cached | In logs | Shown to a model |
|---|---|---|---|---|---|---|
| direct identifier | name, PAN, Aadhaar reference (masked), mobile, email, address lines, date of birth | no | masked or hashed only | process memory, at most 900 s, for the analyst who opened the file | no | only as page text of the file being read, on the machine inside the building |
| quasi identifier | PIN code, city | yes | yes | yes | yes | yes |
| business | amounts, product, codes, flags, dates about the loan | yes | yes | yes | yes | yes |
| system | file number, application ID, EXT_REF, timestamps | yes | yes | yes | yes | no (adds nothing) |

## 2. Per source

| Source | Read how | Kept by Kaagaz | Never kept | Freshness we may assume |
|---|---|---|---|---|
| core (SOAP) | lookups and one-file detail, on demand, paced | application ID, status, EXT_REF, business fields of our writes (journal) | identifiers, except in memory for 900 s for one analyst | live |
| 02:00 SFTP batch | read-only account; manifest-driven | staged copies inside the building; SHA-256 per document; the pickup ledger | nothing leaves the building; no copy outside staging | the night's drop, after `.done` |
| trackers (Excel) | read nightly from the shared drive | file number, branch code, assignee, state, waiting-on documents, received date | the customer name column; the analysts' branch phone column (offered to the team leads separately) | as of the last save; no timestamps on status changes |
| reporting copy (SQL) | `RPT_KAAGAZ_RO`, signed-off columns only | query results for the reconciliation, in the report | identifier columns (denied by the authorizer) | as of 05:00; anything later is invisible |

## 3. What may be cached, and for how long

| What | Where | For how long | Why that long |
|---|---|---|---|
| an applicant's identifiers | the review screen's process memory | 900 s, then purged; every view logged, cache hit or not | long enough for one analyst to work one file; short enough that a forgotten screen holds nothing |
| the mapping and code tables | process memory | until the mapping fingerprint changes | not personal data; must match the signed version |
| a lookup result for the writer | none | not cached | the lookup's whole value is that it is live |
| the reporting copy's results | the morning report | as long as the report is kept (the engagement folder's retention, Day 23) | business and system fields only |

## 4. Checks that hold it (all in `code/tests/`)

- the journal, our log lines and the report contain no customer name or PAN (`test_the_journal_holds_no_customer_identifiers`, the night run's last line)
- the reporting copy denies identifier columns to our account (`test_identifiers_and_unsigned_columns_are_denied_by_the_authorizer`)
- the tracker's customer-name column never reaches the queue (`test_the_customer_name_never_reaches_the_queue`)
- on-demand reads are logged every time and forgotten after the TTL (`test_identifiers_are_read_on_demand_logged_every_time_and_forgotten`)
- the cassette recorded from the sandbox is scrubbed (`test_the_cassette_holds_no_identifiers`)

## 5. Open for Day 23 and Day 24

- Where the staging folder lives after the cutover to AWS Mumbai (M16, 4 January 2027), and who can read it.
- Retention of staged PDFs and of the morning reports.
- Whether a masked view may be shown to a model running outside the building at all, after D08's gates.
