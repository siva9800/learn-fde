# 14 · Build It With AI, and How You Know It's Right

> Day 16 · Section 14 of 18 · [Chapter overview](README.md) · Previous: [13 · Project: the Godavari integration layer](13-project-the-godavari-integration-layer.md) · Next: [15 · Mistakes and debugging](15-mistakes-and-debugging.md)

---

## 14.1 Build it with AI

A coding agent can draft most of this chapter's code in an afternoon. What it cannot do is know
Godavari. The whole technique is: give it the facts, forbid it the guesses, and review it against the
facts.

### The context to give it

- The WSDL (the vendored copy) and the data dictionary (`corespec.py`), with the 23 mandatory fields and
  the computed ones marked.
- Transcript 06, verbatim, and findings A2, A4 and A5. The owner's sentences are the requirements.
- The four outcomes table from section 03 and the state table from section 04, as the contract the writer
  must meet.
- Day 11's `core_write.py`, with the instruction to import `push_to_core` by path and not copy it.
- The mapping's data classes and the reporting sign-off: which columns exist and which may be read.
- One recorded exchange per operation from the cassette, so it sees real envelopes.

What never goes in the context: real customer files, real credentials, the production endpoint, or the
reporting copy's identifier columns. Day 39 owns the rules for agents on customer code.

### A strong prompt

> Build a Python 3.12 integration layer for a 2009 SOAP core lending system. Facts you must not change:
> CreateApplication always creates (no idempotency); GetApplicationByFileNumber returns a shell (APPL_STAT
> S, no APPL_ID) until an application exists, then every application for the file; no writes 17:30 to the
> end of the batch (20:00, 23:00 in the last three days of a month); more than five calls a second returns
> fault CL-E099; the core's transaction timeout is 60 s. Requirements: (1) a zeep client loaded from the
> vendored WSDL file, never from the network, with separate load and operation timeouts and an explicit
> service address; (2) every transport error classified as CoreFault, CoreUnavailable, NotSent or
> AmbiguousOutcome, where a read timeout is ambiguous; (3) a writer that imports Day 11's push_to_core by
> path, journals intent before every call, NEVER retries a create that ended ambiguous, and resolves it by
> lookup only after a 90 s quiet period; (4) a mapping file in TOML that fails closed on unknown codes and
> missing mandatory fields; (5) no customer name, PAN or mobile in any log, journal or report. Write tests
> for the duplicate case with a stand-in that commits and then stalls, and with one that stalls and then
> commits. Do not invent field meanings: where the data dictionary does not say what a field means, write
> "unknown: ask the owner" and stop.

### What it gets right

The zeep boilerplate, WS-Security, the stand-in, envelope parsing, the TOML loader, the openpyxl loop, the
read-only SQLite open, the mapping skeleton from the WSDL, and the hundred small parsing tests a tracker needs.

### The mistakes it makes on this concept

These are specific; each one appeared in drafts while this chapter was built or is in the exercise file.

1. **Retries the create.** "Three attempts with exponential backoff" on `CreateApplication`, because that
   is what retries look like everywhere else. This is DUPLICATE_ON_RETRY.
2. **Treats SOAP as idempotent**, sometimes in a comment that says so.
3. **Checks for existence in the reporting copy** because the SOAP lookup is "slow". The copy is a day old.
4. **Loads the WSDL from the server URL at start-up**, and sets zeep's `timeout` (document loading) but not
   `operation_timeout` (calls), so calls have no timeout.
5. **Catches `Fault` as a business rejection**, including CL-E017 (a deferral), CL-E099 (back off) and
   zeep's "Unknown fault occured" for the HTML maintenance page (not the core at all).
6. **Truncates instead of refusing** (`[:40]` on an address line), losing data silently.
7. **Invents field meanings**: `CUST_FLG_3 = "Y" if income > 25000`. The agent cannot know the flag means
   salaried, and a plausible rule is worse than a blank.
8. **Sends computed fields** (`ROI_PCT`), which the 2009 core silently overwrites.
9. **Logs the payload** at info level, PAN and all.
10. **Ignores the write window**, or hard-codes 20:00 and misses month end.
11. **Reads the tracker by column position and month-first dates**, so 05/11 becomes 11 May.
12. **Saves the workbook after `load_workbook(data_only=True)`**, replacing every formula with its value.
13. **Processes every PDF in the folder and deletes it afterwards**, ignoring the manifest and the
    read-only account.
14. **Reconciles from its own journal**: "10 created, 0 duplicates. All good." Nothing was read from the
    core.

## 14.2 How you know it's right

Whether you or an agent wrote it, these checks decide:

1. **Reproduce the failure first.** Run the naive client against a stand-in that commits and stalls; it
   must make a duplicate. A test suite where nothing can duplicate proves nothing about the writer.
2. **Both timeout shapes.** Commit-then-stall and stall-then-commit, each with the writer under test. If
   lookup-then-retry passes both, your stand-in is not stalling long enough.
3. **Count in the core, not in your code.** Every assertion about duplicates reads the stand-in's records
   (or, at Godavari, the owner's access log), never the writer's own return values.
4. **Never decided early.** Resolving an unknown before the quiet period must return UNKNOWN.
5. **The window from both sides.** The writer holds at 17:40 and makes no call; and when the core says
   CL-E017 at 20:05 because the batch overran, the writer defers instead of failing.
6. **Mapping against the dictionary.** Every core field has an entry; every mandatory one is ours or
   defaulted; computed ones are never ours; every code exists in the core's code table.
7. **Fail closed, both directions.** An unknown code going in and coming out raises.
8. **No identifiers anywhere they should not be.** Scan the journal, the logs, the report and the cassette
   for every synthetic name and PAN.
9. **Their folder is untouched.** Hash the source tree before and after a pickup.
10. **Both clients agree with the recording.** Replay the cassette through both; compare request shapes.
11. **The report balances.** Calls on both sides equal; every exception has a file number.
12. **Run it at a bad time.** Month end at 22:30, Sunday at 07:00, a partial file at 02:30.

### Review checklist

- [ ] No create is retried after an ambiguous outcome; unknowns wait out a quiet period longer than the core's transaction ceiling
- [ ] Day 11's `push_to_core` is imported by path, not copied; the key is Day 11's, stamped in `EXT_REF`
- [ ] The idempotency lookup goes to the system of record, live; never to the reporting copy
- [ ] The WSDL is vendored; nothing is fetched at run time; both timeouts are set; the address is explicit
- [ ] Faults are classified by code from `detail` first, text second, never by HTTP status alone
- [ ] Writes respect the window, including month end, and treat CL-E017 as a deferral
- [ ] The client paces below the core's real limit
- [ ] Every field and code goes through the versioned mapping; its fingerprint matches the sign-off
- [ ] Unknown codes and missing mandatory fields fail before any call
- [ ] No computed field is sent; no value is silently truncated
- [ ] The pickup reads only manifest-listed, size- and hash-checked files after the marker, and never changes their folder
- [ ] The tracker reader finds headers, parses defensively, sends the unreadable to a person and never migrates the customer's name
- [ ] The reporting reader is read-only with a column-level allowlist, bounded and logged
- [ ] No identifier in any log, journal, report or recording
- [ ] The reconciliation reads the core and the owner's log, ties out, and says what it could not check
