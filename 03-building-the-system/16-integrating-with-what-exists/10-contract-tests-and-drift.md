# 10 · Contract Tests Against a Recorded Sandbox, and the Drift Nobody Announced

> Day 16 · Section 10 of 18 · [Chapter overview](README.md) · Previous: [09 · The data you may not copy](09-data-you-may-not-copy.md) · Next: [11 · The reconciliation report](11-the-reconciliation-report.md)

---

## 10.1 Why a build cannot call the sandbox

Godavari's sandbox is "a copy of production refreshed every quarter, masked. The last refresh was in July.
Rules in the sandbox are three months behind." It is down whenever the core is down, it is reachable only
from inside the building, and the owner is watching every call. A build that depends on it fails for
reasons that have nothing to do with your change, or adds noise to the access log he is reading. So the
integration is tested against a **recording** of the sandbox on every build, and the recording is
refreshed deliberately.

A **contract test** checks that two sides of an interface still agree, without running both at once. The
idea is Martin Fowler's "contract test" and, for consumer-driven contracts, the Pact project's; here it
is simpler, because there is only one provider and we cannot change it.

## 10.2 Record once

`record_sandbox.py` drives the sandbox through the hand-built client with a session that keeps every
request and response, and writes ten exchanges to `contracts/cassettes/sandbox-2026-11-10.json`:

```text
lookup_shell           GetApplicationByFileNumber   HTTP 200
create_ok              CreateApplication            HTTP 200
lookup_after_create    GetApplicationByFileNumber   HTTP 200
get_application        GetApplication               HTTP 200
update_kyc             UpdateKYCStatus              HTTP 200
fault_mandatory        CreateApplication            HTTP 500
fault_invalid_code     CreateApplication            HTTP 500
fault_not_registered   CreateApplication            HTTP 500
lookup_unknown         GetApplicationByFileNumber   HTTP 200
fault_batch_window     CreateApplication            HTTP 500
```

The scenarios cover what the integration depends on: the shell, a create, the lookup seeing its own write
at once (the property the safe writer relies on), the detail, a status update, and four faults. Names,
PANs, mobiles and the password are scrubbed at recording time. At Godavari this runs from the machine in
the building after every quarterly refresh and every release the owner announces, and its diff is reviewed
with him before the new cassette is committed.

## 10.3 Replay on every build

`ReplaySession` answers each POST from the cassette, matching the operation and the request's shape. Four
tests use it:

| Test | What it catches |
|---|---|
| both clients read every recorded exchange the same way | a parser change that would misread the core |
| every request has the recorded shape, element by element | a renamed or reordered field (which the core would silently drop) |
| the served WSDL matches the pinned contract | a change on Godavari's side, as a readable diff |
| the known-drift list is owned, unexpired and tested | a sandbox difference nobody re-checked after a refresh |

The first test records one difference on purpose: for the missing `MOB_NO`, the hand-built client sends
the request and the core answers `CL-E023`, while zeep refuses before the network because the WSDL says
`minOccurs="1"`. Both are fine; the test makes sure nobody "fixes" one to look like the other without
knowing why.

The WSDL contract is the schema reduced to (operation, element path, `minOccurs`, type). When Godavari's
side changes, the test prints what changed, not a stack trace:

```text
CreateApplication request: CreateApplicationRequest/Application/MOB_NO removed
CreateApplication request: CreateApplicationRequest/Application/DLR_CD minOccurs 0 -> 1
```

## 10.4 Known drift, with an owner and an expiry

Some differences between sandbox and production are known and accepted. They are written down in
`contracts/known_drift.toml`, each with what differs, what our side does about it, the test that holds
our side, who confirmed it, and an expiry date:

| ID | What differs | Our side |
|---|---|---|
| SBX-01 | `DLR_CD` mandatory for two-wheelers in production since R26.08; the July sandbox does not enforce it; the WSDL marks it optional in both | mapping 1.3.0 always sends it and fails closed if it is empty |
| SBX-02 | the sandbox's credit-check results come from three-month-old rules | nothing ever asserts on `CR_CHK_RSLT` from the sandbox |
| SBX-03 | the 02:00 job does not run against the sandbox; shells for test files are registered by hand | the night run registers its own shells against the stand-in |

SBX-01 is the dangerous direction: the sandbox is more permissive than production. Part B of the project
shows it:

```text
   sandbox          GF-25040 without DLR_CD -> created AP0000000001
   production-like  GF-25040 without DLR_CD -> CL-E023 MANDATORY FIELD MISSING: DLR_CD
```

A contract test against the sandbox alone would have been green while production rejected every
two-wheeler file. What found it was the owner reading the mapping file (version 1.2.0 mapped only the
WSDL's mandatory fields) and saying, in effect, "I told you: three months behind." The test
`test_known_drift_is_owned_unexpired_and_tested` fails the build after 31 January 2027 until someone
re-checks each entry with him; it uses the chapter's date, and a CI job would use today's.

## 10.5 Schema drift on every build, and the other direction

Drift comes from both sides:

- **Theirs:** a release adds a field, a code (`APPLSTAT H`), a rule. The WSDL diff and the reconciliation's
  code-table check (section 11) catch the first two; the owner's release note and the known-drift list
  catch the third.
- **Ours:** someone renames a canonical field, edits the mapping, or "tidies" a request builder. The
  request-shape test and the mapping's fingerprint catch these before anything reaches the sandbox.

The contract tests run in under a second against the cassette. The sandbox itself is touched only by the
recording script and by the month of logged calls, which is the owner's evidence, not your test suite.
