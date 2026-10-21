# 02 · Days One and Two: Access and Reality

> Day 6 · Section 2 of 16 · [Chapter overview](README.md) · Previous: [01 · Why discovery interviews](01-why-discovery-interviews.md) · Next: [03 · Shadowing](03-shadowing.md)

---

## 2.1 What "access and reality" means

The first two days of an engagement have one job, which the course plan names, after a published FDE 90-day playbook, **access and reality** (section 16 notes that the playbook page has since been rewritten and no longer uses the phrase). Access is every credential, ticket and permission you will need, requested on day one because each one has a clock on it. Reality is the gap between what the sales notes, the demo deck and the SOP say the customer has, and what the customer actually has: SSO that is planned for next financial year, repositories that are a shared drive, a warehouse that is forty Excel workbooks.

The two go together because you cannot see reality without some access, and you cannot ask for the right access until you have seen some reality. Day one is where you ask for everything you can name; day two is where you discover what you should have asked for.

## 2.2 The access list, raised on day one

Every item below is a ticket somebody at the customer has to process, and the slowest one decides when the walking skeleton can run on real data. Raise them all on Monday, in writing, with the reason attached, and track them in the engagement log.

| Access | Why you need it | Who grants it at Godavari | Typical clock | What you do meanwhile |
|---|---|---|---|---|
| Building and floor access, a desk near the operators | shadowing; being there at 09:40 when the tracker opens | the COO's office | same day | nothing to wait for |
| Permission to shadow and interview, HR informed | the CISO's rule: "do not record the analysts without telling HR"; people answer differently when they know it is sanctioned | the team leads, HR | a day | prepare the question bank (section 05) |
| Read access to the SOP, the checklists, the forms, the last audit response | the documented process, to compare against the real one | the compliance head, the ops office | a day | read them side by side with the demo deck (Day 2's Monday afternoon) |
| Read access to the document store (SFTP folders) | the shape of the input: pages, order, languages | the CISO, after review | weeks; masked samples sooner | the compliance head's fifty masked files on a machine in the building |
| A core-system sandbox login and the WSDL | the integration surface | the core-system owner, with the CISO's nod | days for the WSDL; weeks for a login | read the WSDL; list the operations; ask the owner how retries behave |
| A read-only view of the tracker | the real state | the team leads | same day; it is a shared drive | sit beside someone who has it open |
| A folder on the customer's drive for your notes | the CISO's rule about where discovery notes live | the CISO | a day | keep notes on paper until then |
| VPN or a customer laptop | anything that touches customer systems | the CISO | weeks | visitor Wi-Fi and a notebook; it is enough for discovery |

The last column is the point. On Day 0's Tuesday the CISO said no, no and not yet, and the fortnight still had seventy hours of real work in it ([Day 2](../../01-the-role/02-the-three-buckets/05-two-weeks-at-godavari.md)). Access is on the critical path for building; it is not on the critical path for understanding.

## 2.3 Reality, in three places

The sales notes said "the documents are in the core system", "the data is in the warehouse" and "they have SSO". Here is where each of those sentences meets the floor, and the question that exposes the gap.

| The sentence | The question that tests it | What Godavari actually has | What it changes |
|---|---|---|---|
| "They have SSO" | "When I open your application in a browser, what logs me in, and could it log in a vendor's application?" | on-prem Active Directory; an Entra sync planned for next financial year; no vendor SSO this year; service accounts through the CISO personally | Day 22 designs around a read-only domain controller inside the VPC; the first prototype has one user and no SSO |
| "The documents are in the core system" | "Show me one. Where does the PDF live, and what does the core system hold about it?" | the core holds a shell record with branch code and file number; the PDF is in a region SFTP folder, 30 to 40 pages, unordered; one file in five has a page that came by WhatsApp and is stapled to the paper file only | page classification is a workstream; the paper file and the system file differ |
| "The data is in the warehouse" | "Which report do the team leads look at every morning, and where does it come from?" | forty Excel workbooks on a shared drive, one per analyst, seven status columns, three colours, no timestamps; the monthly ops report comes from the core's received and sanction dates | the baseline has to be hand-sampled (Day 9); the tool must read and write the tracker (Day 16) |
| "There is an API" | "What happens if I call it twice?" | a 2009 SOAP API, fourteen operations, no idempotency on create; a sandbox refreshed quarterly | the integration layer owns idempotency (Day 16) |

"Repositories" is in the published phrase because at a software customer the first thing you ask for is the code. At a lender the repositories are the SOP, the Word checklists, the forms and the last audit response; ask for them on day one and read them before you shadow, so that on Wednesday you know which step the SOP claims and can see which step the floor does.

## 2.4 What to do with visitor Wi-Fi and a notebook

A rule for the first two days, from Day 2's calendar: **every deployment block has a customer-facing block before it.** With no credentials, the customer-facing blocks are all you have, and they are the most valuable ones. Day 2's calendar has the hours; what each block is for: the kickoff gives you the sponsor's sentence and your question ("nine days doing what?"); the floor walk with Srinivas is a walk, not an interview (count the windows per desk, the printed checklists, the spreadsheet on every screen); the afternoon with the SOP and the deck lists every claim you will test; the access list goes in at 16:00; the CISO's three questions on Tuesday, written verbatim, become the first lines of the questionnaire (Day 23); and Tuesday afternoon's shadowing (section 03) tells you which questions to ask everyone else.

By Wednesday you are on a train to Vijayawada with a notebook of questions that came from the floor rather than from the deck. That is the whole purpose of days one and two.

## 2.5 Where the notes live, and what goes in them

The CISO's answer to "where may my notes live?" was "on our SharePoint, in a folder I give you; not on your laptop; not on your company's drive; and do not record the analysts without telling HR." Treat that as the default at every customer until told otherwise, and apply it from the first hour:

- **File numbers, not customer names.** A shadowing log can say "two-wheeler file, Kukatpally, 34 pages, no address proof". It never needs the applicant's name, PAN or phone number, and a log with those in it is a DPDP incident waiting for a lost laptop. Day 24 owns the law; the habit starts here.
- **No recordings without consent and HR's knowledge.** Recording is tempting because transcription is cheap in 2026 (section 11). In a regulated Indian lender, recording staff at their desks without HR's knowledge is a grievance, and in several customers a contractual breach. Notes, read back at the end, are enough for discovery.
- **The notes are the customer's.** They are about the customer's process and the customer's people. A customer who asks for them should get them. Write every line as if the compliance head will read it, because at the readout she will.

## 2.6 Key takeaways

- Days one and two are access (every ticket raised on Monday, each with a clock) and reality (the gap between the deck, the SOP and the floor).
- Access is on the critical path for building, not for understanding. Visitor Wi-Fi and a notebook are enough for the most valuable discovery work.
- Test the four sentences every sales note contains: SSO, documents in the system, data in the warehouse, an API. Each has a one-line question and, at Godavari, a different answer.
- Decide where the notes live before writing the first one; file numbers, not names; no recording without HR.
