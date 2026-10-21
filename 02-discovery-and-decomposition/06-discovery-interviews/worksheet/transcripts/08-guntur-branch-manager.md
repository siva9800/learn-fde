# Transcript 08 · The Guntur branch manager, upstream producer (far branch)

> Day 6 discovery pack · Interview 8 of 10 · Persona: operator (upstream) · Where: a phone call, Guntur branch · When: week 2, Wednesday, 18:00, after the branch closed · Length: 30 minutes · Recording: none · Synthetic conversation for the course.

**In the room:** the Guntur branch manager (G), on the phone, twelve years at Godavari; the FDE (F). Chosen because Guntur sends more phone photos than any branch in the Vijayawada region, according to the tracker.

## Conversation

**F:** I have talked to Kukatpally. I wanted a branch that is far from both offices, and the Vijayawada team said yours sends the most photographed pages. Can you tell me why?

**G:** The scanner. It was broken for two weeks in August and the replacement is slow; it jams on stapled pages. So my officer photographs the pages on his phone and sends them to the analyst, and we courier the originals to Vijayawada on Fridays. The analyst prints the photos and works from them until the courier arrives.

**F:** How many of your files go that way?

**G:** This month, most of them. Normally one in four.

**F:** What do the files look like?

**G:** Small-business, mostly. Shop owners, auto owners. The income proof is a handwritten declaration in Telugu with the shop's monthly sales, signed by the customer and one witness. There is no salary slip. The bank statement is often a passbook, photographed page by page.

**F:** When one of those files comes back from Vijayawada, what is usually the reason?

**G:** Income proof. They say the declaration is not clear, or the figure does not match the passbook. I understand that. But it takes four days to come back and then the customer has gone to the village, and we start again.

**F:** When a file is wrong after sanction, a figure read wrongly, who hears about it?

**G:** Me. The customer gets a smaller loan than the dealer promised, or an EMI he did not expect, and he comes to the branch. Vijayawada never sees him. I do.

**F:** Which files can you see in the core system?

**G:** Guntur's. The regional manager in Vijayawada sees all of ours. I do not want to see other branches and I do not want them to see mine.

**F:** If the system read your handwritten declarations, what would you want it to do when it is not sure?

**G:** Say so, and send it to a person. Do not send me a file back saying "income proof unclear" when a person could have read it in a minute.

**F:** What is your bad day?

**G:** Market day. Thursday. Every shop owner comes on Thursday because the shop is closed. We do twenty files on a Thursday and four on a Monday.

**F:** If we tested the system on your files, the photographed ones, the Telugu ones, would you give me twenty recent ones?

**G:** Take the whole month.

## Read-back

Confirmed by phone: the scanner, the photographs and the Friday courier, one in four normally, handwritten Telugu income declarations and passbooks, income proof as the top send-back reason here, branch-only visibility, Thursday as the peak, a month of files offered.

## Coded notes

| Code | Verbatim evidence | Kind |
|---|---|---|
| WHATSAPP_CHANNEL | "My officer photographs the pages on his phone and sends them to the analyst, and we courier the originals on Fridays." | architecture |
| PHONE_PHOTO_INPUT | "Normally one in four." (of Guntur's files arrive as phone photographs) | scope |
| HANDWRITTEN_TELUGU | "The income proof is a handwritten declaration in Telugu. The bank statement is often a passbook, photographed page by page." | scope |
| MISSING_DOC_TOP | "Income proof. They say the declaration is not clear, or the figure does not match the passbook." | scope |
| WAIT_ON_BRANCH | "It takes four days to come back and then the customer has gone to the village, and we start again." | metric |
| WRONG_MEANS_CUSTOMER_AT_BRANCH | "He comes to the branch. Vijayawada never sees him. I do." | metric |
| BRANCH_ISOLATION | "I do not want to see other branches and I do not want them to see mine." | architecture |
| FLAG_UNSURE_NOT_GUESS | "Say so, and send it to a person." | architecture |
| BAD_DAY_MONTH_END | "Market day. Thursday. We do twenty files on a Thursday and four on a Monday." (the far-branch version of the peak) | constraint |
| WILLING_TO_LABEL | "Take the whole month." | scope |
