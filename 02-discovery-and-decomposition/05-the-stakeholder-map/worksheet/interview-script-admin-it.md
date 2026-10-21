# Mapping conversation · Admin and IT (system owner, identity, security)

> Day 5 · thirty minutes, their office · run in week 1 · bring nothing to demo
> Purpose: fill the row of someone who can veto or slow the work, in their own words; find the conditions before asking for permission.
> At Godavari: the owner of the 2009 core lending system; the corporate IT identity team; the CISO's office for the first conditions (the full security review is Day 23).

**Before you sit down:** read whatever documentation exists for their system (the WSDL, the access policy, the last vendor's architecture diagram if anyone will share it). Know when their batch runs. Have the constraints list open.

## Opening (minutes 0 to 3)

> "I do not have anything to show you yet, and I would rather not build something you will have to refuse. I am here for the conditions: what a vendor's system may and may not do here, and who decides."

## The systems and their owners (minutes 3 to 10)

| Ask | Listen for | Fills |
|---|---|---|
| "Which systems would a tool like this have to read from and write to?" | the core system, the document store, the SFTP, the directory, the tracker on the shared drive | Day 7 step 3's inputs; the system-owner rows |
| "Who owns each one, by name?" | one person per system; "that is me" | the system owner's row; the calendar |
| "When does each run its batch, backup or refresh?" | the 6 pm credit-check batch; the quarterly sandbox refresh; the nightly HR sync into AD | the customer's calendar; constraints Day 7 step 1 cannot move |
| "What is the one thing a vendor must never do to it?" | a duplicate record; a write outside the window; a load spike at 6 pm | the number they would believe (zero duplicates; calls inside the window) |

## The memory (minutes 10 to 17)

| Ask | Listen for | Fills |
|---|---|---|
| "What happened with the last vendor who integrated here?" | three vendors; which one caused the duplicate records; who had to clean up at 2 am | the fear ("the fourth vendor to break his system") |
| "What did they get wrong, in your words?" | retries without an idempotency key; a sandbox nobody refreshed; a go-live during the freeze | test cases for the integration spike (Day 2 week 2, Day 16) |
| "What would you have needed them to do differently?" | "ask me before the design, not after" | the engagement column: named in the integration workstream |

## The conditions (minutes 17 to 24)

| Ask | Listen for | Fills |
|---|---|---|
| "Under what conditions may a vendor's system touch a loan file?" | masked only until the review passes; on-prem or the Mumbai VPC; never a laptop | the constraints list, verbatim |
| "Where may it run, and who may hold credentials?" | "no vendor holds production credentials"; a service account owned by Godavari | the CISO's number (passed review; VPC; no vendor-held credentials) |
| "What must never leave the building, and what must never be trained on?" | "no customer PII leaves India"; "no model trains on our data" | the compliance head's first sentence; Day 23 and Day 24 inputs |
| "What would you need to see before you said yes?" | the questionnaire; a SOC 2 report; a data-flow diagram with every hop | the engagement column, with a week number |

## Access (minutes 24 to 28)

| Ask | Listen for | Fills |
|---|---|---|
| "How is access granted here: who approves a service account, and how long does it take?" | a ticket, the CISO's sign-off, two to three weeks | the identity team's row; the week-2 ticket |
| "What breaks if it is done wrong?" | the nightly HR sync; a branch manager seeing another branch's files | Day 22's design inputs; the branch-isolation rule Day 6 confirms |

## Who signs (minutes 28 to 30)

| Ask | Listen for | Fills |
|---|---|---|
| "Who else signs before anything goes live?" | the CISO, the compliance head, "the audit committee for anything customer-facing" | the veto list; the readout room (Day 10) |
| "Who gets the audit letter?" | the compliance head | the ghost's proxy |

## Do not ask

- About the workflow, the analysts or the business case (they do not know, and it shows you have not understood their job)
- "Can we have access?" (not in this conversation; conditions first, then the ticket in week 2)
- Anything that promises an architecture ("we would use a vector store...")

## Within the hour

Write every condition in their words into the constraints list and the row. Read it back to them by email the same day ("this is what I understood; please correct me"). Add every system they named to Day 7's inputs table with its owner. Rerun the script and check that nobody who can veto has a first-contact week later than 2.
