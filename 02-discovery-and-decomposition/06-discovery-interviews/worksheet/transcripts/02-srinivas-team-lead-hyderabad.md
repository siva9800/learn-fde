# Transcript 02 · Srinivas, credit-ops team lead, Hyderabad

> Day 6 discovery pack · Interview 2 of 10 · Persona: operator lead · Where: a meeting room beside the Hyderabad credit-ops floor · When: week 1, Thursday, 09:00, before the counting session · Length: 50 minutes · Recording: none; notes read back · Synthetic conversation for the course.

**In the room:** Srinivas (S), Hyderabad credit-ops team lead, twenty-two analysts report to him; the FDE (F).

## Conversation

**F:** You walked me round the floor on Monday. Today I want the parts that are not on the floor. How does a file get to an analyst?

**S:** The batch lands at about two in the morning in the SFTP folder, by branch. At eight I open the folder and the tracker and I assign. I know who is fast on gold loans, who is good with small-business files, who is on leave. I type the file number into their workbook. There is no queue in the core system; the core thinks every analyst can open every file.

**F:** Every file in the company?

**S:** Every file in Hyderabad region. The core is tied to AD. My analysts are in the Hyderabad credit-ops group, so they see Hyderabad region's branches. Vijayawada sees theirs. A branch user sees only their branch. When the Vijayawada lead was on leave in June I could not see her queue at all. I raised a ticket. IT added me to her group by hand. It took two days, and then they forgot to remove me.

**F:** So who can see what is decided by AD groups.

**S:** By AD groups, which come from HR. When someone transfers branch, HR changes the record, the group changes the next night. There is no group for "all branches". The people who can see everything are IT and, I think, the compliance desk. I am an exception they typed in.

**F:** What does the tracker do that the core does not?

**S:** It knows what we are waiting for. The core has a status: received, in process, sent back, sanctioned. "Sent back" tells you nothing. The tracker says "waiting on bank statement since the fourth, called twice". The core has a free-text remarks box for send-back reasons and every analyst writes it differently. "Addr proof", "address", "KYC pending". You cannot count it.

**F:** The COO says the analysts are slow.

**S:** (pause) My people spend the week chasing branches. A file that arrives complete is done in a day and a half, batch included. A file that arrives incomplete is done in eight or nine. A third arrive incomplete. The branches say we send files back for no reason. We say they send rubbish. Both sides have been saying that for five years.

**F:** When a file comes back from a branch, how do you know?

**S:** The branch re-scans and it comes in the next batch, under the same file number, and whoever is assigned sees it. Or it comes by WhatsApp to the analyst and never comes in the batch. Then the core file is incomplete forever and the paper file is complete.

**F:** What number would you believe, if I told you the project had worked?

**S:** Files per analyst per day. Not turnaround. Turnaround depends on the branches. If my people are doing eight a day instead of five, I will believe you.

**F:** What is a bad day for you?

**S:** Month end, like everyone says. And March. March is the RBI audit. Do not put anything new in front of my people in March. Nothing. They are pulling paper files for the auditor.

**F:** Has anyone tried to automate this before?

**S:** 2019. An OCR vendor. It read the printed salary slips and it could not read a handwritten income declaration, which is half of the small-business files. It guessed. One of my seniors caught it putting a monthly income as annual. We switched it off in six weeks. The vendor said we had not trained it. We were not told we had to.

**F:** If this project put a queue in front of your analysts, with the fields already typed and the fourteen documents already checked, what would stop them using it?

**S:** If it is slower than the tracker. If it does not know what we are waiting for. If it adds a screen. My people have the core, the PDF, the tracker and the checklist open. A fifth window is a no.

**F:** Where would it have to live?

**S:** In the tracker's place. Not beside it. And it must write back what it did, so that when the auditor asks in March, there is one file, not two.

## Read-back

Srinivas corrected the batch time: "two in the morning for the file transfer; the credit check is the six pm batch, two different batches." He added that the Word checklist is per product and that gold loans have nine documents, not fourteen.

## Coded notes

| Code | Verbatim evidence | Kind |
|---|---|---|
| SHADOW_TRACKER | "There is no queue in the core system." "I type the file number into their workbook." | architecture |
| BRANCH_ISOLATION | "A branch user sees only their branch." "When the Vijayawada lead was on leave in June I could not see her queue at all." | architecture |
| ACCESS_VIA_AD_GROUPS | "By AD groups, which come from HR. There is no group for 'all branches'. I am an exception they typed in." | architecture |
| SENDBACK_FREE_TEXT | "'Addr proof', 'address', 'KYC pending'. You cannot count it." | scope |
| WAIT_ON_BRANCH | "A file that arrives incomplete is done in eight or nine." | metric |
| BLAME_BETWEEN_SIDES | "The branches say we send files back for no reason. We say they send rubbish." | adoption |
| WHATSAPP_CHANNEL | "Or it comes by WhatsApp to the analyst and never comes in the batch." | architecture |
| TURNAROUND_NUMBER | "Files per analyst per day. Not turnaround." | metric |
| BAD_DAY_MONTH_END | "Month end, like everyone says. And March. March is the RBI audit." | constraint |
| PAST_VENDOR_FAILURE | "2019. An OCR vendor. It guessed. We switched it off in six weeks." | adoption |
| HANDWRITTEN_TELUGU | "It could not read a handwritten income declaration, which is half of the small-business files." | scope |
| TRACKER_LOSS_FEAR | "In the tracker's place. Not beside it. And it must write back what it did." | adoption |
| BATCH_6PM | "Two in the morning for the file transfer; the credit check is the six pm batch." | constraint |
