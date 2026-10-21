# 09 · Shadow Systems and the Golden Examples

> Day 6 · Section 9 of 16 · [Chapter overview](README.md) · Previous: [08 · The questions that change the architecture](08-questions-that-change-the-architecture.md) · Next: [10 · Synthesis and confirmation](10-synthesis-and-confirmation.md)

---

## 9.1 The Excel tracker nobody mentioned

Every operation has a shadow system: the spreadsheet, notebook or chat group that holds what the official system cannot. Nobody mentions it in the first meeting, for three reasons. The sponsor does not know it exists ("What tracker? No."). The operators think it is embarrassing, or think you will take it away. And the people who built the official system regard it as a failure of training, not as a requirement.

At Godavari the shadow systems are:

| Shadow system | What it holds that the core cannot | Who keeps it | What it tells you |
|---|---|---|---|
| the Excel tracker, forty workbooks | assignment, "waiting on X since", three colours with meanings written nowhere | every analyst; the team leads assign in it | the real state of every file, and the real workflow ("the tracker's columns are the steps") |
| personal notebooks and phone lists | branch phone numbers; the core's list is two years old | each analyst, passed from senior to junior | a data-quality failure in the core nobody has reported |
| WhatsApp on personal phones | late pages, as photos | analysts and branch officers | an input channel that is neither allowed nor forbidden |
| the printed checklist | last year's version of the rules | each analyst | a change process that does not reach the floor |
| "in my head and in Lakshmi's" | which address proofs are acceptable | the compliance head and the senior analysts | a rule set that has never been written |

The last row is a shadow system with no artefact at all. It is often the most important one, and the only way to find it is to ask "what do you do when you are not sure?" and then "who do you ask?"

## 9.2 How to find them

- **Ask for it by name, without judgement.** "What is in the Excel sheet?" assumes there is one, which gives permission to show it. "Do you use any spreadsheets?" gets a no.
- **Look at the desk.** Printed lists, sticky notes, a second phone, a notebook beside the keyboard.
- **Ask what they would lose.** "If your laptop died tonight, what would you not be able to rebuild tomorrow?" Lakshmi's answer was not the core.
- **Ask the newest person how they learned.** Bhavani: "I learned the job from the tracker and from sitting beside Lakshmi for a month."
- **Follow the colours and the abbreviations.** "Received WA" in a tracker cell is a channel. A red row is a state.

## 9.3 How to treat them

Read its schema as a requirement: its columns are the states the official system lacks. Plan to read it before you replace it and to write state back, so there is one record. Put its owner on the map; the Vijayawada team lead is the champion because she keeps it alive. Keep its data under the official system's rules, because it holds customer data. And do not call it a workaround in front of the people who keep it, report "they use spreadsheets" to the sponsor as a finding about them, or promise "you will not need the spreadsheet": three vendors said that, and "we needed the spreadsheet".

The adoption rule that follows, "in the tracker's place, not beside it", was said by Srinivas and by the senior analyst independently, and is in section A2 of the synthesis. Day 16 integrates the tracker; Day 33 owns the operator who will not switch.

## 9.4 Capturing the golden examples

The second thing week one must produce, besides the map, is the raw material of the evaluation set. OpenAI's FDE team describes evals agreed with the customer's experts as the contract that comes before serious development; the course's version is a golden set of **100 to 200 real examples, labelled by the customer's experts, agreed before a model is chosen**. [Day 9](../09-success-metrics-and-business-case/README.md) agrees it as a contract and Day 14 builds it, with judges and regression. Day 6's job is narrower: find the examples and the people, while you are on the floor with both.

Three things to capture now:

**1. The labellers, and their condition.** The interviews produced them: Lakshmi ("if my answers are the standard, yes"), the senior analyst ("if my answers are the standard and not the demo's, and I want to see every failure"), and the compliance head for completeness ("I sign it"). Write the condition down. It is the reason the golden set is labelled by them and not by Kaagaz.

**2. Where the examples come from, deliberately not the clean files.** The branch managers offered their worst files: "I can give you thirty"; "take the whole month". A set drawn from clean SFTP scans would pass and mean nothing. The first manifest, agreed on week 2 Friday:

| Source | Files | Why | Offered by |
|---|---|---|---|
| Kukatpally send-backs, last 60 days | 30 | the pilot branch; real address-proof disputes | the Kukatpally manager |
| Guntur phone photos and handwritten Telugu declarations | 40 | the far-branch shape; the 2019 failure mode | the Guntur manager |
| Files the senior analyst has already decided, with her figures | 50 | her test: "a hundred files I have already done" (first half) | the senior analyst |
| Clean two-wheeler SFTP scans from both cities | 40 | the skeleton's slice; the baseline for "easy" | Srinivas |
| Gold and small-business files | 20 | the other checklists (9 and 16 documents) | the Vijayawada team lead |
| **Total** | **180** | inside 100 to 200 | |

Plus the thirty files Lakshmi labelled on Day 2's Wednesday, which are the seed and are not double-counted.

**3. The edge cases, as named test cases.** Every failure story is a test: the monthly-as-annual declaration; the Aadhaar with the old address; the gas bill in the father's name; the passbook photographed page by page; the stapled page that jams the scanner. Name each one and attach it to a file number in the manifest. The playbooks call these "the weird Tuesday" cases.

What not to do this week: choose a model, run the set, or compute a percentage. The senior analyst said "not a percentage; the actual files". Day 14 builds the report she asked for.

## 9.5 Key takeaways

- Every operation has shadow systems: the tracker, the notebook, the WhatsApp channel, the printed checklist, the rule in someone's head. Ask for them by name and read their schema as requirements.
- Read before you replace; write state back; never mock it to the sponsor or copy it to your laptop.
- Week one captures the golden examples' raw material: the labellers and their condition, 100 to 200 real files chosen from the hard cases, and named edge cases. Day 14 builds and runs the set.
