# 03 · Writing for Three Readers at Once

> Day 10 · Section 3 of 13 · [Chapter overview](README.md) · Previous: [02 · What it is for, and its structure](02-what-it-is-for-and-its-structure.md) · Next: [04 · The readout](04-the-readout.md)

---

## 3.1 One document, three ways in

Everyone in the readout room gets the same document. They do not read it the same way.

| Reader | Reads | Is looking for | Stops reading when |
|---|---|---|---|
| the COO | page one, then section 12 | the number, the date, the cost, and what he is signing | page one answers him, or he finds a number he does not trust |
| the CISO (and the compliance head) | section 8, then 10 and 9 | her conditions, in her words, with a gate she controls | she finds a vague sentence where a condition should be |
| Srinivas and the Vijayawada team lead | section 3, then 6 | whether their Tuesday gets better or worse, and whether the tracker survives | they see the SOP's version of their work |

The structure in section 02 is built so that each reader has a front door. The header of the
Godavari document says it in one line: "The COO: page one. The CISO and the compliance head: section
8, then sections 9 and 10. Srinivas and the Vijayawada team lead: sections 3 and 6." Telling people
where to read is a courtesy, and it is also how you make sure the CISO reads section 8 before the
meeting rather than during it.

## 3.2 Page one, for the COO

Page one carries the whole decision. The COO may read nothing else, and the document must still be
signable.

The rules, each from an earlier Day:

1. **Open with the signed problem sentence** (Day 4). It reminds the room what was already agreed.
2. **Three findings, each a number with its method.** "The nine days are mostly waiting: of each
   file's time, 6.4 days is waiting in the queue to be opened (baseline pack)." Not "files wait a lot".
3. **What we will do, in operational words.** "Read every new file on the day it arrives, check it
   against the compliance head's signed rules, tell the branch the same day what is missing, and put
   the fields in front of an analyst who approves every file." There is no model name, and nothing is
   lost by leaving it out.
4. **The target as a range with a population and a date** (Day 9): 3 to 4 days in the two pilot
   branches by day 90. Not "three days".
5. **The money, honestly.** Godavari's case is +15.0 lakh a year at base and minus 1.12 crore on
   analyst hours alone. Page one says both. A COO who discovers the second number on page nine stops
   trusting the first.
6. **The refusals.** The four will-not-do lines, one clause each.
7. **The decisions for today.** Three or four, each something he can say yes or no to.

**No model names on page one.** Day 9 said it; the Part file says it; the checker in section 09 warns
on it. The reason is not secrecy. The COO cannot judge a model; he can judge a turnaround, a cost and
a risk. A model name on page one invites the wrong conversation ("why not the other one?") and dates
the document: models change every six months, the problem does not.

Godavari's page one is about 380 words. If yours is over 450, something on it belongs in a section.

## 3.3 The data and security section, for the CISO

The CISO reads section 8 the way an auditor reads a control: looking for the sentence that would not
survive a question. "All data is processed in a secure, compliant cloud region" does not survive
"which region, approved by whom, and when?".

Write it as a table of her conditions, each with who said it and how the plan meets it, and then a
second table: **where the files are processed at each stage, which files, and the gate she controls**.
For Godavari that table has three rows (the building with masked files, the building with real files
from two branches, Godavari's VPC in AWS Mumbai), and every row's gate is the CISO's written approval.
That table is change C2 from the readout (section 04): she asked for on-prem before any prototype,
and the answer was a staged path with her signature as the gate at each stage.

Three habits that make the section trustworthy:

- **Use her words.** "No customer PII leaves India" is the compliance head's first sentence from Day 5.
  Quote it. Do not paraphrase it into "data residency requirements are respected".
- **Say "in any environment, including tests, logs and backups".** Residency failures happen in logs
  and test copies, not in production databases. Writing it closes the gap she was going to ask about.
- **Defer the detail to its owner, by name.** The full deployment-model argument is Day 21's, the
  questionnaire Day 23's, residency law Day 24's. The document records the decision for these 90 days
  and the gate; it does not try to be the security review.

## 3.4 The workflow section, for the team leads

Srinivas and the Vijayawada team lead will check one thing: does this document describe their work
as it is, or as the SOP says it is? If they see twelve steps, they stop trusting the rest.

So section 3 uses Day 6's nineteen steps, shows where the 6.4 days of queue sit, and has one column
the team leads care about: **what changes at each step in the pilot**. It also answers the question
they will not ask in front of the COO: "is the tracker going away?" The answer is in bold: "the
tracker is not replaced. The system reads its state and writes file status back. Assignment stays
with you."

Write it in their vocabulary. "Waiting on X since" is their column name; "send back" is their verb.
A team lead who recognises their own words in a vendor's document reads the rest as written by
someone who sat beside them, because it was.

## 3.5 Numbers with methods, everywhere

Every number in the document carries its method or a link to one. Day 9 measured them; Day 10 keeps
the method attached as they travel.

| Instead of | Write |
|---|---|
| "turnaround is nine days" | "the hand count puts the median at 9.1 days (8.7 to 9.7); the monthly report says 9.2; both are consistent" |
| "we will save 2,100 hours a month" | "the work that can change is 1.59 of the 4.6 analyst hours a file (timing log, discovery weeks 2 and 3)" |
| "31 percent of files are incomplete" | "28 percent are sent back at least once by the hand count (21 to 35); the monthly report's 31 sits inside that interval, with its caveats written beside it" |
| "the system will be 95 percent accurate" | "the case needs 90 to 95 percent field accuracy on the golden set's mandatory fields, measured at week 6" |

When two sources disagree (31 against 28), say both and why. Choosing the better-looking one silently
is how a CFO learns not to trust the next number.
