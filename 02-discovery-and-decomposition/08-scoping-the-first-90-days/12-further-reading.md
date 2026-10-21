# 12 · Further Reading

> Day 8 · Section 12 of 12 · [Chapter overview](README.md) · Previous: [11 · Exercises](11-exercises.md)

---

## The 90-day shape and the playbooks

| Resource | Why read it |
|---|---|
| cloudsoftsol, *FDE first 90 days*: https://cloudsoftsol.com/blog/fde-first-90-days | the source the Part 2 plan cites for the 30-60-90 shape. Fetched 21 October 2026: it frames the 90 days around a newly hired FDE (learn, own a slice, carry it toward production) with dated artefact windows (discovery notes days 31 to 45, a security review pack days 61 to 75, an evaluation report days 65 to 85) and a small fixed test set agreed with a customer expert. The week-numbered engagement shape in this chapter is the convention as the Part 2 plan summarises it; read the page for its own framing |
| getperspective.ai, *The FDE discovery playbook: validating requirements before you build*: https://getperspective.ai/blog/fde-discovery-playbook-validating-requirements-before-you-build-2026 | fetched 21 October 2026: "eval co-design should start no later than week three of the engagement"; phase gates with exit criteria ("do not advance until every box in the current phase is checked"), which section 02.2 applies to decisions, not work |
| getperspective.ai, *How forward deployed engineers run customer discovery in 2026*: https://getperspective.ai/blog/how-forward-deployed-engineers-run-customer-discovery-2026 | the discovery weeks the plan's first phase holds (Day 6 owns them) |
| Atlassian, *Forward Deployed Engineering Playbook*: https://www.atlassian.com/blog/guides-research/forward-deployed-engineering-playbook | about twelve weeks to a self-sufficient customer team: the bar the week-12 checkpoint tests (Day 28 owns it) |
| OpenAI forward deployed engineering, ZenML LLMOps database summaries: https://www.zenml.io/llmops-database/forward-deployed-engineering-bringing-enterprise-llm-applications-to-production | the customer's experts involved before serious development; why the eval workstream starts in week 1 |
| conikeec, *The forward deployed engineer playbook: a practitioner's field manual*: https://conikeec.substack.com/p/the-forward-deployed-engineer-playbook | scoping, the thin slice and adoption across engagements, from a practitioner |
| Harvard FAS Career Services, *The FDE interview: the definitive 2026 guide*: https://careerservices.fas.harvard.edu/blog/2026/08/01/forward-deployed-engineer-interview-the-definitive-2026-guide-fde/ | sequencing by risk and the thin slice as scored behaviours; the round where "what would you not do?" is asked |

## Tools and calendars

| Resource | Why read it |
|---|---|
| Mermaid, *Gantt diagrams*: https://mermaid.js.org/syntax/gantt.html | the syntax the script generates: sections, `crit` bars, milestones with `0d` |
| Python documentation, `datetime`: https://docs.python.org/3/library/datetime.html | date arithmetic and `weekday()`, which the script's working-day logic rests on |
| Telangana public holidays 2026 (G.O.Rt.No.1715 of 6 December 2025), as listed by Keka: https://www.keka.com/compliance/public-holiday/telangana | the source for Deepavali (Sunday 8 November) and Christmas (Friday 25 December) in the calendar file; a secondary listing of the government order, not the order itself. The 2027 lists, which will fix the Sankranti dates, were not yet published when this chapter was written |

## The Indian context behind Godavari's calendar

| Resource | Why read it |
|---|---|
| Reserve Bank of India, *Master Direction on Know Your Customer (KYC)*, 2016, as amended: https://www.rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=11566 | the documents behind the completeness rules the compliance head signs in week 6, and part of why an inspection month is a blackout |
| The Digital Personal Data Protection Act, 2023 (India Code): https://www.indiacode.nic.in/handle/123456789/19714 | the law behind line 4 of the "will not do" list (Day 24 owns the detail) |

The playbook and interview sources are vendor, recruiter or career-prep content, quoted as they
describe things; the two fetches above were made through a summarising tool and are worth checking in a
browser. Godavari Finance, its calendar, its people and its numbers are invented.
