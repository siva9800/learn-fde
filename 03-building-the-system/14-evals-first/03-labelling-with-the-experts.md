# 03 · Labelling With the Customer's Experts: The Guide, Two Labellers, Trajectories, Agreement and Adjudication

> Day 14 · Section 3 of 16 · [Chapter overview](README.md) · Previous: [02 · The golden set](02-the-golden-set.md) · Next: [04 · What to measure](04-what-to-measure.md)

---

## 3.1 Who labels, and why it must be them

Day 6 found the labellers, and their conditions are the reason this section exists. Lakshmi: "if my answers are
the standard, yes." The senior analyst in Hyderabad: "if my answers are the standard and not the demo's, and I want
to see every failure." The compliance head, for completeness: "I sign it."

Three properties make them the right people, and each one rules out a tempting shortcut:

| Property | Why it matters | The shortcut it rules out |
|---|---|---|
| they do the work today | their judgement is what the system replaces; "correct" means what they would have typed | Kaagaz engineers labelling, "because we know the documents now" |
| they are trusted by the people who will decide | when the COO asks "says who?", the answer ends the argument | an outsourced labelling vendor, cheaper and faster, whose labels nobody at Godavari has a reason to believe |
| one of them is the sceptic | the person most likely to reject the system has defined what passing means | choosing the friendliest analysts, and losing the sceptic in week 8 |

Hamel Husain's guide to LLM judges (section 16) names the same idea from the product side: identify one
**principal domain expert** whose judgement sets the standard, and do not let developers act as their own expert.
For an FDE, the extra twist is that the expert works for the customer, so you are borrowing her hours from her day
job. Day 8 had the team leads book them, never in the last three days of a month.

