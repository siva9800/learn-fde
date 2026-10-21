# 09 · The Data You Are Not Allowed to Copy: Keep It in Place, Read It on Demand, Forget It

> Day 16 · Section 9 of 18 · [Chapter overview](README.md) · Previous: [08 · The metadata translation layer](08-the-metadata-translation-layer.md) · Next: [10 · Contract tests and drift](10-contract-tests-and-drift.md)

---

## 9.1 The constraint, and where it comes from

"No customer PII leaves India, in any environment, including tests, logs and backups" (the compliance head
and the CISO, Day 10 section 8). "Nothing leaves the building before the CISO's review" (finding B1,
decision D08). The contract and the law behind these sentences (the DPA, retention, subprocessors, the
DPDP Act 2023 and its rules, RBI's outsourcing and KYC directions, residency) belong to Day 23 and Day 24.
This section is the engineering that makes them true in an integration layer, where they are easiest to
break by accident: a debug log, a cache, a copy "just for the report", a cassette for tests.

The question to ask of every piece of customer data the integration touches is not "is it encrypted?" but
"does a copy of it exist anywhere it did not need to be?" Encryption in transit answers a different
question; the AI-draft plan confuses the two on purpose.

## 9.2 The rule: read in place, for one file, for one person, and forget

The customer's name, PAN and mobile live in the core. Kaagaz's components (the queue, the journal, the
logs, the reconciliation report) keep a masked form or a hash. When an analyst opens a file,
`in_place.OnDemandApplicant` reads the identifiers from the core through the SOAP port:

```python
def view(self, file_no: str, analyst_id: str, purpose: str) -> dict[str, str]:
    if purpose not in PURPOSES:
        raise PermissionError(f"purpose {purpose!r} is not one the compliance head allowed")
    if not analyst_id:
        raise PermissionError("a named analyst opens a file; a service account does not")
    key = (file_no, analyst_id)
    hit = key in self._cache and self.now() - self._cache[key][0] < self.ttl_s
    if not hit:
        ...                                   # GetApplicationByFileNumber, then GetApplication
    self.views.append(View(self.clock.now().strftime("%Y%m%d%H%M%S"), analyst_id, file_no, purpose, hit))
    return dict(self._cache[key][1])
```

- **For a stated purpose.** Analyst review, a branch call-back, an audit query. "model_context" is not on
  the list, and the night run shows it refused.
- **For a named person.** A service account does not open files.
- **Logged every time, cache hit or not.** The CISO's "who viewed this file", kept for seven years (finding
  A6), is a log of views, not of reads from the core. A cache that skipped the log would make the log lie.
- **Cached in process memory, briefly.** At most 900 seconds, the time one analyst works one file, and
  purged after. Nothing is written to disk.

```text
on demand: GF-AN-1142 opens GF-25001; PAN read from the core and shown as XXXXX4563X in every log; 2 views logged (1 from the 900 s cache)
on demand: refused: purpose 'model_context' is not one the compliance head allowed
```

## 9.3 What may be cached, and for how long

The mapping's data classes decide, per field, and the compliance head owns that section. The
data-handling matrix (`worksheet/godavari-data-handling-matrix.md`) is the version for people:

| What | Where | For how long |
|---|---|---|
| an applicant's identifiers | the review screen's process memory | 900 s; every view logged |
| a lookup result for the writer | nowhere | not cached: its value is that it is live |
| the mapping and code tables | memory | until the mapping's fingerprint changes |
| staged PDFs | staging on the machine in the building | the documents' retention (Day 23 decides) |
| the morning report | the engagement folder | business and system fields only, no identifiers |

## 9.4 Mask at the boundary, hash to join

Two tools do most of the work:

- **Masking at the boundary.** `safe_for_log()` replaces every direct identifier with a mask
  (`PAN XXXXX4563X`) or a placeholder before a record reaches a log line or a report. The boundary is the
  function every log call goes through, not each developer's memory.
- **Hashes instead of values.** The journal stores a SHA-256 of the payload, not the payload; the pickup
  stores a SHA-256 per document. When two systems need to agree that they hold the same thing, compare
  hashes. A salted token (`in_place.token`) lets you join records on a PAN without storing the PAN.

The Part plan's version: "Customer PII stays on the on-prem read replica; only masked fields and document
hashes travel to the pipeline." In this chapter the replica's identifier columns are denied to our account
(section 07), so the only path to a PAN is the on-demand read above, which is logged.

## 9.5 Proving it, not promising it

Every one of these is a test or a line in the run's output, so the CISO's team can check them rather than
take them on trust:

```text
customer names or PANs in our journal, our log lines and the report: 0
```

That last line of the night run scans the journal, every printed line and the report for every synthetic
name and PAN in the 72 Hyderabad files and finds none. The cassette recorded from the sandbox is scrubbed
even though the sandbox is masked, because a recording made from a real sandbox one day will not be. The
tracker's customer-name column never reaches a queue item. The reporting copy refuses the columns.

## 9.6 Keep the index inside

Day 15's retrieval index holds chunks of the same documents. The same rule applies: the index lives inside
the customer's environment, built from the staged copies, never exported (Day 24 decides where that
environment is after the move to AWS Mumbai on 4 January 2027). The integration layer is where the documents
enter Kaagaz's components, so it is the first place to enforce it.

## 9.7 The questions to take to Day 23 and Day 24

- Where does the staging folder live after the cutover (M16), and who can read it?
- How long are staged PDFs and morning reports kept?
- May a masked view ever be shown to a model running outside the building, after D08's gates?
- Does the view log's seven-year retention apply to Kaagaz's log or to Godavari's copy of it?

Write them down now, with the code that would change, so the security review in Day 23 starts from facts.
