# 02 · The Roles: Sponsor, Operators, Blockers, Ghost, and the Three Everyone Forgets

> Day 5 · Section 2 of 12 · [Chapter overview](README.md) · Previous: [01 · Why the map](01-why-the-map.md) · Next: [03 · Whose version is true](03-whose-version-is-true.md)

---

## 2.1 Four roles, and a test for each

The Part 2 plan names four roles. Each is defined by what the person can do to the engagement, not
by their title, and each has a one-line test you can ask about any name that comes up.

| Role | Definition | The test | What they can do to you |
|---|---|---|---|
| **Sponsor** | pays for the work and wants a number they can report upward | "Whose budget line is this, and what will they say to the board?" | stop funding it; redefine success halfway; promise the board a date you did not agree |
| **Operators** | the people whose working day changes if the system is used | "Whose Tuesday is different after go-live?" | quietly not use it; use it and blame it; keep the old tool open beside it |
| **Blockers** | the people who can say no on behalf of something bigger than the project: security, compliance, legal, IT, procurement | "Who can say no, and what are they protecting when they say it?" | veto; slow; add conditions late; require a rebuild |
| **Ghost stakeholders** | never in any meeting, never on the invite list, and able to stop everything: the regulator, the auditor, the insurer, the court | "Who is never in the room but decides what is acceptable?" | a finding, a fine, a licence condition; a stop that nobody inside can reverse |

"Blocker" is not an insult. The CISO who asks "where does the PDF go?" is doing her job, and in week
ten she will be the person who signs the deployment. The word names a capability (the power to say
no) so that you plan for it; section 05.3 turns blockers into the earliest partners you have.

## 2.2 The three everyone forgets

The published interview guides say the strongest signal in the decomposition round, after
clarifying first, is surfacing a missing stakeholder unprompted. On operational problems the same
three are missed almost every time, and Day 7's step 2 will ask for them by name, so learn them
here:

| Role | Definition | At Godavari | Why they are missed |
|---|---|---|---|
| **The upstream producer** | whoever creates the input your system consumes, and is not a user of it | the 300 branch managers whose staff assemble the loan file; 31 percent of files arrive incomplete | they are a cause in the sponsor's story ("branches send rubbish"), not a person; nobody thinks to give a cause a metric |
| **The system owner** | the engineer who runs the system you will write into, and has watched other vendors fail on it | the owner of the 2009 core lending system: the SOAP API, the 6 pm credit-check batch, the sandbox refreshed quarterly | the sponsor says "IT will give you access"; the owner is not "IT", he is one person with a pager and a memory |
| **The eval owner** | the senior individual contributor whose judgement decides whether an output is correct | Lakshmi in Vijayawada and one senior analyst in Hyderabad for extracted fields; the compliance head for completeness rules | the sponsor assumes "correct" is obvious; the 2026 discovery playbooks say explicitly that the eval owner is usually not the sponsor and often not even in the first meeting |

Two more roles are worth a row because they decide adoption:

- **The champion**: one operator who wants this, becomes your first user, and will defend the tool
  on the floor when you are not there. Found, not appointed. At Godavari it is the Vijayawada team
  lead, who keeps the tracker alive by hand and wants its job done properly by something that will
  not lose a file. Day 31 shows how a sceptic becomes one.
- **The sceptic**: the named person who expects the project to fail and has a reason. At Godavari,
  a senior analyst in Hyderabad who remembers the 2019 OCR pilot and says "it will never read
  handwritten income proofs." The discovery playbooks say talk to them in week 0 and extract the
  failure model; do not try to convert them. Her sentence is a test case for Day 14's golden set.

## 2.3 The Godavari cast

Everyone the course has introduced so far, in one table. Names stay as earlier chapters used them;
roles are this chapter's.

| Who | Role(s) | Where | First seen |
|---|---|---|---|
| The COO | sponsor | Hyderabad HQ, fourth floor | Day 0, Monday |
| Srinivas, credit-ops team lead | operator lead | Hyderabad | Day 2, Monday |
| The credit-ops team lead, Vijayawada | operator lead, champion | Vijayawada | Day 2, Wednesday |
| 40 credit-ops analysts, including Lakshmi | operators | Hyderabad and Vijayawada | Day 0, Wednesday |
| Lakshmi and one senior analyst in Hyderabad | eval owners (fields) | Vijayawada and Hyderabad | Day 2, week 2 (30 labelled files) |
| A senior analyst, Hyderabad | sceptic | Hyderabad | this chapter; Day 31 |
| The CISO | blocker | Hyderabad HQ | Day 0, Tuesday |
| The compliance head | blocker, rule owner, eval owner (completeness) | Hyderabad HQ | Day 2, week 2 |
| The core-system owner | system owner | the on-prem data centre | Day 2, Thursday |
| Corporate IT identity team | blocker (admin): AD groups, SSO, service accounts | Hyderabad HQ | this chapter; Day 22 |
| 300 branch managers, Kukatpally first | upstream producers | the branches | this chapter; Day 7 |
| The RBI auditor | ghost | never in the room | Day 0 ("an RBI audit every year") |
| Kaagaz's CEO and engagement lead | own-side sponsor | Kaagaz AI | Day 3 |

Thirteen rows. Day 2's calendar met twelve people in two weeks and called it a lot; the map is why
there were twelve. One person can hold two roles (the compliance head blocks and also owns the
completeness rules, so she is an eval owner for that half of the problem), and a role can be a
group (forty analysts share a row until Day 6's interviews split them).

## 2.4 Your own side is on the map

The last row is easy to leave off and costly to forget. Kaagaz's CEO committed one of four FDEs for
twelve weeks on Day 3's unit-economics model; he wants recurring revenue that survives you leaving
and patterns the product team can sell to a second lender. His version of the problem ("is this
FDE-shaped?") is different from the COO's and from Lakshmi's, and it is the reason the "will not
build" list exists. An FDE who maps only the customer discovers in month four that the person who
can actually stop the engagement is in their own building.

## 2.5 Key takeaways

- Four roles by what they can do to you: sponsor (fund), operators (use or ignore), blockers (veto),
  ghost (a finding nobody inside can reverse).
- Three roles nearly everyone misses: the upstream producer, the system owner, the eval owner.
- The champion is found, not appointed; the sceptic is interviewed, not converted.
- One person can hold two roles; a group can share one row; your own side gets a row.
