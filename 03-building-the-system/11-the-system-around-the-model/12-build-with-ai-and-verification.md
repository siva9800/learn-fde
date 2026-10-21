# 12 · Build It With AI, and How You Know It's Right

> Day 11 · Section 12 of 16 · [Chapter overview](README.md) · Previous: [11 · Project: the split prototype](11-project-the-split-prototype.md) · Next: [13 · Mistakes and debugging](13-mistakes-and-debugging.md)

---

## 12.1 Build it with AI

An FDE in 2026 would write most of this chapter's code with a coding agent, and should. The validators, the
dataclasses, the routing, the fake sandbox and most of the tests are exactly what agents write well. The
danger is concentrated in two places: the agent's instinct to put rules where they are easiest to write (in
the prompt), and its instinct to make code that "handles errors gracefully" (by passing them). Both instincts
produce the failure this chapter exists to prevent.

**Context to give the agent.** The one-page architecture (section 08) and the sorted rules
(`worksheet/godavari-rules-sorted.md`), so it knows which side of the line each rule is on before it writes
anything. The `catalogue.py` dataclasses as the contract. The signed address-proof list as data. Day 6's
findings A7 and A8 verbatim ("I sign it, and if it changes, I sign the change"; "I would rather it says
'cannot tell'"). The conventions: Python 3.12 or newer, type hints, standard library only for the package,
pytest for tests, no network. And the instruction that the model's verdict must never route a file.

**A strong prompt (for one rules module):**

> You are writing `rules_gold.py` for a lender's loan-intake system. The rules are deterministic Python that
> a compliance head signs; no model is called anywhere in this file. Use the `Rule`, `Finding`, `Kind`,
> `Action` and `RuleContext` types from `ruleset.py` (attached) and the field names from `catalogue.py`
> (attached). Implement: the nine required documents (list attached, with which are regulatory); the LTV rule
> with tiers 85 percent up to Rs 2,50,000, 80 percent above that up to Rs 5,00,000, 75 percent above; the
> collateral value from NET weight times the published 22-carat rate on the appraisal date times purity over
> 22, in Decimal, truncated to whole rupees; purity 18 to 24 carat; tenure at most 12 months.
> Requirements: (1) any unreadable or missing input produces a REVIEW finding, never a pass and never an
> exception; (2) money comparisons in integer rupees, no floats; (3) a missing gold rate for the date is a
> REVIEW, never interpolated; (4) every rule has an id, a kind, a one-sentence text the compliance head can
> read, and a source. Then write pytest tests for every boundary: the tier edges, exactly at the cap and one
> rupee over, net weight above gross, a date with no published rate, unreadable purity. Do not use try/except
> to hide errors. Do not read the model's `prompt_only` verdict.

**A second prompt (the reviewer):**

> Review this pipeline as a sceptical compliance engineer. For every rule the customer has (list attached),
> tell me where it is enforced: in code, in a prompt, or nowhere. Find any path where a model's output, verdict
> or confidence can change a route without passing a deterministic check. Find any check that passes when its
> input is None, missing or unparseable. Find any arithmetic done in floats. Cite file and line for each.

**What the agent typically gets right:** the dataclasses and type hints; the PAN regular expression and the
Verhoeff algorithm (it knows them); parametrised pytest tests; the fake sandbox; the report formatting; the
JSON schema for structured outputs; the overall module layout once it is shown the architecture.

**What it typically gets wrong for this concept (check each):**

| Mistake | How it shows | Fix |
|---|---|---|
| **puts the rules in the prompt** | asked for "a completeness checker using the model", it writes a prompt containing the checklist and parses `complete: true` | say in the first line that no model is called in the rules module; review with `grep -n "prompt\|messages\|client" rules_*.py` |
| **lets the model's verdict short-circuit the rules** | `if output.prompt_only.complete: return []` "for efficiency" | the verdict is recorded, never read for routing; a test asserts it |
| **fails open** | `if amount and price and ...`; `except Exception: return []`; `.get("kind", "")` treated as acceptable | demand REVIEW on unreadable input in the prompt; write the None and garbage tests first |
| **floats for money and weights** | `float(net) * rate * 0.85`; `round(amount / price * 100) > 90` hides 90.4 percent | integers and Decimal; a test at one rupee over every cap |
| **the wrong weight, cap or purity base** | gross weight; a uniform 75 percent cap from older guidance; purity over 24 with a 22-carat rate | state the formula in the prompt; test net against gross explicitly |
| **unanchored or loose patterns** | `re.match` without an end anchor accepts an 11-character PAN; `\d{12}` misses "1234 5678 9012" | `fullmatch`; tests for spaced and unspaced numbers; Verhoeff for Aadhaar |
| **dates parsed the American way** | `"%m-%d-%Y"` for Godavari's dd-mm-yyyy; age as `days / 365` | strict format; age by calendar comparison; a test on the 21st birthday |
| **scans only the pages the model labelled** | the Aadhaar check looks at the identity-proof page, so a photocopy's reverse side is never scanned | deterministic scans run on every page, independent of the model |
| **invents reference data** | a hard-coded `GOLD_RATE = 11400`; a dealer list it made up | reference data is a lookup by date with a "none" path; the values come from the customer |
| **copies Day 7's generator into this chapter** | a second `make_loan_files` that drifts from Day 7's | import by path; a test that compares with Day 7's CSV |
| **agrees with you** | asked to review, it praises the design | give it the reviewer prompt above with the rules list as the rubric |

The first three rows are the ones to watch most, because they read as good engineering. "Use the model's
judgement to skip redundant checks", "handle errors gracefully" and "keep it simple" are all phrases an agent
will use to justify exactly the design the compliance head refused. Exercise 3.1 is an agent's draft with nine
of these problems in 60 lines.

## 12.2 How do you know it's right?

Whether you or an agent wrote it, the checks are the same.

1. **Every rule in the customer's list is enforced in code, and you can point to the line.** Walk the sorted
   rules worksheet row by row and write the rule id beside each. A rule with no id is enforced nowhere.
2. **No model output can change a route without passing a check.** Search for every read of `prompt_only`,
   `confidence` and model output in `pipeline.py` and `routing.py`; each must feed a check, not a decision.
3. **Every check fails closed.** For each rule, there is a test with the input missing (`None`), unparseable
   ("12.5 lakh", "O2-11-2026") and at the boundary. Run them; read the action: REVIEW, never a pass.
4. **Boundaries are tested on both sides.** 60 and 61 days; exactly at the cap and one rupee over; the 21st
   birthday and the day before. A single test in the middle of the range proves almost nothing.
5. **The rules are deterministic in fact.** Run the batch twice and compare the CSVs byte for byte; no rule
   reads the clock (rules take `as_of` and the file's dates), the network or a random source.
6. **The fingerprint guards what was signed.** Change one character in a rules file and confirm both modes
   refuse; change only line endings and confirm nothing changes.
7. **Grounding is total.** Count the model's document claims that fail grounding and the ENV-GROUND findings;
   they must be equal (the end-to-end test does this).
8. **The model-alone comparison is fair.** It is the same model on the same files, asked to judge in its
   prompt. If you "help" the baseline less or more than the system, the 61 against 2 means nothing.
9. **The residuals are listed, not hidden.** A run that reports zero misses on synthetic data you generated
   should make you suspicious of the generator, not proud of the system.
10. **The rule sheet matches the code.** Regenerate it and diff it against the one the compliance head has; if
    they differ, she has not reviewed what runs.

**Review checklist:**

- [ ] every customer rule mapped to a rule id, a kind (regulatory or policy) and a source
- [ ] no model call, prompt or model verdict inside any rules module
- [ ] every rule fails closed on missing, unparseable and boundary inputs, with tests on both sides of every boundary
- [ ] money and weights in integers or Decimal; dates parsed with an explicit format; age by calendar
- [ ] deterministic scans (Aadhaar mask) run on every page, not only model-labelled pages
- [ ] grounding before rules; rules see only grounded documents
- [ ] confidence thresholds visibly marked as placeholders until Day 14 sets them
- [ ] regulatory rules have no override path; policy overrides need a named analyst and a written reason
- [ ] the fingerprint and sign-off record checked before any file is processed; pilot mode refuses unsigned rules
- [ ] the integration refuses to write without approval and never duplicates on retry
- [ ] the run is reproducible, reuses Day 7's generator by path, and lists its misses
- [ ] the real-model adapter refuses non-synthetic data and is not needed to run anything
