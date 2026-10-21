# Retrieval change review checklist

> Day 15 artifact. Use it on every pull request that touches chunking, the analyzers, the indexes, fusion, the
> reranker, metadata, the filter or the group source, whether a person or a coding agent wrote it. Each line is a
> yes or no; a "no" needs a written reason in the pull request.

## Permissions (any "no" blocks the merge)

- [ ] The permission filter is applied before ranking, inside the query, for every search path (lexical, dense, any
      new one), and not after results return.
- [ ] Nothing computed from unfiltered results reaches the caller: counts, snippets, highlights, facets, "did you
      mean", the drafted note, debug logs, traces, caches.
- [ ] Chunk ACLs name document groups (branch, role), never user lists; no new "all" group or wildcard.
- [ ] Groups are resolved per request from the newest snapshot; a stale snapshot, an unknown user and the service
      account all return nothing.
- [ ] Loan-file visibility still goes through Day 11's `visible_to`; the agreement test passes.
- [ ] Caches, if any, are keyed by the caller's groups (or user) as well as the query.
- [ ] The permission audit reports 0 violations.

## Data handling

- [ ] No raw PAN, Aadhaar number or other identifier reaches the index or a log; queries are redacted before logging.
- [ ] Only documents in the circular register (approved, with an owner) or the masked summaries are indexed.
- [ ] Superseded and draft documents are filtered by metadata, not by the model or the prompt.

## Quality

- [ ] Recall at 5 on the labelled queries is at or above the gate, overall and in every category; any category that
      fell is named in the pull request even if the average rose.
- [ ] The labels were not edited in the same pull request as the retrieval change (or the label change is reviewed
      separately by the eval owners).
- [ ] No synonym, fold rule or boost was added only to fix a query in the test set.
- [ ] Citations still point at text that is on the cited pages (the citation test passes).
- [ ] Telugu-script and transliterated queries were run, not only English.

## Operations

- [ ] Index build time, query latency (two searches per file opened) and index size are reported against the last
      run.
- [ ] The re-index plan for a changed chunker or analyzer is written: full rebuild, dual index, or switch-over.
