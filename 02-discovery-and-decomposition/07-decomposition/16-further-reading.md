# 16 · Further Reading

> Day 7 · Section 16 of 16 · [Chapter overview](README.md) · Previous: [15 · Exercises](15-exercises.md)

---

## The interview round (read these before any FDE loop)

| Resource | Why read it |
|---|---|
| Harvard FAS Career Services, *The Forward Deployed Engineer interview: the definitive 2026 guide* (August 2026): https://careerservices.fas.harvard.edu/blog/2026/08/01/forward-deployed-engineer-interview-the-definitive-2026-guide-fde/ | the five-step framework this chapter uses, the seven scored behaviours, the 45-to-60-minute format, the example prompts (the 911 case, the logistics agent, the bank with three fraud systems), and "jumping to a solution before scoping" as the most common rejection |
| fdeinterviews.com, *The Palantir decomposition interview, explained*: https://fdeinterviews.com/guide/palantir-decomposition-interview | the four-step variant (frame, layered architecture, thin slice, operational constraints out loud), the 25-minute practice recommendation, "visibility before prediction", the pushback pattern, and the five common mistakes |
| Palantir, *Navigating open-ended questions* (the company's own guidance for its interview; linked from the Harvard guide; search the Palantir careers site for the current page) | the source the guides summarise; read it in the company's words before a Palantir onsite |

## The method on the job

| Resource | Why read it |
|---|---|
| Atlassian, *Forward Deployed Engineering Playbook*: https://www.atlassian.com/blog/guides-research/forward-deployed-engineering-playbook | frequent, painful, measurable; working backwards from the workflow to the AI; the 12-week bar (Days 4 and 28 own these; Day 7's step 1 inherits them) |
| OpenAI forward deployed engineering, two interviews summarised in the ZenML LLMOps database: https://www.zenml.io/llmops-database/forward-deployed-engineering-bringing-enterprise-llm-applications-to-production and https://www.zenml.io/llmops-database/forward-deployed-engineering-for-enterprise-llm-adoption | experts involved before building; evals as the contract; the sequence "golden set before serious development" that step 4 puts first |
| getperspective.ai, *How forward deployed engineers run customer discovery in 2026*: https://getperspective.ai/blog/how-forward-deployed-engineers-run-customer-discovery-2026 | 8 to 10 end-user interviews before production code; the real-workflow map that step 3 is built from (Day 6 owns this) |
| getperspective.ai, *The FDE discovery playbook: validating requirements before you build*: https://getperspective.ai/blog/fde-discovery-playbook-validating-requirements-before-you-build-2026 | "inspect the data path"; "the specific human whose day gets better"; the narrow first release with a safety boundary; "an unvalidated spec is just a well-formatted guess" |
| cloudsoftsol, *FDE first 90 days*: https://cloudsoftsol.com/blog/fde-first-90-days | days 1 to 2 access and reality; discovery weeks 1 to 4; prototype weeks 3 to 6; the shape Day 8 dates the workstreams into |
| conikeec, *The forward deployed engineer playbook: a practitioner's field manual*: https://conikeec.substack.com/p/the-forward-deployed-engineer-playbook | a practitioner's account of scoping, the thin slice and the adoption problem across engagements |
| getperspective.ai, *Palantir's FDE playbook, as read by others*: https://getperspective.ai/blog/palantir-forward-deployed-engineering-playbook-anthropic-openai-copying | how the decomposition habit spread from Palantir to the AI labs and vertical-AI companies |

## The walking skeleton and thin slices

| Resource | Why read it |
|---|---|
| Alistair Cockburn, *Walking skeleton* (the original definition, from his writing on crystal methods and architecture): http://alistair.cockburn.us/Walking+skeleton | "a tiny implementation of the system that performs a small end-to-end function"; the term the interview guides borrowed |
| Steve Freeman and Nat Pryce, *Growing Object-Oriented Software, Guided by Tests* (Addison-Wesley, 2009), chapter 4 | the walking skeleton as the first iteration of a project, with the deployment path included; the clearest book-length treatment |
| Henrik Kniberg, *Making sense of MVP* (2016): https://blog.crisp.se/2016/01/25/henrikkniberg/making-sense-of-mvp | the skateboard-to-car picture; why "earliest testable" beats "a wheel"; useful for explaining thinness to a sponsor |

## The Indian context behind Godavari's step 3

| Resource | Why read it |
|---|---|
| Reserve Bank of India, *Master Direction on Know Your Customer (KYC)*, 2016, as amended: https://www.rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=11566 | the mandatory documents behind the completeness check; the reason those rules are deterministic code the compliance head signs (Day 11) |
| The Digital Personal Data Protection Act, 2023 (India Code): https://www.indiacode.nic.in/handle/123456789/19714 | the law behind "no customer PII leaves India" as a step-1 constraint (Day 24 owns the detail) |

## Inside this course

- [Day 4](../04-picking-the-problem/README.md): the problem Day 7 decomposes, and the scoring sheet that chose it.
- [Day 5](../05-the-stakeholder-map/README.md): the four roles that step 2 extends with a metric each.
- [Day 6](../06-discovery-interviews/README.md): the real workflow and the questions that change the architecture; step 3's raw material.
- [Day 8](../08-scoping-the-first-90-days/README.md): the workstream order dated, with checkpoints and the "will not do" list.
- [Day 9](../09-success-metrics-and-business-case/README.md): step 2's metrics measured and turned into rupees.
- [Day 10](../10-the-discovery-document/README.md): the decomposition written for a COO and defended.
- Day 20: the walking skeleton shipped and demonstrated. Day 42 and Day 44: the method on the capstone and on ten timed drills.

The interview and discovery sources are career-prep or vendor content; the method is quoted as they
describe it, and the scoring behaviours are theirs. Godavari Finance, Rayalaseema Roadways and every
number about them are invented.
