# 02 · Why Enterprise Documents Are Hard: Scans, Tables, Headers, Two Scripts and Versions

> Day 15 · Section 2 of 16 · [Chapter overview](README.md) · Previous: [01 · Why retrieval for enterprise documents](01-why-retrieval-for-enterprise-documents.md) · Next: [03 · Chunking](03-chunking.md)

---

## 2.1 The pile, as it really is

A retrieval tutorial starts with clean Markdown. Godavari starts with this:

| What | What it looks like after text extraction | What it does to retrieval |
|---|---|---|
| Circulars from 2024, printed, signed, stamped, scanned | OCR text with letter confusions ("docurnent", "app1icant"), a rotated APPROVED stamp read as `~ D3V0RPPA · ECNA1LPM0C ~`, words hyphenated across lines | exact words miss; junk tokens enter the index; the stamp sits in the middle of a clause |
| Circulars from 2025 onwards, born digital | clean text, but every page carries "GODAVARI FINANCE LTD · CREDIT OPERATIONS", the circular number and title, "Page 2 of 3", "Internal · uncontrolled when printed" | the same 20 words on every page of every document: every chunk matches every query a little |
| Tables (income proof by applicant type, LTV caps, address alternatives) | rows as `\| a \| b \| c \|` lines, the header row repeated on the next page, sometimes not | a row cut away from its header is meaningless ("twelve-month bank statement" for whom?) |
| Telugu | branch-staff summaries in Telugu script inside English circulars; analysts' notes in Telugu written in Latin letters, spelled three ways | tokenizers shred the script; spellings do not match |
| Versions | forty circular topics (Day 4's "forty circulars in email"), a third of them revised at least once; the 2024 checklist still printed on desks | the superseded version often ranks first: it is older, longer, and quoted more |
| Past loan files | masked decision summaries from the core system, one page each, with branch, product, decision and a note | the most similar file is often in a branch the analyst may not see |

None of this is exotic. It is what every Indian lender, insurer and hospital network has in its document
management system. The FDE who has seen it before plans for it in week 1; the one who has not discovers it in the
demo.

## 2.2 Scans, OCR and stamps

Optical character recognition (OCR) turns a page image into text. On a clean print it is very good. On a 2024
circular that was printed, signed, stamped and scanned at 200 dpi it makes three kinds of mistakes:

- **Letter confusions**: "rn" read as "m", "l" as "1", "o" as "0", "e" as "c". The word "document" becomes
  "docurnent". A keyword search for "document" misses that chunk.
- **Layout noise**: a stamp at an angle, a signature, a handwritten "noted" in the margin, read as a line of
  garbage in the middle of the text.
- **Lost structure**: the scan of a numbered clause sometimes loses the number, so "4.2" is no longer at the start
  of the line and a parser cannot find the clause.

You cannot fix OCR errors in the retriever. You can do three things about them: drop lines that are clearly junk
(section 03.2), let a retriever that is tolerant of spelling (character-level or dense) catch some of what the
exact-word one misses (section 05), and, most usefully, ask the compliance head for the born-digital original.
At Godavari the circulars from 2025 onwards are Word files converted to PDF; only the 2024 ones are scans. Asking for
the source is often the biggest quality win of the week, and it is a discovery question, not an engineering one.

The generator in this chapter imitates the scans honestly but kindly: about 4 percent of long words on a scanned page
get a letter confusion, the stamp appears on page 1, and long words wrap with a hyphen. It never corrupts numbers or
circular numbers, so that the labelled answers stay checkable. Real OCR is not so kind: a PAN read as `AKLPR482lM`
does not match anything, which is one more reason the PAN lookup in section 05 uses a token computed from the
core system's record, not from the scan.

## 2.3 Tables, headers and footers

Two things in a PDF look like content and are not, and one thing looks like decoration and is the most important
content on the page.

**Headers and footers** repeat on every page. In the synthetic corpus, 1,508 lines across 377 pages are boilerplate:
four lines per page. They are harmless to a human and poisonous to search. BM25 gives them low weight because they
are everywhere, but they still shift document lengths, and a fixed-size chunker happily makes a chunk that is half
"Page 2 of 3 Internal · uncontrolled when printed GODAVARI FINANCE LTD · CREDIT OPERATIONS" and half the clause you
wanted. Worse, the running header contains the circular's title, so every chunk of a long circular matches the
title words, and the one chunk that answers the question competes with five that only share the header.

**Tables** carry the rules that matter most. Godavari's income-proof circular, GFL/CO/2025/027, has one table: six
rows, one per applicant type, three columns (type, acceptable proof, conditions). The row Lakshmi needs is
"Self-employed (shop owner, trader, kirana shop) | twelve-month bank statement of the business account, or GST
returns for the last four quarters | a self-declaration of income is also accepted when the requested amount is below
Rs 1,00,000 and a field visit confirms the business". In the rendered PDF the table starts at the bottom of page 2 and
continues on page 3, and page 3 repeats the header row. A chunker that does not know it is in a table cuts the
salaried row onto page 2's chunk with the footer, and the self-employed row onto page 3's chunk with the running
header, with nothing saying what the columns mean.

## 2.4 Telugu and English on one page

Godavari's documents mix two scripts and two ways of writing one language:

- **Telugu script** in English circulars: the 2025 circulars end with a "Summary for branch staff" in Telugu, for
  example "ఆదాయ రుజువు: స్వయం ఉపాధి దరఖాస్తుదారులు 12 నెలల బ్యాంకు ఖాతా వివరాలు లేదా నాలుగు త్రైమాసికాల జీఎస్టీ
  రిటర్నులు ఇవ్వాలి" (income proof: self-employed applicants give twelve months of bank account details or four
  quarters of GST returns).
