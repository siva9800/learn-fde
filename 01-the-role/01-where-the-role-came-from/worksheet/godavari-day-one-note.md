# Day-one note · what a forward deployed engagement at Godavari would look like, versus a services proposal

> The first artifact in the Godavari engagement folder. Written the morning the CEO forwarded one
> line from Godavari Finance's COO: "loan turnaround is nine days, we want three, can your AI do
> it". Nobody has replied yet. This page is for the CEO and the head of sales, so that the reply
> commits Kaagaz AI to the right shape of work. One page. No model names.

**To:** CEO, Head of Sales · **From:** the FDE · **Date:** October 2026 · **Re:** Godavari Finance Ltd, Hyderabad

## What we know (all of it, so far)

An NBFC headquartered in Hyderabad. About 1,200 staff and 300 branches. A loan takes nine days from
application to sanction and the COO wants three. We have not seen a loan file, the core system, or
the people who process files. Everything below is therefore about the shape of the work, not the
solution.

## Two ways Kaagaz could answer

| | A forward deployed engagement | A services proposal |
|---|---|---|
| What Godavari buys | the platform subscription plus a bounded deployment: one engineer in Hyderabad for about 12 weeks | a quote for a custom build: a team, a statement of work, a price per phase |
| Where the work happens | in Godavari's environment (their AWS Mumbai account or their data centre), with their data, under their CISO's rules | in ours, then "migrated" |
| Who decides what to build | discovery with the people who process files, not the demo deck; the first two weeks produce a problem statement, a stakeholder map and a scope with a "will not do" list | the requirements document the customer writes, which will describe the sponsor's version of the problem |
| What done means | 40 credit-ops analysts using the system on a Tuesday, a runbook, and Godavari running it without us | sign-off on the deliverables list |
| What Kaagaz gets | a reference customer, recurring platform revenue, and two or three patterns (document completeness checks, a core-system integration layer, a review queue) that go into the product for the next lender | one-off revenue, a codebase only Godavari uses, and an engineer who cannot be reassigned |
| What it costs us | one senior engineer for 12 weeks and about a tenth of the product team's attention | a team for as long as the customer keeps asking, and a product roadmap held hostage to one customer |
| The risk | we pick the wrong problem in week one; mitigated by discovery first and a walking skeleton in week three | we build exactly what was asked and nobody uses it; mitigated by nothing |

## What I am asking for

1. Reply to the COO with a question, not a number: where do the nine days go today, and who in
   Godavari owns that answer? Offer two weeks of discovery on site before any commitment to "three".
2. Do not quote a custom build. If sales needs a price, price the platform plus a fixed deployment
   fee for 12 weeks, with the scope decided at the end of week two.
3. Let me write the first line of the "will not build" list now: anything that would only ever be
   used by Godavari (a branch CRM, a bespoke reporting tool) is out, however much they want it.

## Why this shape and not the other

This is the model Palantir ran for fifteen years and the one OpenAI, Anthropic and Atlassian copied
for AI (the lineage map in this folder has the dates and sources). The published teams decline pure
services work because every engagement must improve the product, and the published failure is the
one where field engineers built a separate system per customer that the product could never absorb.
We are forty people. We cannot afford one of those.

## What this note does not do

It does not say whether nine to three is possible. We will know after discovery (two weeks), and we
will say so in the discovery document, with a number we can defend and a list of what we will not do.
