# Transcript 09 · The senior analyst, Hyderabad, the sceptic

> Day 6 discovery pack · Interview 9 of 10 · Persona: operator (eval owner and sceptic) · Where: her desk, Hyderabad credit-ops floor, after hours · When: week 1, Tuesday, 15:00, after the afternoon's shadowing · Length: 45 minutes · Recording: none · Synthetic conversation for the course.

**In the room:** the senior analyst (A), fourteen years, the person Srinivas named as "the one who caught the OCR"; the FDE (F).

## Conversation

**F:** Srinivas told me you switched off the last vendor. I would like to hear what it got wrong, in as much detail as you remember, because whatever it was, it is on my list of things to test first.

**A:** It was 2019. It read the printed salary slips, I will give it that. Then a small-business file came through. Handwritten income declaration, Telugu, monthly sales of forty thousand. It typed four lakh eighty thousand as monthly. It had multiplied by twelve, I think, or it read the annual line from the form. The sanction went through at ten times the eligibility. I caught it the next morning because the EMI looked wrong for an auto driver. If I had been on leave, that loan would have been disbursed.

**F:** What happened after?

**A:** They said we had not "trained" it on our forms. Nobody had told us we had to. We switched it off. The vendor left. Nobody asked me what I would have needed.

**F:** What would you have needed?

**A:** For it to say "I cannot read this" instead of guessing. A handwritten Telugu declaration is a person's job. A printed slip is a machine's job. The machine should know which is which.

**F:** When it is wrong today, when the branch has typed a wrong figure on the form, who finds it?

**A:** I do, when I read the slip against the form. It is the whole job. The typing is nothing; the reading is the job. If your system does the typing and I still do the reading, fine. If your system does the reading and I only check what it flags, then on a month-end day I will check nothing and it had better be right.

**F:** What happens to you when it is wrong and you did not catch it?

**A:** An audit query, with my employee ID on it. Not the vendor's.

**F:** What would have to be true for you to trust it on a printed slip?

**A:** Show me a hundred files I have already done, with my figures, and show me where it agreed with me and where it did not, field by field. Not a percentage. The actual files. If it disagrees with me on three and it is right on two of them, I will listen.

**F:** If I asked you to be one of the two people whose answers are the standard for those hundred files, would you?

**A:** If my answers are the standard and not the demo's, yes. And I want to see every failure, not a summary.

**F:** You have the core, the PDF, the checklist and the tracker open. Where would a review screen have to sit?

**A:** Where the tracker is. It has to know what I am waiting for. If it does not know the file is waiting on a bank statement, it is a toy.

**F:** What should never be automated?

**A:** The decision. And the reading of anything handwritten, until it has proved itself on my hundred.

**F:** What is a bad day?

**A:** When the batch fails at six and reruns at nine and I come in to two days of results. And March.

## Read-back

Confirmed: the 2019 failure in detail (monthly read as annual on a handwritten Telugu declaration), "say cannot read" over a guess, the analyst as the person who corrects, the audit query with her ID, a hundred files with her figures as the standard, the review screen in the tracker's place, no automation of the decision or of handwritten reading until proven.

## Coded notes

| Code | Verbatim evidence | Kind |
|---|---|---|
| PAST_VENDOR_FAILURE | "It typed four lakh eighty thousand as monthly. The sanction went through at ten times the eligibility." | evidence |
| HANDWRITTEN_TELUGU | "A handwritten Telugu declaration is a person's job. A printed slip is a machine's job." | scope |
| FLAG_UNSURE_NOT_GUESS | "For it to say 'I cannot read this' instead of guessing." | architecture |
| ERROR_CORRECTION_BY_ANALYST | "I do, when I read the slip against the form. It is the whole job." | architecture |
| WRONG_MEANS_AUDIT_FINDING | "An audit query, with my employee ID on it. Not the vendor's." | constraint |
| WILLING_TO_LABEL | "Show me a hundred files I have already done, with my figures. If my answers are the standard and not the demo's, yes." | scope |
| SHADOW_TRACKER | "Where the tracker is. If it does not know the file is waiting on a bank statement, it is a toy." | adoption |
| NEVER_AUTOMATE_DECISION | "The decision. And the reading of anything handwritten, until it has proved itself on my hundred." | architecture |
| BAD_DAY_MONTH_END | "When the batch fails at six and reruns at nine. And March." | constraint |
| BATCH_6PM | "When the batch fails at six and reruns at nine and I come in to two days of results." | constraint |
