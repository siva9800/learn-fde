# Transcript 05 · The compliance head, blocker and rule owner

> Day 6 discovery pack · Interview 5 of 10 · Persona: admin (rules) · Where: her office, Hyderabad HQ · When: week 2, Monday, 13:00 · Length: 55 minutes · Recording: none · Synthetic conversation for the course.

**In the room:** the compliance head (CH); the FDE (F).

## Conversation

**F:** You said in week one that no customer PII leaves India. I have written that down as a constraint that cannot move. Today I want to understand the checklist, because the analysts tell me a third of files go back for a missing document, and I want to know which rules are fixed and which are judgement.

**CH:** The fixed ones come from the RBI's KYC Master Direction. Proof of identity, proof of address, a photograph, PAN or Form 60. For a loan we add income proof and the product documents: the dealer invoice for a two-wheeler, the valuation for gold, the bank statement for salaried. Fourteen for two-wheeler, nine for gold, sixteen for small-business.

**F:** Those are in the Word checklist the analysts print?

**CH:** Yes. I update it when a circular changes. The analysts do not always get the new one. Last year the Aadhaar masking rule changed and three branches were still sending unmasked copies in August.

**F:** Where is the judgement?

**CH:** Which address proof is acceptable. The Master Direction lists officially valid documents, but a customer brings a rent agreement, or a gas bill in the father's name, and the analyst decides. Senior analysts decide well. Junior ones send the file back to be safe. That is half of the send-backs, I think.

**F:** Is the list of acceptable alternatives written anywhere?

**CH:** In my head and in Lakshmi's. No.

**F:** If I asked you for a week to write it down, as rules that a program could apply, would that be possible?

**CH:** It would be useful for me as well. But I sign it, and if it changes, I sign the change. I do not want a machine deciding that a gas bill is an address proof because it saw one accepted last year.

**F:** That is exactly how I would build it: the completeness rules as code that you sign, and the model never allowed to override them. The model reads the documents; your rules decide whether the file is complete.

**CH:** Then I can live with it.

**F:** What happens when a file is wrong? A mandatory document is marked present and it was not.

**CH:** The auditor samples files in March. A missing KYC document is an observation. Repeated, it is a finding, and findings go to the board and to the RBI. In the worst case there is a monetary penalty, and my name is on the response. So: never mark a document present unless it is present. I would rather it says "cannot tell" and a person looks.

**F:** And the decision itself, the sanction?

**CH:** A human. Named. With the documents the decision rested on, retrievable for seven years. The auditor's question is always the same: show me the decision, who made it, and what it rested on.

**F:** Would you be the person who stands in for the auditor when we design that trail?

**CH:** I already am. Nobody else in this building has sat across the table from him.

**F:** One more. The analysts receive pages by WhatsApp from branch staff when a document arrives late.

**CH:** (long pause) I know. I have not been able to stop it, because the alternative is the customer waiting another day. If your system makes the proper channel as fast as WhatsApp, it stops by itself. If it does not, it continues and I keep not knowing officially.

**F:** For the prototype, before the CISO's review, may we use real files?

**CH:** Masked. I will approve a set of fifty, with names and account numbers blacked out, for use on a machine in this building. Not one page leaves this building before the review.

## Read-back

Confirmed: the fixed rules and the three document counts, the unwritten alternatives list and her week to write it, rules as signed code, "cannot tell" over a guess, the human sanction with a seven-year trail, fifty masked files on-prem.

## Coded notes

| Code | Verbatim evidence | Kind |
|---|---|---|
| NO_PII_OUTSIDE_INDIA | "Not one page leaves this building before the review." | constraint |
| RULES_AS_SIGNED_CODE | "I sign it, and if it changes, I sign the change. I do not want a machine deciding." | architecture |
| MISSING_DOC_TOP | "Which address proof is acceptable. That is half of the send-backs, I think." | scope |
| ALTERNATIVES_UNWRITTEN | "In my head and in Lakshmi's. No." | scope |
| WRONG_MEANS_AUDIT_FINDING | "A missing KYC document is an observation. Repeated, it is a finding." | constraint |
| FLAG_UNSURE_NOT_GUESS | "I would rather it says 'cannot tell' and a person looks." | architecture |
| HUMAN_DECISION_REQUIRED | "A human. Named. With the documents the decision rested on, retrievable for seven years." | architecture |
| NEVER_AUTOMATE_DECISION | "Show me the decision, who made it, and what it rested on." | architecture |
| WHATSAPP_CHANNEL | "I know. I have not been able to stop it." | architecture |
| PROTOTYPE_ON_PREM_MASKED | "Masked. I will approve a set of fifty." | constraint |
| WILLING_TO_LABEL | "It would be useful for me as well." (a week to write the rules) | scope |
| CHECKLIST_DRIFT | "The analysts do not always get the new one." | scope |
