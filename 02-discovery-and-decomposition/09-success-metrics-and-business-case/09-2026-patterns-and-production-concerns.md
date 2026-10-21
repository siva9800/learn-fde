# 09 · 2026 Patterns, Hype, and Production Concerns

> Day 9 · Section 9 of 14 · [Chapter overview](README.md) · Previous: [08 · Pre-registration](08-pre-registration-and-gamed-numbers.md) · Next: [10 · Project](10-project-baseline-pack-and-business-case.md)

---

## 9.1 What practitioners do in 2026

- **The metric is agreed with the customer's experts before the model is chosen.** This is the
  published OpenAI FDE practice (eval-driven development, Part 2's sources) and the reason Day 14's
  golden set is agreed against this chapter's numbers. The 2026 version goes one step further: the
  business case names the eval threshold below which it fails (section 08.5), so the eval is not a
  quality gate floating free of value.
- **The system measures itself from the first slice.** The walking skeleton (Day 7) logs the four
  timestamps and the review-screen time per file from week three, with the same definitions as the
  baseline. Day 19's dashboard then computes the pre-registered metric, not a convenient cousin of it.
- **Value cases are versioned like code**: the pack, the seed, the script and the signed definitions
  live in the engagement folder, and every readout quotes a version.
- **Outcome-linked pricing** (per file, per outcome) is discussed more by AI vendors; it only works
  when both sides signed the baseline and the definition before the first invoice.

## 9.2 What is hype

| Claim you will hear | Why it does not belong in a customer's case |
|---|---|
| "AI improves analyst productivity by 40 percent" (a vendor or analyst-firm study) | someone else's workflow, task mix and baseline; at most a prior for your capture share, never a line in the case |
| an ROI calculator that multiplies seats by hours by salary | hours times salary, the problem's size quoted as the solution's value, and no capacity-versus-cash distinction (sections 05.3, 05.4) |
| "the model is 98 percent accurate" as the headline | the bottom rung (02.2); on which fields, which files, measured by whom? |
| "payback in three months" on a lending system | usually disbursement pulled forward counted as annual (06.3) |
| an AI-written business case produced from a meeting transcript | fluent, complete-looking, and built on numbers nobody measured (section 10.6 shows the mistakes) |

## 9.3 Production concerns

- **PII in the sample.** File numbers only in the pack; no names, PAN numbers or amounts tied to a
  person. The working sheet stays on Godavari's SharePoint (Day 6, B2), with a retention period the
  compliance head approves; purpose limitation under the DPDP Act is Day 24's.
- **The definition must survive the system.** When the tool goes live, the "first opened" timestamp
  moves from the core's record-creation time to the review screen's. Write the mapping down, and run
  both for a fortnight, or the pilot's queue age is measured on a different clock from the baseline's.
- **Seasonality.** March, month-end and festival weeks are flagged in every comparison (Day 37).
- **Cost of measuring.** If a metric needs a manual count every month, design the tool to log it.
- **Assumptions drift.** Re-run the case at each checkpoint with new inputs, and hand the script to
  Godavari's people by day 90 (Day 28): Bhavani and the team leads, not the FDE, run it after.

## 9.4 Key takeaways

- The 2026 pattern ties the eval threshold to the business case and makes the system log its own
  metrics from the first slice.
- Vendor productivity figures are priors, not lines in a customer's case.
- Keep PII out of the pack, keep the clock the same across the switch-over, and hand the measurement
  to the customer's people before you leave.
