# 04 · Metadata as a First-Class Index: What Every Chunk Carries Besides Its Text

> Day 15 · Section 4 of 16 · [Chapter overview](README.md) · Previous: [03 · Chunking](03-chunking.md) · Next: [05 · Hybrid search and reranking](05-hybrid-search-and-reranking.md)

---

## 4.1 Why text is not enough

Three of the questions Lakshmi's panel must get right cannot be answered from text similarity at all:

- *Is this rule still in force?* The 2024 and 2025 Aadhaar circulars say nearly the same thing in nearly the same
  words. Only a date tells them apart.
- *May she see this file?* A Kukatpally summary and a Guntur summary about the same kind of applicant are equally
  similar to her query. Only the branch tells them apart.
- *Is this a policy or a precedent?* "Rent agreement accepted with the landlord's electricity bill" is both a clause
  in the annex and a sentence in a past file. Only the document type tells them apart, and the panel shows them in
  different sections for a reason: one is a rule, the other is a judgement someone made once.

These are not ranking signals to be weighed against relevance. They are **facts about the document that decide
whether it is eligible at all**. That is what "metadata as a first-class index" means: the metadata is indexed and
filtered with the same care as the text, and a filter on it is exact, not approximate.

## 4.2 The fields

Every chunk in the project carries a `DocMeta` (in `metadata.py`):

| Field | Example | Used for | Who owns it |
|---|---|---|---|
| `doc_id` | `GFL/CO/2025/027`, `GF-23417` | citation; exact lookup; supersession links | the register; the core system |
| `doc_type` | circular, rulebook, annex, rbi_digest, loan_decision | the panel's two sections; scope filters | the register |
| `title` | "Income proof for two-wheeler loans by applicant type" | contextual header; display | the register |
| `product` | two-wheeler, gold, small-business, all | filter to the file's product ("all" always passes) | the register |
| `language` | en, mixed, te-latn | analysis per language in the eval; routing to the right analyzer | detected at ingestion, checked |
| `effective_from`, `effective_to` | 2025-04-01, none | the version in force on a date | the compliance head |
| `supersedes`, `superseded_by` | GFL/CO/2024/015 | redirecting old numbers; history | the compliance head |
| `approval_status` | approved, draft | drafts visible to the compliance desk only | the compliance head |
| `branch`, `branch_code` | Guntur, GNT04 | display; Day 11's visibility rule | the core system |
| `acl` | `{GF-BR-GNT04}` or `{GF-ROLE-CREDITOPS, GF-ROLE-COMPLIANCE, GF-ROLE-BRANCH}` | the permission pre-filter | derived from type, approval and branch |
| `source_system` | "compliance circular register", "core lending system, masked decision summary" | provenance in the citation; incident tracing | the pipeline |
| `sensitivity` | internal; confidential: customer file | logging and retention rules (Day 19, Day 24) | the CISO's classification |

Per chunk, on top of the document's metadata: `clause`, `page_start`, `page_end`, `kind` (clause, table, row group,
summary, window) and `heading`.

When the 40-page loan bundles are indexed, add Day 13's page type (application_form, pan_card, income_proof,
dealer_quotation, gold_appraisal, co_applicant_kyc, bank_statement, terms) and the loan ID, so a search can be
restricted to "income proof pages of this file". The Part plan lists loan ID, branch, document type, date, source
system and sensitivity as the minimum; the table above is that list plus what supersession and approval need.

## 4.3 From the register, never from the text

The most important rule about metadata: **take it from the system that owns the fact, not from the document's
text.** The circular says "Effective: 01 April 2025" on page 1, and you could parse it. Do not:

- The text can be wrong or stale: a circular revised after printing, a scan where "2025" reads as "2O25".
- The text cannot carry what happened later. Nothing on GFL/CO/2024/015's page says it was superseded; that fact is
  in the next circular and, properly, in the register.
- Parsing makes the extraction pipeline the owner of a compliance fact, and the compliance head the person who has
  to trust it.

In the project the generator keeps the register (the `Document` fields) separate from the pages, and
`meta_for(doc)` builds metadata from the register only. At Godavari this has a consequence that is bigger than the
code: **there is no register yet.** Day 4 found that "nobody owns the circulars"; they live in email. The retrieval
work forces the question, and the answer is that the compliance head owns a register (number, title, product,
effective date, superseded-by, approval, file), and the index reads only what is in it. That is open question RQ1 in
the design note (`worksheet/godavari-retrieval-design.md`). It is the same move Day 11 made with the rules: the
customer's expert owns the fact, the system enforces it, and there is one place it lives.

The loan summaries' metadata (branch, product, decision, decision date) comes from the core system's record,
through the read replica that [Day 16](../16-integrating-with-what-exists/README.md) integrates. The summary's text
repeats some of it for the analyst's benefit; the filter never reads the text.

## 4.4 Access-control lists name document groups, never users

The `acl` field deserves its own rule, because the wrong design looks right in a demo:

```python
def acl_for(doc: Document) -> frozenset[str]:
    if doc.doc_type == "loan_decision":
        assert doc.branch is not None
        return frozenset({BRANCH_AD_GROUP[doc.branch]})              # Day 11's group for that branch, nothing else
    if doc.approval_status != "approved":
        return frozenset({ROLE_COMPLIANCE})                           # drafts: the compliance desk only
    return frozenset({ROLE_CREDITOPS, ROLE_COMPLIANCE, ROLE_BRANCH})
```

The ACL on a Guntur summary is `{GF-BR-GNT04}`: the **group**, not the list of people in it. The tempting
alternative, computing "who may see this" at indexing time and storing user names on each chunk, is the
counterfactual Day 6 warned about: it demos well, and in week 8 the CISO asks how a transferred manager's access is
revoked, and the honest answer is "at the next re-index". Storing groups means the index never changes when people
move; only the caller's group list does, and that is resolved fresh on every request (section 06.5). A test checks
that no chunk ACL contains a user name.

## 4.5 Filters the panel uses

The review queue knows the file on screen, so the panel can send exact filters along with the query:

| Filter | Value for Lakshmi's Guntur two-wheeler file | Effect |
|---|---|---|
| `doc_types` | policy types for the top section; `loan_decision` for the bottom | the two sections never mix rules and precedents |
| `products` | two-wheeler | gold and small-business circulars drop out; "all" circulars stay |
| `as_of` | today, or the decision date when reviewing an old file | the version in force on that date |
| permissions | her groups, resolved now | everything she may not see is never a candidate |

Filters are cheap, exact and explainable. A rule of thumb that holds up in practice: **anything the system knows for
certain about what the user needs is a filter, not a hope that ranking will sort it out.** Ranking is for what you
do not know.

## 4.6 Metadata quality is a deliverable

Bad metadata fails silently and in the worst direction. A circular with a missing `effective_to` stays "in force"
forever; a summary with the wrong branch is shown to the wrong region; a draft marked approved reaches forty analysts.
Treat metadata like data in a pipeline: validate it at ingestion (every circular has an effective date; every
superseded-by points at a real number; every loan summary has one of the six branch codes), report counts per field
per load, and fail the load rather than index a document with a hole. The project's corpus manifest
(`data/corpus-manifest.csv`) is the shape of the report the compliance head would read after each load.
