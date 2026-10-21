# 15 · Exercises

> Day 15 · Section 15 of 16 · [Chapter overview](README.md) · Previous: [14 · Interview questions](14-interview-questions.md) · Next: [16 · Further reading](16-further-reading.md)

---

Twelve exercises in three levels, including predict-the-output, two break-it-then-fix-it runs and one "review this
AI-written code". Solutions are folded under each. The exercises marked **(tested)** were run on Python 3.14.3 with the
chapter's pinned requirements in a virtual environment (October 2026), and the outputs shown are real. Learning mode:
write the code yourself and use an AI assistant as a tutor or a sceptical reviewer, not as the author. Try first, then
open the solution. For the break-it runs, work on a copy of the course folder so that Day 11 and Day 14 are still
found by path.

## Level 1: warm-up

**1.1 Pre or post?** For each design, say whether it is a pre-filter or a post-filter, and what (if anything) leaks.

(a) `SELECT ... FROM chunks WHERE branch_group = ANY(:groups) ORDER BY embedding <=> :q LIMIT 5`, under a role with
row-level security on `chunks`.
(b) Retrieve the top 20 from the vector store, drop the ones the user may not see, show the first 5.
(c) Retrieve the top 5 for all users, pass them to the model with "only discuss documents the user may see".
(d) Filter to allowed chunks, rank, cache the top 5 under the key `hash(query)`.
(e) Filter to allowed chunks, rank, return the top 5, and show "62 documents matched" computed by a separate count
query over the whole index.

<details><summary>Solution</summary>

(a) Pre-filter, enforced twice (the `WHERE` and the policy). Check the approximate index's "fewer than k" behaviour
(06.4), but nothing leaks. (b) Post-filter: fewer than five results is possible, and anything computed from the 20
(counts, snippets, logs) leaks. (c) Not access control: the model has read everything; permission by prompt (06.8).
(d) Pre-filter for the first user; the cache then serves that user's results to anyone with the same query: key by
groups and query (06.3). (e) Pre-filter for the list, post-filter for the count: the count leaks (06.3).

</details>

**1.2 Which retriever wins?** For each query against Godavari's corpus, predict whether BM25, the dense retriever or
both would find the answer in the top 5, and why: (a) "GFL/CO/2025/052"; (b) "how long is a showroom proforma valid";
(c) "earlier files for PAN FGHPK1234J"; (d) "adde agreement registered kadu"; (e) "ఆదాయ రుజువు స్వయం ఉపాధి";
(f) "can we keep a customer's uid copy without redaction if they agree".

<details><summary>Solution</summary>

(a) BM25: an exact identifier; the dense view splits it into fragments shared by every 2025 circular (05.4 shows the
dense top 3 are other circulars). (b) Both, in this project: BM25 finds it through the one shared word, "valid", and the dense stand-in through its
concept table (showroom to dealer, proforma to quotation). One shared word is luck; "how long can I use a showroom
proforma" would leave BM25 with nothing. (c) Both, because the service treats a PAN as an exact filter
before ranking (05.8); without that, dense alone returns unrelated files. (d) BM25 with folding ("addhe" and "adde"
fold together; "kaadu" and "kadu" too); the dense view sees different strings. (e) Both in this project: the words
appear exactly in the Telugu summary, and the dense stand-in maps them to concepts. (f) Dense: q14, BM25 does not find
it at all, the dense stand-in ranks it first, and plain RRF pushes it to sixth (05.5).

</details>

**1.3 Filter or ranking signal?** For each fact, say whether it should be a metadata filter or a ranking signal:
(a) the analyst's branch groups; (b) the circular is superseded; (c) the circular is about two-wheelers and the file is
a two-wheeler file; (d) the clause was issued recently; (e) the past file was approved rather than sent back;
(f) the document is a draft.

<details><summary>Solution</summary>

Filters: (a), (b), (c) (with "all" documents passing), (f). These are certain facts that decide eligibility (04.5).
(d) Neither, usually: recency is not relevance; the in-force filter already removes what is out of date (07.1).
(e) Neither by default: a sent-back precedent is as useful as an approved one (it shows what not to accept); show the
decision instead of filtering on it, or let the analyst filter.

</details>

**1.4 Predict the output (tested).** Before running, write down what `lexical_terms`, `dense_terms` and `naive_terms`
return for:

```python
s = "Is GFL/CO/2025/027 clause 4.2 still the rule for GF-23417? aadaayam proofs, చిరునామా రుజువు"
```

