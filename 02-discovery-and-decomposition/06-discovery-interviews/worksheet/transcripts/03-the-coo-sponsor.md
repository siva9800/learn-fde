# Transcript 03 · The COO, sponsor

> Day 6 discovery pack · Interview 3 of 10 · Persona: sponsor · Where: his office, fourth floor, Hyderabad HQ · When: week 2, Monday, 16:00 · Length: 30 minutes (he gave 20) · Recording: none; three lines read back at the end · Synthetic conversation for the course.

**In the room:** the COO (C); the FDE (F).

## Conversation

**F:** You said nine days to three. I want to make sure I am counting the same nine days you are. Nine days from what to what?

**C:** From the customer signing the application at the branch to the sanction letter. The board sees it as a median across all products. Last quarter it was 9.2.

**F:** Where does that number come from?

**C:** The core system. Received date to sanction date. Monthly ops report.

**F:** Who else has a number for this?

**C:** The analysts, I suppose, in whatever they keep. The branches complain in their own way. The number that matters is the one the board sees.

**F:** What will the board do with three days?

**C:** Two things. Disbursement comes forward six days on every loan, which is interest we are not earning today. And the dealers. A two-wheeler dealer sends the customer to whichever lender sanctions first. We are losing the fast customers to the fintechs.

**F:** When a loan is sanctioned wrongly, a wrong income figure, say, what happens?

**C:** That is why we have forty analysts. A wrong sanction is a credit loss or an audit observation. The RBI observation is worse than the loss. Three observations and the compliance head is in front of the board.

**F:** So if the system made the analysts faster but raised the error rate, would that be a success?

**C:** (pause) No. But I do not expect it to. The demo was 97 percent.

**F:** The demo was 97 percent on salary slips. A loan file has fourteen document types. I will show you, document by document, what it reads today and what it does not, in two weeks. Is there anything in this process that must never be automated, whatever the accuracy?

**C:** The sanction. A person signs the sanction. The RBI expects a name, and so do I. Everything before it, I do not care who does.

**F:** The analysts told me the files wait three days for a branch to send a missing document. Is that in your nine days?

**C:** It must be. I had assumed the days were in Hyderabad, not the branches. If a third of the nine days is branches, then I want the branches fixed too. Can your system do that?

**F:** It can tell the branch on day one what is missing, with the rule that says why. Whether the branch sends it faster is a branch question, and I would want to talk to two branch managers before I promise anything.

**C:** Talk to Kukatpally. He is the best of them and he complains the most.

**F:** One more. There is an Excel tracker that every analyst runs their day from. It is the real state of every file. Were you aware of it?

**C:** What tracker? (pause) No. If they need a spreadsheet, the core system is failing them, which I knew. Do not build me a better spreadsheet.

**F:** I will not. But the first version has to do the tracker's job, or they will keep the tracker, and then you will have two systems and the same nine days.

**C:** Fine. What do you need from me?

**F:** Twenty minutes every Friday, the compliance head's time for a week to write down the rules, and the CISO's review started this week, not in week ten.

**C:** The review starts this week. Tell her I said so, and then tell me if she does not.

## Read-back

Three sentences read back and confirmed: the number is a median, received to sanction, from the core; the sanction is never automated; the review starts in week two.

## Coded notes

| Code | Verbatim evidence | Kind |
|---|---|---|
| TURNAROUND_NUMBER | "From the customer signing the application at the branch to the sanction letter. Last quarter it was 9.2." | metric |
| WRONG_MEANS_AUDIT_FINDING | "The RBI observation is worse than the loss. Three observations and the compliance head is in front of the board." | constraint |
| NEVER_AUTOMATE_DECISION | "The sanction. A person signs the sanction. The RBI expects a name, and so do I." | architecture |
| HUMAN_DECISION_REQUIRED | "A person signs the sanction." | architecture |
| WAIT_ON_BRANCH | "I had assumed the days were in Hyderabad, not the branches." | evidence |
| SHADOW_TRACKER | "What tracker? No." | adoption |
| TRACKER_LOSS_FEAR | "Do not build me a better spreadsheet." (the sponsor's version of the same fear, inverted) | adoption |
| SECURITY_REVIEW_LONG | "The review starts this week. Tell her I said so." | constraint |
