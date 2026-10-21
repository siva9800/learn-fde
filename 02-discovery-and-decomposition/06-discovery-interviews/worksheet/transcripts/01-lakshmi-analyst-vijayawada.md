# Transcript 01 · Lakshmi, credit-ops analyst, Vijayawada

> Day 6 discovery pack · Interview 1 of 10 · Persona: operator · Where: her desk on the Vijayawada credit-ops floor · When: week 1, Wednesday, 14:00, after a full morning of shadowing · Length: 45 minutes · Recording: none; notes read back in the last five minutes · This conversation is synthetic: Godavari Finance and everyone in it are invented for the course.

**In the room:** Lakshmi (L), eleven years as a credit-ops analyst; the FDE (F). The Vijayawada team lead sat in for the read-back.

## Conversation

**F:** Thank you for letting me sit beside you all morning. I am not going to ask what you think of AI. I want to understand what you did today. Can you show me the last file you finished, from the moment it reached you?

**L:** The one before lunch? Two-wheeler loan, Kukatpally branch. It came in last night's batch. First thing I do is open the tracker, not the system. The tracker tells me which files are mine today. Sir assigns them in the morning in the tracker.

**F:** The tracker is the Excel on the shared drive?

**L:** Yes. One workbook per analyst, one row per file. I open my row, then I open the PDF from the SFTP folder, then I open the core system. The core screen takes forty seconds to load. So I open it first and read the PDF while it loads.

**F:** What do you type into the core?

**L:** Everything. Name, address, PAN, the loan amount, the dealer, the vehicle, the income figure, the co-applicant. Sixty-odd fields. The branch has already typed most of this into the paper form, and I type it again. For a clean file it is about one and a half hours with the checking.

**F:** What is "the checking"?

**L:** Fourteen documents for a two-wheeler file. I go down the checklist. The checklist is a Word file the compliance team sends; I have it printed. Today the file had no address proof. The customer gave an Aadhaar with the old address and the branch said the new one would come.

**F:** What did you do when you found that?

**L:** I phoned the branch. I have the numbers in my notebook, because the branch list in the system is two years old. Then I wrote in the tracker: "waiting on address proof since", today's date. The file sits. Usually three days. Sometimes a week if the customer has gone to the village.

**F:** And how does the address proof come back?

**L:** Officially the branch scans it again and it comes in the next night's batch. In practice the branch boy photographs it and sends it to me on WhatsApp, on my own phone, because the scanner batch goes at five and the customer is standing there at six. I print the photo, staple it to the file, and write "received by WhatsApp" in the tracker.

**F:** Is that allowed?

**L:** Nobody has said no. Nobody has said yes. The file in the system does not have that page. If the auditor asks, the paper file has it.

**F:** What happens after the file is complete?

**L:** Income verification, which is reading the bank statement or the salary slips. Then the credit check runs at six in the evening, as a batch, so anything I finish after about four is tomorrow's result. Then the memo, then the credit manager sanctions.

**F:** When something is wrong in the file, a wrong figure, who finds it?

**L:** Me, if I am careful. The branch types the income from the slip; I read the slip again. If I miss it, the credit manager might catch it, or the auditor catches it in March and then it comes back to me with my name on it.

**F:** So the person who corrects errors today is you.

**L:** Me. Always me. If your system reads the slip and reads it wrong, it will still be me who is asked.

**F:** That is exactly what I need to know. What would make that fair?

**L:** Tell me when it is not sure. Do not guess. If it says "unsure" on a handwritten slip, I will read the slip. If it guesses a number and looks confident, I will trust it on a busy day, and that is the day it will be wrong.

**F:** What is a bad day?

**L:** The twenty-eighth to the thirty-first. Branches push every file they have to hit the month's target. We get three times the files, half of them incomplete. The day after a holiday is the same. On a bad day I do not check the fourteen documents properly; I check the big ones and hope.

**F:** Which document is missing most often?

**L:** Address proof. Then bank statement for the salaried ones, because the customer has to go and get it printed. Then the photo, but that is rare.

**F:** The SOP I was given has twelve steps. How many are there really?

**L:** (laughs) The SOP was written by someone in Hyderabad in 2019. Nobody here has read it. If you want to know the steps, watch the tracker. The tracker is the process.

**F:** If a new system did the typing and the checking, what would you be afraid of?

**L:** That it loses the tracker. The tracker is where I know what I am waiting for. Three vendors have come. Each one said "you will not need the spreadsheet". We needed the spreadsheet.

**F:** Last question. If I brought you a hundred real files and asked you to mark the correct value of every field, so that the system is judged against your answers and not against a demo, would you do it?

**L:** If my answers are the standard, yes. I would rather tell you what is right than be blamed for what it got wrong.

## Read-back (last five minutes, with the Vijayawada team lead)

The FDE read the notes aloud. Lakshmi corrected two things: the clean-file time is "one and a half hours including checking, not for the typing alone", and the WhatsApp pages are "most files from the far branches, maybe one in five overall". The team lead added: "The tracker also has colours. Red is waiting on the branch. Yellow is waiting on the customer. Nobody wrote that down anywhere."

## Coded notes

| Code | Verbatim evidence | Kind |
|---|---|---|
| SHADOW_TRACKER | "First thing I do is open the tracker, not the system." | architecture |
| SOP_VS_REALITY | "If you want to know the steps, watch the tracker. The tracker is the process." | evidence |
| REKEYING | "The branch has already typed most of this into the paper form, and I type it again." | metric |
| MISSING_DOC_TOP | "Address proof. Then bank statement for the salaried ones." | scope |
| WAIT_ON_BRANCH | "The file sits. Usually three days. Sometimes a week." | metric |
| SHADOW_NOTEBOOK | "I have the numbers in my notebook, because the branch list in the system is two years old." | adoption |
| WHATSAPP_CHANNEL | "The branch boy photographs it and sends it to me on WhatsApp, on my own phone." | architecture |
| BATCH_6PM | "Anything I finish after about four is tomorrow's result." | constraint |
| ERROR_CORRECTION_BY_ANALYST | "Me. Always me. If your system reads the slip and reads it wrong, it will still be me who is asked." | architecture |
| FLAG_UNSURE_NOT_GUESS | "Tell me when it is not sure. Do not guess." | architecture |
| BAD_DAY_MONTH_END | "The twenty-eighth to the thirty-first. We get three times the files, half of them incomplete." | constraint |
| TRACKER_LOSS_FEAR | "Each one said 'you will not need the spreadsheet'. We needed the spreadsheet." | adoption |
| WILLING_TO_LABEL | "If my answers are the standard, yes." | scope |
| FILE_ORIGIN_SCAN | "It came in last night's batch." (SFTP from the branch scanner) | architecture |
