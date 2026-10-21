# 15 · Further Reading

> Day 19 · Section 15 of 15 · [Chapter overview](README.md) · Previous: [14 · Exercises](14-exercises.md)

---

All read or checked on 21 October 2026 unless marked.

## The conventions this chapter uses

- OpenTelemetry, *Semantic conventions for generative AI systems*: https://opentelemetry.io/docs/specs/semconv/gen-ai/
  (the page now says the conventions have moved, and links the repository below)
- OpenTelemetry, the gen-AI conventions repository: https://github.com/open-telemetry/semantic-conventions-genai
  (created 5 May 2026; status Development throughout)
  - spans (retrieval, tools, agents, capturing content): https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-spans.md
  - the inference span and its token attributes: https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/client-inference.md
  - metrics: https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-metrics.md
- OpenTelemetry Collector, for exporting these traces into the customer's backend: https://opentelemetry.io/docs/collector/
  (checked that it resolves; not read for this chapter)

## Observability fundamentals (owned outside this course)

- [DevOps Masterclass, learn-observability](../../../DevOps/learn-observability/README.md): metrics, logs, traces,
  Prometheus, Grafana, Loki, the OpenTelemetry Collector and Alertmanager. Especially
  [day 3, dashboards](../../../DevOps/learn-observability/day03-dashboards-grafana/notes.md),
  [day 5, tracing](../../../DevOps/learn-observability/day05-tracing-opentelemetry/notes.md) and
  [day 6, alerting](../../../DevOps/learn-observability/day06-alerting-alertmanager/notes.md).
- Google, *Site Reliability Engineering*, "Monitoring Distributed Systems" (symptoms versus causes, pages that are
  actionable): https://sre.google/sre-book/monitoring-distributed-systems/ (checked that it resolves; not read for this chapter)

## The FDE sources behind the method (from the Part file)

- OpenAI forward deployed engineering, ZenML LLMOps database summary (eval-driven development, trust through
  transparency): https://www.zenml.io/llmops-database/forward-deployed-engineering-bringing-enterprise-llm-applications-to-production
- OpenAI, Morgan Stanley customer story: https://openai.com/index/morgan-stanley/ (the site refused the automated
  check on 21 October 2026; cited as Day 18 cites it)
- Atlassian, *Forward Deployed Engineering Playbook*: https://www.atlassian.com/blog/guides-research/forward-deployed-engineering-playbook
  (not fetched for this chapter)

## Building the pages and the store

- Python, `sqlite3`: https://docs.python.org/3/library/sqlite3.html
- Python, `html.escape`: https://docs.python.org/3/library/html.html
- MDN, Content Security Policy: https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP

## In this course

The chapters this one reads from are linked in the README's header: Days 9, 11 to 18. Forward:
[Day 20](../20-the-walking-skeleton-shipped/README.md) (the skeleton ships with this layer),
[Day 23](../../04-deploying-into-their-world/23-security-review-and-procurement/README.md) (the DPA),
[Day 24](../../04-deploying-into-their-world/24-data-residency-and-indian-law/README.md) (residency, the DPDP Act),
[Day 27](../../04-deploying-into-their-world/27-reliability-in-their-production/README.md) (SLOs and on-call),
[Day 36](../../06-from-customer-to-product/36-feeding-product-and-research/README.md) and
[Day 37](../../06-from-customer-to-product/37-measuring-value-honestly/README.md) (evals as currency; value measured).
