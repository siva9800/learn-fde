# 04 · Designing Against Rubber-Stamping: The Forced Look, Spot Checks, and the Signals That Someone Stopped Looking

> Day 18 · Section 4 of 13 · [Chapter overview](README.md) · Previous: [03 · Confidence routing](03-confidence-routing-from-the-golden-set.md) · Next: [05 · The review queue screen](05-the-review-queue-screen.md)

---

## 4.1 Automation bias, in plain words

When a machine is usually right, people stop checking it: a sensible response that makes the rare wrong answer
dangerous. The research name is **automation bias**. A systematic review of 74 studies in clinical decision support (Goddard, Roudsari and Wyatt,
JAMIA 2012) lists what makes it worse and what reduces it:

| Makes it worse | Reduces it |
|---|---|
| workload, task complexity and time pressure | stressing the user's accountability for the decision |
| high trust and confidence in the system | where the advice is placed on the screen |
| | offering information rather than a direct recommendation |
| | training |

Read that table with the senior analyst's sentence beside it: "on a month-end day I will check nothing". Workload
and time pressure are Godavari's March. The design levers below come straight from the right-hand column.

## 4.2 Five design levers

**1. Offer information, not a verdict.** The accepted band says "Accepted: no action needed", not a green tick that
reads as "correct". Every accepted field still shows its source line. The reject band offers no value at all: a
wrong guess on screen anchors the reader, so the analyst keys from the page.

**2. Make highlights mean something.** If most highlighted fields are fine, people learn to ignore highlights. Day
14 found Day 11's placeholder flagging 65 percent of applicant names; the bands cut printed-page highlights to fields
where one in twelve is wrong (section 03.4). Handwritten Telugu remains the weak spot, by the eval owners' choice.

**3. Force one look per file, at the riskiest field.** Every file, even a clean one, has exactly one "Look at this
first" field, placed first on the screen, and the approve button stays disabled until it has been opened. The
choice is deterministic (`choose_forced()` in `queue.py`):

```python
standing_hits = [v for v in lookable if v.row.cell in standing]   # cells whose confirmation failed
pool = standing_hits or lookable
return max(pool, key=lambda v: (v.impact * v.risk, v.band == Band.REVIEW, v.row.field))
```

`impact` is agreed with the eval owners (3 for a value that feeds an eligibility rule or the core-system record of
money or identity); `risk` is the upper bound on that cell's error rate from **development** data only. Cells whose
test confirmation failed form a standing list, and their field wins. This week that means the on-road price on all
60 pilot files.

That is a trade-off to say out loud. The same field on every file becomes routine, and routine is what automation
bias feeds on. The standing list is meant to be temporary: when Day 11's owner ships the "letter among the digits"
check and the Day 14 gate re-measures, the on-road price leaves the list and the forced look moves to whichever field
is riskiest on each file.

**4. Put her name on it.** The decision record (section 06) carries the analyst's ID, the time, and the seconds she
spent on the forced field. Accountability is one of the review's mitigators, and it is also simply what the auditor
asks for (Day 6, finding A6).

**5. Check the accepted fields behind her.** Random spot checks, below.

## 4.3 Spot checks of auto-accepted fields

The golden set can bound the auto-accept band only so far; production must keep measuring it. The sampler draws,
**after approval**, about 10 percent of approved files with auto-accepted fields per branch, at least three per
branch a week, plus every file from a session the detector suspected:

```python
def draw_key(key: str, file_id: str) -> float:
    """A number in [0, 1) from the key and the file number: same inputs, same draw, on any machine."""
    return int(hashlib.sha256(f"{key}|{file_id}".encode()).hexdigest()[:12], 16) / 16 ** 12
```

Three properties matter more than the arithmetic:

- **Reproducible by the auditor, unpredictable to the analyst.** The key is held by the compliance head, not by the
  analysts' tool; anyone with the key and the file numbers can redo the draw. If analysts knew which files were
  checked, they would be careful on exactly those.
- **Blind.** The second reader sees the page, not the approved value, and keys the auto-accepted fields herself.
- **Within the branch rule.** Kukatpally files go to the senior analyst in Hyderabad and Guntur files to Lakshmi in
  Vijayawada, because an analyst sees a file only through her branch group (Day 6, finding A1; Day 11's
  `visible_to`). A disagreement goes to the two team leads (Day 14, adjudication rule 2) before anyone calls it an
  error.

