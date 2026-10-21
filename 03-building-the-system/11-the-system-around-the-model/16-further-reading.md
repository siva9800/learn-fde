# 16 · Further Reading

> Day 11 · Section 16 of 16 · [Chapter overview](README.md) · Previous: [15 · Exercises](15-exercises.md)

---

Links were checked in October 2026. Those marked "(fetched)" were read for this chapter and the quotations in
the text come from them; those marked "(not fetched)" are cited from the Part plan or from earlier chapters and
were not re-read here.

## The split, as the teams that invented the role describe it

| Resource | Why read it |
|---|---|
| OpenAI forward deployed engineering, ZenML LLMOps database summary, *Bringing enterprise LLM applications to production*: https://www.zenml.io/llmops-database/forward-deployed-engineering-bringing-enterprise-llm-applications-to-production (fetched) | the source of this chapter's anchors: "use determinism wherever possible and LLMs only where their probabilistic nature adds value"; the automotive "at least two suppliers for critical components like tires" constraint "checked 100% of the time through deterministic code"; the model exploring "a simulator ... as an educated business user would"; eval-driven development; the metadata translation layer (Day 16) |
| OpenAI and others, ZenML summary, *Forward deployed engineering for enterprise LLM adoption*: https://www.zenml.io/llmops-database/forward-deployed-engineering-for-enterprise-llm-adoption (fetched) | how FDE work shifted as models improved: less plumbing, more customer problems; evals that feed back to product teams (Day 36) |
| Anthropic, *Building effective agents*: https://www.anthropic.com/research/building-effective-agents (not fetched) | workflows versus agents; why a fixed workflow with a model in specific steps is often the right design (Day 17 builds on it) |
| Atlassian, *Forward Deployed Engineering Playbook*: https://www.atlassian.com/blog/guides-research/forward-deployed-engineering-playbook (not fetched) | working backwards from the workflow to the AI; the context the eight boxes come from |

## The model box: structured outputs and tools (Day 12 owns these)

| Resource | Why read it |
|---|---|
| Anthropic, *Structured outputs*: https://platform.claude.com/docs/en/build-with-claude/structured-outputs (fetched) | what constrained decoding guarantees ("schema compliance in most cases"), the cases where it does not, and the JSON Schema features not supported (numeric constraints, recursive schemas); the adapter's schema follows it |
| Anthropic, *Tool use overview*: https://docs.claude.com/en/docs/agents-and-tools/tool-use/overview (not fetched) | declaring deterministic functions as tools; section 9.2's "the tool's result is authoritative" |
| OpenAI, *Structured outputs guide*: https://platform.openai.com/docs/guides/structured-outputs (not fetched) | the same contract on another vendor; useful for writing the vendor-neutral client layer in Day 12 |
| Anthropic Python SDK: https://github.com/anthropics/anthropic-sdk-python (not fetched; version 1.17.0 installed and inspected offline for the adapter) | the client the optional adapter uses |

## The Indian rules behind Godavari's rule set

| Resource | Why read it |
|---|---|
| Reserve Bank of India, *Master Direction on Know Your Customer (KYC)*, 2016, as amended: https://www.rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=11566 (not fetched; cited in Day 7) | officially valid documents, the documents deemed acceptable for address, and the Aadhaar requirements behind TW-DOC-02 to 05, TW-ADDR-LIST and TW-KYC-MASK; the compliance head owns the current text |
| Cyril Amarchand Mangaldas, *FIG Paper No. 52: RBI directions on lending against gold and silver collateral* (November 2025): https://corporate.cyrilamarchandblogs.com/2025/11/fig-paper-no-52-rbi-directions-on-lending-against-gold-and-silver-collateral-a-harmonised-regulatory-framework/ (fetched) | a law firm's summary of the Reserve Bank of India (Lending Against Gold and Silver Collateral) Directions, 2025, issued 6 June 2025, compliance by 1 April 2026: the 85, 80 and 75 percent LTV tiers, LTV maintained through the tenor, uniform assaying and certificates showing purity and gross and net weight. Read the RBI's own notification (search rbi.org.in for the title) before relying on it; this chapter did not fetch the primary text |
| The Digital Personal Data Protection Act, 2023 (India Code): https://www.indiacode.nic.in/handle/123456789/19714 (not fetched; cited in Day 7) | why "nothing leaves India" shapes where the model may run (Day 24 owns it) |

## Rules as code, beyond plain Python

| Resource | Why read it |
|---|---|
| OMG, *Decision Model and Notation (DMN)*: https://www.omg.org/dmn/ (not fetched) | the decision-table standard rule owners can read directly; worth knowing when rule counts reach the hundreds (section 9.4) |
| Open Policy Agent documentation: https://www.openpolicyagent.org/docs/latest/ (not fetched) | policy as code for authorisation decisions; the natural home for visibility rules at scale (Day 22) |
| Python documentation, `decimal`: https://docs.python.org/3/library/decimal.html (not fetched) | why money and weights are Decimal or integer rupees in the rules |
| pytest documentation: https://docs.pytest.org/ (not fetched; pytest 9.1.1 used) | parametrised boundary tests, as in `test_rules.py` |

## Inside this course

- [Day 6](../../02-discovery-and-decomposition/06-discovery-interviews/README.md): the findings this chapter turns into
  code, especially A7 (rules as signed code), A8 ("unsure", not a guess) and B4 (wrong means an audit finding).
- [Day 7](../../02-discovery-and-decomposition/07-decomposition/README.md): the walking skeleton and the generator this
  chapter imports.
- [Day 10](../../02-discovery-and-decomposition/10-the-discovery-document/README.md): the signed scope, decisions D04
  and D07, and the risk register (R7 for gold).
- [Day 12](../12-llm-apis-for-production/README.md): the model box as production code. [Day 14](../14-evals-first/README.md):
  the golden set that sets the thresholds. [Day 17](../17-agents-and-workflows/README.md): the split applied to
  a state machine. [Day 18](../18-verification-and-trust/README.md): the review queue.
  [Day 41](../../07-ai-era-toolkit/41-red-teaming-your-deployment/README.md): attacking the split.

The market figure in section 01 comes from a vendor's analysis of job postings and is quoted as published.
Godavari Finance, its rules, limits, rates, people and files are invented; the RBI rules are real and are
summarised, not reproduced.