Why two labellers and not one? Because one person's labels contain her slips and her habits, and you cannot tell
them apart from the truth. Two independent labels on every file let you measure how often careful people disagree
(the ceiling on any system's accuracy claim), find the places the labelling guide is vague, and catch most of each
person's slips. Labelling every file twice doubles the cost; this chapter does it on all 200 files because the set
is small and the stakes (a go or no-go) are high. A common compromise on larger sets is to double-label a random
fifth and single-label the rest, then report agreement on the double-labelled part.

## 3.2 The labelling guide comes first

Before anyone labels a file, the FDE and the two labellers write a **labelling guide** together: a few pages that
say, for every output, what counts as correct. Godavari's is in the worksheet folder
([`worksheet/godavari-labelling-guide.md`](worksheet/godavari-labelling-guide.md)), version 1.0, signed on the M05
date. Its section numbers are cited in the adjudication log, which is how you know the guide is doing its job.

The parts that matter most are the ones that look pedantic:

- **4.1 Address:** the full address as on the form, including the city and PIN code.
- **4.2 PAN:** only from the PAN card. If there is no PAN card, leave it blank, even if the form shows a PAN. (The
  form's PAN is the customer's claim; the card is the evidence. The model must learn the same rule, so the labels
  must encode it.)
- **4.4 Amounts:** never convert. If a declaration does not say monthly or annual, type it as written and add a note.
  (This is the 2019 OCR pilot's failure from Day 6, written as a labelling rule.)
- **4.6 Cannot read it:** type UNREADABLE; do not guess. (The synthetic labellers in this chapter never use it; real
  ones will, and the adjudicators read those pages with them.)

Each of those rules exists because two careful people did something different without it. You will not think of
all of them in advance. The first thirty labelled files (M05) are where most of them are found; the guide is
revised before the next hundred.

## 3.3 What a label records

A label is everything the analyst would have produced and decided for the file, as she would have done it on a
normal day. Here is one adjudicated record from the truth file, trimmed (`data/golden/truth-adjudicated.jsonl`):

```json
{"file_id": "GF-42025",
 "fields": {"address": "38-70, BRODIPET, GUNTUR 522002", "applicant_name": "PRASAD BANDARU",
            "application_date": "29-10-2026", "date_of_birth": "16-03-1997", "dealer_code": "DLR-GNT-011",
            "mobile": "6353808235", "monthly_income": "60000", "on_road_price": "109500",
            "pan": "DGLPB2476W", "quotation_date": "09-10-2026", "requested_amount": "70060",
            "tenure_months": "24"},
 "missing": ["proof_of_address"], "send_back": true, "reasons": ["MISSING:proof_of_address"],
 "minutes": 56.7, "split": "test", "bundle_sha256": "...",
 "trajectory": [{"step": 1, "action": "open_file", "pages": 23},
                {"step": 2, "action": "find_document", "doc": "application_form", "page": 12}, "...",
                {"step": 29, "action": "decide", "send_back": true, "reasons": ["MISSING:proof_of_address"]}]}
```

Keep this record in mind; it comes back in section 11, because one of its values is wrong.

Four groups of answers, and each one feeds a metric:

| Group | What the analyst records | The metric it feeds (section 04) |
|---|---|---|
| fields | twelve mandatory fields per product, as typed | field-level accuracy (Day 9) |
| documents | each checklist document present or absent, with its page | page classification, document detection, completeness recall and precision |
| decision | would she send it back, and every reason from the list | send-back recall and precision |
| trajectory and time | the steps she took, with page numbers, and the minutes | evidence-page agreement; the human cost; the benchmark for Day 17 |

## 3.4 Recording expert trajectories

OpenAI's FDE team, working with a semiconductor customer, defined **trajectories** with the customer's experts:
"the sequence of actions an expert would take to solve specific problems", which then "become labeled evaluation
sets against which the LLM's performance is measured". In a coding example from the same summary they recorded "the
actual sequence of 20+ actions a human engineer would follow".

Why record the steps and not only the answer? **The steps show where the evidence is**: Lakshmi reads the PAN from
page 21, the PAN card, not page 12, the form; a model that gives the right PAN from the form will fail on the next
file where the two disagree, so the harness reports **evidence-page agreement** (100 percent on the synthetic files,
because the stub reads the first page of each type as the analysts do; one of the first numbers to watch on real
files). **The steps are the benchmark for workflows**: Day 17's state machine is compared with them, step by step.
**The minutes are the business case**: measured human effort per file, by stratum (42 and 48 minutes here), which Day
37 compares against production. And now and then the steps reveal a check nobody wrote down, as Day 6's shadowing did.

What to capture, per step: the action (open, find document, read field, cross-check, look up, decide), the page or
pages, and a timestamp. Do not capture free-text think-aloud for every step; it is expensive and rarely used. Ask
for a one-line note only where the analyst did something unusual.

## 3.5 Inter-annotator agreement, in plain words

**Inter-annotator agreement** is how often two labellers, working independently on the same items, give the same
answer. It answers a question that comes before any model is scored: is the task defined well enough that careful
people agree on it? If Lakshmi and the senior analyst agree on 92 percent of PANs, a model cannot meaningfully be
claimed to be 99 percent accurate on PANs, because "accurate" has a 92 percent ceiling until the guide is fixed.

There are two measures, and you need both.

**Raw agreement** is the share of items where the two answers match. It is easy to explain and the right number for
field values, where there are thousands of possible answers and agreement by luck is nearly impossible.

**Cohen's kappa** is for yes-or-no and category answers ("would you send it back?", "is the PAN card present?").
Raw agreement misleads there, because when most files share the same answer, two people agree a lot just by both
saying the common thing. Kappa subtracts the agreement you would expect by chance from people with the same habits:

> kappa = (observed agreement - agreement expected by chance) / (1 - agreement expected by chance)

A worked example in Godavari's words: suppose 95 of 100 files are complete, Lakshmi marks 95 complete and the
senior analyst marks 95 complete, but they disagree on 10 files (each calls 5 of the other's "complete" files
incomplete). Raw agreement is 90 percent, which sounds good. But two people who each say "complete" 95 percent of
the time would agree about 90.5 percent of the time by chance alone. Kappa is (0.900 - 0.905) / (1 - 0.905), a little
below zero: on the files that matter, the incomplete ones, they do not agree at all. A test in the chapter holds
exactly this case (`test_kappa_punishes_agreement_that_comes_from_a_skewed_base_rate`).

How to read kappa: 1 is perfect, 0 is chance, below 0 is worse than chance. Published rules of thumb call values
above about 0.8 strong agreement; treat any such band as a conversation starter, not a pass mark, and always show
the raw agreement and the counts beside it.

## 3.6 Godavari's agreement report

This is the real output on the 150 test files, before adjudication (`code/build_golden_set.py`, also written to
`data/agreement-report.md`):

```text
  field                   n  exact agree  normalised
  applicant_name        150       82.0%       98.0%
  date_of_birth         150       66.0%       97.3%
  pan                   150       92.0%       92.0%
  address               150       95.3%       95.3%
  mobile                150       78.0%       98.0%
  requested_amount      150       61.3%       98.7%
  tenure_months         150       98.7%       98.7%
  monthly_income        100       67.0%      100.0%
  application_date      150       73.3%       98.7%
  on_road_price         100       56.0%      100.0%
  dealer_code           100       98.0%       98.0%
  quotation_date        100       64.0%       99.0%
  gross_weight_g         50      100.0%      100.0%
  net_weight_g           50      100.0%      100.0%
  purity_carat           50       98.0%       98.0%
  appraisal_date         50       66.0%      100.0%
  all fields           1800       79.8%       97.8%

  decisions (Cohen's kappa = agreement beyond chance; 1 is perfect, 0 is chance):
    would send the file back      raw  96.7%   kappa 0.93
    file is incomplete            raw  97.3%   kappa 0.95
    each required document found              kappa 0.94
```

Read it column by column, the way you would with the labellers in the room.

**Exact against normalised.** Exact agreement is 79.8 percent; after the registered normaliser forgives format
(Rs and commas, slashes in dates, case, a space in a mobile number), it is 97.8 percent. The 18-point gap is the
senior analyst typing "Rs 1,25,000" and "15/03/1986" where Lakshmi types "125000" and "15-03-1986". That is not
disagreement, and a report that showed 79.8 percent would send the team chasing a problem that does not exist. It
is also why the normaliser is part of the metric's definition (section 04.2): agree on it before the first score.

**The fields still below 98 percent after normalising are the guide's to-do list.**

- **PAN, 92.0 percent.** Nine of the twelve PAN disagreements are files with no PAN card, where the senior analyst
  typed the form's PAN and Lakshmi left it blank. Guide section 4.2 already says "only from the PAN card"; she is
  following twenty years of habit. The fix is a conversation and a sentence in bold on the form, not a model change.
- **Address, 95.3 percent.** Seven disagreements, all the senior analyst dropping the city and PIN code. Guide 4.1.
- **The rest** (a percent or two each) are genuine slips: a swapped digit in a date of birth, a letter confused in a
  dealer code. Those are what adjudication is for.

**Decisions.** A kappa of 0.93 on "would you send it back" and 0.95 on "is the file incomplete" are high, and the
raw disagreements behind them are worth reading one by one: the senior analyst not counting a father's electricity
bill as a problem ("we always accepted the father's bill") and accepting some over-margin amounts; Lakshmi not
counting the days on a utility bill. Each is a rule question, so each goes to the compliance head.

## 3.7 Adjudication: a written rule, named people, a log

**Adjudication** is how a disagreement becomes a single label. Do it by a rule written before labelling starts,
not by whoever is free that afternoon. Godavari's rule (in the guide, section 8, and in `code/evals/labels.py` as
`ADJUDICATION_RULE`):

1. Normalise both labels with the registered normaliser. If they are equal, that is the label.
2. A field typed differently goes to **Srinivas and the Vijayawada team lead**, together, who read the source page
   and record what is on the paper, citing the guide. (Two leads, one from each city, so neither city's habits win
   by default.)
3. A document, completeness or send-back disagreement goes to **the compliance head**, who decides it against the
   signed rules and the alternatives list. If no signed rule covers it, the file is sent back and the case goes on a
   rule-gap list.
4. **Nobody from Kaagaz adjudicates.** An agreed label is final unless an audit reopens it.

Rows from the real log (`data/golden/adjudication-log.csv`):

```text
file_id,item,lakshmi,senior_analyst,final,decided_by,reason
GF-40030,field:date_of_birth,09-01-1997,69-01-1997,09-01-1997,Srinivas and the Vijayawada team lead,read from the source page
GF-40109,reason:ADDRESS_STALE,False,True,True,the compliance head,decided against ADDR-AGE (60 days)
GF-40170,field:address,"35-19, Brodipet, Guntur 522002","35-19, Brodipet","35-19, BRODIPET, GUNTUR 522002",Srinivas and the Vijayawada team lead,labelling guide 4.1: the full address as on the form
GF-40417,field:pan,None,MVPPM5456S,None,Srinivas and the Vijayawada team lead,labelling guide 4.2: PAN only from the PAN card
GF-40430,reason:PHOTO_UNCLEAR,True,False,False,the compliance head,no signed rule makes this a send-back reason
GF-41166,reason:OVER_MARGIN,True,False,True,the compliance head,decided against TW-AMT-MARGIN (90 percent)
```

On the 150 test files: 39 field adjudications by the team leads, 26 document and decision adjudications by the
compliance head, 65 in all, out of 1,800 field cells and 150 decisions. Two things to notice.

**Adjudication is rule-making in disguise.** "Photograph unclear" was written as a send-back reason six times
across the 200 files, and the compliance head ruled each time that no signed rule makes it one. That is either a
gap in the rules (add a photograph-quality rule, signed) or a habit to stop (tell the branches the photo is fine).
Either way, the decision now exists in writing, and the model will be measured against it. The same is true of the
father's electricity bill: before the signed alternatives list v0.3 (Day 11), it was a matter of opinion; now it
is a rule, and the adjudication cites it.

**The log is evidence for the auditor.** When the RBI inspection arrives in February 2027 and asks how Godavari
knows the system's completeness check matches its own policy, the answer includes this log: who decided each
disputed case, against which rule, on which date.

## 3.8 Agreement is not correctness

Two people can agree and both be wrong. A smudged digit on a handwritten form can be read the same wrong way by two
careful readers, and adjudication never sees it, because there was no disagreement to adjudicate.

On the engagement you cannot measure this directly. In this chapter you can, because the synthetic generator knows
what is really on the paper. The agreement report's last line:

```text
  field labels where both agreed, or the adjudicators read it, and the paper says otherwise: 3 of 1800 (visible only because the data is synthetic)
```

Three cells in 1,800, about 0.2 percent. Small, and not zero: the golden set is a very good answer key, not a
perfect one. Two defences work on real data:

- **The double-keyed audit** Day 9 registered: re-key a sample of golden-set files from scratch, by someone who did
  not label them, and compare. It estimates the shared-error rate.
- **Investigate every confidently-wrong field starting with the label.** When the model and the label disagree and
  the model was confident, look at the page before blaming the model. Section 11 finds that one of the baseline
  run's seven confidently-wrong fields is GF-42025's requested amount, where both labellers typed 70060 and the
  paper says 70000. The model was right. The label goes back to the team leads, and the truth file gets a new version.

## 3.9 The analysts' own error rate

Day 9 registered one more number: "the analysts' own keying error rate", the same accuracy definition applied to
the people, the fair comparison for the compliance head. From the same run:

```text
  each eval owner against the adjudicated truth (Day 9's 'analysts' own keying error rate'):
    Lakshmi              99.28% of 1800 field cells  (95% 98.77% to 99.58%); 42 minutes a file on average
    the senior analyst   98.50% of 1800 field cells  (95% 97.83% to 98.97%); 48 minutes a file on average
```

It is biased upward: each labeller is measured against a truth file she helped create, so shared mistakes score as
correct, and the conditions (no queue, the guide open beside her) are kinder than a Tuesday afternoon. Read it as a
ceiling. A system at 97.5 percent is one to two points below two of Godavari's best analysts working slowly, which is
the right frame for the conversation; Day 9's double-keyed sample under production conditions is the honest baseline.

## 3.10 Key takeaways

- The customer's experts label, two of them, independently; the sceptic is one of them on purpose.
- Write the labelling guide with them before labelling; the first thirty files find most of its gaps.
- A label records fields, documents, the decision with reasons, the trajectory and the time.
- Trajectories show where the evidence is, benchmark the workflow, price the human time and surface unwritten steps.
- Raw agreement for values, Cohen's kappa for decisions; always with the counts. Normalise format before you measure.
- Adjudicate by a written rule, with named customer people, logged; adjudication turns opinions into rules.
- Agreement is not correctness; audit, and check the label first when the model is confidently "wrong".
