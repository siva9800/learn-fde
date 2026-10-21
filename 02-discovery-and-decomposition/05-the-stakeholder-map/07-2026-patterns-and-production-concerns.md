# 07 · 2026 Patterns, What Is Hype, and Keeping the Map Alive in Production

> Day 5 · Section 7 of 12 · [Chapter overview](README.md) · Previous: [06 · The three persona scripts](06-persona-scripts.md) · Next: [08 · Project: the Godavari stakeholder map](08-project-godavari-stakeholder-map.md)

---

## 7.1 What has changed about stakeholder maps in AI deployments

The grid is from 1991 and the four roles would have been recognisable to a Palantir Delta in 2012.
Three things are specific to AI deployments in 2026 and the published playbooks reflect them:

| Pattern | What it is | Why it is new |
|---|---|---|
| **The eval owner as a named role** | the senior individual contributor whose labels define "correct", co-designing the rubric in weeks 3 to 4 (the discovery playbooks), distinct from the sponsor | a deterministic system is correct or broken; a model's output is judged, and someone has to be the judge in writing before the golden set (Day 14) can exist |
| **The CISO as a gate on model choice, not just hosting** | "does your model train on our data", "which country is the server in", training-use and retention policies in the questionnaire (Day 23) | security used to decide where software ran; now it decides which model may be called, through which gateway, with what data (Days 24 and 25) |
| **The sceptic as a test-case source** | the person who says "it will never read handwritten income proofs" is asked for file types, not converted | model failures are categorical ("this kind of document"), so a sceptic's objections map directly onto eval categories |
| **Adoption as a measured stakeholder outcome** | "curiosity drives initial adoption, value drives sustained usage" (Atlassian); operators' usage tracked as a metric from day one (Day 33) | an AI tool that is optional and sits beside a spreadsheet loses to the spreadsheet silently; the operators' row has a number on it now |

## 7.2 What is hype

| Claim | What is true | What to do instead |
|---|---|---|
| "An AI agent can draw the stakeholder map from the customer's Slack and email." | it can list names and frequencies; it cannot know who is cc'd because they can object, who people apologise to, or that the compliance head reports to the audit committee | use it to draft rows from your own notes (section 08.6), never from the customer's data, which the CISO has not allowed you to read anyway |
| "The sponsor is the customer; everyone else is a requirement." | the sponsor signs; the operators decide whether it is used; the eval owner decides whether it is right | three lists (section 04.3), three persona scripts |
| "Get executive buy-in and the rest follows." | buy-in gets you into the building; it does not get a service account, a labelled file or a used tool | the blocker in week 1, the champion found, the sceptic interviewed |
| "Stakeholder management is a project-manager's job, not an engineer's." | 70 percent or more of FDE postings ask for customer-facing discovery; the decomposition round scores it; the FDE is the person in the room when the CISO asks where the PDF goes | own the map; it decides the architecture (the auditor's row alone changes three layers of the skeleton) |
| "Interest is fixed." | interest moves: the CISO's rises the week a prototype touches real data; the COO's falls after the readout until the next board date | re-score monthly (section 07.3) |

## 7.3 Production concerns: the map goes stale

A stakeholder map drawn in week 0 and never touched is wrong by week 8. What changes, and the
habit that keeps it right:

| What changes | Example at Godavari | Habit |
|---|---|---|
| People leave or move | the Vijayawada team lead is promoted to a branch role in month three; the champion is gone | a named second for every row with "must change: yes"; Day 28 treats "the champion has left" as a sign you are not done |
| Interest rises or falls | the CISO's interest goes from 2 to 5 the week the pilot touches production files | re-score power and interest at every Day 8 checkpoint (weeks 2, 4, 6, 12); rerun the script |
| Roles split | "40 analysts" becomes three rows after Day 6: the ten in the pilot, the thirty watching, the two labelling | let rows split; never merge them back for tidiness |
| New ghosts appear | an internal audit team you did not know existed asks for the model's change log | the "who gets the letter" question again, every month |
| The sponsor's number moves | "three days" becomes "three to four days in the pilot branches by day 90" (Day 9) | the sponsor's row carries the current sentence and the date it changed |
| Your own side changes | Kaagaz's CEO asks whether a second lender wants the same pattern (Day 35) | the own-side row is reviewed in the internal weekly, not only the customer's |

Version the map the way Day 10 versions the discovery document: updated at every checkpoint, never
rewritten, with the date in the file. The engagement folder keeps the week-0 version beside the
current one; the difference between them is a large part of what you learned.

## 7.4 A note on what the map says about people

The map records what people said, what they want and how they could stop the work. It is read by
the sponsor, often by the people on it, and sometimes by their managers. Three rules keep it a
working document rather than a liability:

- **Their words, not your judgement.** "Three vendors have broken this system before" is a quote;
  "obstructive" is an opinion that will be read by the person it describes.
- **Roles and capabilities, not character.** "Stops it by: veto" describes a power the CISO has
  and should have. It does not say she will use it.
- **Nothing a person would be surprised to read.** If a row could not be shown to the person in it,
  rewrite the row. The sceptic's row says "expects it to fail; the 2019 pilot did not read handwritten
  income proofs", which she would agree with and probably said herself.

The map contains names and views of identifiable people at the customer, which is personal data in
the ordinary sense. Keep it in the engagement folder under the same handling as the rest of the
customer's material, and do not paste it into tools the CISO has not approved (Day 39 owns what
never goes into an agent's context).

## 7.5 Key takeaways

- New in 2026: the eval owner as a role, the CISO as a gate on model choice, the sceptic as a
  source of test cases, adoption as a stakeholder metric.
- The hype is "the sponsor is the customer" and "an agent can draw the map from Slack". Neither
  survives a CISO.
- Re-score at every checkpoint; name a second for every must-change row; let rows split.
- Their words, roles not character, nothing they would be surprised to read.
