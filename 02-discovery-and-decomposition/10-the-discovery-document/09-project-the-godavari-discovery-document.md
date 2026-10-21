# 09 · Project: Assemble, Check and Sign the Godavari Discovery Document

> Day 10 · Section 9 of 13 · [Chapter overview](README.md) · Previous: [08 · 2026 patterns and production concerns](08-2026-patterns-and-production-concerns.md) · Next: [10 · Mistakes and debugging](10-mistakes-and-debugging.md)

---

## 9.1 The brief

It is Monday of discovery week four. The readout is on Friday 20 November (M08 in Day 8's plan). By
Wednesday you owe the room a pre-read; by Friday evening, a signed version. The engagement folder
needs:

1. **the discovery document**, assembled from Days 4 to 9, in the structure of section 02, written for
   the three readers of section 03, and after the readout carrying the four changes and the decision
   log;
2. **a checker** that refuses to let a document go out with a missing section, a decision without an
   owner or a date, a refusal without a reason, or a broken link to a source artifact;
3. **the checker's output** on the real document and on an AI-written draft, so that you know what a
   script can catch and what only a reviewer can.

| Path | What |
|---|---|
| [`worksheet/godavari-discovery-document.md`](worksheet/godavari-discovery-document.md) | the signed version 1.0, with changes C1 to C4 marked |
| [`worksheet/ai-draft-discovery-document.md`](worksheet/ai-draft-discovery-document.md) | an AI-written draft with at least fourteen problems; exercise 3.1 |
| [`code/check_discovery_doc.py`](code/check_discovery_doc.py) | the checker: five error checks, seven warning checks, exit code 1 on any error |

Run from the chapter folder on **Python 3.14.3** (October 2026), standard library only, no packages,
keys or downloads. Each run takes about 0.3 seconds.

```bash
python -X utf8 code/check_discovery_doc.py worksheet/godavari-discovery-document.md
python -X utf8 code/check_discovery_doc.py worksheet/ai-draft-discovery-document.md
```

## 9.2 Part A: assemble the document

Work in this order. It is the reverse of the reading order, on purpose.

1. **Copy, do not write, the sources' conclusions.** For each of sections 1 to 7, open the artifact,
   find its conclusion, and paste it with a link. The problem sentence goes in verbatim. The
   baseline table comes from Day 9's pack as it stands, both columns (report and hand count).
2. **Write the two new sections.** Section 8 (data and security) collects the conditions from Day 5's
   constraints list and Day 6's findings B1, B2, A1 and A6 into one table, then adds where files are
   processed at each stage. Section 12 turns Day 5's open collisions and Day 8's next milestones into
   decisions, each with a decider and a date.
3. **Risks, open questions and refusals from the sources.** Risks from Day 7's expected failures, Day
   8's buffers and Day 9's sensitivity table. Open questions from Day 8's assumptions and Day 9's
   "what decides it". Refusals from Day 8's lists, adding the "and instead" column from Day 4.
4. **Page one, last.** Seven blocks (section 3.2), under 450 words, no model names, every number
   traceable to a linked source.
5. **The header.** Who reads what, the version, the next version's date.
6. **After the readout:** mark each change in the text, add the change log rows, append the decisions
   to the log, fill the sign-off.

Godavari's version is the chapter's answer. Fill your own from the six artifacts first, then compare;
where yours is longer, find the paragraph that restates a source instead of linking it.

## 9.3 Part B: the checker

`code/check_discovery_doc.py` splits the Markdown on `##` and `###` headings, parses every table, and
runs twelve checks.

| Code | Check | Kind | Why a script and not a reviewer |
|---|---|---|---|
| E1 | the 16 required sections are present (the 12 of section 02 plus page one, the decision log, the change log, the sign-off) | error | reviewers miss what is absent |
| E2 | the problem statement is one sentence, in a blockquote | error | the signed sentence must be identifiable |
| E3 | every decision row (decided, still to decide, log) has an owner and a date containing a digit | error | "ASAP" and "leadership" read as filled |
| E4 | every will-not-do or not-now row has a reason of four words or more | error | "phase 2" reads as a reason |
| E5 | every relative link resolves to a file | error | sources get renamed |
| W1 | no technology words on page one | warning | a judgement call; the word list is crude |
| W2 | every number on page one appears in at least one linked source | warning | catches invented numbers, cheaply |
| W3 | page one under about 450 words | warning | |
| W4 | open questions have an owner and a due date | warning | |
| W5 | will-not-do lines say who agreed | warning | |
| W6 | at least one link into each of Days 4 to 9 | warning | continuity: the document assembles, not rewrites |
| W7 | no placeholders (TBD, TODO) | warning | |

Two design choices worth reading in the code. **Columns are found by header words**, not position
(`decided by|who decides|owner`, `because|reason|why`), so the checker works on anyone's table
layout. **W2 searches the text of the files the document links**, with commas stripped, so "1,400"
and "1400" match; a number on page one that appears in none of them is either computed (say how) or
invented. W2 is a warning because small integers will nearly always be found somewhere; it is the
large, specific numbers it catches.

## 9.4 Part C: run it on the real document

```text
== godavari-discovery-document.md: 16 of 16 required sections, 20 decisions, 9 will-not-do lines, 12 linked files resolved ==
PASS: 0 errors, 0 warnings
```

Twenty decisions: six decided at the readout, four still to decide, ten in the log. Nine refusal
rows: four will-not-do lines and five parked ones. Twelve source files resolved, across all six
earlier Days. The first run, before the final edit, printed one warning (W5 on the parked list, which
has a "revisit" column instead of "agreed by"); that was the checker being wrong, so the rule now
skips tables whose header says "not now" or "revisit". Treat your own checker's false positives the
same way: fix the rule, do not edit the document to please it.

To see that each error check bites, break three things in a copy (a date changed to "soon", a reason
changed to "phase 2", a link misspelt):

```text
== _break.md: 16 of 16 required sections, 20 decisions, 9 will-not-do lines, 11 linked files resolved ==
  ERROR   E3 '12.1 Decided at this readout': decision D05 commit to the two-branch pilot fr... has no date ('soon')
  ERROR   E4 '2 build collections call summaries' reason is a label, not a reason: 'phase 2'
  ERROR   E5 broken link: ../../06-discovery-interviews/worksheet/situational_map.md
FAIL: 3 errors, 0 warnings
```

## 9.5 Part D: run it on the AI draft

```text
== ai-draft-discovery-document.md: 14 of 16 required sections, 4 decisions, 3 will-not-do lines, 0 linked files resolved ==
  ERROR   E1 missing section: open questions (no heading matches /open question/)
  ERROR   E1 missing section: change log (no heading matches /change log|version history/)
  ERROR   E2 problem statement is 2 sentences; the signed statement is one
  ERROR   E3 '11. Decisions needed': decision approve the GPT-4o pipeline has no owner
  ERROR   E3 '11. Decisions needed': decision approve the GPT-4o pipeline has no date ('')
  ERROR   E3 '11. Decisions needed': decision approve auto-approval threshold has no date ('ASAP')
  ERROR   E3 '11. Decisions needed': decision approve phase 2 chatbot has no date ('')
  ERROR   E4 'Branch CRM' reason is a label, not a reason: 'deferred'
  ERROR   E4 'Collections summaries' reason is a label, not a reason: 'phase 2'
  ERROR   E4 'Core system changes' has no reason ('because')
  ERROR   E5 broken link: ../../08-scoping-the-first-90-days/worksheet/90-day-plan.md
  ERROR   E5 broken link: ../../06-discovery-interviews/worksheet/discovery-synthesis.md
  warning W5 '10. Out of scope': no 'agreed by' column
  warning W1 page one names technology: 'GPT-4o' (the COO signs outcomes, not components)
  warning W1 page one names technology: 'RAG' (the COO signs outcomes, not components)
  warning W1 page one names technology: 'vector' (the COO signs outcomes, not components)
  warning W2 page-one numbers found in no linked source: 2, 2.4, 67, 12000
  warning W6 no link to any Day 4 (problem) artifact (04-picking-the-problem/)
  warning W6 no link to any Day 5 (stakeholders) artifact (05-the-stakeholder-map/)
  warning W6 no link to any Day 6 (discovery) artifact (06-discovery-interviews/)
  warning W6 no link to any Day 7 (decomposition) artifact (07-decomposition/)
  warning W6 no link to any Day 8 (90-day plan) artifact (08-scoping-the-first-90-days/)
  warning W6 no link to any Day 9 (baseline and case) artifact (09-success-metrics-and-business-case/)
  warning W7 line 72: placeholder: | approve the GPT-4o pipeline | TBD | |
FAIL: 12 errors, 12 warnings
```

Read what it did **not** say. The decision log's single row, "use RAG architecture, decided by Kaagaz,
week 1", passes: it has an owner and a date. A human sees that a vendor decided the customer's
architecture in week one, before any interview. "Approve auto-approval threshold, Godavari leadership"
passes the owner check. "100 percent accuracy on KYC fields", "continuous fine-tuning" on Godavari's
files and "a secure, SOC 2 compliant cloud region" (no India) are all in sections the script does not
read for meaning. Exercise 3.1 lists the rest.

## 9.6 Build it with AI

**Context to provide:** the six artifacts (paths, not pastes, if the agent can read the folder); the
section list and the three-reader table from sections 02 and 03; the four will-not-do lines verbatim;
the rule that every number must be quoted from a source with its method; the CISO's conditions
verbatim. Say what it must not do: "do not compute any number not in the sources; do not name a model
or technology on page one; do not soften a condition into an adjective".

**A strong prompt (assemble, then attack):**

> Assemble a discovery document from the artifacts in these six folders, using exactly these sections
> [paste section 2.2]. For every number you write, add the source file in brackets; if a number is not
> in a source, do not write it. Quote the problem statement and the four will-not-do lines verbatim.
> Then, as a separate output, review your own draft as the CISO would: list every sentence in the data
> and security section that she could answer with "which region, approved by whom, when?". Then as the
> COO: list every number on page one he could not repeat to his board with its method.

**What the agent typically gets right:** the structure; linking; tables; a fluent page one; the
mechanical parts of the decision log; writing the checker (it is the kind of script an agent writes in
one pass, and it will propose sensible column-matching).

**What it typically gets wrong for this concept:**

| Mistake | How it shows | Fix |
|---|---|---|
| **invents connecting numbers** | "67 percent faster", "12,000 hours a year", "2.4 crore in savings" | W2; and the prompt's "source in brackets" rule; delete anything without one |
| **turns the honest case into a savings case** | drops Day 9's minus 1.12 crore; calls it a cost case | check page one against Day 9's "this is a speed case, not a cost case" |
| **softens conditions** | "secure, compliant cloud region"; "data residency respected" | quote the condition; say "in any environment, including tests, logs and backups" |
| **drops or blurs refusals** | "out of scope: phase 2"; the chatbot as a "phase 2 quick win" | E4; the will-not-do lines verbatim from Day 8 |
| **names technology on page one** | "a GPT-4o extraction pipeline with RAG" | W1; the COO signs outcomes |
| **makes the vendor the decider** | "decided by Kaagaz"; "Godavari leadership" | every decided-by is a named role at the customer, except on Kaagaz's own lines |
| **uses the SOP, not the real workflow** | "the documented 12-step process" | section 3 from Day 6's nineteen steps |
| **removes the human decision** | "clean files auto-approved" | finding A6 and decision D07; this one is a governance line (Day 32) |
| **agrees with every objection** | asked to draft the readout answers, it says yes to the chatbot and to on-prem forever | ask for "not now, because, and instead", with the reason taken from a signed artifact |

## 9.7 How do you know it's right?

1. **The checker passes** with no errors, and every warning is either fixed or explained.
2. **Trace page one.** Each number on it, followed to its source, matches to the decimal (9.1, not 9;
   28 percent and 31, both).
3. **Read section 8 as the CISO.** For every sentence, ask "which, who, when?". Every condition is in
   the words of the person who set it.
4. **Read section 3 as a team lead.** Nineteen steps, their column names, the tracker kept.
5. **Count the refusals.** Four will-not-do lines with reason, alternative and names; each parked
   item with a revisit point.
6. **Every decision's decider is the right person**, not just a person: the compliance head for the
   error rate, the CISO for the gates, the COO for scope.
7. **The changes are marked and logged**; the change log lists exactly the changes in the text.
8. **Nothing restates a source** that could be a link and a conclusion.

**Review checklist:**

- [ ] checker: 0 errors; warnings explained
- [ ] problem sentence verbatim, with who signed it and when
- [ ] page one: under 450 words, no model names, the honest money (both the net and the floor), the refusals, today's decisions
- [ ] every number with its method or a link; disagreements between sources shown, not resolved silently
- [ ] section 8: each condition in its owner's words; where files are processed at each stage; the gate and who controls it
- [ ] section 3: the real workflow, the tracker kept, in the operators' words
- [ ] will-not-do: reason, alternative, names; parked list with revisit points
- [ ] decisions: named decider, date; none decided by the vendor for the customer
- [ ] changes marked in the text and listed in the change log; next version dated
- [ ] signed by everyone who can veto, plus the operator leads

## 9.8 What goes into the engagement folder

| Artifact | Used by |
|---|---|
| `worksheet/godavari-discovery-document.md` (signed 1.0) | Day 11 (building begins on these terms), Days 21 and 23 (section 8's gates), Day 29 (the weekly readout opens with "still to decide"), Day 30 (bad news is measured against section 7), Day 32 (the will-not-do list defended under pressure) |
| the decision log | every later Day that cites a decision by ID |
| `code/check_discovery_doc.py` | every new version, before it is sent; Day 42's capstone document |

## 9.9 Extend it

- Add a `--diff old.md new.md` mode that lists decisions removed (never allowed) and decisions added.
- Run the checker on Day 4's memo, Day 8's plan and Day 9's case. Which checks make sense for them, and
  which do not? What does that tell you about which document is the signature document?
