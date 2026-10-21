# 07 · 2026 Patterns, What Is Hype, and the Production Concerns of a Ratio

> Day 3 · Section 7 of 12 · [Chapter overview](README.md) · Previous: [06 · Reading an offer](06-reading-an-offer.md) · Next: [08 · Project: is Godavari worth an FDE?](08-project-godavari-unit-economics.md)

---

## 7.1 What the best teams are doing in 2026

Three patterns from the published sources that change the economics, dated 2026:

**The AI-piled FDE team.** Dataland describes its two-person team as "extremely AI piled":
meta-agents that speed up building customer agents and automate the outer loop of maintaining
them. The economic effect is on the denominator. If one FDE can keep ten customers' deployments
alive because agents do the routine maintenance, ARR per head rises without any change to pricing.
Part 7 of this course (Days 39 to 41) is the toolkit for doing this inside a customer's constraints.

**Product absorbing what FDEs used to build.** OpenAI's team expected, six months before the 2026
panel, to build about fifty separate products from its engagements. Improved coding-agent
capabilities made roughly 80 percent of those possible as extensions of an existing product
instead, leaving two standalone tracks (regulatory document authoring and workflow automation).
Read economically: the "custom build" that used to need an FDE for months is increasingly a
configuration of a product that already exists. The FDE's hours move from building to discovery,
evals and adoption, which is why bucket three is the fastest-rising in postings (Day 2).

**Rotation as a structural fix.** Nominal rotates engineers between the field and the core
product. The economic reason: the engineer who met the gap on site fixes it in the product, so the
next deployment is shorter. Day 38 owns the design; here it is the published answer to section 03.

## 7.2 What is hype

| Claim you will hear | What the sources support |
|---|---|
| "FDE is the new consulting; the big money is in services again" | The published teams say the opposite: services revenue is the drug, and the measure is recurring revenue per engineer. A vendor that drifts into services is not a new model; it is the old one |
| "Every AI company needs a large FDE team" | OpenAI runs about ten major engagements at a time with over 90 people; Ramp runs five to six customers per FDE remotely; Dataland has two. The best teams are small relative to revenue and refuse to become "a cast of thousands" |
| "FDE pay is 300 to 450 thousand dollars" | For a mid-level FDE at a frontier lab, as a posted band, half or more in equity. A recruiter's average across all employers is 238 thousand, and India's Glassdoor base average is 12 lakh. The band is the employer's economics, not the title's |
| "India's FDE market grew 19x" | True as published (Indeed, June 2025 to June 2026), from a small base; the monthly multiple fell to 6x by August 2026. A fast-growing title with a small denominator |
| "Agents will replace FDEs" | Agents are replacing FDE hours spent on maintenance and routine building (Dataland, OpenAI's 80 percent). The hours spent on discovery, trust and the "will not build" line are the ones growing |

## 7.3 Production concerns: running the ratio, not just computing it

A ratio computed once in a slide is a slide. The teams that stay out of the trap run it like a
production metric.

| Concern | What it means for the economics | What to do |
|---|---|---|
| **Cost** | FDE time is the denominator. Every unplanned on-site week, every custom screen, every "quick fix" after handoff lands there. Serving cost (inference, the model gateway, support) lands in the margin | Log FDE hours per customer from day one; the Day 19 cost dashboard carries both |
| **Latency of the signal** | Revenue arrives monthly; the damage from a services drift shows up at renewal, a year later | Watch the leading indicators from section 3.4 monthly: FDE share after handoff, the "will not build" list, patterns shipped |
| **Scale** | Customer count per FDE is the lever. Ramp's five to six is possible only when custom changes are minimal | Each engagement's exit criterion is a number: the FDE's share of time drops below a tenth by month four |
| **Security and compliance** | A VPC deployment, a security review and a DPDP memo (Part 4) cost FDE weeks that a SaaS deployment does not | Price the deployment fee for the customer's deployment model; a 12-week fee for an on-prem bank is a loss |
| **Monitoring** | The number that gets gamed is one-time revenue dressed as recurring (a "subscription" that is really a maintenance retainer for a side-build) | Count ARR only for revenue that would bill if the FDE resigned tomorrow. Day 37 has the full list of gamed numbers |

The last row is the one to carry into section 08: **ARR is revenue that recurs without you.** If
Godavari's subscription only bills next year because the FDE is still there, it is not ARR,
whatever the invoice calls it.

## 7.4 Key takeaways

- 2026 patterns: agents shrinking the maintenance denominator (Dataland), products absorbing most
  custom builds (OpenAI's 80 percent), rotation fixing the gap at source (Nominal).
- Hype: services are back, every company needs a big FDE team, the title pays 300 thousand, agents
  replace FDEs. Each has a sourced correction.
- Run the ratio monthly with leading indicators; count ARR only for revenue that recurs without you.
