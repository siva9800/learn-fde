# 05 · Hybrid Search and Reranking: BM25, Dense Vectors, Reciprocal Rank Fusion, and a Second Look

> Day 15 · Section 5 of 16 · [Chapter overview](README.md) · Previous: [04 · Metadata as a first-class index](04-metadata-as-an-index.md) · Next: [06 · Permission-aware retrieval](06-permission-aware-retrieval.md)

---

## 5.1 Two retrievers, two kinds of failure

There are two families of first-stage retriever, and they fail on different queries.

**Lexical retrieval** scores a chunk by the query's words that appear in it, weighted by how rare each word is in
the corpus. BM25 is the standard formula (search engines from Lucene to Postgres-adjacent extensions use it or a
close cousin). It is exact, fast, explainable ("it matched GFL/CO/2025/052 because that string is in the chunk"),
and blind to meaning: "earnings" does not match "income".

**Dense retrieval** turns the query and every chunk into vectors with an embedding model and scores by similarity
(cosine). It matches meaning: "proof of earnings for a shop owner purchasing a scooter" lands near "income proof for
a self-employed two-wheeler applicant". It is fuzzy on purpose, so it is weak exactly where lexical is strong:
identifiers, numbers, codes and rare words it has not seen.

The Part plan's Short says it in one line: *vector search cannot find a PAN number; keyword search can; use both.*
This section shows why, with the project's numbers, and then shows the trap in "use both".

## 5.2 BM25, inside

For a query with terms q1 to qn and a chunk D:

```text
score(D) = sum over query terms t of   idf(t) * tf(t, D) * (k1 + 1)
                                       ---------------------------------------------
                                       tf(t, D) + k1 * (1 - b + b * |D| / avgdl)

idf(t)   = ln(1 + (N - df(t) + 0.5) / (df(t) + 0.5))
```

`tf` is how often the term is in the chunk, `df` how many chunks contain it, `N` the number of chunks, `|D|` the
chunk's length and `avgdl` the average length. `k1` (1.2) controls how fast repeated terms stop adding score; `b`
(0.75) how much long chunks are penalised. The `idf` form is Lucene's, which never goes negative.
`lexical.py` implements exactly this in about 30 lines, and a test checks it against the formula on a three-chunk
index. Note where the permission filter sits: inside the scoring loop, so a chunk the caller may not see is never
scored (section 06).

What makes BM25 work on Godavari's corpus is not the formula; it is the **analyzer** that turns text into terms,
because you control it:

- **Identifiers stay whole.** `GFL/CO/2025/027`, `GF-23417`, clause numbers like `4.2` and PAN tokens are matched by
  their own patterns before ordinary words. A default analyzer splits `GFL/CO/2025/027` into `gfl`, `co`, `2025`,
  `027`, and then every 2025 circular matches the query.
- **Telugu script stays whole** (section 02.4).
- **Transliteration folds.** Lowercase Latin words pass through a handful of rules (`aa` to `a`, `ee` to `i`, `th`
  to `t`, `dh` to `d` and so on, plus a plural `s`), applied to the index and the query alike. "aadaayam", "aadayam"
  and "adayam" all become `adayam`. The folded keys look odd ("proof" becomes `pruf`); that does not matter, because
  nobody reads them and both sides are folded the same way.
- **Stopwords go.** "what", "is", "for", "the".

## 5.3 Dense retrieval, inside, and this chapter's stand-in

A real embedding model is a neural network that maps text to a vector of a few hundred to a few thousand numbers,
trained so that texts with similar meaning land close together. Two properties matter for an FDE:

1. It sees text through its own **subword tokenizer**, which you do not control. `GFL/CO/2025/027` becomes several
   pieces shared with every other circular number; a PAN token becomes hex fragments; "aadaayam" becomes whatever
   fragments its vocabulary has for unfamiliar Latin strings.
2. It matches **paraphrase**, including across scripts when the model is multilingual: "ఆదాయం" and "income" can land
   near each other.

The project must run offline, with no model download, so `dense.py` is a **stand-in, not an embedding model**, and
it is labelled that way everywhere. It hashes features into a 2,048-dimension signed vector and normalises it:

- the words as a subword model would see them (`dense_terms`: lowercased pieces; identifiers fall apart; no folding);
- **concepts** from a small hand-written table: "shop owner", "proprietor", "trader" and "business" map to one
  concept; "scooter", "bike" and "two-wheeler" to another; Telugu-script words for income, proof, address, rent and
  agreement to the same concepts as their English equivalents.

