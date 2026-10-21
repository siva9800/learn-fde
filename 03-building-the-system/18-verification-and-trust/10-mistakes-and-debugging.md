# 10 · Common Mistakes and Debugging

> Day 18 · Section 10 of 13 · [Chapter overview](README.md) · Previous: [09 · Build it with AI, and how you know it's right](09-build-with-ai-and-verification.md) · Next: [11 · Interview questions](11-interview-questions.md)

---

Each row is **symptom, cause, fix**, with the section that explains it.

## 10.1 On the floor

| Symptom | Likely cause | Fix |
|---|---|---|
| Analysts say "it highlights everything" and stop reading highlights | thresholds set by hand, or a stratum where nearly every highlight is right (handwritten Telugu: 96 percent) | fit per cell from data; tell the eval owners what the handwritten condition costs; rely on the forced look and dwell there (03.4, 04.2) |
| The senior analyst finds a wrong auto-accepted value in week one | the cell was never confirmed on test, or a new branch's documents differ from the golden set | withdraw the cell in the bands file today (no deployment); add the file to development; check that branch's stratum (07.3) |
| A wrong on-road price reaches the core system although the file was "in review" | the flag was on another field (the margin rule names the requested amount) | link a rule's finding to every field it reads; the price is on the standing forced-look list (02.3, 08.7) |
| Approvals arrive in bursts at 18:00 on month-end days | workload, not character: the queue doubled | the detector's burst signal to the team lead as a workload alert; targeted second reads; move files, not blame (04.4) |
| Analysts keep the Excel tracker open beside the queue (Day 10, risk R4) | the queue does not show what the file is waiting for | the reason on every row; the CSV export; the tracker's columns in the queue (05.2) |
| The branch manager disputes a send-back | the note cites a rule but not Godavari's clause, or a superseded one | cite by number from the register, in force on the day; refuse stale citations (02.4, 06.3) |
| The auditor asks who checked a field and nobody can say | corrections stored as the new value only | the correction record and the decision record (06.1, 06.4) |

## 10.2 In the numbers

| Symptom | Likely cause | Fix |
|---|---|---|
| Every cell's threshold is 0.70 | zero-error rule on a small development split, no floor | never below the lowest development confidence shown correct (03.2) |
| The band report looks perfect: 0 wrong auto-accepted | it is the "after withdrawal" number, computed on the split used to withdraw | quote the "before" number and the spot-check bound; label the "after" one optimistic (03.3) |
| The pooled bound passes and the field that matters fails | the confirmation was pooled | per-cell, zero-tolerance confirmation (03.3) |
| A withdrawn cell's examples look like the model was right | the label is wrong (GF-42025's 70060) | re-adjudicate first; new truth-file version; then refit (03.3; Day 14, 03.8) |
| The spot-check error rate is zero for a month and everyone relaxes | 47 fields a week cannot see a 1 percent rate | report the upper bound, not the point estimate; 299 fields to see one error (04.3) |
| The detector flags the best analyst | speed alone was used | require two signals (04.4) |
| The minutes per file do not match the team leads' stopwatch | seconds per field are assumptions | replace them with the pilot timer's medians (03.4, 08.7) |

## 10.3 In the code

| Symptom | Likely cause | Fix |
|---|---|---|
| A name shows as bold text or breaks the page | autoescape off: `select_autoescape` with `.html.j2`, or a `safe` filter | `autoescape=True` explicitly; the hostile-value test (05.6) |
| The page is blank in one cell, no error | a misspelt template variable rendered as empty | `StrictUndefined` (render.py) |
| The crop's lines run together on one line | Jinja2's `trim_blocks` ate the newline after a block tag inside `<pre>` | emit the newline explicitly; check a rendered page, not only the tests |
| The auditor's re-draw of the sample does not match | `hash()` or an unseeded `random` was used | keyed SHA-256 of the file number (04.3) |
| `__pycache__` appears in Day 11's folder | this chapter imported Day 11 without `sys.dont_write_bytecode` | set it in `paths.py` before any import from other chapters |
| `SignoffError` on Monday morning | pilot mode, and the rules on disk are not the signed ones | do not switch to prototype mode; find out what changed since M10 (Day 11's fingerprint) |

## 10.4 A routine for "the analysts do not trust it"

Ask which field on which kind of page; pull that cell from the band report and its corrections from the log; open
three of those files with the analyst and read the source line together; decide with the eval owners whether to
withdraw the cell, fix the envelope (Day 11's owner) or show the evidence better; tell the analyst what changed. Trust
comes back one field at a time, the same way it was lost.
