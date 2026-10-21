# 05 · Numbers You Can Defend: Intervals, Strata, Paired Comparisons and the Average That Hides a Branch

> Day 14 · Section 5 of 16 · [Chapter overview](README.md) · Previous: [04 · What to measure](04-what-to-measure.md) · Next: [06 · Deterministic checks and LLM judges](06-checks-and-judges.md)

---

This section has the only statistics in the chapter. There are four ideas, each with its code in
`code/evals/stats.py` (under a hundred lines, standard library only), and each answers a question somebody at Godavari
will ask you out loud. If statistics makes you nervous, read the plain-words box at the top of each part and the
example under it; that is enough to use the harness correctly.

## 5.1 Every number has a count and an interval

> **In plain words.** If you measured on a different 150 files from the same month, you would get a slightly
> different number. The interval is the range the number would usually land in. Narrow means "trust the digits";
> wide means "trust the direction".

The harness never prints a share without its count and a 95 percent interval. The reason is visible in one table
from the baseline run:

```text
stratum                            files fields  accuracy     95% interval   cw  flagged  compl. recall
branch=Dilsukhnagar                   20    240    98.3%   95.8% to  99.4%    0     18%           100%
branch=Guntur                         35    420    96.9%   94.8% to  98.2%    5     20%           100%
branch=Kukatpally                     35    420    98.6%   96.9% to  99.3%    0     24%           100%
```

Dilsukhnagar looks better than Guntur, 98.3 against 96.9. But Dilsukhnagar's interval runs from 95.8 to 99.4 and
Guntur's from 94.8 to 98.2; they overlap a lot. "Dilsukhnagar files are read better" is not a claim these 20 files
can support. "Guntur has five of the seven confidently-wrong fields" is a different and more useful observation
(section 5.4), because it points at specific files you can open.

## 5.2 The Wilson interval, and why not the one from school

> **In plain words.** The usual school formula, "p plus or minus 1.96 times the square root of p(1-p)/n", breaks
> near 0 and 100 percent, which is exactly where eval numbers live. The Wilson interval does not.

Take completeness recall: 76 incomplete files, all 76 flagged. The school formula gives 100 percent plus or minus
zero, which claims certainty from 76 files. The Wilson interval (`wilson(76, 76)`) gives about 95.2 to 100 percent,
which says what is true: no misses seen, and a miss rate up to about 5 percent cannot be ruled out yet. The same
applies to the confidently-wrong rate, 7 in 1,800 cells: Wilson gives 0.19 to 0.80 percent, an interval that is
lopsided because the rate cannot go below zero.

```python
def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """95 percent Wilson score interval for k successes in n trials. (0, 1) when n is 0."""
    if n == 0:
        return 0.0, 1.0
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return max(0.0, centre - half), min(1.0, centre + half)
```

A test pins it to a textbook value (81 of 100 gives 72.2 to 87.5 percent) and to the edges (0 of 20, 20 of 20).

## 5.3 Twelve fields from one file are not twelve independent coin flips

> **In plain words.** A blurred phone photo is bad for every field on it. Counting its twelve fields as twelve
> separate chances overstates how much evidence you have. Resample whole files instead.

The Wilson interval on 1,800 field cells assumes each cell is independent. They are not: fields from the same file
share a scanner, a branch, a handwriting and a page order. The honest interval comes from a **cluster bootstrap**:
pretend the 150 files are the population, draw 150 files from them with replacement 2,000 times, compute accuracy
each time, and take the middle 95 percent of those values (`cluster_bootstrap` in `stats.py`, seeded so the report
is reproducible).

On this run the two agree closely:

```text
  field-level accuracy (normalised)    97.5%   95% 96.7% to 98.1% (fields), 96.7% to 98.2% (files resampled)
```

That is because the stub's errors are spread fairly evenly across files. On real files they will not be: one
branch's scanner or one analyst's handwriting can concentrate errors, and the file-level interval will be visibly
wider. Report the file-level interval for the headline and in the week-6 pack; the field-level Wilson interval is
fine for per-field and per-stratum rows, where you also show the count.

## 5.4 Slicing by stratum so an average cannot hide a branch

> **In plain words.** Report every number for every slice that varies or that a decision depends on. The average is
> a summary of the slices, not a substitute for them.

The headline is 97.5 percent. The slices tell a different story, and every line below is from the real run:

| Slice | What the average hid |
|---|---|
| `field=on_road_price`: 92.0 percent, 6 of the 7 confidently-wrong fields | one field carries almost all the risk; it has no second source to cross-check against (section 11.4) |
| `branch=Guntur`: 5 of the 7 confidently-wrong fields | a pilot branch, live in a week; its files need to be opened with the Guntur branch manager before go-live |
| `handwritten_telugu=yes`: 96.0 percent, 46 percent flagged | Day 10's risk R1: accurate enough, but almost half the fields go to review, so the hours saved there are small |
| `field=applicant_name`: 94.7 percent, 65 percent flagged | most name fields are flagged by Day 11's placeholder threshold; Day 18 must set it from data or analysts will learn to ignore the highlight |

