# 12 · Build It With AI, and How You Know It Is Right

> Day 15 · Section 12 of 16 · [Chapter overview](README.md) · Previous: [11 · Project: the Godavari retrieval service](11-project-the-godavari-retrieval-service.md) · Next: [13 · Mistakes and debugging](13-mistakes-and-debugging.md)

---

## 12.1 What a coding agent is good at here, and where it is dangerous

Retrieval code is a good fit for a coding agent: BM25, RRF, a chunker, a test harness are well known, and an agent
writes them quickly and mostly correctly. It is also where an agent's defaults are most dangerous, because the defaults
come from tutorials, and tutorials have one user, clean Markdown, no versions and no permissions. The agent will build
the tutorial unless the context says otherwise. Building mode, in the course's terms: the agent drafts, you review,
and you own the result.

## 12.2 The context to give it

Give the agent files, not a description. At minimum:

| Give it | Why |
|---|---|
| Day 6's finding A1 verbatim (`02-discovery-and-decomposition/06-discovery-interviews/worksheet/godavari-discovery-synthesis.md`) | the rule in the customer's words, including "at the moment of the query" and "no all-branches group" |
| Day 11's `intake/reference.py` and `intake/routing.py` paths, with "import by path, never copy" | so it reuses `visible_to` and the group names instead of inventing its own |
| three real (here: synthetic) extracted pages, including the income table across a page break and a scanned page with the stamp | so it sees headers, footers, junk and split tables before it writes a chunker |
| the register fields (section 04.2) and the statement that metadata comes from the register, not the text | so it does not parse dates out of PDFs |
| ten labelled queries with spans, including a PAN, a circular number, a Telugu-script query and a transliterated one | so the eval is in the first draft, not the last |
| the non-negotiables, written as a list (below) | so they are checked against, not remembered |

## 12.3 A strong prompt

```text
You are working in learn-fde/03-building-the-system/15-retrieval-for-enterprise-documents/code/.
Build a standard-library Python package, godavari_retrieval, for the analysts' policy-and-precedent panel
inside the review queue (NOT a chatbot; no free conversation).

Read first: the Day 6 finding A1 file, Day 11's intake/reference.py and intake/routing.py (import them by path
via a small day11.py; never copy them), and the three sample pages in data/sample-pages-*.txt.

Non-negotiables:
1. Permissions are a pre-filter: compute the allowed chunk set from metadata BEFORE any scoring, pass it into
   BM25 and dense search, and compute every count, snippet, log line and drafted note only from allowed results.
2. Chunk ACLs hold document groups (branch group from BRANCH_AD_GROUP, role groups), never user names.
3. Resolve the caller's groups per request from the newest snapshot JSON; refuse if older than 36 hours; unknown
   user, empty groups and the service account see nothing. Loan files use Day 11's visible_to.
4. No raw PAN in the index or logs: index an HMAC token; tokenise PANs in queries; redact in logs.
5. Only versions in force on as_of are candidates; a superseded circular number in a query is redirected with
   a notice. Drafts are visible only to GF-ROLE-COMPLIANCE.
6. Chunk by structure (clauses, tables with caption and header on every row group, page ranges); fixed windows
   only as a fallback. Learn headers and footers by repetition.
7. Lexical analyzer: keep circular numbers, file numbers, clause numbers and PAN tokens whole; keep Telugu
   script [ఀ-౿]+ whole; fold transliteration variants. Fuse BM25 and dense with RRF (k = 60).

Deliver with pytest tests: a permission audit over every user x every labelled query with zero violations; a
naive post-filter variant and a test proving it leaks through the count, the debug log and the note while the
pre-filter does not; recall at 1/3/5/10 on the labelled queries run AS THE ASKING USER. Show me real output.
Do not add synonyms or boosts to fix individual labelled queries.
```

## 12.4 What the agent typically gets right

BM25 (usually with the right formula, sometimes with the negative-idf variant), cosine similarity, a working RRF,
dataclasses with type hints, a reasonable test layout, and a chunker that splits on numbered headings when you show it
numbered headings. Given the prompt above, most of the project's structure comes back in one or two passes.

