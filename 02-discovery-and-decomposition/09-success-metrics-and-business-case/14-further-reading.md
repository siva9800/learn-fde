# 14 · Further Reading

> Day 9 · Section 14 of 14 · [Chapter overview](README.md) · Previous: [13 · Exercises](13-exercises.md)

---

Links checked in October 2026 where marked **(fetched)**. The others are the sources Part 2 cites, not
re-fetched for this chapter; the FDE playbook sources are vendor or career-prep content, quoted as they
describe the method.

## The FDE practice behind the chapter

- Atlassian, Forward Deployed Engineering Playbook: frequent, painful, *measurable*; working backwards
  from the outcome. https://www.atlassian.com/blog/guides-research/forward-deployed-engineering-playbook
- OpenAI forward deployed engineering, ZenML LLMOps database summaries: experts involved and success
  agreed before building; eval-driven development.
  https://www.zenml.io/llmops-database/forward-deployed-engineering-bringing-enterprise-llm-applications-to-production
  and https://www.zenml.io/llmops-database/forward-deployed-engineering-for-enterprise-llm-adoption
- FDE first 90 days: the golden set of real examples, labelled by the customer's experts, agreed before
  a model is chosen. https://cloudsoftsol.com/blog/fde-first-90-days
- The FDE discovery playbook: validating requirements before you build.
  https://getperspective.ai/blog/fde-discovery-playbook-validating-requirements-before-you-build-2026

## Measurement and statistics, in plain words

- Kingman's formula (the utilisation / (1 - utilisation) term behind section 05.5; "generally very
  accurate, especially for a system operating close to saturation"). **(fetched)**
  https://en.wikipedia.org/wiki/Kingman%27s_formula
- Goodhart's law, the one-line reason for pre-registration. https://en.wikipedia.org/wiki/Goodhart%27s_law
- Stratified sampling: the idea, allocation and weighting. https://en.wikipedia.org/wiki/Stratified_sampling
- The bootstrap, for the median's interval. https://en.wikipedia.org/wiki/Bootstrapping_(statistics)
- Python's `statistics` and `random` modules, all the script uses.
  https://docs.python.org/3/library/statistics.html and https://docs.python.org/3/library/random.html
- `importlib.util.spec_from_file_location`, for importing Day 7's generator by path.
  https://docs.python.org/3/library/importlib.html

## Indian regulation behind the risk line

- Reserve Bank of India, Master Direction on Know Your Customer (KYC), 2016, as amended: the mandatory
  documents behind the completeness check. https://www.rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=11566
- RBI press releases, where each monetary penalty on a regulated entity is published (the index page
  was **fetched** on 21 October 2026; the current fortnight listed no NBFC KYC penalty, so search the
  archives for "monetary penalty" and "NBFC" to build the penalty range). https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx

## In this course

- [Day 3](../../01-the-role/03-the-economics/README.md): Kaagaz's side of the ledger this case reconciles with.
- [Day 4](../04-picking-the-problem/README.md): the placeholder rate and the "baseline exists" gate.
- [Day 5](../05-the-stakeholder-map/README.md): the number each person would believe.
- [Day 6](../06-discovery-interviews/README.md): the real workflow; the queue nobody reported.
- [Day 7](../07-decomposition/README.md): step 2's metrics and the generator this chapter imports.
- [Day 8](../08-scoping-the-first-90-days/README.md): the pilot weeks the targets are dated against.
- [Day 14](../../03-building-the-system/14-evals-first/README.md): the golden set and the accuracy threshold.
- [Day 37](../../06-from-customer-to-product/37-measuring-value-honestly/README.md): measuring the result against this baseline.
