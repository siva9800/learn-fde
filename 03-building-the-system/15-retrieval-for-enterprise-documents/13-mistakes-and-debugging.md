# 13 · Common Mistakes and Debugging

> Day 15 · Section 13 of 16 · [Chapter overview](README.md) · Previous: [12 · Build it with AI, and how you know it is right](12-build-with-ai-and-verification.md) · Next: [14 · Interview questions](14-interview-questions.md)

---

Each row is **symptom, likely cause, fix**, with the section that explains it.

## 13.1 Documents and chunks

| Symptom | Likely cause | Fix |
|---|---|---|
| Every query returns the same few long chunks near the top | headers and footers inside chunks; the running header's title words match everything | learn boilerplate by repetition and drop it; drop edge lines carrying the document's own number (03.2) |
| A scanned circular never matches an obvious query | OCR letter confusions ("docurnent"); hyphenation across lines; the stamp in the middle of a clause | re-join hyphenation; drop junk lines; ask the compliance head for the born-digital original (02.2, 03.2) |
| The answer row of a table is found but the analyst cannot tell what it means | a row chunk without the caption and header | every row group carries caption and header; never split a row (03.4) |
| A table answer is cited to the wrong page | pages taken from the caption line only, not the rows | record the page of every line in the block; cite the range (03.4, 07.4; exercise 2.3) |
| Telugu queries return rubbish, English ones are fine | `\w+` tokenization cuts Telugu at every vowel sign | match `[ఀ-౿]+` as one token (02.4) |
| Transliterated notes are found only when spelled exactly like the query | no folding; or folding applied to the index but not the query | fold rules on both sides, in the analyzer you control (05.2) |
| "రుజువుగా" in a document does not match "రుజువు" in a query | Telugu suffixes; exact-word matching | character n-grams for Telugu script, or a light suffix list, measured on the labelled set (02.4; exercise 3.4) |
| A circular number in the query matches every circular from that year | the analyzer split `GFL/CO/2025/027` into `gfl`, `co`, `2025`, `027` | identifier patterns before word patterns (05.2) |
| The same clause appears twice in the top three | two row groups of one table, or overlapping windows | collapse results by clause key before display (07.4) |

## 13.2 Ranking and fusion

| Symptom | Likely cause | Fix |
|---|---|---|
| Hybrid is no better than BM25 alone; recall at 1 is worse | RRF rewards agreement; answers found by only one retriever sink | rerank the fused head; deepen the rerank; weighted RRF or routing by query type (05.5 to 05.7) |
| "Hybrid" results are dominated by one retriever | raw scores added across retrievers on different scales | fuse by rank (RRF), or normalise scores per query before a weighted sum (05.5) |
| A paraphrased query is fixed at depth 50 but not at 20 | the answer sits below position 20 after fusion | set rerank depth from the eval and the latency budget (05.6) |
| The reranker made things worse | it was applied to bad chunks: long windows cover many query words | fix chunking first; rerank last (03.7) |
| A PAN or file-number query returns similar-looking but wrong files | the identifier was treated as text to be ranked | detect identifiers and filter to exact matches before ranking (05.8) |
| Recall jumped after someone added synonyms | the synonyms were written for the labelled queries | remove them; add new queries of the same shape to the next labelling round (08.5) |

## 13.3 Permissions

| Symptom | Likely cause | Fix |
|---|---|---|
| The list on screen is clean but the count says "4 of 62" | count computed before the filter | compute every count from the allowed set (06.3) |
| An analyst sees fewer than k results although her branches have many | post-filter on the top k; or an approximate vector index filtering after its scan | pre-filter; in pgvector, iterative scans, partial indexes or partitioning (06.4) |
| A debug log or trace names another branch's file | logging inside ranking, before the filter | log only returned results; audit the logs a search writes (06.3, 12.6) |
| The drafted note mentions a file the analyst cannot see | the note was drafted from unfiltered results, or the model was told to "ignore" them | draft only from results shown; never permission by prompt (06.8) |
| A transferred manager still sees the old branch after the nightly sync | user lists stored on chunks at index time; or a session cache of groups | ACLs on document groups; resolve groups per request (04.4, 06.5) |
| Everyone sees everything for an hour one morning | a fail-open default ("no groups: skip the filter") hit when the snapshot load failed | fail closed; refuse on a stale or missing snapshot (06.6) |
| Two analysts typing the same query see each other's results | a results cache keyed by query text only | key caches by the caller's groups and the query, or do not cache (06.3) |
| The compliance desk cannot find a draft circular | the draft was given a future effective date and the freshness filter hid it | approval and effectiveness are separate fields (07.2) |
| The eval says recall is high but analysts say the panel is weak | the eval runs as an all-seeing user | run each query as the user who asked it (08.3) |

## 13.4 A routine for "the panel showed the wrong thing"

When an analyst reports a bad result, work through the layers in order, and stop at the first one that is wrong:

1. **Permissions**: was every shown result one she may see, and was the snapshot fresh? (`may_see` on each result.)
   If not, this is an incident, not a quality bug; Day 27 owns the incident process.
2. **Metadata**: was the right version in force, the right type, the right product? (Look up the register entry.)
3. **Chunks**: does a chunk exist that contains the answer, whole, with its header? (Search the chunks for the span.)
4. **First stage**: is that chunk in the BM25 top 50? In the dense top 50? (Run each retriever alone.)
5. **Fusion and rerank**: where did it land after RRF, and after the reranker? (Print ranks at each stage.)
6. **Display**: was it collapsed away, or cut by k?

Write down which layer failed, add the query to the labelled set with its span, and only then fix. Most "the model is
bad" reports end at step 2 or 3.

## 13.5 Key takeaways

- Chunking and metadata decide more of retrieval quality than the embedding model; fix them first and measure.
- Lexical search wins on exact form (identifiers, PANs, transliterations); dense wins on meaning; RRF rewards
  agreement, so rerank the fused head.
- Permissions are a pre-filter on metadata, before ranking, from groups resolved per request, failing closed. Every
  count, snippet, log and note comes from allowed results only. Never permission by prompt.
- Superseded documents are filtered by the register's dates; old numbers are redirected with a notice; citations name
  the clause and the version.
- Measure retrieval alone, as the asking user, with spans, an interval and a permission audit at zero.
