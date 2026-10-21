# 07 · 2026 Patterns, Hype, and Production Concerns

> Day 18 · Section 7 of 13 · [Chapter overview](README.md) · Previous: [06 · Corrections and explanations](06-corrections-and-explanations.md) · Next: [08 · Project: the review-queue model](08-project-the-review-queue-model.md)

---

## 7.1 What practitioners use (as of October 2026)

- **Grounded extraction with page regions.** Document-extraction services and vision-capable models can return, with
  each field, the page and a region or quote it came from. This is the raw material for the crop. Treat the region as
  a claim, exactly as Day 11 treats the quote: check that the text inside the box is what the value says, and show a
  warning when it is not. Names and response shapes differ by vendor and change often; Day 12's client layer is where
  that difference is absorbed.
- **Human-in-the-loop as a workflow state.** Agent and workflow frameworks now ship "interrupt for approval"
  primitives. They give you a pause; they do not give you the screen, the bands, the forced look or the record. The
  gate belongs to Day 17's state machine; what the human sees at the gate is this chapter.
- **Corrections into the eval loop.** Teams that ship well route every correction to the development set and refit
  thresholds on a schedule, never on the test set. The schedule matters more than the tooling.
- **Sampling for quality in production.** A fixed random share of "machine-accepted" work goes to a blind human
  check, reported with an interval. It is old (statistical quality control predates software) and it is still the
  only honest measure of the band nobody looks at.

## 7.2 What is hype

| Claim | Why to be careful |
|---|---|
| "The model's confidence is calibrated, so route on it alone" | a score is a ranking signal at best; the golden set showed confidently-wrong values at 0.90 to 0.97 that a threshold cannot separate. Route on it only together with deterministic checks and evidence |
| "Let the model explain its reasoning to the operator" | prose explanations borrow trust; show the evidence chain (value, quote, check, rule, clause). Model prose only where code verifies it (the branch note) |
| "Auto-approve the clean files" | at Godavari it is decision D07 and the auditor's condition; elsewhere it is a business decision taken with the eval and the spot-check numbers, never a UI default |
| "A self-verifying model removes the need for review" | a second call to the same model shares its blind spots (Day 14, section 06.7: never self-judge unchecked) |

## 7.3 Production concerns

**Where the crops live.** A crop of a PAN card is a copy of customer PII. It is generated where the pages are (the
machine in the Hyderabad building during the pilot, under decision D08; AWS Mumbai after M16), stored with the file,
retained with it, and never sent to a vendor's support channel or pasted into a ticket. Residency is Day 24's; the
screen must not create a second, unmanaged copy of the file.

**Every page view is a view.** The CISO's view log (Day 6) applies to the review screen: opening a file page records
who, when and which file, the same way Day 15's retrieval logs what it returned. The branch rule applies to the
screen too: no page renders for an analyst outside the file's branch group.

**Latency.** The analyst should never wait for a crop. Generate the screen's evidence at ingestion (the 2 a.m. SFTP
batch), so that the 9 a.m. "ready" promise (Day 9) covers it. Rendering itself is cheap: the project renders twelve
pages and the queue in well under a second.

**Monitoring.** Hand Day 19 these signals, each per branch, per field and per band: the band mix; the correction
rate in the review band against the expected wrong share (5.4 percent on the test split); the dwell distribution;
spot-check disagreements and their adjudicated outcome; and the share of files where the forced field was corrected.
A rising correction rate in the auto band's spot checks is the first sign of drift.

**The kill switch is data, not code.** When spot checks find a wrong auto-accepted value in a cell, the response is
to set that cell's status to "withdrawn" in the bands file (versioned, reviewed by the eval owners), which moves it to
review and onto the standing forced-look list at the next file. No deployment, no prompt change. Then investigate.

**Change control.** The band policy, the impact weights, the citation table and the Telugu labels are all reviewed by
named Godavari people: the eval owners for the bands and weights, the compliance head for the citations, Lakshmi and
the Vijayawada team lead for the labels. Each file says its status at the top, and the screen's banner repeats it.

**The calendar.** No band refit during the change freeze (17 to 31 December), only withdrawals. New analysts in the
Hyderabad wave (6 January) and the Vijayawada wave (18 January) get dwell floors from their own first week. Month-end
and the RBI inspection from 1 February are when the workload signals matter most.

## 7.4 Key takeaways

- Page regions and quotes are claims to check, then the raw material for the crop.
- Framework interrupts give a pause, not a screen; the gate is Day 17's, the screen is this chapter's.
- Route on confidence only with deterministic checks and evidence; prose explanations borrow trust.
- Crops are PII; views are logged; evidence is built at ingestion; the kill switch is a reviewed data change.
