# 09 · Advanced and 2026 Patterns, and What Is Hype

> Day 15 · Section 9 of 16 · [Chapter overview](README.md) · Previous: [08 · Evaluating retrieval](08-evaluating-retrieval.md) · Next: [10 · Production concerns](10-production-concerns.md)

---

Tool names here are as of October 2026 and will date; the method in sections 03 to 08 will not. Every option below is
named vendor-neutrally: what it is, when it fits, what to check. The project itself uses none of them, so that it runs
offline on any laptop.

## 9.1 Where the index lives: three vendor-neutral shapes

| Shape | Examples (October 2026) | Fits when | Check |
|---|---|---|---|
| A database the customer already runs, with vector and full-text search | PostgreSQL with the pgvector extension (0.8.7 per its README) and built-in full-text search; row-level security for permissions | the customer has a DBA team and Postgres on-prem or in AWS Mumbai; corpus in the hundreds of thousands of chunks | approximate-index filtering (iterative scans, partial indexes, section 06.4); who owns upgrades |
| A search engine the customer already runs | OpenSearch with BM25, k-NN, hybrid queries and the score-ranker processor's RRF (from 2.19); the security plugin's document-level security | the customer already has a search cluster and a team that operates it | the filter is in the query's filter context; the plugin's version and configuration |
| A local, embedded option | SQLite's FTS5 (which has a built-in `bm25()` ranking function) plus an in-process vector search; or this chapter's pure-Python indexes | the pilot: one machine in the Hyderabad building, a few thousand chunks, no new infrastructure | it does not scale to many writers; backups; it is a pilot shape, said out loud |

At Godavari the pilot runs on a machine in the Hyderabad building under the CISO's staged approval, and then moves
with everything else to AWS Mumbai in January. A local index for the pilot and the customer's own Postgres for
production is a reasonable path; where the index may live, and whether masked summaries may leave the read replica at
all, is [Day 24](../../04-deploying-into-their-world/24-data-residency-and-indian-law/README.md)'s and Day 16's
decision (RQ2 in the design note). Do not introduce a new managed vector database into a customer whose CISO took
eight weeks to review one vendor; the security review is part of the cost.

## 9.2 A real embedding model, offline

The dense stand-in has two methods, `embed(text)` and `search(query, allowed, k)`. A real model replaces `embed`.
For Godavari the constraints are: runs inside India (no customer text to a foreign endpoint, Day 24), ideally inside
the building for the pilot, handles Telugu script, and is licensed for commercial use. That points to an open
multilingual embedding model served locally (for example from the multilingual-e5 or BGE-M3 families; check the
current versions, licences and sizes yourself; they were not tested for this chapter). Choose by running the 40
queries plus the analysts' real ones, per category, against the stand-in's numbers. Expect the paraphrase and Telugu
categories to improve and the identifier category to stay where lexical keeps it. Expect transliterated Telugu to stay
weak, which is why the fold rules stay in the lexical analyzer whatever model you choose.

Fine-tuning an embedding model on Godavari's vocabulary is possible and almost never the first step. It needs labelled
pairs you do not yet have, and the eval tells you whether the off-the-shelf model is the bottleneck at all.

## 9.3 Patterns worth knowing

- **Layout-aware extraction.** Parsers that return headings, reading order and table cells from a PDF (open-source
  libraries and cloud document-AI services both exist) make structure-first chunking easier. Check their output on
  the customer's ten worst pages by eye before trusting them; scanned 2024 circulars are where they differ most.
- **Contextual chunk headers, and model-written context.** This chapter prepends the document title and section
  heading to each chunk before indexing. A published variant asks a model to write a sentence of context for every
  chunk ("This clause is from the 2025 two-wheeler income circular and covers self-employed applicants") and indexes
  that too. It helps when headings are weak; it costs a model call per chunk at indexing time, and the written context
  must be treated as system text, never shown as if Godavari wrote it.
- **Parent and child chunks.** Index small chunks for precision, return the parent section for context. Query q16
  ("papers on my mobile") is a candidate: the purpose clause matches the question and the rule is in the next
  section's clause.
- **Query rewriting.** A small model expands "oldest borrower for a bike loan" into "maximum age two-wheeler applicant".
  It would fix q17. It also adds a model call to every search, and its rewrites must be logged and evaluated like any
  other prompt (Day 13).
- **Agentic retrieval.** A model issues several searches as tool calls, reads, and searches again. Useful for multi-step
  questions; slower and harder to evaluate. The permission filter must sit inside the search tool, so the agent can
  only ever retrieve what the analyst could; [Day 17](../17-agents-and-workflows/README.md) builds tools that way.

## 9.4 Long context: does it end retrieval?

Models with very long context windows are common in 2026, and a fair question is: why not put all 61 circulars in the
prompt? For the **policy half alone**, at Godavari's size, that is a legitimate design to measure, not dismiss: the
current circulars are a few dozen pages. Measure it against retrieval on the same labelled queries before deciding.

The reasons it does not replace retrieval here are specific, not fashionable:

1. **Permissions.** The precedent half cannot be "put everything in the prompt": the analyst may see a sixth of the
   files, and the forbidden five-sixths cannot be in the context at all (section 06.8).
2. **Freshness and citations.** The superseded versions must not be in the context, which means filtering by metadata
   anyway, and a citation to clause 4.2 needs the clause boundaries the chunker found.
3. **Cost and latency per file opened.** Two searches cost milliseconds; a long-context call costs a model call with
   tens of thousands of input tokens every time a file is opened, inside Day 12's 12-rupee-per-file ceiling.
4. **Position effects.** Day 13 showed what happens on page 38 of a long input. More context is not the same as more
   attention.

## 9.5 What is hype

| Claim | What is true |
|---|---|
| "A vector database solves enterprise search." | It is one retriever. Identifiers, codes, transliterations and versions need lexical search and metadata; permissions need a filter in the right place. |
| "Better embeddings are the fix." | At Godavari chunking moved recall at 5 by 10 points with no model change; the embedding was the last thing worth changing. Measure first. |
| "Tell the model to ignore what the user cannot see." | That is not access control (section 06.8). |
| "Hybrid search is always better than either alone." | Fusion rewards agreement; measured here, RRF alone equalled BM25 alone at 5 and was worse at 1 (section 05.5). |
| "GraphRAG for everything." | Knowledge graphs help when questions follow relationships across many documents; policy lookup by clause and precedent by similarity do not. |
| "Semantic caching cuts cost." | A cache keyed by query meaning serves one user's results to another unless the key includes the caller's groups. |
| "Long context ends retrieval." | Not while permissions, freshness and citations exist (section 9.4). |
