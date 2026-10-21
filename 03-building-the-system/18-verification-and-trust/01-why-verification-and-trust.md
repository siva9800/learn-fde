# 01 · Why Verification and Trust Live in the Interface

> Day 18 · Section 1 of 13 · [Chapter overview](README.md) · Next: [02 · Trust per field: show the evidence](02-trust-per-field-show-the-evidence.md)

---

## 1.1 Two screens on the same Monday

Monday 7 December 2026, 10 a.m., the first day of the pilot (milestone M13). A Guntur file opens on an analyst's
screen in Vijayawada. The system has read its dealer quotation and says the on-road price is **37,150 rupees,
confidence 93 percent**.

On the first screen, that is all she sees: a value and a green tick. The price is plausible for a used scooter.
She has eleven more files. She moves on. The core system now carries a price that is one lakh rupees too low, and
the margin rule that should protect Godavari has been fed a wrong number.

On the second screen, the value sits beside the line it was read from:

```text
  dealer quotation, page 10:   On-road price: Rs I,37,150      <- the quote, highlighted
```

She sees the capital "I" where a "1" should be in two seconds, corrects the value to 137150, picks "misread
character" as the reason, and the correction becomes a labelled example for the golden set. The model, the
confidence and the file are identical on both screens. The only difference is what the interface shows.

This is the case Day 14 found in its confidently-wrong list (GF-40821, six of seven such errors were the on-road
price, all the same OCR mistake). Day 14 measured it. This chapter decides what the analyst sees so that it is
caught every time, and so that the screen earns the trust that the business case depends on.

## 1.2 Why it matters for your career

The published pattern is that building takes weeks and trust takes months. As the ZenML LLMOps database summarises
OpenAI's forward deployed engineering work (read 21 October 2026):

- **Morgan Stanley.** "The technical pipeline was built within 6-8 weeks", but "it took an additional 4 months of
  pilots", with "user feedback collection, evaluation refinement, and iteration to build trust with wealth advisors".
  The FDE team "worked closely with advisors to label data, verify outputs" and "develop verification tools for
  cases where confidence was lower". The result reported is 98 percent adoption among advisors.
- **An APAC automotive manufacturer.** The "customer-conservative approach" included "showing reasoning explanations
  before actions", "providing verification widgets, and exposing detailed tables for manual checking", which the
  summary says "builds trust".

Notice where the four months went: not into the model, into the people checking its work. Applied AI work appears in
80 percent or more of the 1,000 FDE postings analysed in 2026 (Day 2), and the interviewers who ask "how would the
operator know when it is wrong?" are asking about this chapter. An engineer who can only answer "we show a
confidence score" has not designed the part that decides adoption.

## 1.3 What Godavari told you in discovery

Three findings from Day 6 (transcripts in Day 6's worksheet) set the requirements before any screen was drawn:

| Who | What they said | What it forces |
|---|---|---|
| Bhavani, junior analyst | asked whether she would have caught the 2019 pilot's wrong income: "I would not know. That is the honest answer." (REVIEW_WILL_NOT_CATCH_ALL) | review alone is not a safety net; the screen must point at the risky field and show its source |
| The senior analyst, Hyderabad (the sceptic) | "If your system does the reading and I only check what it flags, then on a month-end day I will check nothing and it had better be right." | design against rubber-stamping, and measure it |
| The same senior analyst | "Show me where it agreed with me and where it did not, field by field. Not a percentage. The actual files." | trust is earned per field, with evidence, not per system with a score |

Day 5's map names her as the sceptic and Lakshmi as an eval owner. Both are in this chapter: their own keying error
on the golden set (Day 14, section 03.9) becomes the bar that an auto-accepted field must meet, and they do the blind
second reads that check it.

## 1.4 Where this chapter sits

Day 11 built the pipeline, the envelope, the signed rules and routing by route (blocked, send back, review, ready).
Day 14 built the golden set and measured the confidently-wrong rate. Day 15 built clause-level citations. Day 17, in
parallel, owns the approval state and the gate an approval passes through. This chapter owns **what the operator
sees**: which band each field lands in, what is on the screen first, what the analyst must look at, and what the
system learns from her. It imports Day 11, Day 14 and Day 15 by path and re-teaches none of them.

## 1.5 The hard parts, named early

- **Confidence is not evidence.** A model can be 93 percent sure of a misread. The screen must show the source.
- **The development split is small.** Fifty files cannot reveal a one-in-a-hundred failure. You will watch it miss
  the on-road price, and the test split catch it.
- **Careful people stop being careful.** Highlights that are usually wrong train people to ignore them; month-end
  turns review into a click. You design for that, and you measure it without turning it into surveillance.
- **The auditor and the branch manager need different explanations of the same decision.** Both come from the same
  record.

> **Analogy (Telugu audience).** The family doctor who shows you the report and points at the one number that matters,
> versus the one who hands over a prescription. You trust the first one, and you trust him more after the day he says
> "this one I want to check again".
