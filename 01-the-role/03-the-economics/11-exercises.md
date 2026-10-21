# 11 · Exercises

> Day 3 · Section 11 of 12 · [Chapter overview](README.md) · Previous: [10 · Interview questions](10-interview-questions.md) · Next: [12 · Further reading](12-further-reading.md)

---

Ten exercises in three levels, including a predict-the-output and a break-it on the model, and one
"review this AI-written assessment". Solutions are folded under each one. The exercises marked
**(tested)** use `code/unit_economics.py`, run on Python 3.14.3 (October 2026) from the chapter
folder, and the outputs shown are real. Learning mode: do the thinking yourself; use an AI
assistant as the sceptical CFO (section 8.5's prompt), not as the author.

## Level 1: warm-up (no code needed)

**1.1 Which column?** For each sentence, say whether it describes the consulting model or the FDE
model, and name the row of section 2.1's table it belongs to.

(a) "The second bank's pipeline took as long as the first."
(b) "The fee is fixed; if we run over, it is our problem."
(c) "She is at 92 percent utilisation this quarter."
(d) "Renewal came through and nobody from our side has been on site since March."
(e) "The client owns the code at the end."
(f) "The next lender needed six weeks instead of twelve."

<details><summary>Solution</summary>

(a) consulting; next customer. (b) FDE; what is sold (bounded fee). (c) consulting; how the
engineer is measured. (d) FDE; renewal. (e) consulting; what the customer owns. (f) FDE; how
revenue grows (patterns lower the next cost). (Section 02.1.)

</details>

**1.2 Read the posting.** Each line is from a 2026 posting with "Forward Deployed Engineer" in the
title. Mark it FDE economics, deployment or solutions economics, or consulting economics, and say
which word decided it.

(a) "Own the customer's deployment end to end and drive renewal and expansion."
(b) "Deliver custom AI solutions across multiple client accounts; maintain billable utilisation."
(c) "Implement and configure the platform for enterprise customers; resolve implementation tickets; travel up to 40 percent."
(d) "Embed with strategic customers; feed deployment friction and feature gaps back to Product and Research."
(e) "Join our AI practice; work against client statements of work."

<details><summary>Solution</summary>

(a) FDE: "own", "renewal". (b) consulting: "billable utilisation", no product. (c) deployment or
solutions: "implementation tickets", "configure"; fine, priced as such. (d) FDE: "feed back to
Product", which is the patterns channel. (e) consulting: "practice", "statements of work".
(Section 04.3.)

</details>

**1.3 Source the figure.** For each figure, give the source type, the date, and the one caveat you
would say aloud with it: (a) 12 lakh; (b) 300 to 450 thousand USD; (c) 19 times; (d) 70 to 90 lakh;
(e) 215 thousand USD.

<details><summary>Solution</summary>

(a) Glassdoor India average base, January 2026 update, reported October 2026: 28 submissions,
base only. (b) posted total-compensation band for mid-level FDEs from a June 2026 analysis of
1,000 postings: half or more is equity; frontier-lab population. (c) Indeed India FDE postings,
June 2025 to June 2026, reported October 2026: from a small base; monthly multiple down to 6x by
August. (d) Cartesia founding-FDE posting, July 2026, fde.directory: one employer-stated range for
a founding role. (e) Palantir median from the course's Part 1 research note (recruiter sources):
not on the cited page I could fetch; quote as a note, not a fact. (Section 05.)

</details>

## Level 2: apply

**2.1 Predict the output (tested).** Before running, predict what changes in the table if
`SUBSCRIPTION_PER_YEAR` is halved to 60 lakh and nothing else moves. Which scenario's rev/FDE
drops most, and does scenario B still clear the 3x floor? Then run it.

<details><summary>Solution</summary>

All FDE scenarios lose half their subscription revenue but keep the deployment fee and the FDE
cost, so every ratio roughly halves. Real run: A 6.5x to 4.0x; B 11.0x to 6.0x; C 11.1x to 6.1x;
B1 (branch CRM) 2.2x to 1.2x with a slightly negative contribution; B2 (the slip with no renewal)
3.9x to 2.4x. B still clears the floor; the base cases all do, because FDE time after deployment is
small. The one that newly crosses the floor is B2: a halved price plus a slip plus no renewal is a
services engagement. The lesson: at this pricing the ratio moves with price in proportion, but it
moves with FDE time by multiples, which is why section 03 is about time, not discounts. (Section
08.2.)

</details>

**2.2 Break it, then fix it (tested).** Set `FDE_SHARE_STEADY = 0.0` and run. ARR/FDE for scenario
B becomes what? Why is the script's answer misleading, and what one-line change makes the measure
honest?

<details><summary>Solution</summary>

`arr_per_fde_head` divides by `last.fde_fte`, which is now zero for a single-customer scenario, and
the method returns 0.0 (the guard). A zero where the true value is "infinite" reads as "no ARR per
head", the opposite of the truth. Fix: return `float("inf")` or print "no FDE needed" when ARR is
positive and FTE is zero; better, keep a floor on steady-state FDE time (no deployment needs zero
upkeep) and document it. The deeper lesson: a measure with the engineer in the denominator must
say what it does when the engineer leaves entirely, which is the stated goal of the model.

</details>

**2.3 Reprice for on-prem.** Godavari's CISO insists on the on-prem data centre rather than AWS
Mumbai, adding (you estimate) eight FDE weeks for the air-gapped deployment and the security
review. Change the constants to model it and report rev/FDE for scenario B. Then decide: raise the
deployment fee, absorb it, or decline the on-prem option, and write the sentence you would say to
the COO.

<details><summary>Solution</summary>

`FDE_WEEKS_FIRST = 20` gives five deployment months instead of three; FDE cost over 36 months rises
from 36 lakh to 44 lakh (two extra full-time months at 5 lakh, minus the two 20-percent months
they replace); B falls from 11.0x to 9.0x, still well above the floor. The decision is commercial,
not arithmetic: absorbing 8 lakh once is affordable, but the pattern (every NBFC's CISO asks the
same) means the on-prem path should be a priced deployment option with its own fee, which is also
a product pattern (Day 21). The sentence: "On-prem adds about eight weeks; we will price it as a
deployment option rather than absorb it, so that neither of us is paying for the other's
constraint." (Sections 02.2, 07.3.)

</details>

**2.4 The hiring-manager round, out loud.** With a partner or an AI acting as the manager, ask the
ten questions from section 6.2 about a fictional team. Have the manager play two versions: a team
measured on ARR per FDE that declined an engagement last quarter, and a "practice" measured on
utilisation. Record it. Could you tell which was which by question four?

<details><summary>Solution</summary>

A strong run tells them apart by question three ("what did the last engagement send to product?")
or four ("one you turned down"). The practice manager answers three with "we document lessons
learned" and four with "we don't really turn down work". If you needed all ten, your questions were
too polite; make three and four direct. (Section 06.2.)

</details>

## Level 3: challenge

**3.1 Review this AI-written assessment.** `worksheet/ai-draft-fde-shaped-assessment.md` is an
agent's one-page "is Godavari FDE-shaped?" memo, written from the same brief. It contains at least
seven problems: figures quoted as published facts that are not, a floor attributed to a company
that never published one, a qualifying question answered from the sponsor's pitch, an ARR number
that is not ARR, a "will not build" line that nobody asked for, a pay claim presented as a promise,
and a conclusion the model does not support. Find them, then rewrite the memo in one page.

<details><summary>Solution</summary>

The seven, in the order they appear: (1) "Ramp requires at least 3x" (Ramp publishes the measure,
not a floor; 3x is Kaagaz's own). (2) "Godavari will renew for five years" stated as a fact (an
assumption; the model runs three). (3) "Research-interesting: yes, because LLMs on Telugu documents
are novel" (answered from enthusiasm; the honest answer is no, and the engagement is taken on the
product hypothesis instead). (4) ARR of 1.56 crore in year one (the 36 lakh deployment fee is
one-time; ARR is 1.2 crore). (5) "We will not build a mobile app" (nobody asked; the real line is
the branch CRM the COO raised). (6) "An FDE on this engagement can expect 40 lakh" (a pay promise
from a 28-submission Glassdoor figure plus a posting range). (7) "Therefore the engagement clears
the floor under every scenario, including full-time customisation" (the model shows 2.2x for B1).
A possible eighth: it cites "OpenAI's 90-person team" as a reason Kaagaz should hire four more
FDEs, which confuses a published headcount with a ratio. (Sections 02.5, 07.3, 08.)

