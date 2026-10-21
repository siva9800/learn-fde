# 01 · Why Retrieval for Enterprise Documents: The Right Clause, for the Right Person, From the Right Version

> Day 15 · Section 1 of 16 · [Chapter overview](README.md) · Next: [02 · Why enterprise documents are hard](02-why-enterprise-documents-are-hard.md)

---

## 1.1 A Wednesday in Vijayawada

It is Wednesday 25 November 2026, week 5 of the engagement. The discovery document was signed on Friday (milestone
M08, [Day 10](../../02-discovery-and-decomposition/10-the-discovery-document/README.md)). Lakshmi has a Guntur
two-wheeler file open. The applicant runs a kirana shop near Brodipet, wants Rs 85,000, has no income tax return,
and has given a twelve-month bank statement and a notarised rent agreement with his landlord's electricity bill.

Lakshmi has two questions, and she asks them a dozen times a day in some form:

1. **What does the policy say?** Is a bank statement enough income proof for a self-employed applicant, or does
   Godavari still want two years of returns? Is a rent agreement acceptable for the address, and with what?
2. **What have we done before?** Has an analyst in her region accepted a file like this, and on what evidence?

Today she answers the first from a printed Word checklist that, as she showed you in week 1, is the 2024 print
when a 2025 version exists (Day 6, code CHECKLIST_DRIFT), and from circulars that live in email "with unclear
versions" (Day 4). She answers the second from memory, or by asking the senior analyst across the room. A junior
analyst like Bhavani does not have the memory, so she sends the file back "to be safe". The compliance head
thinks that habit is half of all send-backs (Day 6, transcript 05).

Retrieval is the engineering that answers both questions in two seconds, inside the screen Lakshmi already has
open, with the clause and the past file in front of her, so she can decide. That is the whole job of this chapter.

## 1.2 Not the chatbot

Before anything else, a sentence you will repeat to the COO: **this is not the branch policy chatbot.**

The COO asked for that chatbot at kickoff. Day 4 scored it 55 of 100 and declined it: nobody counted the calls,
nobody owned the forty circulars, no branch was asked. Day 10 made it decision D06 ("the branch chatbot is not in
these 90 days"), with Kukatpally counting policy calls from 9 November and Guntur from 23 November so that the
question can come back at the day-90 review with a number. It is on the signed will-not-do list.

What this chapter builds is different in four ways, and you should be able to say all four:

| | The declined chatbot | This chapter's retrieval |
|---|---|---|
| Who uses it | branch staff, anyone | the 40 credit-ops analysts, inside the review queue |
| What it does | answers free questions in conversation | returns clauses and past files for the file on screen; the query is pre-filled from the file |
| What it produces | a generated answer | the clause text with its citation, and up to three past files with their decisions; any note is drafted only from those |
| Where it lives | a new channel | a panel in the screen the analyst already uses (Srinivas, Day 6: "a fifth window is a no") |

The difference is not cosmetic. It is the difference between a product nobody asked for and a tool inside the
workflow the engagement is already changing (W6, the review queue, in [Day 8](../../02-discovery-and-decomposition/08-scoping-the-first-90-days/README.md)'s plan).
If the COO later wants the chatbot, the retrieval layer built here is what it would stand on, and the count at
Kukatpally and Guntur is what decides whether it is worth it.

## 1.3 The finding that shapes everything

In week 2, five interviews told you the same thing independently (Day 6, finding A1, code BRANCH_ISOLATION): branch
visibility at Godavari is enforced by Active Directory groups synced nightly from HR; a branch user sees only that
branch; a regional analyst sees the region; there is no "all branches" group and the CISO will not create one for
a vendor. The CISO's words: anything that retrieves a loan file "has to filter by the caller's groups at the moment
of the query, not at the time we indexed the file". The Kukatpally manager's reason: "Our targets are per branch.
If I could see Miyapur's pipeline I would know their dealers."

So the past-files half of the panel has a hard rule attached. When Lakshmi asks for similar files, the most similar
file in the whole company may be a Kukatpally file. She must never see it: not in the list, not in a count, not in
a snippet, not in a note the system drafts, not in a debug log. Section 06 shows, with real output, how the most
common first design leaks exactly that file, with its dealer's name and its on-road price, while showing a clean
list on screen.

## 1.4 Why it matters for your career

Retrieval is in the applied-AI bucket that appears in 80 percent or more of the 1,000 FDE postings analysed in
2026 (CURRICULUM.md), and the course plan names "SSO and permission-aware retrieval" as one of the things that
makes deployment mean the customer's environment rather than yours. In practice, three things separate the FDE
who gets trusted with a customer's documents from the one who does not:

- **They know where retrieval quality is actually lost.** It is rarely the embedding model. It is the scanned page,
  the table split across a page break, the repeated header that matches every query, the superseded circular that
  ranks first because it is older and longer. The fix is boring engineering, and it moves the number more than any
  model swap (section 03 measures it).
- **They can explain permissions to a CISO in one diagram.** "The filter runs inside the query, before ranking; the
  index stores document groups, not users; the caller's groups are resolved per request; anything stale or unknown
  fails closed." A CISO who hears that in week 5 writes it into her review as a strength. One who discovers in week
  8 that you filter afterwards stops trusting everything else you built (Day 6, section 08.3).
- **They measure retrieval on its own.** Recall at k on a small labelled set, before any model sees a passage, so a
  bad answer can be traced to the retriever or to the model and not argued about.

## 1.5 What you will be able to do

By the end of the chapter you can take a pile of scanned, stamped, mixed-language PDFs with versions, and:

- clean and chunk them by structure, keeping tables intact and every chunk tied to a clause and a page;
- index metadata as a first-class part of the search (type, product, branch, language, effective date,
  superseded-by, approval status, access groups);
- run BM25 and a dense retriever, fuse them with reciprocal rank fusion, rerank, and say which wins on which query
  and why;
- enforce a permission filter at query time from directory groups, and prove with an audit that nothing leaks;
- handle superseded documents and cite the exact clause;
- evaluate retrieval with recall at k on labelled queries, with an interval, and gate changes on it.

## 1.6 The hard parts, named early

This chapter feels like three chapters at first: document engineering, search engineering and security engineering.
That is normal; they are one problem seen from three sides. Three things will feel wrong before they feel right:

1. **The best retrieval improvement is often deleting text** (headers, footers, stamps), not adding a model.
2. **Hybrid search does not mean "both are better than either".** Fusion rewards agreement; a document that only one
   retriever finds can sink. Section 05 shows the case and the fix.
3. **The leak is invisible on screen.** A post-filter shows a correct list. The leak is in the count, the log and the
   note. You find it only if you look for it on purpose, which is why the permission audit is a test, not a review
   comment.