## 12.5 The mistakes it makes for this concept

These are specific to retrieval with permissions, and the AI draft in `code/exercises/ai_draft_retrieval.py` contains
most of them, deliberately, for exercise 3.1:

1. **Post-filtering.** Even when asked for a pre-filter, a first draft often ranks everything and filters the top k,
   because that is how most examples are written. Check where the filter line is, not what the docstring says.
2. **Counts and notes from unfiltered results.** The list is filtered; `total`, the facet counts and the LLM summary
   are computed from `hits` before the filter.
3. **User lists in the index.** "Precompute allowed users per chunk for speed" looks like an optimisation and is the
   week-8 re-index Day 6 warned about.
4. **Fail open.** `if not groups: return all` "for admins", or "if the user is not found, use default groups".
5. **Permission by prompt.** A system prompt telling the model to ignore other branches' documents.
6. **A cache keyed by query only.** Shared across users.
7. **`\w+` tokenization.** Telugu shredded, `GFL/CO/2025/027` split into four common tokens.
8. **Versions by "latest issue date".** Picks the draft, or ignores that an old file needs the old rule; no
   supersession notice.
9. **Scores added across retrievers** and called hybrid, instead of rank fusion.
10. **Raw query in logs**, PAN included.
11. **An eval run as an all-seeing user**, and recall "at 5" computed over the top 10.
12. **Synonyms added until the test passes.** Ask "which of these entries did you add because a labelled query
    failed?" and remove them.

## 12.6 How do you know it is right?

Whether you or an agent wrote it, check in this order. Each check has a number or a yes, not an impression.

**1. Read the filter's position.** In every search path, find the line that applies permissions. It must come before
any scoring call, and nothing computed before it may reach the response. This is a two-minute read and the most
important review in the chapter.

**2. Run the permission audit with zero tolerance.** Every user in the snapshot, every labelled query, both scopes,
top 10. Zero violations. Then add a user with no groups, an unknown user and the service account, and confirm they get
nothing. Then swap in the second snapshot and confirm the transferred user's results move without re-indexing.

**3. Run the leak test against the rejected design.** Keep the naive post-filter in the codebase as a test fixture
and assert that it leaks (through the count, the log, the note). If a refactor makes the leak test fail, either the
fixture broke or your test of the real service is no longer testing anything.

**4. Look at chunks, by eye.** Print the chunks of the three worst documents: the scanned one, the one with the split
table, the mixed-language one. No footer, no stamp, no orphan row, a clause and a page range on each. Ten minutes.

**5. Check the labels before the system.** Every span findable in some in-force chunk; superseded spans absent from
old versions; precedent labels complete (by construction here, by pooling with real data).

**6. Compare against baselines, per category.** BM25 alone, dense alone, naive chunks. The final configuration should
beat each overall, and you should be able to say why each category moved. A category that got worse while the average
rose is a finding, not a footnote.

**7. Report the interval.** 39 of 40 is 0.87 to 1.00. Say that, not "97.5 percent".

**8. Check citations mechanically.** The cited text is on the cited pages of the cited version.

**9. Read the logs a search writes.** Run one search as Lakshmi with a Kukatpally file as the best match and read
every line the system wrote, including debug and trace output. The Kukatpally file number must not be there.

## 12.7 Review checklist

The full checklist for every retrieval pull request is `worksheet/retrieval-review-checklist.md`. The short version:

- [ ] Permission filter before ranking in every search path; nothing from unfiltered results in any output.
- [ ] ACLs are document groups; groups resolved per request; stale, unknown and service-account callers see nothing.
- [ ] Day 11's `visible_to` is the branch rule; no copy of it.
- [ ] No raw PAN in index or logs.
- [ ] Only versions in force; drafts for compliance only; old numbers redirected with a notice.
- [ ] Structure-first chunks with clause and page range; tables whole or with caption and header per group.
- [ ] Identifiers and Telugu whole in the lexical analyzer.
- [ ] Recall at 5 at or above the gate overall and per category, run as the asking user; permission audit at zero.
- [ ] No synonym or boost added to pass a labelled query; labels not edited in the same pull request.