</details>

**3.2 Your own employer.** Take the company you work for now (or the last one). Fill section 2.1's
table for it honestly: what is sold, what the customer owns, what happens at renewal, how you are
measured. Then write the one paragraph you would say in a hiring-manager screen that answers "why
FDE, and why leave" using only that table. No figures from this chapter allowed.

<details><summary>Solution</summary>

There is no model answer; the test is whether the paragraph names a business-model difference (what
recurs, who owns the outcome, what compounds) rather than a preference ("I want more customer
contact"). Day 45 turns this paragraph into the "why FDE" story with the "I" not "we" rule.

</details>

**3.3 Extend the model.** Add a `serving_cost_share_on_prem` so that scenario B can be run with
Godavari on AWS Mumbai (22 percent) and on-prem (say 12 percent, because the customer pays for
hardware, but with the eight extra FDE weeks from 2.3). Print both. Which deployment model is
better for Kaagaz over 36 months, and does the answer change if Godavari renews for only one year?

<details><summary>Solution</summary>

Real run: over 36 months, on-prem's lower serving cost (36 lakh saved over three years on a 1.2
crore subscription) more than pays for the extra FDE weeks (8 lakh), so on-prem wins on
contribution by 28 lakh (3.09 crore against 2.81). With a single year, the saving is 12 lakh
against 8 lakh of extra FDE time, and on-prem still wins, but by only 4 lakh; if the on-prem path
adds more than about three months rather than two, AWS Mumbai wins. The point for Day 21: the
deployment model is a commercial decision whose answer depends on the renewal and on how long the
customer's constraints keep the FDE on site, which is why the CISO's preference and the CEO's
model have to be in the same conversation.

</details>