That reproduces the two properties above in a form you can read. It is not a substitute for a real model on real
data, and section 09.2 shows where a local model would plug in behind the same two methods (`embed`, `search`). The
concept table is also a trap you should notice: it is easy to "fix" a failing query by adding a word to it, which is
tuning the system to the test. The project leaves its one miss unfixed for that reason (section 08.5).

Search over the stand-in is **exact**: the query vector is compared with every allowed chunk. That matters for
permissions, because an approximate index behaves differently under a filter (section 06.4).

## 5.4 Where each wins, measured

Recall at 5 on the 40 labelled queries (section 08), by category, structure-aware chunks, no fusion:

| Category | Queries | BM25 only | Dense stand-in only | What decides it |
|---|---|---|---|---|
| identifier (circular and rulebook numbers) | 6 | 1.00 | 0.67 | the number is one exact token for BM25 and four common fragments for the dense view |
| table-row | 5 | 1.00 | 0.60 | the row's words are the query's words; the dense vector of a long row group averages six rows |
| superseded | 6 | 1.00 | 0.83 | both are filtered to the version in force; dense misses q20 ("dealer quotation valid 15 days") behind other quotation clauses |
| paraphrase | 7 | 0.57 | 1.00 | "showroom proforma", "uid copy without redaction", "papers on my mobile": no shared words |
| PAN | 3 | 1.00 | 1.00 | the PAN is a lookup filter in both (section 5.8) |
| precedent, Telugu script, transliteration, access | 13 | 1.00 | 1.00 | distinctive words on both sides in these queries |
| **all** | **40** | **0.925** | **0.875** | |

And two direct probes from the same index, as Lakshmi:

```text
GFL/CO/2025/052 | lexical [('GFL/CO/2025/052', 'header')]
GFL/CO/2025/052 | dense [('GFL/CO/2025/058', 'header'), ('GFL/CO/2025/060', 'header'), ('GFL/CO/2025/062', 'header')]

vyavasayam adayam | lexical [('GF-24072', 'summary'), ('GF-21776', 'summary'), ('GF-24576', 'summary')]
      Analyst note: Vyavasayam adayam; 2 acres.
      Analyst note: Vyavasayam adayam; 5 acres.
      Analyst note: Vyavasaayam aadaayam; 1 acres.
vyavasayam adayam | dense [('GF-24072', 'summary'), ('GF-21776', 'summary'), ('GF-21467', 'summary')]
```

The circular number: BM25 returns exactly the circular asked for; the dense view returns three other 2025 circulars,
because "gfl", "co" and "2025" are in all of them. The transliteration: both find the two notes spelled exactly like
the query; only BM25 finds the third, spelled "Vyavasaayam aadaayam", because the fold rules make the spellings one
key. You can add a fold rule in an afternoon when the analysts show you a new spelling. You cannot add one to a hosted
embedding model.

So the reasons lexical wins on circular numbers, PAN-like identifiers and Telugu transliterations are the same
reason: **you control its analyzer, and those three are problems of exact form, not meaning.** Dense wins on
paraphrase because paraphrase is a problem of meaning.

## 5.5 Reciprocal rank fusion, and the trap in "use both"

Two ranked lists need to become one. Their scores cannot be added: a BM25 score of 14.2 and a cosine of 0.31 are on
different scales, and the scale of BM25 changes with the query. **Reciprocal rank fusion** (RRF, Cormack, Clarke and
Buettcher, SIGIR 2009) uses ranks only:

```text
RRF(d) = sum over lists L of 1 / (k + rank_L(d))        k = 60, ranks start at 1
```

```python
def rrf(rankings: Sequence[Sequence[int]], k: int = RRF_K) -> list[tuple[int, float]]:
    score: dict[int, float] = {}
    best: dict[int, int] = {}
    for ranking in rankings:
        for r, doc in enumerate(ranking, start=1):
            score[doc] = score.get(doc, 0.0) + 1.0 / (k + r)
            best[doc] = min(best.get(doc, r), r)
    return sorted(score.items(), key=lambda kv: (-kv[1], best[kv[0]], kv[0]))
```

k = 60 comes from the paper and is the default `rank_constant` in OpenSearch's score-ranker processor (introduced in
OpenSearch 2.19, docs read 21 October 2026); the pgvector README recommends RRF or a cross-encoder for combining
Postgres full-text search with vector results. RRF is simple, needs no tuning and no score calibration, and it is the
right default.

Now the trap. Fused, structure-aware chunks give recall at 5 of **0.925**: no better than BM25 alone, and recall at 1
drops from 0.738 to 0.662. The paraphrase category stays at BM25's 0.57, not dense's 1.00. Why? Look at query q14,
"can we keep a customer's uid copy without redaction if they agree":

