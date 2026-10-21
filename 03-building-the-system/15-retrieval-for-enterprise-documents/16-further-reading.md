# 16 · Further Reading

> Day 15 · Section 16 of 16 · [Chapter overview](README.md) · Previous: [15 · Exercises](15-exercises.md)

---

Pages marked **(read 21 Oct 2026)** were fetched while writing this chapter and the facts quoted from them were
checked against the page that day. Pages marked **(not fetched)** are well-known references cited from the course's
sources or from memory; check the current version before relying on a detail.

## Ranking

| Resource | Why read it |
|---|---|
| Gordon V. Cormack, Charles L. A. Clarke and Stefan Buettcher, *Reciprocal rank fusion outperforms Condorcet and individual rank learning methods*, SIGIR 2009: https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf (the link redirects to the author's PDF; the PDF was retrieved but not machine-readable, so the formula here is quoted from the paper as widely cited) | the RRF formula and k = 60, in four pages |
| Stephen Robertson and Hugo Zaragoza, *The probabilistic relevance framework: BM25 and beyond*, Foundations and Trends in Information Retrieval, 2009: https://doi.org/10.1561/1500000019 (not fetched) | where BM25's k1, b and idf come from, and why they work |
| OpenSearch documentation, *Score ranker processor*: https://docs.opensearch.org/latest/search-plugins/search-pipelines/score-ranker-processor/ (read 21 Oct 2026) | RRF for hybrid queries, "Introduced 2.19", `rank_constant` default 60 |

## Storage, filtering and permissions

| Resource | Why read it |
|---|---|
| pgvector README: https://github.com/pgvector/pgvector (read 21 Oct 2026; install instructions at v0.8.7) | "With approximate indexes, filtering is applied after the index is scanned"; iterative index scans (`strict_order`, `relaxed_order`, `hnsw.max_scan_tuples`); partial indexes and partitioning; hybrid search with Postgres full-text search and RRF or a cross-encoder |
| PostgreSQL 18 documentation, *Row security policies*: https://www.postgresql.org/docs/current/ddl-rowsecurity.html (read 21 Oct 2026) | default deny with no policy; owners bypass unless `FORCE ROW LEVEL SECURITY`; superusers and `BYPASSRLS` always bypass |
| SQLite, *FTS5 extension*: https://www.sqlite.org/fts5.html (not fetched) | a local full-text index with a built-in `bm25()` ranking function, for pilots on one machine |
| OpenSearch security plugin, document-level security (search the OpenSearch documentation for your version; not fetched) | enforcing a role-based filter inside the cluster |

## Text, scripts and languages

| Resource | Why read it |
|---|---|
| Python documentation, `re` module, the `\w` class: https://docs.python.org/3/library/re.html (not fetched) | why `\w` does not include combining marks, which is why Telugu is shredded |
| Unicode code chart, Telugu (U+0C00 to U+0C7F): https://www.unicode.org/charts/PDF/U0C00.pdf (not fetched) | the block the lexical analyzer keeps whole; the vowel signs and the virama |

## Patterns

| Resource | Why read it |
|---|---|
| Anthropic, *Introducing contextual retrieval* (2024): https://www.anthropic.com/news/contextual-retrieval (not fetched) | model-written context per chunk, combined with BM25 and reranking; the published variant of section 09.3's contextual headers |
| OWASP, *Top 10 for LLM Applications*: https://genai.owasp.org/llm-top-10/ (a Part 3 source) | retrieved text as an attack surface; Day 41 owns it |

## The FDE and Indian context

| Resource | Why read it |
|---|---|
| OpenAI forward deployed engineering, ZenML LLMOps database summaries: https://www.zenml.io/llmops-database/forward-deployed-engineering-bringing-enterprise-llm-applications-to-production and https://www.zenml.io/llmops-database/forward-deployed-engineering-for-enterprise-llm-adoption (Part 3 sources) | the metadata translation layer and "deterministic constraints", which is what the permission filter is |
| Reserve Bank of India, *Master Direction on Know Your Customer (KYC)*, 2016, as amended: https://www.rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=11566 (cited in Day 7; not fetched here) | the officially valid documents and the Aadhaar redaction requirement that the corpus's digest paraphrases; the Master Direction text prevails |
| The Digital Personal Data Protection Act, 2023 (India Code): https://www.indiacode.nic.in/handle/123456789/19714 (cited in Day 7; not fetched here) | why PANs are tokenised and deletions reach vectors and caches; Day 24 owns the detail |

## Inside this course

- [Day 6](../../02-discovery-and-decomposition/06-discovery-interviews/README.md): finding A1 (BRANCH_ISOLATION, ACCESS_VIA_AD_GROUPS), the view log, CHECKLIST_DRIFT, ALTERNATIVES_UNWRITTEN.
- [Day 4](../../02-discovery-and-decomposition/04-picking-the-problem/README.md) and [Day 10](../../02-discovery-and-decomposition/10-the-discovery-document/README.md): why the branch chatbot was declined (C5, decision D06).
- [Day 11](../11-the-system-around-the-model/README.md): `visible_to`, the branch groups and the signed rule constants this chapter imports.
- [Day 13](../13-prompts-as-code/README.md): page types, the page-38 lesson, untrusted text in prompts.
- [Day 14](../14-evals-first/README.md): golden sets, labelling and the Wilson interval this chapter imports.
- [Day 16](../16-integrating-with-what-exists/README.md): where the documents come from; [Day 22](../../04-deploying-into-their-world/22-identity-in-their-company/README.md): where the groups come from; [Day 24](../../04-deploying-into-their-world/24-data-residency-and-indian-law/README.md): where the index may live; [Day 41](../../07-ai-era-toolkit/41-red-teaming-your-deployment/README.md): attacks through retrieved text.

The circulars, rulebooks, digests, loan files, PANs, people's group memberships and every number about Godavari are
invented and generated by code. The RBI digests in the corpus are paraphrases written for the synthetic corpus, not
quotations; the Master Direction's own text prevails.
