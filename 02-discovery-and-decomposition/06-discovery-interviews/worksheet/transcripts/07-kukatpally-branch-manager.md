# Transcript 07 · The Kukatpally branch manager, upstream producer

> Day 6 discovery pack · Interview 7 of 10 · Persona: operator (upstream) · Where: the Kukatpally branch, Hyderabad, at the back counter · When: week 2, Wednesday, 12:30, after the labelling call · Length: 40 minutes · Recording: none · Synthetic conversation for the course.

**In the room:** the Kukatpally branch manager (B), nine years at Godavari, four at this branch; the FDE (F); a branch officer at the scanner behind us.

## Conversation

**F:** The COO told me you are the best branch and that you complain the most. I want the complaint. But first, show me how a loan file leaves this branch.

**B:** Customer comes with the dealer's quotation. My officer fills the application form by hand with the customer, collects the fourteen documents, photocopies them, and the customer signs each copy. The file goes in that tray. At five, the officer scans the whole tray into the SFTP folder, one PDF per file. Thirty, forty pages each.

**F:** In what order?

**B:** Whatever order the papers are in. Nobody sorts them. The scanner does not know what a PAN card is.

**F:** What happens when a document is missing at five?

**B:** We send the file anyway, because the customer has signed today and the dealer is waiting. The officer writes "address proof to follow" on the form. Hyderabad finds it the next day and sends the file back. Then we chase the customer, he brings it in two days, and the officer photographs it and sends it to the analyst on WhatsApp, because if we wait for the five o'clock scan it is another day, and then the batch, another day.

**F:** Whose WhatsApp number?

**B:** The analyst's own. We know them. Lakshmi in Vijayawada handled our files for two years before the regions changed.

**F:** What is the complaint?

**B:** Credit-ops sends files back for no reason. Last month, a file came back saying "KYC pending". Everything was there. The analyst wanted a different address proof than the one we sent, and nobody told us which. The customer came to the branch and shouted at me, not at Hyderabad. The dealer took the next customer to a fintech.

**F:** If the system told you on the same day, before the file joined the queue, exactly which document was missing and which rule said so, would that change your day?

**B:** It would change my month. Half of my send-backs are things I could fix in an hour if I knew on day one.

**F:** In the core system, which files can you see?

**B:** Mine. Kukatpally's. When I moved here from Miyapur, for one day I could still see Miyapur and not Kukatpally. Then it flipped. IT said it is from HR.

**F:** Should a branch manager ever see another branch's file?

**B:** No. Never. Our targets are per branch. If I could see Miyapur's pipeline I would know their dealers. The regional manager sees us all; that is his job, not mine.

**F:** What is a bad day here?

**B:** The last three days of the month. We have a target. Every file we can sign, we sign, and we send what we have. I know Hyderabad hates it. I have a target.

**F:** Last question. If I asked you to pick ten of your recent files that came back, and tell me honestly what was wrong with each, so that we test the system on your files and not on clean ones, would you?

**B:** Pick the ten that came back? I can give you thirty.

## Read-back

Confirmed: hand-filled form, fourteen photocopies, scan at five in whatever order, "to follow" files sent anyway, WhatsApp to the analyst's personal number, branch-only visibility from HR, month-end push, thirty send-back files offered.

## Coded notes

| Code | Verbatim evidence | Kind |
|---|---|---|
| FILE_ORIGIN_SCAN | "At five, the officer scans the whole tray into the SFTP folder, one PDF per file. Thirty, forty pages each." | architecture |
| PAGE_ORDER_UNLABELLED | "Whatever order the papers are in. Nobody sorts them." | architecture |
| MISSING_DOC_TOP | "The officer writes 'address proof to follow' on the form." | scope |
| WHATSAPP_CHANNEL | "The officer photographs it and sends it to the analyst on WhatsApp." | architecture |
| BLAME_BETWEEN_SIDES | "Credit-ops sends files back for no reason." "The customer came to the branch and shouted at me." | adoption |
| SENDBACK_FREE_TEXT | "A file came back saying 'KYC pending'. Everything was there." | scope |
| WRONG_MEANS_CUSTOMER_AT_BRANCH | "The customer came to the branch and shouted at me, not at Hyderabad. The dealer took the next customer to a fintech." | metric |
| DAY_ONE_FEEDBACK_WANTED | "Half of my send-backs are things I could fix in an hour if I knew on day one." | scope |
| BRANCH_ISOLATION | "No. Never. Our targets are per branch. If I could see Miyapur's pipeline I would know their dealers." | architecture |
| ACCESS_VIA_AD_GROUPS | "For one day I could still see Miyapur and not Kukatpally. Then it flipped. IT said it is from HR." | architecture |
| BAD_DAY_MONTH_END | "The last three days of the month. Every file we can sign, we sign, and we send what we have." | constraint |
| WILLING_TO_LABEL | "Pick the ten that came back? I can give you thirty." | scope |