- **Telugu in Latin letters** in analysts' notes: "Applicant kirana kottu naduputhunnadu; nelaki aadaayam about Rs
  30,000". The same word is spelled "aadaayam", "aadayam" and "adayam" by three different people. "Vyavasaayam" and
  "vyavasayam" (agriculture). "Adde" and "addhe" (rent). 92 of the 300 synthetic summaries carry notes like this.

Each breaks a different part of a naive pipeline. Here is the first one, from the project's real output:

```text
Telugu, two tokenizers: naive \w+ gives ['ఆద', 'య', 'ర', 'జ', 'వ']; the lexical analyzer gives ['ఆదాయ', 'రుజువు']
```

The regular expression `\w+` is what most people write first. In Python, `\w` matches letters and digits, but
Telugu vowel signs (the marks that turn ద into దా) are Unicode combining marks, not letters, so `\w+` cuts every
word at every vowel sign. "ఆదాయ రుజువు" (income proof) becomes five meaningless fragments that match fragments of
every other Telugu word. The fix is one line: match the whole Telugu block, `[ఀ-౿]+`. The bug is common
because nothing crashes; Telugu queries just return rubbish, and nobody on an English-speaking team notices.

Transliteration breaks the other half. "aadayam" and "aadaayam" are different strings to any exact-match index, and
a general-purpose embedding model, trained mostly on English and on Telugu script, has seen very little Telugu in
Latin letters, so it does not reliably place them near each other either. Section 05 shows why the analyzer you
control (a few folding rules: "aa" to "a", "th" to "t") beats the model you do not on these words.

There is a third, quieter problem: Telugu is agglutinative. "రుజువు" (proof) and "రుజువుగా" (as proof) are one word
with a suffix. An exact-word index treats them as unrelated. The corpus writes the key terms in their plain form
in the branch summaries, and exercise 3.4 asks you to measure what character n-grams would buy on suffixed forms.

## 2.5 Versions and superseded circulars

The compliance head told you in week 2: "I update [the checklist] when a circular changes. The analysts do not
always get the new one. Last year the Aadhaar masking rule changed and three branches were still sending unmasked
copies in August." In the corpus, that rule exists twice:

- GFL/CO/2024/007, effective 1 February 2024: an unmasked copy "may" be kept with the customer's written consent.
- GFL/CO/2025/012, effective 1 June 2025, superseding it: "An unmasked Aadhaar copy is not kept with consent."

The two versions use nearly the same words. A search for "unmasked Aadhaar copy kept with consent" matches the old
one better, because the old one literally says "kept ... with the customer's written consent". A retriever that
does not know about versions will confidently return the rule that stopped being true eighteen months ago, with a
perfect citation. This is the most dangerous retrieval failure in a regulated business, because it looks correct.

Across the corpus, 61 approved circulars cover 40 topics; 21 of them have been superseded. Add a draft circular the
compliance head is still working on, which analysts must not see at all, a 2024 product rulebook replaced in January
2026, and the address-proof alternatives annex that the compliance head signed on 20 November (the list that "lives
in my head and in Lakshmi's", Day 6 finding A7, now written down).

## 2.6 The corpus this chapter generates

Everything above is generated by `code/godavari_retrieval/corpus.py`, seeded, in about 40 milliseconds:

```text
documents: 370 = annex 1, circular 62, loan_decision 300, rbi_digest 3, rulebook 4
approved circulars: 61 in 40 series; 21 superseded; drafts: 1
loan decisions per branch: Kukatpally 50, Dilsukhnagar 50, Vijayawada-Benz Circle 50, Guntur 50, Warangal 50, Rajahmundry 50
languages: en 274, mixed 4, te-latn 92
scanned (OCR noise, stamp, hyphenation): 9; pages: 377
```

Two design decisions in the generator matter for everything that follows:

1. **The register and the text are separate.** Each document has a register entry (type, product, dates,
   supersession, approval, branch), the way the compliance head's circular register or the core system's file
   record holds it, and separately the pages as a PDF extractor would hand them over. The chunker only sees pages.
   Metadata comes from the register. Section 04 explains why you never parse an effective date out of the text.
2. **The rulebook numbers come from Day 11's signed rules.** The two-wheeler rulebook's "Loan amount Rs 20,000 to
   Rs 300,000; finance up to 90 percent" is generated from `rules_two_wheeler.MAX_AMOUNT` and friends in
   [Day 11](../11-the-system-around-the-model/README.md)'s package, imported by path. The text an analyst reads
   cannot drift from the rule the code enforces, and a test checks it.

The six branches and their AD groups are Day 11's too (`GF-BR-KKP01` for Kukatpally to `GF-BR-RJY06` for
Rajahmundry), and so are the empanelled dealers that appear in the summaries. Nothing is copied.
