# 02 · The Measured Job: What 1,000 Postings Ask For

> Day 2 · Section 2 of 12 · [Chapter overview](README.md) · Previous: [01 · Why this chapter](01-why-this-chapter.md) · Next: [03 · The buckets up close](03-the-buckets-up-close.md)

---

## 2.1 The analysis, and what kind of source it is

The figures this chapter rests on come from one piece: *2026 FDE hiring trends: what 1,000 job posts
reveal*, published on 8 June 2026 by Perspective AI, a recruiting-platform vendor. Its stated method:
roughly 1,000 English-language FDE postings sampled across frontier labs, applied-AI startups and Fortune
500 AI teams in the first half of 2026, normalised against public postings at Palantir, OpenAI, Anthropic
and Scale AI, and corroborated against third-party trackers. It does not say how postings were selected
or de-duplicated, or how the skill shares and the time split were computed.

So: **vendor content, dated June 2026, with a described but not reproducible method.** That is the
source type, and you should say it whenever you quote the numbers. It is also, as of October 2026, the
only published analysis of FDE postings at that scale, which is why this course uses it. The
figures are quoted exactly as published and refreshed yearly; the "what dates fastest" note in
CURRICULUM.md owns that promise.

## 2.2 The three shares

| Bucket | Share of postings (H1 2026) | What the postings list | What this course calls it |
|---|---|---|---|
| Core engineering | 95 percent or more | Python and/or TypeScript, SQL, cloud (AWS or GCP), containers (Docker, Kubernetes) | bucket 1: production-grade work in a codebase and an environment you did not build |
| AI-specific | 80 percent or more | LLM application development, RAG and retrieval, prompt and eval workflows, agent orchestration | bucket 2: applied AI, meaning the system around the model; not training |
| Customer-facing and discovery | 70 percent or more, "rising fast" | customer empathy, requirements discovery, stakeholder management, translating ambiguous business problems, running discovery sessions | bucket 3: finding the right problem, scoping it, winning trust, saying no, handing off |

Three things to read off this table before anything else.

**The buckets overlap in almost every posting.** 95, 80 and 70 add to 245 percent. The typical posting
asks for all three; a posting that asks for only one is either not an FDE role or is a different role
wearing the title (Day 3 teaches you to spot the second case). This is the single most useful fact in
the chapter for a job seeker: you will not find the posting that tests only your bucket.

**The absolute numbers matter less than the direction.** Core engineering at 95 percent is table stakes:
nobody gets the job for it, and nobody gets it without it. Applied AI at 80 percent is the reason the
role exists in 2026. Customer-facing at 70 percent and rising is the one that separates candidates,
because it is the one most engineers have not done, and the analysis itself flags it as the fastest
rising. Day 0 said the same in one line; the number behind it is this row.

**The lists are specific.** "Running discovery sessions" and "translating ambiguous business problems"
are not soft-skill filler; they are the exact names of the Day 4 to Day 10 chapters. "Prompt and eval
workflows" and "agent orchestration" are Days 13, 14 and 17. The postings and the course are describing
the same job because both are reading the same published playbooks (Day 1).

## 2.3 The traits the postings add

Under a fourth heading with no percentage, the analysis lists what it calls execution traits: **radical
ownership, problem decomposition, comfort with ambiguity, product sense.** Treat these as the connective
tissue between the buckets rather than a fourth bucket. Ownership is what turns bucket 1 into "the
outcome is mine" rather than "the ticket is done". Decomposition is bucket 3's core method (Day 7).
Comfort with ambiguity is the week-one experience at Godavari, where the CISO says no and the COO wants
a date. Product sense is the 10 percent internal slice: knowing which customer-specific fix is a product
feature (Day 35).

## 2.4 The time split, and the figure that comes with it

The same analysis says postings "consistently describe a split of roughly 60 percent customer-facing
time, 30 percent deployment-specific code, and 10 percent internal work." It does not say how many
postings state a split. Read "consistently describe" as "the postings that mention a split tend to say
this", not as a measured mean. Section 04 takes the split apart and section 05 builds a fortnight that
lands on it.

Beside it, the analysis quotes a second source: **Stack Overflow's 2026 developer survey, as cited there,
reports that 41 percent of AI engineers now spend more than 30 percent of their time in customer-facing
work, up from 12 percent in 2023.** Two cautions. First, that is a figure about AI engineers in general,
not about FDEs, and it is quoted second-hand. Second, when this chapter was written (October 2026) the
figure could not be found on the public survey site, so it is reported here as "as quoted by the June
2026 analysis", not as the survey's own words. If you use it in an interview, use it that way. What it
supports, if accurate, is the direction of bucket 3: customer-facing time for engineers who work with AI
has gone from unusual to common in three years, and the FDE role is the far end of that trend.

## 2.5 How to read figures like these

You will meet numbers like these in every posting analysis, salary report and "state of" survey for the
rest of your career. A short discipline, which this course applies to its own figures:

| Ask | For this analysis |
|---|---|
| Who published it and what do they sell? | a recruiting-platform vendor; the piece is marketing as well as research |
| What was counted, over what period? | about 1,000 English-language postings, first half of 2026 |
| Is the method reproducible? | no: sampling, de-duplication and coding are not described |
| Is the figure a share, a mean or a "tends to"? | the bucket shares are shares of postings; the 60/30/10 is "consistently describe"; the Stack Overflow figure is second-hand |
| Does the direction survive if the number is off by ten points? | yes: all three buckets in most postings, bucket 3 rising, the week mostly with the customer |

The last row is the test. Nothing in this chapter depends on 70 being 70 rather than 62. Everything
depends on all three buckets appearing in most postings and the third one rising, and those claims are
also what Day 1's lineage and every published team account (section 04.4) say in different words.

## 2.6 Key takeaways

- One analysis, roughly 1,000 postings, first half of 2026, vendor-published, method described but not
  reproducible: quote it exactly and say so.
- Core engineering 95 percent or more, applied AI 80 percent or more, customer-facing discovery 70
  percent or more and rising fastest. They overlap; the typical posting asks for all three.
- The week is described as roughly 60/30/10. A second-hand Stack Overflow figure points the same way for
  AI engineers generally; use it with its caveat.
- Read any such figure by asking who counted, what, how, and whether the direction survives a ten-point
  error.
