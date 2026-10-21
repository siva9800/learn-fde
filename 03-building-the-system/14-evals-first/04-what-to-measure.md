# 04 · What to Measure: Fields, Documents, Completeness, and the Confidently Wrong Answer

> Day 14 · Section 4 of 16 · [Chapter overview](README.md) · Previous: [03 · Labelling with the customer's experts](03-labelling-with-the-experts.md) · Next: [05 · Numbers you can defend](05-numbers-you-can-defend.md)

---

## 4.1 Metrics that match the job

[Day 9](../../02-discovery-and-decomposition/09-success-metrics-and-business-case/README.md) built a metric ladder:
business outcomes at the top (turnaround, files decided with a document missing, withdrawals), operational metrics
in the middle (hours per file, queue age, send-back delay), and **system metrics** at the bottom, which are
"engineered; never the headline". The golden set measures the bottom rung. Each system metric is a lever on a rung
above it, and the eval report should say which.

| Metric | In plain words | Lever on | Who asks about it |
|---|---|---|---|
| **field-level accuracy** | of the mandatory fields, how many did the system get right | hours per file (analysts stop re-typing fields they trust) | the COO, through the business case |
| **confidently wrong rate** | of the fields, how many were wrong with nothing telling the analyst to look | files decided on a wrong value; the analysts' trust | the senior analyst, the compliance head |
| **flag rate** | of the fields, how many were sent to review | hours per file (every flag is a look) | the team leads |
| **page classification and document detection** | did it recognise each page and find each document | completeness, and every field read from those pages | the FDE (a diagnostic) |
| **completeness recall** | of the files truly missing a document, how many did the rules flag | files decided with a document missing | the compliance head |
| **completeness precision** | of the files the rules flagged, how many really were missing something | false send-backs, customers' lost days | the branch managers |
| **send-back recall and precision** | the same pair for the analysts' whole "would you send it back" decision | send-back delay | Srinivas and the Vijayawada team lead |
| **cost and latency per file** | rupees and seconds for one file through the system | the cloud line in the case; ready by 9 a.m. | the COO, Day 12's budgets |

Day 9's three registered system metrics (field-level accuracy, completeness recall, completeness precision) are
measured exactly as defined there. The others are added here because the report needs them to explain the first
three, and they are labelled "Day 14" in the eval plan so nobody mistakes them for pre-registered numbers.

## 4.2 Field-level accuracy, exact and normalised

Day 9's definition, quoted: "share of mandatory fields where the extracted value equals what the eval owners
(Lakshmi, the senior analyst) would have typed; handwritten Telugu fields reported separately", measured on "the
held-out part of the golden set".

Three words in it need code before they mean anything.

**"Mandatory fields".** All twelve per product that Day 11's envelope treats as mandatory (`MANDATORY_FIELDS` in
`intake/routing.py`, imported, not copied): for two-wheeler, name, date of birth, PAN, address, mobile, requested
amount, tenure, monthly income, application date, on-road price, dealer code and quotation date. Not the six the
model is best at. Day 9 listed "computed only on the fields the model is good at" as a known way to game the number.

**"Equals".** Exact string equality is too strict: "Rs 1,25,000" and "125000" are the same amount, and on this run
exact match reports 89.0 percent where the normalised comparison reports 97.5 percent, almost all of the gap being
capital letters in addresses and format in dates. Loose equality is worse: a matcher that accepts amounts "within 10
percent" or names that "start the same" will call a monthly income read as annual, or a transliteration variant,
correct. The answer is a **registered normaliser** (`code/evals/normalise.py`): one function per kind of field that
forgives format and never forgives content.

```python
def normalise(field_name: str, value: str | None) -> str | None:
    """The canonical form of a value for comparison, or None for "not in the file"."""
    ...
    if kind == "amount":     # "Rs 1,25,000" -> "125000"; never rounds, never converts
        digits = re.sub(r"(?i)^rs\.?\s*", "", text).replace(",", "").replace(" ", "")
        return digits.split(".")[0] if re.fullmatch(r"\d+(\.\d+)?", digits) else text
    if kind == "date":       # 15/03/1986 -> 15-03-1986
        ...
```

Its tests are written as two lists, and the second list is the important one:

