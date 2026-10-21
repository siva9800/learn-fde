# 16 · Further Reading

> Day 14 · Section 16 of 16 · [Chapter overview](README.md) · Previous: [15 · Exercises](15-exercises.md)

---

Read dates are 21 October 2026 unless marked. Sources marked "not fetched" were cited from the course's Part 3 plan or
from earlier chapters and could not be opened for this chapter; their URLs are as the plan gives them.

## The FDE practice behind "evals first"

| Resource | Why read it |
|---|---|
| ZenML LLMOps database, *Forward deployed engineering: bringing enterprise LLM applications to production* (summary of an OpenAI FDE interview): https://www.zenml.io/llmops-database/forward-deployed-engineering-bringing-enterprise-llm-applications-to-production | the source of "eval-driven development", evaluation sets "before significant development begins", expert trajectories as labelled evaluation sets, "no LLM-based code is considered done until verification exists", and the Morgan Stanley timeline (6 to 8 weeks to build, about 4 more months of pilots and evaluation refinement, 98 percent adoption) as summarised there |
| ZenML LLMOps database, *Forward deployed engineering for enterprise LLM adoption (OpenAI, Ramp, Nominal, Dataland)*: https://www.zenml.io/llmops-database/forward-deployed-engineering-for-enterprise-llm-adoption | many eval sets per problem, customers building their own evaluations, and evaluation data that "feeds back to post-training teams" (Day 36's theme) |
| OpenAI, *Morgan Stanley* customer story: https://openai.com/index/morgan-stanley/ | the primary account of the advisors labelling and the eval framework. **Not fetched**: the page returned 403 on 21 October 2026; figures in this chapter are as summarised by ZenML and cited in the Part 3 plan |
| Atlassian, *Forward Deployed Engineering Playbook*: https://www.atlassian.com/blog/guides-research/forward-deployed-engineering-playbook | the playbook the course leans on for frequent, painful, measurable problems and the 12-week bar; read for how a vendor frames success criteria with customers. Not fetched for this chapter |
| cloudsoftsol, *FDE first 90 days*: https://cloudsoftsol.com/blog/fde-first-90-days | cited by the Part 3 plan for "the golden set of 100 to 200 examples before model choice". Day 6's fetch found a 30-60-90 plan recommending "a small fixed test set of real questions with expected answers, agreed with a customer subject-matter expert", with no count; the 100 to 200 figure is the course's |
| conikeec, *The forward deployed engineer playbook: a practitioner's field manual*: https://conikeec.substack.com/p/the-forward-deployed-engineer-playbook | a practitioner's account of verification and trust across engagements. Not fetched for this chapter |

## Evals and judges, method

| Resource | Why read it |
|---|---|
| Hamel Husain, *Using LLM-as-a-Judge for evaluation: a complete guide* (2024, modified 1 September 2026): https://hamel.dev/blog/posts/llm-judge/ | binary pass or fail over 1-to-5 scores; one principal domain expert; written critiques that become few-shot examples; measure agreement with the expert and report true positive and true negative rates separately; dev and test splits kept out of the prompt. Section 06 follows it closely |
| Hamel Husain, *Your AI product needs evals* (29 March 2024): https://hamel.dev/blog/posts/evals/ | the case for domain-specific evals at three levels (unit tests, human and model review, A/B tests), from a real product |
| Anthropic, *Define success criteria and build evaluations*: https://platform.claude.com/docs/en/test-and-evaluate/develop-tests | grading methods (code-based, human, model-based) with examples; "Generally best practice to use a different model to evaluate than the model used to generate the evaluated output"; and a useful tension with this chapter: it prefers "more questions with slightly lower signal automated grading" over fewer hand-graded ones. Both are right: a large automated suite for development, a small expert golden set for the decisions |
| OpenAI, *Working with evals*: https://developers.openai.com/api/docs/guides/evals | the provider's Evals API; on 21 October 2026 the page says the Evals platform is being deprecated with a scheduled shutdown on 30 November 2026, which is section 09.1's point about tools |
| Lianmin Zheng and others, *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena* (2023): https://arxiv.org/abs/2306.05685 | the study behind position, verbosity and self-enhancement bias, and the finding that strong judges reach over 80 percent agreement with human preferences, about the level humans reach with each other |
| Shreya Shankar and others, *Who Validates the Validators? Aligning LLM-Assisted Evaluation of LLM Outputs with Human Preferences* (2024): https://arxiv.org/abs/2404.12272 | aligning judges with users' own grades, and "criteria drift": grading outputs is how people discover their criteria. Why the rubric is versioned |

## The statistics, in the original

| Resource | Why read it |
|---|---|
| Edwin B. Wilson, "Probable inference, the law of succession, and statistical inference", *Journal of the American Statistical Association* 22 (1927) | the Wilson score interval, which behaves near 0 and 100 percent where eval numbers live |
| Jacob Cohen, "A coefficient of agreement for nominal scales", *Educational and Psychological Measurement* 20 (1960) | Cohen's kappa |
| Quinn McNemar, "Note on the sampling error of the difference between correlated proportions or percentages", *Psychometrika* 12 (1947) | the paired comparison the gate uses, here computed exactly as a binomial test on the changed cells |
| Bradley Efron and Robert Tibshirani, *An Introduction to the Bootstrap* (Chapman and Hall, 1993) | resampling, including why you resample the unit that is independent (here, the file) |

## The Indian context

| Resource | Why read it |
|---|---|
| The Digital Personal Data Protection Act, 2023 (India Code): https://www.indiacode.nic.in/handle/123456789/19714 | the law behind keeping the real golden set in the building and masking what leaves; Day 24 owns the detail |
| Reserve Bank of India, *Master Direction on Know Your Customer (KYC)*, 2016, as amended: https://www.rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=11566 | the documents behind the completeness labels the compliance head signs (Day 11 owns the rules) |

## Inside this course

- [Day 6](../../02-discovery-and-decomposition/06-discovery-interviews/README.md): the labellers, their conditions and the 180-file manifest.
- [Day 9](../../02-discovery-and-decomposition/09-success-metrics-and-business-case/README.md) and its [metric definitions](../../02-discovery-and-decomposition/09-success-metrics-and-business-case/worksheet/godavari-metric-definitions.md): the definitions measured here, quoted, never reworded.
- [Day 10](../../02-discovery-and-decomposition/10-the-discovery-document/README.md): risks R1, R2, R7, change C4, decisions D07 and D08.
- [Day 11](../11-the-system-around-the-model/README.md): the system this chapter measures, imported by path.
- [Day 12](../12-llm-apis-for-production/README.md) and [Day 13](../13-prompts-as-code/README.md): the cost per file, and the prompt releases every gate run scores.
- [Day 18](../18-verification-and-trust/README.md): thresholds set from this harness. [Day 19](../19-observability-for-ai-systems/README.md): the same metrics in production. [Day 27](../../04-deploying-into-their-world/27-reliability-in-their-production/README.md): the golden set as a production check. [Day 36](../../06-from-customer-to-product/36-feeding-product-and-research/README.md): evals as the currency.

Godavari Finance, its people, its files and every number about them are invented; the golden set and the stub's
errors are generated by code in this repository and in Days 7 and 11.
