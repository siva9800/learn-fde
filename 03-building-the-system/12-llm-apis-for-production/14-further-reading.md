# 14 · Further Reading

> Day 12 · Section 14 of 14 · [Chapter overview](README.md) · Previous: [13 · Exercises](13-exercises.md)

---

Vendor pages change often. Those marked "read 21 October 2026" were fetched for this chapter and the
figures quoted from them are as of that date.

## Structured outputs and tool use

| Resource | Why read it |
|---|---|
| Anthropic, *Structured outputs*: https://platform.claude.com/docs/en/build-with-claude/structured-outputs (read 21 October 2026) | `output_config.format`, strict tool use, the supported and unsupported schema keywords, grammar compilation and its 24-hour cache, the refusal and `max_tokens` exceptions |
| OpenAI, *Structured outputs*: https://developers.openai.com/api/docs/guides/structured-outputs (read 21 October 2026; formerly at platform.openai.com/docs/guides/structured-outputs, which the Part file cites and which now redirects) | `text.format` with `strict: true`, the `refusal` field, first-request schema latency |
| Anthropic, *Tool use overview*: https://docs.claude.com/en/docs/agents-and-tools/tool-use/overview (cited by the Part file; not fetched for this chapter) | tool definitions, the request-response loop, parallel calls, `is_error` results |
| Anthropic, *Building effective agents*: https://www.anthropic.com/research/building-effective-agents (cited by the Part file; not fetched) | workflows versus agents: why the extraction pipeline here is a workflow (Day 17 builds on it) |

## Errors, retries and rate limits

| Resource | Why read it |
|---|---|
| Anthropic, *Errors*: https://platform.claude.com/docs/en/api/errors (read 21 October 2026) | the status codes, 529 overload, request ids, mid-stream errors, long requests and why to stream or batch them |
| Anthropic, *Rate limits*: https://platform.claude.com/docs/en/api/rate-limits (read 21 October 2026) | token bucket, RPM, ITPM and OTPM, cache-aware input limits, `retry-after` and the rate-limit headers, the spend-cap 429, acceleration limits |
| Marc Brooker, *Exponential backoff and jitter*, AWS Architecture Blog (2015): https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/ (not fetched for this chapter) | the simulation behind "full jitter" |
| Stripe API reference, *Idempotent requests*: https://docs.stripe.com/api/idempotent_requests (cited by the Part file; not fetched) | the idempotency-key pattern for writes, which Day 17 applies to the core system |
| Martin Fowler, *CircuitBreaker* (2014): https://martinfowler.com/bliki/CircuitBreaker.html (not fetched for this chapter) | the pattern's origin and its three states |

## Cost, caching and batch

| Resource | Why read it |
|---|---|
| Anthropic, *Pricing*: https://platform.claude.com/docs/en/about-claude/pricing (read 21 October 2026) | per-model prices, cache write and read multipliers, batch at 50 percent, `inference_geo` and regional premiums |
| OpenAI, *Pricing*: https://developers.openai.com/api/docs/pricing (read 21 October 2026; openai.com/api/pricing returned 403 to the fetch) | standard and batch prices, cached input, the 10 percent regional-processing uplift |
| Anthropic, *Batch processing*: https://platform.claude.com/docs/en/build-with-claude/batch-processing (read 21 October 2026) | limits, the 24-hour expiry, unordered results keyed by your ID, the 1-hour cache for batches |
| Anthropic, *PDF support*: https://platform.claude.com/docs/en/build-with-claude/pdf-support (read 21 October 2026) | the 1,500 to 3,000 tokens per page estimate, page and size limits |

## Residency and model routes (Day 24 owns the subject)

| Resource | Why read it |
|---|---|
| Anthropic, *Claude in Amazon Bedrock*: https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock (read 21 October 2026) | regions and endpoint types (Mumbai and Hyderabad listed as global only), features not supported on Bedrock, including Message Batches |
| AWS What's New, *Amazon Bedrock now supports OpenAI models in India* (18 August 2026): https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-bedrock-openai-india-v1/ (read 21 October 2026) | GPT-5.6 Terra and Luna with India Geo cross-Region inference in Mumbai and Hyderabad |
| ecorpit, *OpenAI per-request regional processing, India storage only* (August 2026): https://ecorpit.com/openai-per-request-regional-processing-india-storage-only-2026/ (third-party; seen in search results only, not fetched) | a third-party reading of OpenAI's residency table; verify against OpenAI's own page before relying on it |

## Inside this course

- [Day 11](../11-the-system-around-the-model/README.md): the eight boxes, the deterministic-versus-LLM split, the `ExtractionModel` seam this chapter implements.
- [Day 9](../../02-discovery-and-decomposition/09-success-metrics-and-business-case/README.md): the 26 lakh cloud line the per-file budget is cut from.
- [Day 13](../13-prompts-as-code/README.md): the prompt inside the call, versioned.
- [Day 14](../14-evals-first/README.md): the golden set that decides thresholds and model swaps.
- [Day 16](../16-integrating-with-what-exists/README.md): tools that wrap the SOAP API and the SFTP drop.
- [Day 17](../17-agents-and-workflows/README.md): tool loops as state machines; idempotent writes.
- [Day 19](../19-observability-for-ai-systems/README.md): cost per call traced, the cost-per-file dashboard.
- [Day 24](../../04-deploying-into-their-world/24-data-residency-and-indian-law/README.md): residency and model choice.

The Godavari files, names, PANs and amounts are synthetic and generated by `code/godavari_llm/synthetic.py`.
The fake provider's rates are knobs, not measurements of any vendor.
