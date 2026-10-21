# 13 · Further Reading

> Day 13 · Section 13 of 13 · [Chapter overview](README.md) · Previous: [12 · Exercises](12-exercises.md)

---

Pages marked "fetched October 2026" were read while writing this chapter; the others are stable references that were
not re-fetched, so check the current page before quoting them.

## Long documents and where models lose facts

| Resource | Why read it |
|---|---|
| Nelson F. Liu, Kevin Lin, John Hewitt, Ashwin Paranjape, Michele Bevilacqua, Fabio Petroni, Percy Liang, *Lost in the Middle: How Language Models Use Long Contexts* (TACL, 2023): https://arxiv.org/abs/2307.03172 (fetched October 2026) | the measured U-shape: "performance is often highest when relevant information occurs at the beginning or end of the input context", including on long-context models; the research behind section 06.2 |
| Anthropic, *Prompting best practices*, long context prompting: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices (fetched October 2026; the older long-context-tips URL redirects here) | vendor guidance for inputs over 20k tokens: long documents at the top, the query at the end ("up to 30 percent" better in their tests), documents wrapped in tags, quotes extracted first |
| Anthropic, *Models overview*: https://platform.claude.com/docs/en/about-claude/models/overview (fetched October 2026) | the 1M-token context windows of current models, and retirement dates per model ID (section 06.6, 07.4) |

## Model versions and drift

| Resource | Why read it |
|---|---|
| Anthropic, *Model IDs and versioning*: https://platform.claude.com/docs/en/about-claude/models/model-ids-and-versions (fetched October 2026) | dateless IDs from the 4.6 generation are fixed snapshots; earlier aliases point to the latest dated snapshot; weights are fixed per ID but serving infrastructure can change observable behaviour (section 07.4) |

## Templates and versioning

| Resource | Why read it |
|---|---|
| Jinja2 3.1 API documentation: https://jinja.palletsprojects.com/en/stable/api/ (fetched October 2026) | `Environment`, `StrictUndefined` ("barks on print and iteration as well as boolean tests and all kinds of comparisons"), loaders, `jinja2.meta` |
| Jinja2 sandbox documentation: https://jinja.palletsprojects.com/en/stable/sandbox/ (not re-fetched) | when templates themselves come from people you do not fully trust; not a defence for rendering customer text as a template, which you never do |
| Semantic Versioning 2.0.0: https://semver.org/ (not re-fetched) | the MAJOR.MINOR.PATCH rules section 04.1 adapts |
| GitHub, *About code owners*: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners (not re-fetched) | requiring the engagement's FDE on every change to `prompts/` |

## The method behind it

| Resource | Why read it |
|---|---|
| OpenAI forward deployed engineering, two interviews summarised in the ZenML LLMOps database: https://www.zenml.io/llmops-database/forward-deployed-engineering-bringing-enterprise-llm-applications-to-production and https://www.zenml.io/llmops-database/forward-deployed-engineering-for-enterprise-llm-adoption | eval-driven development and deterministic constraints: why every release here carries a score and no prompt carries a rule (Part 3 sources) |
| OWASP Top 10 for LLM Applications: https://genai.owasp.org/llm-top-10/ (not re-fetched) | prompt injection as the first entry; Day 41 owns it, section 07.5 previews it in one line |

## Inside this course

[Day 6](../../02-discovery-and-decomposition/06-discovery-interviews/README.md) (the findings behind the rules),
[Day 11](../11-the-system-around-the-model/README.md) (the rules themselves), [Day 12](../12-llm-apis-for-production/README.md)
(the adapter and caching), [Day 14](../14-evals-first/README.md) (the golden set), [Day 19](../19-observability-for-ai-systems/README.md)
(per-release dashboards), [Day 41](../../07-ai-era-toolkit/41-red-teaming-your-deployment/README.md) (the wrapper under attack).

Godavari Finance, its files and every number about them are invented; the fake model's behaviour is a caricature
built for reproducibility, not a measurement of any vendor's model.
