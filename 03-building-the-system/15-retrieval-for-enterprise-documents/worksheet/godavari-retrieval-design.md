# Godavari · policy and precedent lookup in the review queue · retrieval design note

> Day 15 artifact for the engagement folder. Version 0.3, Wednesday 25 November 2026 (engagement week 5).
> Author: the Kaagaz FDE. Readers: the CISO (permissions, logging, PAN), the compliance head (the circular
> register, approval, supersession), Srinivas and the Vijayawada team lead (the panel). For Day 23's security
> questionnaire, section "Access control in retrieval", and Day 22's identity work. All numbers below are from
> `code/run_demo.py` on synthetic data; none is a claim about Godavari's real documents yet.

## 1. What this is, and what it is not

It is **a panel inside the analyst's review queue** with two short lists: the policy clauses that apply to the file
on screen, and up to three similar past files from the analyst's own branches, each with its decision. The query is
pre-filled from the file (product, applicant type, the document in question) and the analyst can edit it.

It is **not the branch policy chatbot**. That stays on the will-not-do list (decision D06, Day 10): no free
conversation, no branch staff, no answer written without the clause beside it, no new window (Srinivas: "a fifth
window is a no"). An analyst decides every file (decision D07); the panel shows evidence and decides nothing.

## 2. What is indexed

| Source | Count (synthetic) | Owner | Who may see it |
|---|---|---|---|
| Credit-ops circulars, approved | 61 in 40 series, 21 of them superseded | the compliance head (the circular register) | role groups: credit ops, compliance, branch staff |
| Draft circulars | 1 | the compliance head | the compliance desk only |
| Product rulebooks and the address-alternatives annex | 4 and 1 | the compliance head; rule numbers generated from Day 11's signed code | as approved circulars |
| RBI digests approved for analysts | 3 | the compliance head (the RBI text prevails) | as approved circulars |
| Masked loan-file decision summaries | 300, 50 per pilot-era branch | the core-system owner (read replica, Day 16) | the branch's AD group only (Day 11's `visible_to`) |

Not indexed: raw loan files, PAN, Aadhaar numbers, anything from WhatsApp or personal phones, anything not in the
circular register. A PAN in a summary is replaced at indexing by a keyed token (HMAC; the key in Godavari's KMS,
Day 25); a PAN typed into a query is tokenised the same way and is never stored or logged.

## 3. Access control: the pre-filter

1. **Every chunk carries the document's groups, never a list of users.** A loan summary carries its branch group
   (for example `GF-BR-GNT04`); a circular carries the role groups. A transfer changes the user's groups, not the
   index.
2. **The caller's groups are resolved at the moment of the request** from the newest nightly snapshot of the
   directory (the export is Day 22's). A snapshot older than 36 hours refuses to answer.
3. **The filter runs before ranking.** The ranking code is given only the chunk positions the caller may see, so a
   hidden document is never scored, counted, summarised or logged.
4. **Fail closed.** Unknown user, no groups, or the service account's own identity: nothing is returned. There is
   no all-branches group and the tool does not ask for one. The service account holds no groups.
5. **One rule, one place.** For loan files the filter calls Day 11's `visible_to(groups, branch)`; a test checks
   the chunk ACL and that function agree on every chunk for every user.

Measured: 4,315 results checked for 7 users x 40 queries x 2 scopes, **0 violations**. The rejected design (rank
everything, filter the list afterwards) wrote 567 of 1,000 debug-log lines about files the user may not see, and its
drafted note named a Kukatpally file, its dealer and its on-road price to a Vijayawada-team analyst.

## 4. Freshness and citations

- Each circular has an effective date and, when replaced, a superseded-by link, kept in the register. By default
  only the version in force today is searchable. A query that quotes an old number is redirected to the current one
  with a notice. Reviewing an older file can ask "as of" its decision date and get the version in force then.
- Every result cites document number, version (by number and effective date), clause and pages. The panel shows
  the clause text, not a paraphrase.

## 5. Logging

One view-log entry per search: time, user, the snapshot the groups came from, the query with PANs replaced by
`[PAN]`, and the document numbers shown. Nothing about documents not shown. Retention seven years with the other
view records (Day 6, finding A6; the CISO's requirement); the store is Day 19's and Day 24's decision.

## 6. Quality, measured on its own

40 labelled queries (answer spans, run as the asking user): recall at 5 is **0.975**; 39 of 40 fully answered in the
top 5, 95 percent Wilson interval 0.87 to 1.00. Lexical search alone 0.925, the dense stand-in alone 0.875, naive
fixed-size chunks 0.825. The one miss ("oldest borrower allowed for a bike loan") is kept as a miss rather than
fixed by adding words to the synonym table, because that would tune to the test.

## 7. Open questions

| # | Question | Owner | Needed by |
|---|---|---|---|
| RQ1 | Does the compliance head accept owning the circular register (effective dates, supersession, approval) as the only source the index reads? | the compliance head | before real circulars are loaded |
| RQ2 | May masked decision summaries leave the core read replica for the index host, or must the index sit beside the replica? | the CISO, the core-system owner (Day 16, Day 24) | before real summaries are loaded |
| RQ3 | Which embedding model, run where? Telugu coverage measured on these 40 queries plus the analysts' own | the FDE (Day 24 decides residency) | before the stand-in is replaced |
| RQ4 | 40 queries cannot show 95 percent with any confidence; Lakshmi and the senior analyst to write 100 more from real lookups, labelled in Day 14's process | the eval owners (Day 14) | before the pilot uses the panel |
