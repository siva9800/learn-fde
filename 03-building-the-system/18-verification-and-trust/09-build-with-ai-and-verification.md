# 09 · Build It With AI, and How You Know It's Right

> Day 18 · Section 9 of 13 · [Chapter overview](README.md) · Previous: [08 · Project: the review-queue model](08-project-the-review-queue-model.md) · Next: [10 · Mistakes and debugging](10-mistakes-and-debugging.md)

---

## 9.1 Build it with AI: the context to give

A coding agent can write most of this chapter's code in an afternoon. What it cannot know is the customer. Give it:

- **The packages it must import and must not copy**: Day 11's `intake` (pipeline, `MANDATORY_FIELDS`,
  `check_signoff`), Day 14's `evals` (`golden.select`, `normalise.norm_equal`, `stats.wilson`, the truth file), Day
  15's `godavari_retrieval.corpus`. Paste their function signatures, not their bodies.
- **The decisions that are not the agent's to make**: D07 (a named analyst decides every file), the compliance head's
  sign-off and pilot mode, the branch-visibility rule, the senior analyst's condition on handwritten fields, the
  1.5 percent bar and where it comes from.
- **The data discipline**: fit on development only, confirm on test, a failed confirmation only removes automation.
- **The page constraints**: static, self-contained, escaped, no script, English and Telugu labels, bands in words.
- **The environment**: Python 3.14, the pinned `requirements.txt`, tests in a virtual environment, no network.

## 9.2 A strong prompt

> Build a Python package `godavari_review` for Godavari Finance's loan-file review screen. Import, never copy, these
> packages by path: [signatures]. (1) A tuner: for each mandatory field and each source-page stratum (printed,
> handwritten Telugu), fit an auto-accept threshold on the development split only, as the lowest threshold with at
> least 15 development fields above it that have no deterministic finding and are all correct, never below the
> lowest such confidence; confirm on the test split, withdrawing any cell with a wrong auto-accepted value (never
> moving a threshold); block handwritten Telugu cells until their own test fields bound the error at or below 1.5
> percent. Report seconds per file and wrong values per band under three policies. (2) A renderer: Jinja2 with
> `autoescape=True` set explicitly and `StrictUndefined`; one static page per file with the source line beside every
> field, the band in words in English and Telugu (`lang="te"`), the rule, its sign-off status and the clause from the
> register, exactly one forced-look field first, and no script or external resource. Refuse to render in pilot mode
> if the rules are unsigned. No bulk approve. (3) A sampler: a keyed SHA-256 draw, 10 percent per branch with a floor
> of 3, plus targeted files. (4) A rubber-stamping detector that reads only the screen's log. Write pytest tests for
> each rule above, including a hostile value in a field. Do not auto-approve anything.

## 9.3 What the agent gets right

The Jinja2 boilerplate, dataclasses, CSV, grid search, SHA-256 draw, Poisson tail and test scaffolding, fast.

## 9.4 The mistakes it makes on this concept

| Mistake | Why it is wrong here | How you catch it |
|---|---|---|
| tunes thresholds on all 200 labelled files, or on the test split | the number it reports is then a training score | `fit()` refuses non-development rows; a test proves it |
| one global threshold, "0.85 for everything" | the on-road price and a handwritten name are different problems | the band report has one row per cell |
| chooses the threshold by pooled accuracy | the pooled bound passed while six on-road prices were wrong | the per-cell, zero-tolerance confirmation test |
| lowest zero-error threshold with no floor | auto-accepts confidences development never saw correct (0.70 on a field whose lowest correct value was 0.87) | the no-extrapolation test |
| f-string HTML, or Jinja2's `safe` filter on a value, or `select_autoescape(["html"])` with `page.html.j2` | a customer name becomes markup | the hostile-value test and the `.j2` trap test |
| Bootstrap and a web font from a CDN, an `htmx` script | the page reaches the internet from inside the Hyderabad building | the "loads nothing" test and the CSP |
| "auto_approved" route for all-green files | contradicts D07 and the auditor's condition | code review against the decision list; grep for "approve" |
| the band shown as a background colour only | fails WCAG 1.4.1 and colour-blind analysts | bands in words in both languages |
| citation by "most similar circular" | will cite a superseded circular sooner or later | citations by number from a reviewed table; the stale-citation test |
| a correction overwrites the value with no reason or original | the example is lost and the auditor sees no trail | the correction record requires both values and a reason |
| `hash(file_id) % 10 == 0` for the sample | Python randomises string hashes per process, so the auditor cannot reproduce the draw | keyed SHA-256; the reproducibility test |
| shows the analyst which files will be spot-checked | people are careful on exactly those | draw after approval; the key is not in the analysts' tool |
| the detector ranks analysts by seconds per file and mails HR | speed alone is not a flag; it will be gamed and the analysts lost | two signals required; governance agreed first (section 04.5) |
| second reads assigned to "any available eval owner" | breaks the branch-visibility rule | second reader chosen by branch |
| copies Day 11's thresholds or rules into this package | two versions of the truth | imports only; nothing written into other chapters' folders |

## 9.5 How do you know it's right?

Whoever wrote the code, check these before you show a screen to an analyst:

1. **Reproduce the baseline first.** The placeholder thresholds must give Day 14's seven confidently wrong fields. If
   not, you are measuring a different system.
2. **Read the band report cell by cell**, not the summary. Every withdrawn cell needs its examples read with the eval
   owners, and the label checked first (two of this chapter's four withdrawals rest on suspect labels).
3. **Try to break the page**: put `<script>`, a quote character and Telugu text in a value, the evidence and the
   note; open the page with the network disconnected; tab through it without a mouse; view it in greyscale.
4. **Check one page against the paper.** For three files, compare every value, quote and line number with the
   synthetic page text. A crop that points at the wrong line is worse than no crop.
5. **Check the citations against the register**, by hand, for every rule that fired in the week: right document,
   right clause, in force on the decision date.
6. **Check the forced look on a clean file.** It must exist, and it must be the field the eval owners would pick.
7. **Plant one stamping session** in a clean log and confirm the detector flags exactly that one.
8. **Show the screen to the sceptic** before the pilot, with a file the system got wrong. If she cannot find the
   error in ten seconds, the design is not done.

**Review checklist**

- [ ] Thresholds come from development only; the test split only confirms, and only removes automation.
- [ ] Every cell is per field and per stratum; handwritten Telugu cells are blocked until proved.
- [ ] Deterministic findings always mean review; "unsure" always means key in.
- [ ] Every field shows its source line or an explicit "source not found"; confidence is labelled as one signal.
- [ ] Every rule shows its id, kind, sign-off status and a clause in force, quoted from the register.
- [ ] Exactly one forced-look field per file, first on the page; approve disabled until it is done.
- [ ] Autoescape set explicitly; no `safe` filter on any value; no script, external stylesheet, font or image; a CSP.
- [ ] Bands in words in English and Telugu; `lang="te"`; keyboard order is the work order.
- [ ] No bulk approve, confirm, override or send back.
- [ ] Spot checks drawn by a keyed hash after approval, blind, within the branch rule, adjudicated.
- [ ] The detector reads only the log, needs two signals, and its use is agreed with the analysts.
- [ ] Every correction has both values and a reason, and goes to development as a single-labeller candidate.
- [ ] Pilot mode refuses unsigned rules; the banner shows the rules' status on every page.