How much checking is enough? To see at least one error with 95 percent probability when the true error rate is 1
percent, you need n = ln(0.05) / ln(0.99), which is **299 fields**. The pilot's first week checked 47 auto-accepted
fields at random, so the band's real error rate is bounded at 7.6 percent after week one and needs about six weeks of
checks to say something sharp. That is why the checks start on day one and why they never stop.

## 4.4 Measuring whether people are looking

The review screen logs, per field shown: the band, whether it was the forced field, the seconds on it, and the action
(accepted, confirmed, corrected, keyed, "not in the file"); and per file, the approval time. `stamping.py` reads only
that log, never the truth, and computes per analyst per half-day:

| Signal | Threshold (to be set from pilot week 1's timer) | Why |
|---|---|---|
| median seconds on fields to check | under 3 | nobody reads a crop and compares it in that time |
| median seconds on the look-first field | under 2 | the forced look became a click |
| approvals inside 20 minutes | 3 or more | the assessment between files was skipped as well |
| (weekly) corrections against the bands' expected wrong share | Poisson chance of this few under 0.05 | the analyst corrects far less than the files need |

A session is "suspected" only when the dwell is low **and** either the forced-look dwell or a burst agrees. Speed
alone is not a flag, because an expert can be fast. The pilot week's result (real output, simulated analysts):

```text
  H3      2026-12-11 PM       3         2.8         4.6         3  fast: no action (speed alone is not a flag): median 2.8 s on fields to check
  V2      2026-12-11 PM       3         1.2         1.6         3  suspected: second read of these files: median 1.2 s on fields to check; median 1.6 s on the look-first field; 3 or more approvals inside 20 minutes
  sessions: 48; suspected 1; fast-only 2
```

H3 is planted as fast and accurate; V2 is planted as rubber-stamping on Friday afternoon, after Thursday's batch
failed at six and reran at nine and two days of files landed at once (Day 6's BATCH_6PM). The detector separates them.
That shows the code does what it was designed to do on behaviour we planted; it does not show the thresholds are right
for Godavari's analysts, which only their real timings can.

Two honest results from the same run:

- **The override count is weak evidence in a week.** Every analyst, the rubber-stamper included, has a "chance of
  this few corrections" above 0.10, because the expected count is about two per week. Time-on-field catches it the
  same afternoon; override rates need weeks; spot checks give the ground truth.
- **The rubber-stamp cost nothing this time.** The targeted second read of V2's three Friday files found no wrong
  value: there happened to be none to miss. The one wrong value left in an approved file all week was in a careful
  analyst's normal session. That is why rubber-stamping survives in real teams: most of the time nothing goes wrong,
  and the day something does is the 2019 pilot.

## 4.5 Measuring people is a governance decision

The timing log is personal data about Godavari's employees. Before the pilot, agree in writing with Srinivas, the
Vijayawada team lead and the six analysts: what is measured, that it is about the system and the workload (queue
size, month-end, alert fatigue), who sees it (the team lead, as "these files need a second read" and "this afternoon
was overloaded"), who does not (HR), and how long it is kept. Treat it as personal data under the DPDP Act and agree
retention with the compliance head; Day 24 owns the law. A detector that becomes a performance ranking will be
gamed within a week (people will dwell on fields without reading them), and you will have lost both the signal and
the analysts.

Planting known errors ("canaries") is standard in crowd labelling. On a lender's live files it puts a wrong value
one click from the core system; use canaries only in a labelled training queue.

## 4.6 Key takeaways

- Automation bias grows with workload and time pressure; design with accountability, placement and information
  rather than verdicts.
- Exactly one forced look per file, at the riskiest field by impact times development risk; the standing list wins.
- Spot-check auto-accepted fields after approval: keyed hash, blind, within the branch rule, adjudicated.
- 299 fields to see a 1 percent error once; start on day one.
- Time-on-field catches rubber-stamping the same day; override counts need weeks; speed alone is not a flag.
- Agree what is measured with the people measured, before you measure it.