| Forgiven (format) | Never forgiven (content) |
|---|---|
| "Rs 1,25,000" = "125000" | "125000" against "1250000" (the stray zero) |
| "15/03/1986" = "15-03-1986" | "RAAVI TEJA" against "RAVI TEJA" (the transliteration variant) |
| "Ravi Teja  Pasupuleti" = "RAVI TEJA PASUPULETI" | "ABCPP1234K" against "ABCPP1284K" (one OCR character) |
| "98765 43210" = "9876543210" | "32000" against "384000" (monthly read as annual) |
| "30" = "30.0" grams | an address without its city and PIN |

The normaliser is part of the metric. Changing it changes every accuracy number, so it changes with the same
signatures as the definition, and the report always shows exact accuracy beside normalised accuracy: if the gap
suddenly widens, the normaliser has started forgiving something new.

**"Would have typed", for things that are not there.** When the source document is missing (no PAN card), the
label is "not in file". A model that returns nothing is correct; a model that returns the form's PAN is wrong, even
though that PAN may be the right number, because the analyst would not have typed it (guide 4.2). And when the
model says "unsure" (Day 11's first-class "I do not know"), the field is not correct, because it is not what the
analyst would have typed, but it is honestly flagged, which leads to the most important distinction in the chapter.

## 4.3 The four outcomes, and the one that matters most

Accuracy alone mixes two very different kinds of wrong. A field can be wrong and flagged (the analyst is told to
look, and she fixes it) or wrong and unflagged (it looks fine and is not). The harness puts every field into one of
four outcomes:

```python
def field_status(name: str, pred: str | None, label: str | None, flagged: bool) -> str:
    """The four outcomes. 'confident_wrong' is the one that matters most: a wrong value nobody is told to check."""
    if norm_equal(name, pred, label):
        return "correct_flagged" if flagged else "correct"
    return "wrong_flagged" if flagged else "confident_wrong"
```

"Flagged" means any finding from Day 11's envelope or rules names that field: a confidence under its threshold, the
model saying unsure, the PAN card disagreeing with the form, a value not supported by its own quote, a rule that
could not be checked.

| Outcome | What the analyst experiences | What it costs |
|---|---|---|
| **correct** | a value she can accept at a glance | nothing; this is the saving |
| **correct, flagged** | a highlighted value she checks and finds right | a few seconds of review; too many and she stops trusting the highlights |
| **wrong, flagged** | a highlighted value she checks and corrects | the time to fix it; the system did its job by saying "look" |
| **confidently wrong** | a value that looks exactly like a correct one, and is not | whatever happens next: a wrong amount in the core system, a sanctioned file with a misread PAN, an audit finding |

The **confidently wrong rate** is the metric that matters most for Godavari, for three reasons written down weeks
before this chapter:

- **Review does not catch it.** Day 6's Bhavani, asked whether she would have noticed the 2019 pilot's income read
  twelve times too small: "I would not know." A busy analyst checks what she is told to check. The OCR pilot was
  switched off in six weeks for exactly this kind of error.
- **Trust is built on it.** The business case rests on capture share (Day 9, section 08.5): analysts stop re-typing a
  field only when they trust it. One confidently-wrong amount found by the senior analyst in pilot week one can
  undo a month of good numbers.
- **It is what decision D07 protects against.** An analyst approves every file in these 90 days precisely because the
  system can be confidently wrong. Measuring how often is how D07 is ever revisited.

The harness reports it three ways: as a rate with an interval, as **unflagged precision** (when the system does not
flag a field, how often is it right; this is what an analyst's trust actually rests on), and as a **list of every
case**, file by file. The baseline run:

```text
  field-level accuracy (normalised)    97.5%   95% 96.7% to 98.1% (fields), 96.7% to 98.2% (files resampled)
  field-level accuracy (exact string)  89.0%
  confidently wrong (wrong, not flagged)   7 = 0.39%   95% 0.19% to 0.80%
  when a field is NOT flagged, it is right 99.50% of the time
  fields flagged for review             21.8%
```

The list is the senior analyst's report, and Day 10's change C4 put it in the week-6 pack: "the actual files the
system got wrong, not only a percentage". Section 11 reads it.

## 4.4 Pages and documents

Two diagnostics sit under the field numbers, because most field errors start one step earlier.

**Page classification accuracy** is the share of pages whose type the model got right, against the printed title the
analyst read. On this run, 98.9 percent. Most misses are pages on long files left unclassified ("lost in the middle",
Day 13's page-40 problem) and phone photos.

**Document detection** compares the documents that survived Day 11's grounding check (a document claim stands only
if its quote is on the cited page) with the documents the analysts found: precision 100 percent (grounding throws out
every invented document before any rule sees it, which is its job) and recall 98.4 percent (a few real documents
were on pages the model could not classify).

When field accuracy drops on a stratum, look here first: a missed page is a whole document's fields gone at once.

## 4.5 Completeness: precision and recall in plain words

The completeness check is deterministic code (Day 11's signed rules), but it runs on what the model found, so it
must be measured too. Day 9's definitions:

- **Completeness recall:** "of files truly missing a mandatory document, the share the rules flag". A miss is a file
  that goes forward incomplete: the compliance head's risk. Her bar is no misses.
- **Completeness precision:** "of files the rules flag, the share truly missing something". A false flag sends a
  complete file back to the branch and costs the customer days: the branch managers' risk. The bar is "agreed with
  the branch managers after the first run".

The baseline run, against the compliance head's completeness labels:

```text
  completeness recall 100.0% (0 misses of 76 incomplete files) · precision 95.0% (4 false flags)
  missing-document recall 100.0% · precision 77.1%
```

The file-level pair is the one Day 9 registered. The document-level pair underneath explains the 4 false flags: when
some pages of a file cannot be classified, Day 11's rule does not guess. It says "not found; pages 7 and 19 could not
be classified, check them first" and routes the file to review rather than sending it back (Day 11, section 11.6).
That counts as a flag for the document, so document-level precision is lower (77.1 percent), but all four
false flags are of this "check these pages first" kind: they send the file to an analyst, not to the branch. (One
of the four files was sent back anyway, for a real reason: a utility bill 82 days old.) This is the right trade,
and the branch managers should be shown it in exactly these terms: 4 complete files of 74 went to an analyst
first, and no complete file went back to the branch because of a document the system failed to find.

Remember the interval from section 02.2: 0 misses in 76 incomplete files means the true miss rate is probably under
about 5 percent. That is why the compliance head's production target is a monthly measure on every file, not this
number.

## 4.6 The analysts' send-back decision

The analysts' label also says whether they would have sent the file back and why. The harness compares it with
whether any signed rule (regulatory or policy) raised a problem on the file:

```text
  send-back recall 100.0% · precision 91.1% (92 files the analysts would send back)
```

Recall is 100 percent: every file the analysts would send back has a rule finding. Precision is 91.1 percent: nine
files raise a rule finding that the analysts would not send back for. Three are the "check these pages first"
document findings above; two are the margin rule firing because the model misread the on-road price (section 11
follows one of them); two are the amount rules firing on a requested amount read ten times too large (Day 11's stray
zero on a handwritten form, which is exactly what those rules should catch); two are the age rule unable to read a
date of birth. All nine went to review,
not to the branch, so the cost is analyst time, not customer time. This pair is the closest thing in the report to "does
the system decide like Godavari's analysts", and it is the one the team leads read first.

## 4.7 Cost and latency per file

Record rupees and seconds per file in the same run, by stratum. With the stub the whole run takes about a tenth of a
second; on the real model, Day 12's measured Rs 6.34 (p50) to Rs 8.73 (p95) per file makes a full run about Rs 950 to
Rs 1,300 (section 10.3). If a candidate prompt is more accurate and twice as expensive on long Guntur files, that is a
trade the COO decides, and he can only decide it if the eval measured it.

## 4.8 What not to put in the headline

Accuracy on answered fields only (rewards guessing); average confidence (the model's opinion of itself); one number
across all files and fields (hides the stratum that failed); text-overlap scores such as ROUGE for the branch notes
(a note that drops one missing document can overlap 95 percent with a correct one); and "the model agreed with the
rules" (the rules run on the model's output, so agreement with itself is not evidence).

## 4.9 Key takeaways

- Measure the system rung of Day 9's ladder, and say which business number each metric moves.
- Field-level accuracy on all mandatory fields, with a registered normaliser that forgives format and never content;
  report exact beside normalised.
- Every field is correct, correct-flagged, wrong-flagged or confidently wrong; the last is the one that matters most,
  reported as a rate, as unflagged precision and as a file-by-file list.
- Pages and documents explain most field errors; look there first.
- Completeness recall is the compliance head's number, precision the branch managers'; show both, with counts.
- Record cost and latency in the same run, by stratum.
