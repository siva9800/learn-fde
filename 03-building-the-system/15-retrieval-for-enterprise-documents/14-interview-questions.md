# 14 · Interview Questions

> Day 15 · Section 14 of 16 · [Chapter overview](README.md) · Previous: [13 · Mistakes and debugging](13-mistakes-and-debugging.md) · Next: [15 · Exercises](15-exercises.md)

---

Sixteen questions in the forms they take in FDE loops: the enterprise system-design round ("design retrieval over a
bank's documents"), the practical coding round, and the follow-ups a hiring manager asks about a past deployment.
Answer out loud first, then compare. Section numbers point to the full explanation.

## Design

**Q1. Design document retrieval for a lender's credit analysts. Where do you start?**

With the documents and the permissions, not the model. I would ask what the documents are (policy circulars with
versions, past loan files), who may see what (at a lender, branch visibility from directory groups), and what the
analyst does with the answer (decides a file, so citations matter). Then: clean and chunk by structure with a clause
and page on every chunk; metadata from the register (type, product, effective dates, superseded-by, approval, branch,
ACL); BM25 plus a dense retriever fused with RRF and reranked; a permission pre-filter from groups resolved per
request; supersession by date; and recall at k on labelled queries run as the asking user, plus a permission audit at
zero, before any model writes a sentence. I would put it inside the screen the analysts already use, not in a new
chatbot. (Sections 01 to 08.)

**Q2. Why not just use a vector database?**

Because it is one retriever, and the hard queries at a lender are not semantic. Circular numbers, PANs and file numbers
are exact strings that a subword embedding model splits into common fragments; transliterated Telugu is spelled three
ways and the model has seen little of it; the right version of a circular is a date question; permissions are a filter
question. Measured on our labelled set, BM25 alone got every identifier query and the dense retriever a third wrong;
the dense retriever won on paraphrase. You need both, plus metadata. (05.4.)

**Q3. Pre-filter or post-filter for permissions, and why does it matter if the list on screen is the same?**

Pre-filter: decide the allowed set from metadata first and let the ranking code touch nothing else. A post-filter shows
a clean list and leaks through everything computed before the filter: the count ("showing 4 of 62"), facets, snippets in
debug logs, a model-drafted summary, caches keyed by query, and fewer than k results, which itself tells the user
something exists. In our project the post-filter's note named another branch's file, its dealer and its on-road price.
(06.2, 06.3.)

**Q4. The CISO says permissions must be resolved "at the moment of the query". How do you implement that without
re-indexing when someone changes branch?**

Store document groups on chunks, never user lists: a Guntur file carries the Guntur branch group. Resolve the caller's
groups per request from the newest directory snapshot, and fail closed if it is stale. When HR moves someone, their
groups change in the next sync and the index does not change at all. I would also tell the CISO what this does not fix:
the directory's own one-night lag is hers, and the retrieval layer matches it exactly. (04.4, 06.5.)

**Q5. How do you handle superseded documents?**

As metadata, not ranking: effective-from, effective-to and superseded-by from the owner's register, and a filter on
"in force on the as-of date", which defaults to today and can be set to a past decision date for audits. A query that
quotes an old number is redirected to the current one with a visible notice, which also tells the analyst her printed
copy is stale. I would not use date decay in ranking: an old circular still in force is valid, and a new one on another
topic is not more relevant. (07.1 to 07.3.)

**Q6. Where is retrieval quality usually lost?**

In chunking and extraction. Headers and footers in every chunk, tables cut from their headers, OCR noise, a page break
in the middle of a rule. In our project, the same retrievers on the same queries went from recall at 5 of 0.825 to 0.925
just by chunking by structure and cleaning, and a reranker on the naive chunks made them worse. (03.1, 03.7.)

**Q7. How do you chunk a table?**

Keep it whole if it is small. If it is large, split into row groups and put the caption and the header row on every
group, never split a row, drop a header repeated after a page break, and cite the page range. A row without its header
is unreadable to a person and weakly matched by a retriever. (03.4.)

**Q8. Explain reciprocal rank fusion. When does it fail?**

Score each document by the sum over lists of 1 / (k + rank), k = 60, ranks from 1. It needs no score calibration. It
rewards agreement: a document ranked first by one retriever and absent from the other scores less than one ranked fourth
by both. So it can bury exactly the paraphrase answers you added dense retrieval for. A reranker over the fused head
fixes most of that; depth matters, and you set it from the eval. (05.5, 05.6.)

## Evaluation

**Q9. How do you evaluate retrieval on its own?**

A labelled set of queries with known answers, run through retrieval only, scored with recall at k (is the answer on the
screen?) and MRR (how high?). Label answer spans rather than chunk IDs so the labels survive re-chunking; make
superseded-version answers impossible to score; run each query as the user who asked it; report per category and with
an interval; and run a permission audit next to it with a target of exactly zero. (08.2 to 08.7.)

**Q10. Your recall at 5 is 97.5 percent on 40 queries. What do you tell the COO?**

That 39 of 40 is consistent with a true rate anywhere from about 87 to 100 percent, that it is synthetic data with
planted answers, and that the number to believe is the first run on a few hundred real lookups labelled by the
analysts. Forty queries are good for comparing configurations and finding broken categories, not for promising a
percentage. (08.6.)

**Q11. A test query fails. A colleague adds a synonym and it passes. Problem?**

Yes: that is tuning to the test, the retrieval version of training on the test split. The number goes up and stops
meaning anything. Keep the miss, report it, and add new queries of the same shape to the next labelling round so a real
fix is measured on queries it was not built from. (08.5.)

## Practical and on the job

**Q12. Write a tokenizer for Telugu and English documents. What goes wrong with `\w+`?**

In Python, `\w` does not match Telugu vowel signs (they are combining marks), so `\w+` cuts every Telugu word into
fragments. Match the Telugu block, `[ఀ-౿]+`, as one token, match identifiers (circular numbers, file numbers,
PAN tokens) before ordinary words, and fold Latin transliteration variants on both index and query. (02.4, 05.2.)

**Q13. How do you let analysts search by PAN without putting PANs in the index?**

Index a keyed token, an HMAC of the PAN with a key in the customer's KMS; tokenise the PAN in the query the same way;
treat it as an exact filter before ranking; redact it in logs. A plain hash is not enough because the PAN space is
small and structured. And the "not found" message must be "no file you can see", never a hint that a file exists in
another branch. (05.8, 06.6.)

**Q14. Why not tell the model to ignore documents the user cannot see?**

Because it has already read them. Whether it repeats them depends on phrasing and luck; it cannot be audited; and a
document can carry instructions of its own. Access control is deterministic code before ranking, and the model only
sees what the caller may see. (06.8.)

**Q15. Tell me about a time retrieval leaked something, or nearly did.** (Use the STAR shape, in the first person.)

"At a lender, the first version of our past-files lookup ranked everything and filtered the top five. The list looked
right in every demo. I wrote a test that searched as a Vijayawada analyst for a case whose best match was a Hyderabad
file, and read every line the search wrote. The count included the hidden file, the debug log had its number, and the
summary named its dealer. I moved the filter in front of ranking, made counts and notes come only from allowed results,
and added a permission audit over every user and every labelled query to CI with a target of zero. I showed the CISO
both runs side by side; she used the audit result in her review." (06.3, 08.7.)

**Q16. The customer has 300 branches; a branch user may see one. What breaks at scale?**

Filter selectivity. A user who may see 0.3 percent of the index is the worst case for approximate vector search, where
filtering after the index scan returns far fewer than k results. Use the engine's filtered or iterative scan modes,
partial indexes per region or branch, or partitioning, and test recall for the most restricted user, not the average
one. (06.4, 10.3.)

## Quick-fire round

- *k in RRF?* 60, from the 2009 paper; OpenSearch's default rank constant.
- *BM25's k1 and b?* About 1.2 and 0.75: term saturation and length normalisation.
- *What is a contextual chunk header?* Title and section prepended to the indexed text, not shown as the clause.
- *Where do effective dates come from?* The owner's register, never the PDF text.
- *Permission audit target?* Zero.
- *What does a stale group snapshot do?* Refuses the request.
- *Is this the branch chatbot?* No: a panel inside the review queue, with citations, for analysts; the chatbot stays on
  the will-not-do list.
