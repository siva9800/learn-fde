# 03 · Whose Version of the Problem Is True, and Whose Judgement Defines "Correct"

> Day 5 · Section 3 of 12 · [Chapter overview](README.md) · Previous: [02 · The roles](02-the-roles.md) · Next: [04 · Power and interest](04-power-and-interest.md)

---

## 3.1 Both are true from where each sits

The COO's version: "the analysts are slow." Lakshmi's version: "we wait three days for the branch,
then the batch runs overnight." The temptation is to decide who is right. Do not. Each person
describes the part of the process they can see, and each is accurate about that part.

| | The COO sees | Lakshmi sees |
|---|---|---|
| The unit of work | a loan: application to sanction, nine days | a file: fourteen documents, three of them missing |
| Where time goes | forty salaries and a number that has not moved in two years | a tracker row that says "waiting on bank statement since Tuesday" |
| Who could change it | the analysts, by working faster | the branch, by sending a complete file; the core system, by not batching at 6 pm |
| What "better" means | three days, on a slide, before the next RBI cycle | fewer chases, fewer files bouncing back, no blame for a wrong field |
| What they cannot see | that most of the nine days are waiting, not working | that the board has been promised a number and someone will be held to it |

Read the last row twice. The COO cannot see the waiting because nothing reports it: the core system
records the sanction date and the application date, and the tracker that holds the waiting lives on
a shared drive he has never opened. Lakshmi cannot see the board because nobody tells analysts what
the board was promised. Neither is wrong; each is missing the other's data.

## 3.2 Holding both: write them side by side and look for the lever

The method is mechanical, which is why it works under pressure:

1. **Record each version verbatim**, in the "their version" column of the map. Not your paraphrase.
   "The analysts are slow" and "we wait three days for the branch" are evidence; "throughput
   issues" is not.
2. **Ask what each version would need to be true.** The COO's needs analyst time to be the bulk of
   the nine days. Lakshmi's needs waiting to be the bulk. These are testable, and Day 6's shadowing
   and Day 9's two-week sample test them. (At Godavari, waiting wins: the three-day resend and the
   overnight batch dominate.)
3. **Find the lever that moves both numbers.** A completeness check on day one tells the branch
   what is missing before the file joins the queue. It cuts the COO's turnaround (fewer files wait
   three days) and Lakshmi's chases (she no longer discovers the gap on day four). Day 7's skeleton
   is built around exactly that lever, and it was found here, by refusing to pick a side.
4. **Write the one sentence both would sign.** Day 4's problem statement does this: "...because
   intake is manual and a third of files are incomplete." The COO reads "nine days"; the analysts
   read "a third of files are incomplete"; both are in the sentence.

When the two versions cannot be reconciled by a single lever, that is not a failure of the method;
it is a finding. Write it into the conflicts list (section 04.4) and carry it to the readout.

## 3.3 Whose judgement defines "correct": the eval-customer split

A second split hides inside the first, and it is the one that decides whether Part 3's evals mean
anything. **The person who buys the system and the person whose judgement defines a correct output
are almost never the same person.** The 2026 discovery playbooks call the second one the eval owner
and say plainly that they are a senior individual contributor, usually a domain expert, and not the
sponsor.

At Godavari:

| Question | Who decides | Why them |
|---|---|---|
| Is this extracted field correct? | Lakshmi and one senior analyst in Hyderabad | they would have typed it; they know that a salary slip for the wrong month is wrong even when the digits are read perfectly |
| Is this file complete? | the compliance head | she owns the checklist against RBI's KYC Master Direction and decides which alternatives are acceptable |
| Is this decision auditable? | the RBI auditor, through the compliance head | he judges once a year, against the trail the system left |
| Is this fast enough? | the COO | turnaround is his number |
| Is this usable? | the forty analysts, by using it | adoption is the only honest measure |

Notice that the COO decides nothing about correctness. If you let the sponsor define "correct"
("it should be 97 percent accurate, like the demo"), the golden set (Day 14) is labelled by the
wrong people against the wrong standard, and the first audit finding is yours. The map's eval-owner
rows are the contract that prevents it: the people in those rows label the files, their labels are
the standard, and Day 9's targets are written against their standard, not the demo's.

> One sentence to say in the first week, to the COO, in those words: "You decide how fast it has
> to be. Lakshmi and the compliance head decide what counts as right. We will measure both and
> show you both every week."

## 3.4 The version nobody said: the ghost's

The auditor's version of the problem is "show me the decision, who made it, and the documents it
rested on." Nobody at Godavari says it in the first meeting because it is not a problem to them; it
is the weather. It still decides the architecture: a human decision recorded per file, a trail that
survives a model upgrade, no automation of the KYC completeness rules without a signed version of
them. Day 7's section 4.5 handles what happens when the sponsor's metric collides with it (the
skeleton obeys the ghost). This chapter's job is to get the sentence on the map in week 0, with
the compliance head named as the person who speaks for him in the room.

## 3.5 Key takeaways

- The sponsor's version and the operators' version are both true; each describes the part of the
  process its author can see. Record both verbatim and test what each would need to be true.
- Look for the lever that moves both numbers; at Godavari it is day-one completeness.
- The buyer and the judge of correctness are different people. Name the eval owners on the map and
  let their labels, not the demo, define "correct".
- The ghost's version is never spoken in the room; write it down anyway, with a named proxy.
