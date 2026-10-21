# 10 · Production Concerns: Latency, Cost, Scale, Re-indexing, Security and Monitoring

> Day 15 · Section 10 of 16 · [Chapter overview](README.md) · Previous: [09 · Advanced and 2026 patterns](09-advanced-and-2026-patterns.md) · Next: [11 · Project: the Godavari retrieval service](11-project-the-godavari-retrieval-service.md)

---

## 10.1 Latency: two searches per file opened

The panel runs two searches each time an analyst opens a file (policy and precedent). In the project, on a laptop,
both together take about 11 milliseconds over 635 chunks, and building both indexes takes about 0.1 seconds. Those
numbers are for a toy. The budget that matters is the review screen's: the panel must fill before the analyst has read
the first extracted field, a second or two at most, or she stops looking at it. Where the time goes in production:

| Step | Rough cost | Lever |
|---|---|---|
| permission resolution | a lookup in the in-memory snapshot | load the snapshot once per night; never call the directory per search |
| lexical and dense first stage | milliseconds in a tuned engine | approximate indexes with iterative scans (section 06.4); filter selectivity |
| embedding the query | milliseconds to tens of milliseconds on a CPU for a local model | one embedding shared by both searches |
| reranking the top 50 | the largest cost with a real cross-encoder: 50 pairs per search | rerank depth from the eval (20 cost 2.5 points of recall at 5 here); batch the pairs; a GPU if the CISO's environment has one |
| the drafted note | a model call, hundreds of milliseconds to seconds | draft it lazily, when the analyst expands the panel, not on every open |

## 10.2 Cost

Retrieval itself is cheap: no per-query fee for self-hosted search, a few CPU-milliseconds per search. The costs
that matter are indexing (embedding every chunk once, and again when the model changes), a reranker on the critical
path, and the note, if a model drafts it. At Godavari's volume (about 2,400 applications a month, so a few thousand
file opens a month across 40 analysts), a model-drafted note on every open is still small against Day 12's
12-rupee-per-file ceiling, but it is a line in the ledger like every other model call, and it should only run when the
analyst wants it.

## 10.3 Scale

The pilot corpus (a few hundred circulars, a few thousand summaries) fits in memory on one machine. Production at 300
branches means summaries for every decided file, growing by about 2,400 a month, plus, later, the bundles' pages. That
is still modest for Postgres or OpenSearch. The thing that scales badly is not the data; it is **filter selectivity**:
a branch credit officer who may see one branch in 300 is searching a third of a percent of the index. In an
approximate vector index that is exactly the "fewer than k" case (section 06.4), so plan partial indexes,
partitioning by region, or iterative scans, and test recall for the most restricted user, not the average one.

## 10.4 Re-indexing

Every change to the chunker, the analyzer, the fold rules or the embedding model means re-indexing everything. Plan it:

- **Version the index.** The chunker version, the analyzer version and the embedding model are recorded with the
  index, the way Day 13 records a prompt with its model snapshot. A citation from last month must still resolve.
- **Build beside, switch, keep the old one.** Build the new index alongside the live one, run the eval and the
  permission audit against it, switch the panel over, and keep the old index until the new one has a clean week.
- **Incremental updates for content, full rebuilds for logic.** A new circular or a new decision summary is an
  insert. A supersession is a metadata update on the old version (its `effective_to` and `superseded_by`), not a
  delete: the old version must stay retrievable "as of" past dates for audits.
- **Deletions are real.** If a document must be removed (a summary indexed in error, a customer's data-erasure request
  under the DPDP Act, [Day 24](../../04-deploying-into-their-world/24-data-residency-and-indian-law/README.md)), remove
  it from the text index, the vectors, any cache and the backups policy; vectors of a document are that document's
  data.

## 10.5 Security, beyond the filter

- **The service account holds no groups**, and the retrieval service acts with the analyst's groups for every
  request (finding A1). It cannot be used to browse.
- **Logs carry identifiers, never content.** The view log stores user, time, snapshot, the query with PANs redacted,
  and document numbers shown. Debug logs follow the same rule: chunk IDs of returned results only. Retention is seven
  years for view records (Day 6, finding A6; circular S-RETENTION in the corpus).
- **No raw PAN in the index**, a keyed token instead; the key in the customer's KMS ([Day 25](../../04-deploying-into-their-world/25-network-secrets-and-egress/README.md)).
- **Retrieved text is untrusted data.** A circular or a note could carry instructions. When a model reads retrieved
  passages, they are wrapped as data, the way Day 13 wraps customer pages; the attacks are Day 41's.
- **The security questionnaire.** Section "access control in retrieval" of [Day 23](../../04-deploying-into-their-world/23-security-review-and-procurement/README.md)'s
  questionnaire gets the design note's section 3 and the audit's result, as a diagram and a number.

## 10.6 Monitoring

What to watch once the panel is in front of analysts ([Day 19](../19-observability-for-ai-systems/README.md) owns the
dashboards and traces):

| Signal | Why |
|---|---|
| a retrieval span in every trace, with result count, top score and filter selectivity | "why did the panel show nothing for this file" in one query |
| panel use: opened, expanded, clause clicked, past file clicked | adoption, and whether it reduces Bhavani's "send back to be safe" |
| zero-result rate by user and by branch | a sync failure or a metadata hole shows up as one branch suddenly finding nothing |
| superseded-number notices per week | how many old printed copies are still in use; a report for the compliance head |
| snapshot age at query time; refusals for staleness | the group sync is healthy |
| the permission audit, nightly, against the live index with the newest snapshot | permissions are the one thing that must never regress silently |
| the 40-query recall at 5, nightly, and on every index rebuild | quality drift after content changes |

The most useful signal is the analysts' own: a "this did not help" button on the panel, linked to the trace, so that a
miss becomes a labelled query for the next eval round (Day 18 and Day 19 do this for extraction).
