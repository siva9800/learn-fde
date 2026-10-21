# 08 · 2026 Patterns and Production Concerns

> Day 10 · Section 8 of 13 · [Chapter overview](README.md) · Previous: [07 · The Part 2 retrospective](07-the-part-2-retrospective.md) · Next: [09 · Project: the Godavari discovery document](09-project-the-godavari-discovery-document.md)

---

## 8.1 What practitioners do in 2026

**The document is assembled, not written from scratch, and an agent can do much of the assembly.**
Given the six artifacts, a coding or chat agent produces a well-structured first draft in minutes. That
is real and worth using. What it cannot do is decide what each reader needs, and it reliably makes
three mistakes (section 09.6): it invents connecting numbers, it softens conditions into adjectives,
and it drops the refusals because nothing in the sources looks like a requirement. Use it for the
first draft and for the cross-check; do the cutting yourself.

**Docs as code.** The working copy is Markdown in a repository, beside the artifacts it links, so links
can be checked and changes diffed. A check like this chapter's script runs before every version goes
out. The signed copy of record is still a PDF per version on the customer's side. Both, not either.

**Pre-registration travels with the document.** Day 9's metric definitions are signed alongside the
discovery document, not after the pilot. Teams that learned this from experimentation practice now
treat an unsigned metric definition as an open risk.

**Short, asynchronous pre-reads.** A recorded five-minute walk-through of page one, sent with the
pre-read, lets the COO's staff brief him before Friday. It does not replace the meeting; the readout
exists for the objections that need two people in the same room.

**AI meeting notes, with the customer's permission.** Many teams now let a transcription tool draft the
readout's minutes. At Godavari, Day 6 recorded nothing and notes stay on Godavari's SharePoint; a
vendor's transcription service would be a new subprocessor for the CISO's review (Day 23). Ask first;
take notes by hand if the answer is no.

## 8.2 What is hype

| Claim | What is true |
|---|---|
| "AI writes the discovery document; the FDE just reviews it" | it drafts well and judges badly; the hard part is what to cut and what to refuse, which is the FDE's |
| "A live dashboard replaces the document" | a dashboard shows numbers; it does not record who agreed to what, or why something was refused |
| "Skip the readout; send it for e-signature" | the objections that need the room (C2, C3) then arrive in week eight, one at a time, by email |
| "The document is done once signed" | it is versioned at every checkpoint; a document unchanged at week eight is not being used |
| "Longer is more thorough" | the CISO reads her section in full only if it is a page; the rest is links |

## 8.3 Production concerns

**Confidentiality.** The document describes Godavari's security posture, its audit exposure and its
business case. Treat it as the customer's confidential document: on their SharePoint, shared by name,
never pasted into a public AI tool. If you use an agent to draft it, use one your contract and the
CISO allow (Day 39 owns the rules for agents on customer material).

**No PII inside it.** The document quotes numbers, never files. If an example needs a file, use a
golden-set ID the eval owners can look up, not a customer's name or PAN.

**It feeds the security review.** Section 8 is the first draft of answers Day 23's questionnaire will
ask: where data is processed, who holds credentials, what is logged, what is retained. Keeping the two
consistent saves the CISO a round of questions.

**The cost of the readout is people's hours.** Eight senior people for an hour, plus four pre-read
conversations. That is why the pre-reads exist: the meeting is spent only on what needs everyone.

**Decision latency is a metric.** Count the days from "decision needed" to "decided" in the log. At
Godavari, the four open items have dates within two weeks. If that interval grows, the engagement is
slowing down before any milestone slips, and Day 29's weekly readout should say so.