None of those four facts is visible in "97.5 percent". Each one is a decision for a named person this week. That
is what slicing is for.

There is a second, quieter reason. If the set's mix and production's mix differ (and by design they do, section
02.3), the overall average can move even when no slice changed. The candidate that adds a Telugu-heavy batch to the
set looks worse; the one tested on more SFTP scans looks better. Comparing slice by slice is immune to that.

## 5.5 From the golden set to a production estimate

The golden set over-samples hard cases, so its average is pessimistic. To estimate production, weight each
stratum's accuracy by its share in production rather than its share in the set. With channel as the stratum,
using Day 7's two-week sample as the production mix (sftp 57.5 percent, mixed 27 percent, phone 15.5 percent):

| Channel | Golden-set accuracy | Share in the set | Share in production (Day 7 sample) |
|---|---|---|---|
| sftp_scan | 97.7% | 46% | 57.5% |
| mixed | 97.7% | 22% | 27.0% |
| phone_photo | 97.0% | 32% | 15.5% |

Reweighted: 0.575 x 97.7 + 0.270 x 97.7 + 0.155 x 97.0 = about 97.6 percent, a tenth of a point above the set's
97.5. Small here, because the stub's errors barely depend on the channel; on real files the gap between clean scans
and phone photos is usually much larger, and so is the correction. Two rules when you do this: say it is an
estimate with the weights shown, and never use it in place of the per-stratum numbers.

## 5.6 Is the new run better? Compare on the same files

> **In plain words.** When you change a prompt and rerun, most fields come out the same. Only the fields that
> changed carry information. Count how many went right-to-wrong and how many went wrong-to-right, and ask whether a
> fair coin could have produced that split.

Two runs on the same 150 files are **paired**: each field cell in one run has a twin in the other. Comparing the
two accuracies as if they came from different samples throws that away and gives intervals so wide that nothing is
ever significant. The paired approach (McNemar's idea, computed exactly) looks only at the cells that changed:

```python
def paired_worse_p(regressions: int, fixes: int) -> float:
    """Of the fields that changed between two runs on the same files, `regressions` went right to wrong and
    `fixes` went wrong to right. If the change did nothing, each changed field is a fair coin. The value
    returned is the chance of seeing this many regressions or more from a coin."""
    return binom_tail_ge(regressions, regressions + fixes, 0.5)
```

Two real comparisons from the gate:

```text
rerun of the unchanged model, all fields:   5 right-to-wrong, 8 wrong-to-right of 1800 fields, p=0.8666
trimmed prompt, field=monthly_income:      10 right-to-wrong, 0 wrong-to-right of 100 fields,  p=0.0010
```

The rerun moved thirteen cells, in both directions, as noise does. The trimmed prompt moved ten cells in one
field, all the same way; a fair coin does that about once in a thousand tries. The first is nothing; the second is
a regression, and it is only 0.5 points of the overall average.

## 5.7 Many slices, many chances to be fooled

The gate checks 36 strata, two rules each. Every check is a small chance of a false alarm, and the chances add up.
This is the **multiple comparisons** problem, and you can measure it instead of arguing about it: rerun the
unchanged model many times and count how often the gate fails. `code/gate_false_alarms.py` does this, 30 reruns:

```text
looser: any net 3 regressions at p < 0.05, net new confident wrong > 1
  false alarms on unchanged reruns: 3 of 30 (most often: regressions:channel=phone_photo, regressions:channel=sftp_scan, confident wrong:all)
```

A gate that blocks one pull request in ten for no reason gets switched off by the second week. The stored policy
(section 07) is stricter per stratum and measured at 0 false alarms in 30 while still catching the trimmed prompt
every time. The general rule: the more slices you check, the stricter each check must be, and the only way to know
you have it right is to measure the gate's own error rate.

## 5.8 What 150 files can and cannot see

On 1,800 cells a paired, one-directional loss of about a point is visible; on a branch's 240 to 420 cells, a field
that breaks on several files; on one field's 100 cells, four or more net regressions; on 76 incomplete files, a rule
that misses several, not a miss rate of 1 to 2 percent. The answer to what 150 files cannot see is not a bigger set
(the experts' time is the constraint) but **production monitoring** of the same metrics (Day 19) and **adding the
failures production finds to the set** (section 08.5).

## 5.9 Key takeaways

- No share without its count and a 95 percent interval; Wilson near 0 and 100 percent, file-level bootstrap for the headline.
- Slice by every stratum that varies or decides something; the average is a summary, never a substitute.
- Reweight strata to estimate production, show the weights, and keep the slices.
- Compare runs on the same files, cell by cell; only the changed cells carry information.
- More slices need stricter checks; measure the gate's false-alarm rate rather than guessing it.
- What 150 files cannot see, production monitoring and a growing set must.
