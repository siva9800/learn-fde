# 16 · Further Reading

> Day 17 · Section 16 of 16 · [Chapter overview](README.md) · Previous: [15 · Exercises](15-exercises.md)

---

Read on 21 October 2026 unless marked. Library documentation changes; the dates say which version these notes
describe.

## The distinction, and agent design

| Source | Why read it |
|---|---|
| Anthropic, *Building effective agents* (Erik S. and Barry Zhang, 19 December 2024): https://www.anthropic.com/research/building-effective-agents | the workflows-versus-agents definitions quoted in section 02; the five workflow patterns; stopping conditions, checkpoints for human feedback, sandboxed testing, tool documentation and "poka-yoke your tools" (fetched; the page notes that much of the tooling it describes has changed since) |
| Anthropic, *Tool use overview*: https://docs.claude.com/en/docs/agents-and-tools/tool-use/overview | the API mechanics Day 12 owns: tool definitions, results, errors (cited by the Part 3 plan; not re-fetched for this chapter) |

## Idempotency and durable execution

| Source | Why read it |
|---|---|
| Stripe API reference, *Idempotent requests*: https://docs.stripe.com/api/idempotent_requests | the key pattern quoted in section 06.2: saved responses, parameter comparison, 255 characters, 24-hour pruning, no personal data in keys (fetched) |
| Temporal documentation, *Workflows*: https://docs.temporal.io/workflows | event history replay, determinism, side effects in activities (section 09.3; fetched) |
| LangGraph documentation, *Interrupts*: https://docs.langchain.com/oss/python/langgraph/interrupts | human-in-the-loop with a checkpointer, resuming on the same thread, and the warning about re-run side effects (section 09.2; fetched) |

## Tools across a boundary, and security

| Source | Why read it |
|---|---|
| Model Context Protocol specification, *Tools* (version 2025-06-18): https://modelcontextprotocol.io/specification/2025-06-18/server/tools | "a human in the loop with the ability to deny tool invocations", untrusted annotations, server and client security duties (section 09.4; fetched) |
| OWASP Top 10 for LLM Applications (2025): https://genai.owasp.org/llm-top-10/ | LLM06:2025 Excessive Agency is this chapter's subject from the attacker's side; LLM01:2025 Prompt Injection is Day 41's (fetched for the list of entries only) |

## From the Part 3 plan, for context

| Source | Why read it |
|---|---|
| ZenML LLMOps database, *Forward deployed engineering: bringing enterprise LLM applications to production*: https://www.zenml.io/llmops-database/forward-deployed-engineering-bringing-enterprise-llm-applications-to-production | deterministic constraints in code, expert trajectories as evaluation sets (used by Day 14; not re-fetched here) |
| OpenTelemetry, *Semantic conventions for generative AI systems*: https://opentelemetry.io/docs/specs/semconv/gen-ai/ | how Day 19 will trace each state and tool call (not fetched for this chapter) |

## In this course

- [Day 11](../11-the-system-around-the-model/README.md): the split this chapter applies, and the rules and core push it imports.
- [Day 12](../12-llm-apis-for-production/README.md): tool-use mechanics, the client, the ledger, idempotency keys for model calls.
- [Day 14](../14-evals-first/README.md): the golden set, expert trajectories, the gate.
- [Day 15](../15-retrieval-for-enterprise-documents/README.md): the permission-aware search used as a read tool.
- [Day 16](../16-integrating-with-what-exists/README.md): the SOAP integration, lookup before create, the safe writer.
- [Day 18](../18-verification-and-trust/README.md): the review screen in front of the approval queue.
- [Day 41](../../07-ai-era-toolkit/41-red-teaming-your-deployment/README.md): attacks through tools and documents.