<details><summary>Solution</summary>

```text
lexical: ['GFL/CO/2025/027', 'clause', '4.2', 'still', 'rule', 'GF-23417', 'adayam', 'pruf', 'చిరునామా', 'రుజువు']
dense:   ['gfl', 'co', '2025', '027', 'clause', '4', '2', 'still', 'rule', 'gf', '23417', 'aadaayam', 'proofs', 'చిరునామా', 'రుజువు']
naive:   ['is', 'gfl', 'co', '2025', '027', 'clause', '4', '2', 'still', 'the', 'rule', 'for', 'gf', '23417', 'aadaayam', 'proofs', 'చ', 'ర', 'న', 'మ', 'ర', 'జ', 'వ']
```

The lexical analyzer keeps the circular number, the clause number and the file number whole, drops stopwords, folds
"aadaayam" to "adayam" and "proofs" to "pruf" (the fold rules turn "oo" into "u"; the key looks odd, and it does not
matter because both sides are folded), and keeps Telugu whole. The dense view splits every identifier. `\w+` shreds the
Telugu into seven single letters and keeps every stopword.

</details>

## Level 2: apply

**2.1 RRF by hand (tested).** BM25 returns `[A, B, C, D]` and the dense retriever returns `[C, E, A, F]`. With k = 60,
compute the fused order and scores. Which documents tie, and how does the project break the tie?

<details><summary>Solution</summary>

A: 1/61 + 1/63 = 0.03227; C: 1/63 + 1/61 = 0.03227; B: 1/62 = 0.01613; E: 1/62 = 0.01613; D: 1/64 = 0.01563; F: 1/64 =
0.01563. Real output of `rrf([['A','B','C','D'],['C','E','A','F']])`:

```text
[('A', 0.032266458495966696), ('C', 0.032266458495966696), ('B', 0.016129032258064516), ('E', 0.016129032258064516), ('D', 0.015625), ('F', 0.015625)]
```

A and C tie, B and E tie, D and F tie. Ties break by the best single rank (A and C both have a rank 1), then by ID, so
the order is deterministic, which matters for a test suite and for an analyst who refreshes the panel. Notice that B,
ranked second by BM25, falls below A and C, which both retrievers liked: agreement wins (05.5).

</details>

**2.2 Break it, then fix it: move the filter (tested).** In a copy of `service.py`, change `RetrievalService.search`
so that the allowed set ignores permissions (use only `passes_filter`), and instead drop forbidden results from the
ranked list just before taking the top k. The list on screen still contains only allowed results. Predict which of the
36 tests fail, then run them.

<details><summary>Solution</summary>

Real result: exactly one test fails.

```text
FAILED tests/test_permissions_and_leaks.py::test_a_pan_lookup_never_reveals_a_file_in_another_branch
E        +  where 1 = Response(user='lakshmi', query_logged='prior applications PAN [PAN]', results=[], total_matches=1, ...
```

Every list-based test still passes, because the filter still runs before the top k and before the note. What leaks is
the **count**: Lakshmi's PAN query for the Warangal-only PAN now reports one match while showing none, and the "no file
you can see matches this PAN" notice disappears, so she learns that a file with that PAN exists in a branch she cannot
see. This is the most instructive version of the bug: a late filter that looks correct everywhere except in one
number. The fix is the original code: permissions in `allowed_positions`, before ranking. The lesson for your own test
suites: test counts and notices, not only lists (06.3).

</details>

**2.3 Break it, then fix it: page tracking (tested).** In a copy of `chunking.py`, stop recording the page of table
rows (remove `cur.pages.append(pno)` from the table-row branch of `_parse`). Predict which tests fail and what the
income table's citation becomes.

<details><summary>Solution</summary>

Real result: three tests fail.

```text
FAILED tests/test_freshness_citations_eval.py::test_every_citation_quotes_text_that_is_on_the_cited_pages
FAILED tests/test_text_and_chunking.py::test_table_crossing_a_page_break_stays_one_chunk_with_its_header_once
FAILED tests/test_text_and_chunking.py::test_the_income_table_keeps_each_row_whole_with_caption_and_header
```

Both row groups of clause 4.2 are now cited as page 2 only (`[('GFL/CO/2025/027#4.2#0', 2, 2), ('GFL/CO/2025/027#4.2#1',
2, 2)]`), while the self-employed row is on page 3. An analyst following the citation would open the page without her
row. The citation test catches it mechanically because it checks that the cited text is on the cited pages (07.5).