```text
q14 lexical hit rank []      (the answer is not in BM25's list at all)
q14 dense hit rank [1]       (the dense stand-in puts it first)
q14 hybrid hit rank [6]      (after fusion it is sixth, outside the top 5)
```

A document ranked first by one list and absent from the other scores 1/61 = 0.0164. A document ranked fourth by both
scores 1/64 + 1/64 = 0.0313. **RRF rewards agreement.** When one retriever is confidently right and the other has
never heard of the answer, fusion buries it under documents both retrievers found mildly relevant. That is not a
bug in RRF; it is what the formula does, and on most queries agreement is a good signal. On exactly the queries you
added dense retrieval for, it is not.

## 5.6 Reranking: a second, closer look

A **reranker** takes the query and one candidate together and scores how well that candidate answers that query. A
cross-encoder model does this by reading both in one pass, which is far more accurate than comparing two vectors made
separately, and far too slow to run over the whole corpus. So the pattern is: retrieve broadly and cheaply (BM25 plus
dense, fused, top 20 to 100), then rerank that head carefully, then take the top k.

The project's reranker is again a readable **stand-in**: for each candidate it scores the share of the query's terms
the chunk covers, the share of the query's word pairs it contains, the share of the query's concepts it shares, an
exact identifier match, and a small share of the fused score. A real cross-encoder learns all of that and more.

What the reranker fixes, measured:

| Configuration | R@1 | R@3 | R@5 | R@10 | MRR | Paraphrase R@5 |
|---|---|---|---|---|---|---|
| hybrid RRF | 0.662 | 0.900 | 0.925 | 0.950 | 0.792 | 0.57 |
| hybrid RRF + rerank top 20 | 0.738 | 0.925 | 0.950 | 0.975 | 0.850 | 0.71 |
| hybrid RRF + rerank top 50 | 0.738 | 0.950 | 0.975 | 0.975 | 0.860 | 0.86 |

**Rerank depth is a knob you set from the eval and the latency budget.** At depth 20, q16 ("a customer sent papers
to my mobile on a messaging app") is still lost: its answer sits below position 20 after fusion, so the reranker never
sees it. At depth 50 it is recovered. A real cross-encoder costs a few milliseconds to tens of milliseconds per
candidate on a CPU, so 50 candidates for each of two searches per file opened is a real number to put in the latency
budget, and section 10 does.

Remember section 03.7: the same reranker made naive chunks worse (0.825 to 0.750). Reranking amplifies whatever the
chunks are. It is the last step, not the fix.

## 5.7 Alternatives to plain RRF

You will meet these; know what each is for:

| Technique | What it does | When to reach for it |
|---|---|---|
| Weighted RRF | multiply each list's contribution by a weight | when the eval shows one retriever is more reliable for this corpus |
| Score normalisation (min-max, z-score) then weighted sum | puts scores on one scale per query | when you have a calibrated dense model and want to use score gaps, not just ranks |
| Query routing | send identifier-shaped queries to lexical only, or boost it | when queries are clearly typed (a PAN, a circular number), as at Godavari |
| Learned sparse retrieval (SPLADE-style) | a model that outputs weighted terms, indexed like BM25 | when you want lexical exactness with some learned expansion |
| Late interaction (ColBERT-style) | token-level vectors compared at query time | high quality, higher storage; rarely the first thing an FDE ships |

None of these changes the order of work: chunks first, analyzer second, fusion third, reranker fourth, and the eval
deciding each step.

## 5.8 Identifiers are lookups, not similarity

One design decision from the project generalises: **when the query contains an identifier, treat it as a filter.**
If Lakshmi types a PAN, she wants the files with that PAN, not files similar to a sentence containing a PAN. The
service turns the PAN into its keyed token (section 06.6 explains why the index never holds a raw PAN), restricts the
candidates to chunks carrying that token, and only then ranks:

```text
  Lakshmi, a repeat customer's PAN: 2 shown, 2 matches counted
    1. GF-24620 · Vijayawada-Benz Circle (VJB03) · decided 08 Jul 2026
    2. GF-22015 · Guntur (GNT04) · decided 21 Jan 2025
  Lakshmi, a PAN whose only file is in Warangal: 0 shown, 0 matches counted
    notice: no file you can see matches this PAN
```

Before this change the second query returned three unrelated files from her own region (GF-24620, GF-22015 and
GF-21467) that matched on "prior" and on the word "PAN", which every summary's "PAN token:" line contains. That is the dense-only failure in its purest form, and it would have looked like an answer. The same
principle applies to file numbers and circular numbers: exact first, ranking second. Notice also the wording of the
notice: "no file you can see", never "this PAN has a file in another branch".
