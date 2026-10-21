# 05 · Reading an Org Without an Org Chart: Finding the Rows the Sponsor Did Not Mention

> Day 5 · Section 5 of 12 · [Chapter overview](README.md) · Previous: [04 · Power and interest](04-power-and-interest.md) · Next: [06 · The three persona scripts](06-persona-scripts.md)

---

## 5.1 The org chart is not the map

Godavari has an org chart. It shows the COO above "Credit Operations" above two team leads above
forty analysts, and "Information Technology" as a box to one side. It does not show that one
engineer in the data centre owns the 2009 core system and its 6 pm batch; that the compliance head
reports to the board's audit committee, not to the COO; that the Vijayawada team lead's spreadsheet
is the real state of every loan; or that a senior analyst in Hyderabad was on the 2019 OCR pilot
and has opinions. The map has to be read off the organisation itself. Here are the signals, each
with the question that turns it into a row.

## 5.2 Eleven signals

| Signal | What it tells you | The question to ask next |
|---|---|---|
| Who is cc'd on the sponsor's emails but never speaks | someone the sponsor keeps informed because they can object | "Should I meet them before the readout?" |
| Who the sponsor glances at before answering a question | the person whose approval the sponsor needs | map them one level above where the chart puts them |
| Who is named in the SOP and absent from every meeting | an owner of a step nobody thinks of as a stakeholder | "Who signs when this step changes?" |
| Who owns the shared drive, the folder, the spreadsheet | the real owner of the real state | that is the champion or the sceptic; interview them in week 0 |
| Who approved the last vendor, and who switched it off | the veto, and the memory of it | "What did the last vendor get wrong, in your words?" |
| Who runs the batch, the backup, the quarterly refresh | the system owner | their calendar is now your calendar |
| Who gets the audit letter | the proxy for the ghost | they speak for the regulator in the room; get their first sentence on the map |
| Who trains new joiners | the person whose mental model of the workflow is the official one | and the person who knows where the official one is wrong |
| Who people apologise to in meetings | power the chart does not show | score them 4 on power until proved otherwise |
| Who says "we tried that" | the sceptic | one hour, week 0, extract the failure model |
| Who asks for a demo before you have anything | enthusiasm, not necessarily a champion | a champion wants their problem solved; an enthusiast wants a demo |

Two of these produced rows at Godavari that the COO never mentioned. "Who owns the spreadsheet"
found the Vijayawada team lead and the tracker (Day 0, Wednesday). "Who gets the audit letter" found
the compliance head and, behind her, the auditor; her first sentence, "no customer PII leaves
India", went straight into the constraints list before any architecture existed.

## 5.3 Blockers as early partners: the CISO in week one, not week ten

The CISO said no, no and not yet on Day 0's Tuesday. The instinct that follows is to avoid her until
there is something impressive to show. The published practice (the Atlassian playbook: "build
permissions, security and auditability in from day one"; the discovery playbooks' admin and IT slot
in the week-0 map) is the reverse, for a reason you can state as arithmetic:

| | Blocker met in week 1 | Blocker met in week 10 |
|---|---|---|
| What they write | conditions: "VPC in Mumbai, nothing leaves India, no production credentials to the vendor" | a refusal, because the conditions were not met and there is no time to meet them |
| What it costs you | a questionnaire started in week 2 (Day 23); a deployment model chosen with her in the room (Day 21) | a rebuild of the deployment, or the end of the engagement |
| What the sponsor sees | a plan with the CISO's name on a line | a surprise, and a vendor who "did not do their homework" |

The words for the week-1 meeting are short: "I do not have anything to show you yet, and I would
rather not build it in a way you will have to refuse. What are the conditions under which a vendor's
system may touch a loan file here?" Then write down every sentence she says, verbatim, and read
them back. The CISO's row on the map is filled by her, not by you. Day 2's calendar already has
this meeting on Tuesday of week 1 and the questionnaire draft on Tuesday of week 2; the map is why
those blocks exist.

The same move works on the compliance head (a fifteen-minute call in week 1 for her first sentence,
a full session in week 2 for which rules are fixed and which are judgement) and on the core-system
owner (the sandbox spike in week 2, with the duplicate record on retry shown to him the same day).
Every one of them becomes a partner by being asked for conditions before being asked for permission.

## 5.4 The champion and the sceptic

Two people on the map carry adoption, and the sponsor can point you to neither.

**The champion** is the operator who wants the problem solved badly enough to use an unfinished
tool and tell you what is wrong with it. Three tests: they own a workaround (the tracker), they
describe the problem in their own numbers ("eleven files waiting on bank statements this morning"),
and they ask when they can try it rather than when it will be ready. The Vijayawada team lead passes
all three. A champion appointed by the sponsor ("Lakshmi will be your point of contact") is a
liaison, which is useful and different.

**The sceptic** is the person who expects it to fail and has evidence. The discovery playbooks say
the hour with them is the highest-leverage hour of week 0, and the reason is practical: their
failure model is a list of test cases. "It will never read handwritten income proofs" becomes a
category in Day 14's golden set, and the Day 31 workshop where she watches those files get flagged
for review instead of guessed is the moment she becomes the second champion. Do not argue with her
in week 0. Ask "what did the 2019 pilot get wrong, specifically?" and write down every file type she
names.

## 5.5 The customer's calendar

The last thing to read off the organisation is time. Every enterprise has dates on which nothing
changes, and the sponsor will not mention them because they are obvious to him. For a Hyderabad
NBFC (all invented for the course, and the shape is the point):

| Fixed date | What it means for the engagement |
|---|---|
| RBI inspection, expected in the January-to-March quarter | the compliance head and the auditor's proxy are unavailable for weeks; no new process goes live during it; the audit trail must exist before it |
| Core-system release freeze, the last two weeks of every quarter | no SOAP changes, no sandbox refresh; the integration spike cannot land in those weeks |
| Financial year end, 31 March | the COO's number is reported then; a pilot result in February is worth more than a better one in April |
| Sankranti week in Vijayawada; Dussehra | half the analysts on leave; shadowing and the pilot workshop must avoid them |
| Month-end disbursement push | analyst hours per file are not comparable in the last three days of a month; the Day 9 baseline sample must know this |

Put these on the map as a row of their own or as a short list under it. Day 8 sequences the 90-day
plan around them; Day 5's job is that they are known in week 0, not discovered in week 7 when the
sandbox goes dark for a freeze.

## 5.6 Key takeaways

- The org chart shows reporting lines; the map shows who can fund, use, veto, slow, judge or ignore.
  Read the second off the organisation with the eleven signals.
- A blocker met in week 1 writes conditions; met in week 10, a refusal. Ask for conditions before
  permission.
- The champion is found by three tests; the sceptic's failure model is a list of test cases.
- The customer's calendar (audit, freeze, year end, festivals, month end) is on the map from week 0.
