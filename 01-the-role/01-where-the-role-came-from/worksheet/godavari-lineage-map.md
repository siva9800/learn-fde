# Lineage map · where the Kaagaz AI engagement model comes from

> One page for the Godavari engagement folder. Written on day one at Kaagaz AI, before any reply to
> the COO's introduction, so that everyone who touches the engagement (the CEO, sales, the product
> team, the FDE who replaces you) can see which published model we are following and which parts we
> have changed. Every figure is dated; vendor and recruiter sources are marked. Refresh yearly.

**Engagement:** Godavari Finance Ltd, Hyderabad · **Vendor:** Kaagaz AI · **Author:** the FDE · **Date:** October 2026 · **Version:** 1

## 1 · The model we are following, in one line

An engineer from the vendor works inside the customer, with the customer's data and under the
customer's rules, builds what the product lacks for that customer, and sends the pattern back so the
product improves. The customer gets an outcome; the vendor gets a better product. Nobody bills hours.

## 2 · The lineage, in four steps

| Step | Who | When | What they did | What we take from it |
|---|---|---|---|---|
| Invented | Palantir | 2005 onwards (vendor source, May 2026); first-hand account from 2015 (primary, Oct 2024) | Engineers ("Deltas") on site 3 to 4 days a week with a customer-facing partner ("Echo", the deployment strategist); product engineers ("Devs") turned field work into Foundry | the pairing; the loop back to product; the warning from the "dark ages" when field teams built parallel systems |
| Proved it pays | Palantir | S-1, September 2020; Foundry 50 percent or more of revenue and 80 percent gross margin in 2023 (primary, Oct 2024) | the custom work became a product with software margins, not a services firm with people margins | the test for every custom build at Godavari: will it become product? |
| Copied for AI | OpenAI | 2 FDEs in January 2024 to 90+ by 2026; about ten major engagements at a time (company interviews) | evals before serious development; no LLM code done without verification; services work declined | evals first (Day 14); the "will not build" list (Day 3) |
| Everyone's model | Anthropic, Atlassian, Databricks, Scale, vertical AI, Indian IT majors | 2025 to 2026 postings; Atlassian playbook October 2026; India postings up nearly 19x June 2025 to June 2026 (press, Oct 2026) | the same shape: senior engineer, embedded, owns the outcome, feeds product; about 12 weeks to a self-sufficient customer team (Atlassian) | the 12-week bar for Godavari's handoff (Day 28) |

## 3 · Who plays which role at Godavari

| Palantir's name | The role | At Kaagaz AI for Godavari |
|---|---|---|
| Delta (forward deployed software engineer) | lives in the customer's data; builds what the product lacks; sends the pattern back | you |
| Echo (deployment strategist) | owns the relationship; maps the workflow with the operators; runs training and demos; presents to the C-suite | there is no Echo. Kaagaz has 40 people. You carry both halves until a customer success lead exists, and you write down which hat you are wearing in each meeting |
| Dev (product developer) | generalises what the field learns into the platform | the Kaagaz product team; you owe them one patterns note per fortnight |

## 4 · What we are copying and what we are not

| We copy | We do not copy |
|---|---|
| the engineer on site, in Hyderabad and Vijayawada, with their data and under their rules | six-to-twelve-month embeds; Godavari gets 12 weeks to self-sufficiency, then a lighter touch |
| the loop back to product: every Godavari-specific fix is tagged "product candidate" or "Godavari only" | building Godavari's branch CRM or anything else that would never become product |
| evals built with the customer's experts before serious development | hand-written prompt-per-policy work; it did not scale at Klarna and it will not scale across 300 branches |
| the 12-week bar for a self-sufficient team | an open-ended services contract priced by the hour |

## 5 · Dated figures used on this page

| Figure | Date | Source and type |
|---|---|---|
| first FDEs 2005; 100+ FDEs by 2014; 1,000+ AIP bootcamps by end 2024 | May 2026 | Perspective AI blog (vendor; sells to the FDE market) |
| on site 3 to 4 days a week; 8 to 12 week pilots mostly on data access; Foundry 50 percent or more of revenue; 80 percent gross margin in 2023 | October 2024 | Nabeel S. Qureshi, former Palantir FDE (primary) |
| OpenAI FDEs 2 (Jan 2024) to 90+ (2026); about ten major engagements | 2024 interview and 2026 panel | ZenML summaries of OpenAI interviews (company) |
| Morgan Stanley: 6 to 8 weeks to build, about 4 months to trust | 2023 engagement, reported 2024 | same |
| about 12 weeks to self-sufficient teams | 4 October 2026 | Atlassian playbook page (company) |
| India FDE postings up nearly 19x | June 2025 to June 2026 | Indeed data via Analytics India Magazine, 14 October 2026 (press) |
| FDE is post-sale; SE is pre-sale and paid on deals | 22 April 2026 | Paraform (recruiter) |

Eight of the nineteen rows in `data/fde-timeline.csv` rest on vendor or recruiter content. The
pairing, the loop and the margins rest on primary and company sources. Treat the dates of Palantir's
early years as approximate.
