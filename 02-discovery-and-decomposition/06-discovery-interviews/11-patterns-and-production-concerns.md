# 11 · 2026 Patterns, the Hype, and Production Concerns

> Day 6 · Section 11 of 16 · [Chapter overview](README.md) · Previous: [10 · Synthesis and confirmation](10-synthesis-and-confirmation.md) · Next: [12 · Project: the discovery pack](12-project-the-discovery-pack.md)

---

## 11.1 What practitioners use in 2026

| Pattern | What it is | Where it helps | Where it does not |
|---|---|---|---|
| **Transcription and note clean-up** | speech-to-text on interviews, then an assistant tidies the notes | cheap and accurate in English and increasingly in Telugu; frees you to listen | only with the interviewee's consent and HR's knowledge; the audio and transcript are customer data, so they stay where the CISO says |
| **Asynchronous interviews at scale** | a vendor's tool sends a structured interview to many users and collects answers; one vendor (getperspective.ai, May 2026) argues for 15 to 40 async interviews in weeks 1 to 2, saying "variance matters more than volume" | breadth: a hundred branch officers could answer "what came back last week and why" | no shadowing; no pause before the honest answer; no read-back; the vendor sells the tool |
| **Assistant-prepared question banks** | an assistant drafts persona scripts from the stakeholder map | a good first draft in minutes (section 12) | it writes leading and hypothetical questions unless told not to |
| **Assistant-assisted coding and synthesis** | an assistant proposes codes and groups quotes | speed on ten transcripts | it invents findings nobody said; section 12 is about this failure |
| **Process mining** | reconstructing the workflow from system event logs | when the real work happens in a system with timestamps | at Godavari the real state is in a tracker with no timestamps and a WhatsApp chat; the logs show the twelve steps, not the nineteen |

## 11.2 What is hype

- **"Synthetic users" instead of interviews.** Tools that generate persona answers from a model are sometimes sold as a substitute for talking to operators. They produce the average answer, which is the sponsor's version. No synthetic user would have said "it typed four lakh eighty thousand as monthly", because that sentence is a memory. The transcripts in this chapter are synthetic because the course needs teaching data; on an engagement, a synthetic transcript is a fabricated finding.
- **"AI will discover the workflow from your documents"** or "automate discovery". It will discover the documented workflow, which is the SOP; the seven undocumented steps are in no document. And the trust built by watching (section 03) comes from a person sitting there.

Use the tools for speed on the parts that are clerical (transcribing, tidying, counting). Keep the parts that need a person in the room.

## 11.3 Production concerns

Discovery has no servers, but it has the same concerns as production, in a different form.

| Concern | In discovery | At Godavari |
|---|---|---|
| **Security and privacy** | notes, recordings, photos of screens and sample files are customer data; under India's DPDP Act personal data needs a purpose and a safeguard (Day 24 owns the law) | notes on Godavari's SharePoint; file numbers, not names; no recording without HR; masked files on a machine in the building |
| **Cost** | your time and theirs; ten interviews, four shadowing sessions, a review, plus travel | most of the 42.5 customer-facing hours in Day 2's planned fortnight, plus the sessions that did not fit it (see `worksheet/interview-plan.md`), and an hour of each interviewee's day; ask for an hour, take forty-five minutes |
| **Latency** | the time from hearing a finding to it reaching the design | coded the same evening; synthesised every three or four interviews; the AD-group finding reached the decomposition in week two |
| **Scale** | 300 branches cannot all be visited | two branch managers chosen near and far; the async breadth tools (11.1) for the rest; the pilot branches revisited in week 7 |
| **Bias** | a sample chosen by the sponsor is the sponsor's version | the plan includes the sceptic, the newest analyst and the far branch, chosen by you |
| **Monitoring** | the map goes stale | revisit at each checkpoint (Day 8); re-shadow in the pilot branches; version the map, never rewrite it |

## 11.4 Key takeaways

- Use transcription, async breadth and assistants for the clerical parts, with consent and under the customer's data rules.
- Synthetic users, automatic workflow discovery and "automated discovery" are hype: they find the documented process and the average answer.
- Discovery has production concerns: notes as PII, the cost of everyone's hours, how fast findings reach the design, sampling bias, and a map that goes stale.
