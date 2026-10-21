# Review queue design · Godavari Finance: loan-file intake pilot

> Engagement folder · Day 18 · Week 6, Thursday 3 December 2026 · Version 0.1 (draft for review) · For Srinivas, the
> Vijayawada team lead, Lakshmi and the senior analyst (eval owners), and the compliance head · All numbers are from
> `data/band-report.md` and `data/pilot-week-1/pilot-week-report.md`; every file in them is synthetic

## 1. What an analyst sees on a file

1. **Look at this first**: one field per file, the one most likely to be wrong and most costly if it is. For now it is
   always the on-road price (it was misread six times in our 150 test files, for example "Rs I,37,150" read as 37,150).
   The file cannot be approved until this field is checked.
2. **Fields to check**: highlighted, each beside the line of the document it came from. Confirm or correct, with a
   reason from a list.
3. **Key in from the page**: fields the system was unsure about. It offers no guess. "Not in the file" is an answer.
4. **Accepted fields**: no action needed, each still shown with its source line.
5. **Rules, branch note and decision record**: each rule with its sign-off status and Godavari's clause; what the
   branch must fix; who decided, when, on which pages, and what was accepted, confirmed, corrected or keyed.

Every label is in English and Telugu. The Telugu labels for applicant name, address and monthly income are copied
from the form; the rest are drafts. **Lakshmi and the Vijayawada team lead: please correct them before Monday.**

## 2. The bands and what they cost

| | Every field reviewed | Old settings | Proposed bands |
|---|---|---|---|
| fields needing no action (of 1,800 test fields) | 0 | 1,408 | 971 |
| wrong values nobody is told to check | 0 | 7 | 0 |
| analyst minutes per file, twelve mandatory fields | 2.91 | 1.31 | 1.83 |
| analyst hours a month at 1,400 files | 67.8 | 30.5 | 42.6 |

The proposed bands cost about 12 analyst hours a month more than the old settings (about Rs 5,500 at Rs 456 an hour)
and remove about 65 unflagged wrong values a month. Minutes are estimates until the screen's timer measures week one.

Handwritten Telugu fields are always checked until each field has been right on at least 253 test fields with none
wrong (the senior analyst's condition, written as a number). On printed pages, three fields in four need no action.

## 3. Checks behind the analyst

- **Spot checks**: after approval, about 10 percent of files per branch (at least three a week) get a blind second read
  of their accepted fields: Kukatpally by the senior analyst, Guntur by Lakshmi. Disagreements go to the two team
  leads. The draw uses a key held by the compliance head; analysts are not told which files are drawn.
- **Workload signals**: the screen records seconds per field. A session where fields are checked in under three
  seconds and the look-first field in under two, or with three approvals inside twenty minutes, goes to the team lead
  as "these files need a second read; this afternoon was overloaded". Speed alone is never flagged.

## 4. Corrections

Every correction is kept with the old value, the new value, a reason and the analyst. Corrections become candidate
examples for the golden set's development part, only after a second label and the team leads' adjudication. The
rehearsal week produced 35 candidates.

## 5. Decisions needed before Monday 7 December

| # | Decision | Who |
|---|---|---|
| 1 | the 1.5 percent bar for accepted fields (the senior analyst's own keying error on the golden set) | the eval owners |
| 2 | the impact weights that choose the look-first field | the eval owners |
| 3 | the citation table: one circular clause per signed rule | the compliance head, with the rules at M10 |
| 4 | what the screen records about analysts, who sees it, how long it is kept, and that it never goes to HR | Srinivas, the Vijayawada team lead and the six pilot analysts; retention with the compliance head |
| 5 | re-adjudication of GF-42025 (requested amount) and GF-41981 (applicant name), whose labels look wrong | Srinivas and the Vijayawada team lead |

## 6. Not yet proved

- The real minutes per field (week one's timer).
- The error rate of accepted fields in production: the spot checks bound it at 7.6 percent after one week and need
  about six weeks to say something sharp.
- That the on-road price misreading is fixed: it needs the system's "letter among the digits" check, measured on the golden
  set, before the look-first field can move to other fields.