</details>

**2.4 A new spelling.** The Guntur branch manager sends five notes in which "income" is written "aadhaayamu". Without
running anything, does the current fold rule set match it to "aadaayam"? Write the rule you would add, the labelled
query you would add with it, and the risk of the rule.

<details><summary>Solution</summary>

No. The folds give "adayamu" for "aadhaayamu" ("dh" to "d", "aa" to "a"), and "adayam" for "aadaayam"; the trailing
"u" (a common Telugu ending when transliterated) keeps them apart. A rule that drops a final "u" after "m" ("mu" to "m")
would join them. Add a labelled precedent query written with "aadhaayamu" whose span is one of those Guntur files, so
the rule is measured. The risk is over-folding: English words ending in "mu" are rare, but a rule like "drop any final
u" would also merge unrelated transliterated words. Every fold rule is a small analyzer change and triggers a re-index
(10.4).

</details>

**2.5 The product filter (tested).** Write a test that, for Lakshmi's two-wheeler file, a gold-only circular never appears in
the policy section when the panel passes `products=frozenset({"two-wheeler"})`, while circulars for "all" products
still can. Which existing function does the work?

<details><summary>Solution</summary>

`passes_filter` in `permissions.py` drops a chunk whose product is neither "all" nor in the filter's set. A test:

```python
def test_product_filter(svc, now):
    f = SearchFilter(as_of=now.date(), doc_types=POLICY_TYPES, products=frozenset({"two-wheeler"}))
    r = svc.search("lakshmi", "LTV appraisal purity gold loan", now, k=10, f=f)
    assert all(x.chunk.meta.product in ("two-wheeler", "all") for x in r.results)
```

The query is deliberately about gold: run without the product filter, the top three results are all gold documents
(`['gold', 'gold', 'gold']` in the tested run); with it, the test passes. A filter test should always use a query that
would fail without the filter.

</details>

## Level 3: challenging

**3.1 Review this AI-written code.** `code/exercises/ai_draft_retrieval.py` was written by a coding agent from a short
prompt. It runs and it demos well. Find at least twelve problems, rank them by severity, and say how each would show up
at Godavari.

<details><summary>Solution</summary>

Most severe first:

1. **Post-filter** (`hits` ranked over all chunks, `visible` filtered last): fewer than k results and every leak in
   06.3.
2. **The LLM summary is drafted from `hits`**, unfiltered, so another branch's file can be summarised to the analyst.
3. **Permission by prompt** (`SYSTEM_PROMPT` "Ignore any documents ..."): not access control (06.8).
4. **The cache is keyed by query only** (`_CACHE[query]`): one analyst's results served to another.
5. **Fail open**: `or not c["allowed_users"]` shows any chunk with an empty ACL to everyone.
6. **User lists computed at index time** (`allowed_users` from the groups file): a transfer is invisible until a
   re-index; also, policy documents are given every user in the file, including the service account if it is listed.
7. **`total` counts over all chunks**: the count leaks (06.3).
8. **Raw query logged** (`log.info("... query=%s")`): PANs in logs.
9. **No supersession**: "newest version" is chosen by `issued` within the top k only, by `doc_id`, which never
   matches across versions because each version has its own number, so superseded circulars are returned as current;
   drafts are not distinguished from approved circulars at all.
10. **`\w+` tokenizer**: Telugu shredded; circular numbers split into common tokens.
11. **Fixed 500-character chunks** with no cleaning, overlap or table handling; `page` is the chunk index, so the
    citation is wrong.
12. **"Hybrid" adds a BM25 score to a cosine**: different scales; BM25 dominates; not fusion.
13. **BM25 bugs**: `avg = 100` hard-coded; idf without the `1 +` can go negative for common terms, so matching a common
    word lowers the score.
14. **The eval runs as `compliance.desk.01`**, who sees every branch, so permissions are never exercised and the most
    similar forbidden file counts as a hit; and "recall at 5" is computed over `k=10`.
15. **`json.load(open(...))`** never closes the file, and nothing checks the snapshot's age.

At Godavari, items 1 to 7 are the CISO's review failing; 8 is a DPDP problem; 9 is the August 2025 Aadhaar story
repeated; 10 to 13 are quality; 14 makes the eval number meaningless.

</details>

