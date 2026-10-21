# 06 · The 2026 Adopters: Who Copied the Model, and What Each One Changed

> Day 1 · Section 6 of 12 · [Chapter overview](README.md) · Previous: [05 · Why AI made it everyone's model](05-why-ai-made-it-everyones-model.md) · Next: [07 · What the role is not](07-what-the-role-is-not.md)

---

## 6.1 The spread, dated

Every figure below is dated and attributed. Where the source is a vendor or recruiter, it says so.
The table is the human-readable version of `data/fde-timeline.csv`, which the project's script renders
and checks (section 09). Names without a fetched source (Databricks, Scale, Harvey, Sierra, Decagon,
Hebbia, the Indian IT majors) come from the course plan's reading of 2026 postings and are listed as
such.

| When | Who | What | Source and type |
|---|---|---|---|
| 2005 onwards | Palantir | first engineers placed inside government customers; 100+ FDEs by 2014; the model described in the September 2020 S-1 | Perspective AI blog, 14 May 2026 (vendor; sells to the FDE market) |
| 2015 to 2024 | Palantir | three to four days a week on site; pilots of 8 to 12 weeks; Foundry 50 percent or more of revenue; 80 percent gross margin in 2023 | former FDE's account, 15 October 2024 (primary) |
| 2023 | OpenAI | Morgan Stanley (first enterprise GPT-4 customer; 6 to 8 weeks build, about 4 months trust); Klarna (400+ policies, the approach that became Swarm) | OpenAI interview summarised by ZenML (company) |
| January 2024 to 2026 | OpenAI | 2 FDEs to 39 (2024 interview), plan for 52 by end 2024, 90+ by the 2026 panel; about ten major engagements at a time; services work declined | same, plus the 2026 panel (company) |
| 2026 panel | Ramp, Nominal, Dataland | Ramp: 5 to 6 customers per FDE, mostly remote; Nominal: rotation between field and core; Dataland: multiple millions of ARR per FDE head with two FDEs; FDE roles up about 10x in a year | ZenML panel summary (company) |
| to June 2026 | Anthropic | Forward Deployed Engineer, Applied AI: embeds with strategic customers; builds production applications on Claude inside customer systems; delivers MCP servers, sub-agents and agent skills; "identify and codify repeatable deployment patterns and contribute insights back to our Product and Engineering teams"; 25 to 50 percent travel; USD 200,000 to 300,000 base; posting removed 18 June 2026 | General Catalyst and Built In job boards (job board) |
| 4 October 2026 | Atlassian | playbook page: FDEs are "senior engineers, bringing AI engineering and applied AI together in a single role"; start from a business outcome and build production code, agents, integrations and redesigned workflows; "about 12 weeks to self-sufficient teams" | Atlassian blog (company) |
| 2026 postings | Databricks, Scale, Harvey, Sierra, Decagon, Hebbia | the title adopted at data platforms and vertical-AI companies | course plan reading of postings (not fetched for this chapter) |
| June 2025 to June 2026 | India | Indeed postings up nearly 19 times; Bengaluru, Hyderabad, Chennai, Delhi, Mumbai and remote; Glassdoor January 2026 average base about 12 lakh (range 9 to 16 lakh, 28 submissions) | Analytics India Magazine, 14 October 2026, citing Indeed and Glassdoor (press) |
| 2026 | Indian IT majors and GCCs | Infosys, Tech Mahindra, BCG X, QuantumBlack, the Databricks and Google Cloud GCCs, Peakflo, Cartesia named as hirers | course plan citing fde.directory (recruiter; Day 3 has the pay detail) |

Three of the ten rows rest on vendor or recruiter content: the early Palantir dates, and the Indian
employer list. The pairing, the loop, the margins and the AI-era growth rest on primary and company
sources.

## 6.2 What each adopter kept and what it changed

The model did not copy cleanly. Each team kept the core (an engineer embedded, owning the outcome,
feeding product) and changed the parts that did not fit its product or its economics.

| Team | Kept | Changed |
|---|---|---|
| **OpenAI** | the embed; the loop (evals and patterns to product and research); the refusal of pure services work | engagements chosen on two axes (product hypothesis, or research-interesting industry); eval-driven development as the method; about ten engagements at a time rather than one per team |
| **Anthropic** | the embed with strategic customers; patterns codified back to Product and Engineering; frequent travel | the artifacts are AI-native (MCP servers, sub-agents, agent skills); the engineer also "builds long-term customer relationships", the Echo's half |
| **Atlassian** | senior engineers starting from a business outcome; production code and integrations | a time box: about 12 weeks to a self-sufficient customer team, where Palantir embeds ran six to twelve months |
| **Ramp** | FDEs who write production code | remote, five to six customers per engineer, inside the core codebase; the measure is enterprise revenue divided by FDE salaries |
| **Nominal** | the Delta role | rotation between field and core as the structural answer to the dark ages |
| **Dataland** | two engineers, deeply embedded | the economics made explicit: multiple millions of ARR per FDE head |
| **The Indian IT majors** | the title | the risk Day 3 names: a services engagement wearing the FDE title; read the posting for the loop before accepting |

The row that matters most for Godavari is Atlassian's. Twelve weeks is the bar the course sets for
handoff (Day 28), and it is the number in the day-one note: one engineer in Hyderabad for about twelve
weeks, then Godavari runs it without you.

## 6.3 India, with the caveats

The 19-times figure is real and it is small. Indeed's managing director for India is quoted in the
Analytics India Magazine piece; the base was low enough that 19 times is still a modest absolute
number, and Indeed says its FDE sample is too small for a reliable median salary. Glassdoor's January
2026 average of about 12 lakh rests on 28 submissions. The postings span everything from a services
tier at 5 to 10 lakh to founding roles at 70 to 90 lakh (Day 3). What the figure tells you is
direction: the title has arrived in Hyderabad, and the companies using it range from frontier-lab GCCs
to IT services firms relabelling delivery roles. Section 07 is how to tell them apart.

## 6.4 What has not changed since 2005

Strip the model names and the dates and one sentence survives every adopter: **the engineer owns the
outcome, not the recommendation.** A Delta at Airbus owned whether the production line got faster.
An OpenAI FDE at Morgan Stanley owned whether the advisers used it. An Atlassian FDE owns whether the
customer team is self-sufficient in twelve weeks. You, at Godavari, own whether forty analysts close
the Excel tracker. Everything else in this Part (the buckets, the week, the economics, the titles) is
detail around that sentence, and the interview's "why FDE?" is answered by it.

## 6.5 Key takeaways

- The spread is datable: Palantir from 2005 (vendor source), the first-hand account from 2015, OpenAI
  from 2 to 90+ between January 2024 and 2026, Anthropic and Atlassian postings and playbooks through
  2026, India up nearly 19 times to June 2026.
- Each adopter kept the embed, the outcome and the loop, and changed the time box, the artifacts, the
  ratio or the engagement selection.
- Atlassian's 12 weeks is Godavari's bar.
- The India figure shows direction, not pay; the sample is small and the title covers a wide range of
  jobs.
- What has not changed: the engineer owns the outcome, not the recommendation.
