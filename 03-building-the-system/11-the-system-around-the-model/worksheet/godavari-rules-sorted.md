# Godavari Finance · the rules, sorted: regulatory, policy, judgement

> Engagement folder · Day 11 · Week 3 · Every rule and judgement in loan-file intake that the engagement has
> found so far, with its bin, where it lives, its owner, its source and its rule id in the prototype. Built from
> the Day 6 transcripts and synthesis, the compliance head's week-2 alternatives list, and the Day 10
> discovery document. Synthetic Godavari policy for the course; RBI references are to the public texts, which
> the compliance head owns.

**Bins.** Regulatory: from the RBI or the law; code; no override. Policy: Godavari's own; code; a named analyst
may override with a written, logged reason. Judgement: the model proposes with evidence; a person decides.
Format and verification checks are engineering checks in the envelope, owned by the FDE, not signed rules.

## Two-wheeler (v0.3, reviewed draft) and gold (v0.1, draft)

| # | Rule or judgement | Bin | Lives in | Owner | Source | Rule id |
|---|---|---|---|---|---|---|
| 1 | photograph, PAN or Form 60, proof of identity, proof of address in the file of record | regulatory | code | the compliance head | RBI KYC Master Direction; checklist | TW-DOC-02 to 05; GL-DOC-02 to 05 |
| 2 | co-applicant KYC in the file when a co-applicant is named | regulatory | code | the compliance head | RBI KYC Master Direction | TW-DOC-14 |
| 3 | application form, income proof, bank statement, dealer quotation, NACH mandate, cancelled cheque, insurance proposal, declaration and consent, field verification | policy | code | the compliance head (checklist owner) | Godavari two-wheeler checklist (fourteen documents in all) | TW-DOC-01, 06 to 13 |
| 4 | appraisal certificate (purity, gross and net weight) and the key fact statement | regulatory | code | the compliance head | RBI gold-lending directions 2025; KFS requirement | GL-DOC-06, GL-DOC-09 |
| 5 | gold application form, pledge form, ownership declaration | policy | code | the compliance head | Godavari gold checklist (nine documents in all) | GL-DOC-01, 07, 08 |
| 6 | address proof is an OVD or on the signed alternatives list, in the applicant's own name | regulatory | code | the compliance head | RBI KYC Master Direction; alternatives list v0.3 (week 2) | TW-ADDR-LIST, GL-ADDR-LIST |
| 7 | a utility bill used as address proof is at most 60 days old | regulatory | code | the compliance head | alternatives list v0.3 | TW-ADDR-AGE, GL-ADDR-AGE |
| 8 | no page shows an unmasked Aadhaar number | regulatory | code, every page | the compliance head | Aadhaar masking requirement; the circular three branches missed (code CHECKLIST_DRIFT) | TW-KYC-MASK, GL-KYC-MASK |
| 9 | gold amount within the tiered LTV cap (85, 80, 75 percent) of net weight x purity x the published 22-carat rate on the appraisal date | regulatory | code | the compliance head; treasury publishes the rate | RBI (Lending Against Gold and Silver Collateral) Directions, 2025 | GL-LTV |
| 10 | two-wheeler amount Rs 20,000 to Rs 3,00,000 | policy | code, override | product owner (synthetic) | product note | TW-AMT-RANGE |
| 11 | two-wheeler amount at most 90 percent of the on-road price | policy | code, override | product owner | product note | TW-AMT-MARGIN |
| 12 | tenure 12 to 48 months (two-wheeler), at most 12 (gold) | policy | code, override | product owner | product note | TW-TENURE, GL-TENURE |
| 13 | applicant 21 to 60 on the application date | policy | code, override | product owner | product note | TW-AGE |
| 14 | dealer quotation dated 0 to 30 days before the application | policy | code | product owner | product note | TW-DATE-QUOTE |
| 15 | bank statement ends within 30 days before the application and covers three months | policy | code | product owner | product note | TW-BANK-AGE |
| 16 | gold purity 18 to 24 carat; appraisal 0 to 3 days before the application | policy | code | product owner | product note | GL-PURITY, GL-APPRAISAL-DATE |
| 17 | sanction before disbursement | policy | code, in the core write | credit operations | process note | `core_write.push_to_core` |
| 18 | an analyst sees only files of branches in her Active Directory groups; no all-branches group | regulatory (the CISO's) | code, inside the query | the CISO | Day 6, finding A1 | `routing.visible_to`; Days 15, 22 |
| 19 | nothing is written to the core system without a named analyst's approval; one record per file | regulatory (the auditor's, via D07) and the owner's condition | code | the compliance head; the core-system owner | D07; finding A5 | `core_write.push_to_core` |

## Envelope checks (engineering, not signed rules)

| Check | What it guards against | Id |
|---|---|---|
| a document claim's quote is on the cited page, which carries the claimed title | hallucinated presence | ENV-GROUND |
| a value's digits are in its own quote | silent conversion (the 2019 monthly-as-annual failure) | ENV-EVIDENCE |
| confidence at or above the field's threshold; "unsure" sent to review | guessing | ENV-CONFIDENCE, ENV-UNSURE |
| PAN format and holder letter; PAN card against form; surname initial | OCR misreads | ENV-PAN-FORMAT, ENV-PAN-MATCH, ENV-PAN-SURNAME |
| name on form against PAN card | transliteration variants | ENV-NAME-MATCH |
| income on proof against form | misread income | ENV-INCOME-MATCH |
| dealer empanelled for the branch | wrong or invented dealer | ENV-DEALER |
| salary-account pick has three monthly salary credits | wrong statement chosen | ENV-SALARY-ACCT |

## Judgements (the model proposes; a person decides)

| Judgement | The model's job | The check or the reviewer |
|---|---|---|
| reading a scanned, stamped, hand-annotated application form | extract each field with page and quote; say "unsure" | the envelope; the analyst sees the crop (Day 18) |
| which page is which document, in a 40-page unordered bundle | label every page | grounding; missing plus unclassified pages goes to review |
| which of several bank statements is the salary account | pick one | ENV-SALARY-ACCT; the analyst decides on disagreement |
| explaining a discrepancy to the analyst and the branch | draft the note from code's findings | code checks every rule id is cited |
| whether a document is genuine | none; not attempted | the analyst, on the original |
| whether to sanction the loan | none | a named credit manager; never automated (A6, D07) |

## Written down because of this sorting

- The acceptable alternatives for address proof (rows 6 and 7), which lived "in my head and in Lakshmi's",
  are now a table in code, v0.3. The compliance head's later decision D04 (Day 10) uses the same definition.
- Rule 15 and rule 14 were "what the analysts do" and had no written source; the product owner confirms them
  before the signature at M10.