**3.2 Write the questionnaire answer.** Day 23's security questionnaire asks: "Describe how your system ensures users
can only access documents they are authorised to view." Write the answer for Godavari in at most 150 words, using only
facts from this chapter and the design note.

<details><summary>Solution</summary>

A model answer: "Retrieval enforces Godavari's Active Directory branch and role groups before any ranking. Each indexed
chunk carries the groups of its source document (for a loan summary, its branch group), never user names. For every
request the caller's groups are resolved from the newest nightly directory snapshot; a snapshot older than 36 hours,
an unknown user or a user with no groups receives no results. The service account holds no groups and always acts with
the analyst's groups. Search, counts, logs and any drafted text are computed only from documents the caller may see.
Drafts are visible to the compliance desk only. No PAN is stored in the index or logs. A permission audit over every
user and every labelled query runs on every change and nightly; the current result is 4,315 results checked, zero
violations. Every search writes a view-log entry retained for seven years."

</details>

**3.3 The compliance desk's request.** The compliance head asks for "how many files like this one exist in each
branch", to spot inconsistent decisions across the region. Design it so that analysts' branch isolation is unaffected.

<details><summary>Solution</summary>

It is a different feature for a different role, not a mode of the analysts' panel. Serve it only to principals with
`GF-ROLE-COMPLIANCE` (whose six branch groups are typed in, so the pre-filter already allows every branch for them);
compute counts from the allowed set like every other count; put it behind a separate endpoint so that no analyst code
path can call it; log it in the view log with the counts shown. Add a permission test: an analyst calling the endpoint
gets a refusal, not a smaller count. Ask the CISO before building it; it is a new way to see across branches even for a
role that is allowed to.

</details>

**3.4 Telugu suffixes.** Add character n-grams (for example, 3- to 5-character grams) for Telugu-script tokens to the
lexical analyzer, as extra terms. Write two labelled queries using suffixed forms ("రుజువుగా", "బిల్లుతో") whose spans
are in the Telugu summaries, and measure recall at 5 before and after, plus the change on the other 40 queries.

<details><summary>Solution</summary>

A sketch: in `lexical_terms`, for a `tel` match, append the token and every n-gram of the token for n in 3 to 5,
prefixed (for example `te3:`) so that they never collide with whole words. Expect the suffixed queries to be found after
the change and not before, and expect a small amount of noise on the other Telugu queries, because short n-grams are
shared by unrelated words. The deliverable is your own numbers in a table, before and after, per category, which is the
point: an analyzer change is a measured change with a re-index plan (10.4), not a hunch. Your numbers will depend on
the n you choose; report them with the interval.

</details>

**3.5 Into Postgres.** Move the chunks into PostgreSQL 18 with full-text search, pgvector and a row-level security
policy keyed on the caller's groups (passed as a session setting by the service). Re-implement the permission audit
against the database, and show that a `SELECT` without a `WHERE` on the branch still returns only allowed rows.

<details><summary>Solution</summary>

Outline: a `chunks` table with `acl text[]`, `tsv tsvector`, `embedding vector(n)` and the metadata columns; `ALTER
TABLE chunks ENABLE ROW LEVEL SECURITY` and `FORCE ROW LEVEL SECURITY` (owners bypass otherwise); a policy `USING (acl
&& string_to_array(current_setting('app.groups'), ','))`; the service connects as a role that is not the owner, not a
superuser and has no `BYPASSRLS`; it sets `app.groups` per request from the snapshot. Fuse `ts_rank_cd` results and
vector results with RRF in SQL or in Python. Run the audit through the database. Then test the approximate index under
the most restrictive user (one branch) with and without `hnsw.iterative_scan`, and record how many results come back at
k = 5 (06.4). Expect to find the "fewer than k" case before you turn iterative scans on.

</details>

**3.6 Your own corpus.** Take a document set you know (your company's policies, a public set of RBI master directions,
a hospital's SOPs). Write ten labelled queries with spans across at least four categories, chunk naively and by
structure, and report recall at 5 for both with BM25 alone. Then write the one-paragraph permission model for it, even
if the documents are public: who would see what, where the groups come from, and what fails closed.

<details><summary>Solution</summary>

There is no single answer. A good submission has the ten queries in a file, both recall numbers with the interval, the
three worst chunks printed and explained, and a permission paragraph that names a pre-filter, document groups, per-request
resolution and the fail-closed cases. If structure-aware chunking does not beat naive on your corpus, say why: very
short documents, or documents with no structure, are the usual reasons.

</details>
