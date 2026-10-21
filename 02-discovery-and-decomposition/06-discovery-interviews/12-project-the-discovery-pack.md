# 12 · Project: The Godavari Discovery Pack

> Day 6 · Section 12 of 16 · [Chapter overview](README.md) · Previous: [11 · 2026 patterns and production concerns](11-patterns-and-production-concerns.md) · Next: [13 · Mistakes and debugging](13-mistakes-and-debugging.md)

---

## 12.1 The brief

It is week 2 Friday at Godavari. Before the readout, the engagement folder needs the discovery pack: the evidence that Day 7's decomposition, Day 9's baseline and Day 14's golden set will all be built on. Five deliverables:

1. an **interview plan** built from the stakeholder map, with a persona and a reason per row;
2. **persona question banks** for operators, admins and sponsors, with the six architecture questions;
3. **shadowing logs** and **ten coded interview transcripts**;
4. the **situational map**: nineteen steps in Mermaid, with systems, permissions and the handoffs that break, reviewed with the operators;
5. a **findings synthesis** with the architecture-changing findings first, every finding citing its codes, checked by a script that tallies the codes and refuses any finding no interviewee gave.

The transcripts are synthetic, written for the course as realistic conversations with Godavari's people. On a real engagement they are your notes, filed where the CISO says.

The files are listed in the [chapter overview](README.md#files): the plan, the question bank, two shadowing logs, ten transcripts in [`worksheet/transcripts/`](worksheet/transcripts/) (Lakshmi, Srinivas, the COO, the CISO, the compliance head, the core-system owner, the Kukatpally and Guntur branch managers, the senior analyst and Bhavani), the [situational map](worksheet/situational-map.md), the [synthesis](worksheet/godavari-discovery-synthesis.md), an [AI-written draft](worksheet/ai-draft-findings.md) for exercise 3.1, and [`code/tally_findings.py`](code/tally_findings.py).

Run on **Python 3.14.3** (October 2026), standard library only, from the chapter folder:

```bash
python -X utf8 code/tally_findings.py worksheet/transcripts worksheet/godavari-discovery-synthesis.md
```

## 12.2 Parts A to D: plan, bank, shadow, transcripts

Do these in the order of sections 03 to 06, on your own customer or on Godavari as a paper exercise. Two rules make the script possible:

- every transcript has a title line `# Transcript NN · Who` and a header with `Persona: operator`, `admin` or `sponsor`;
- every transcript ends with `## Coded notes` and a table of code, verbatim evidence, kind.

Write the code list as you go. Godavari's settled at 45 codes across 112 coded mentions.

## 12.3 Part E: the map

Build it from the logs (section 07.4). Every row has a source column naming a transcript or log. Review it with the operators and record the corrections at the top.

## 12.4 Part F: the synthesis, checked by code

`tally_findings.py` does four things. It parses each transcript's coded-notes table and checks that codes are UPPER_SNAKE_CASE, kinds are one of six, and every code has evidence. It counts **independent interviews** per code (a code twice in one transcript counts once). It marks a code a **requirement** at three or more interviews and a **hypothesis** below. And it reads the synthesis for codes in square brackets and checks both directions: a cited code with no transcript is an **unsupported** finding, and a requirement not cited is a **missed** one. It exits 1 on any unsupported finding, so it can sit in a pre-readout check.

The run on the finished synthesis (0.35 seconds; the middle of the frequency table is cut here, and the full table is in `data/godavari-discovery-synthesis-tally.md`):

```text
== 10 transcripts read from worksheet\transcripts ==
  T01  Lakshmi, credit-ops analyst, Vijayawada            operator       14 codes
  T02  Srinivas, credit-ops team lead, Hyderabad          operator lead  13 codes
  T03  The COO, sponsor                                   sponsor         8 codes
  T04  The CISO, blocker and admin                        admin          10 codes
  T05  The compliance head, blocker and rule owner        admin          12 codes
  T06  The core-system owner                              admin          11 codes
  T07  The Kukatpally branch manager, upstream producer   operator       12 codes
  T08  The Guntur branch manager, upstream producer (far  operator       10 codes
  T09  The senior analyst, Hyderabad, the sceptic         operator       10 codes
  T10  Bhavani, junior analyst, Vijayawada                operator       12 codes

interviews by persona: admin 3, operator 5, operator lead 1, sponsor 1

== frequency table: 45 codes, 112 coded mentions ==
code                             ivws  status      kinds                            personas
BAD_DAY_MONTH_END                   7  requirement constraint                       admin, operator, operator lead
WHATSAPP_CHANNEL                    6  requirement architecture                     admin, operator, operator lead
BRANCH_ISOLATION                    5  requirement architecture                     admin, operator, operator lead
SHADOW_TRACKER                      5  requirement adoption, architecture           operator, operator lead, sponsor
WAIT_ON_BRANCH                      5  requirement evidence, metric                 operator, operator lead, sponsor
WILLING_TO_LABEL                    5  requirement scope                            admin, operator
ACCESS_VIA_AD_GROUPS                4  requirement architecture                     admin, operator, operator lead
...
DUPLICATE_ON_RETRY                  1  hypothesis  architecture                     admin
...

requirements (3+ interviews): 17; hypotheses (1 to 2): 28
architecture-changing requirements:
  - WHATSAPP_CHANNEL: 6 interviews (admin, operator, operator lead)
  - BRANCH_ISOLATION: 5 interviews (admin, operator, operator lead)
  - SHADOW_TRACKER: 5 interviews (operator, operator lead, sponsor)
  - ACCESS_VIA_AD_GROUPS: 4 interviews (admin, operator, operator lead)
  - FLAG_UNSURE_NOT_GUESS: 4 interviews (admin, operator)
  - ERROR_CORRECTION_BY_ANALYST: 3 interviews (operator)
  - FILE_ORIGIN_SCAN: 3 interviews (admin, operator)
  - NEVER_AUTOMATE_DECISION: 3 interviews (admin, operator, sponsor)

== synthesis check: godavari-discovery-synthesis.md cites 44 codes ==
every cited code is supported by at least one transcript
every requirement-level code is cited
single-source codes cited (keep them labelled as hypotheses): CHECKLIST_DRIFT, DUPLICATE_ON_RETRY, IDEMPOTENCY_LOOKUP_EXISTS, NOTES_STAY_ON_SITE, NO_TRAINING_ON_DATA, PAGE_ORDER_UNLABELLED, PHONE_PHOTO_INPUT, REVIEW_WILL_NOT_CATCH_ALL, RULES_AS_SIGNED_CODE, SANDBOX_STALE, SENDBACK_CAUTION, SSO_NOT_AVAILABLE, VIEW_LOG_REQUIRED

wrote data/godavari-discovery-synthesis-tally.csv and data/godavari-discovery-synthesis-tally.md
```

How to read it:

- **The branch-isolation finding is a requirement from three personas.** BRANCH_ISOLATION in five interviews, ACCESS_VIA_AD_GROUPS in four, across admins, operators and an operator lead. That is section 08's finding, counted.
- **The analyst-as-corrector finding comes from operators only,** which is why the review queue is designed with the analysts, not for them.
- **Thirteen single-source codes are cited, and the script says so.** Each one must be labelled single-source in the synthesis or backed by a test. A5's idempotency is backed by the week-two spike; A7's signing condition waits for the compliance head's first signature.
- **The first run was not clean.** On the first draft of the synthesis the check printed:

  ```text
  MISSED: requirement-level codes not cited in the synthesis:
    - WRONG_MEANS_AUDIT_FINDING (3 interviews)
  ```

  The COO, the compliance head and the senior analyst had each said, in their own words, that a wrong record means an audit observation. It became B4. That is what the second direction of the check is for.

## 12.5 Build it with AI

An FDE in 2026 uses an assistant in two places in this project: **preparing questions** and **synthesising notes**. Both are useful. One of them has a failure specific enough to design around.

**Context to give it.** The Day 5 stakeholder map (roles, each person's version in their words); the Day 4 problem statement; the six architecture questions; the never-ask list from `question-bank.md`; and the customer's data rules ("no customer names in anything you produce; file numbers only"). For synthesis, the coded transcripts themselves, never a summary of them, and only if the customer's rules allow transcripts to be sent to that assistant at all (Day 39 owns what may go in an agent's context; at Godavari, the CISO's rule means an assistant running inside the customer's environment or none).

**Prompt 1 (prepare the questions):**

> Here is a stakeholder map for a lender's loan-intake engagement and the six questions that change the architecture. For each persona (operators, admins, sponsors), draft an interview script of 10 to 13 questions. Rules: every question asks about a specific, recent instance or an artefact ("show me the last one", "what is in the sheet"), never a hypothetical ("would you use"); no question may contain a proposed solution or the words AI, model, automate or chatbot; each question has a "then" column saying what the answer would change in the design; the six architecture questions appear in every script in a form that fits that seat. After the scripts, list any of your questions that a strict reviewer would call leading, and rewrite them.

**Prompt 2 (synthesise, without inventing):**

> Here are ten interview transcripts, each ending in a coded-notes table. Group the codes into findings. Rules: a finding may only cite codes that appear in at least one transcript's coded-notes table, in square brackets; every finding states how many separate transcripts contain each of its codes; a finding with codes from fewer than three transcripts is labelled "hypothesis"; for each finding, quote one line of verbatim evidence and name the transcript; put findings that change who may see what, where data comes from, what may be written, or what must never be automated first. Then write a section titled "What was not found" listing things a reader might expect that no transcript contains. Do not add any system, number, request or preference that is not in a transcript.

Then run the script on what it returns. The prompt reduces the failure; the script is what catches it.

**What it gets right:** the structure of the scripts and the synthesis; open, artefact-based questions once told to; persona variation; grouping codes into themes; a first draft of section D; clean formatting. On ten transcripts it saves an evening.

**What it gets wrong for this concept:**

| Mistake | How it shows | Fix |
|---|---|---|
| **invents findings nobody said** | `ai-draft-findings.md`: "analysts would welcome a conversational assistant" [CHATBOT_WANTED]; "the core exposes a REST API" [REST_API_AVAILABLE]; "manual accuracy is approximately 92 percent" [MANUAL_ACCURACY_92]. The script flags seven such codes | every finding must cite codes from the transcripts; run the script; delete anything unsupported |
| **invents findings without codes** | a fluent sentence with no square brackets, so the script cannot see it: "analysts indicated they would be happy to stop using the tracker" | require a code on every finding; read every uncoded sentence against the transcripts by hand |
| **cites a real code for an unreal finding** | "the compliance head is open to the model determining document acceptability" cited as [RULES_AS_SIGNED_CODE], which says the opposite | for each finding, open the quote the code points to and check it says what the finding says. The script cannot do this |
| **misses the inconvenient** | the draft has no batch window, no "unsure" requirement, no human sanction, no audit observation; twelve requirement-level codes missed | the second direction of the check; section A must contain every architecture-kind requirement |
| **resolves conflicts the interviewees did not resolve** | "the COO is primarily focused on speed" turned into "auto-sanction low-risk files", when the COO said "a person signs the sanction" | conflicts go to the readout agenda, not into a finding |
| **turns a constraint into a solution** | "files arrive via WhatsApp and should be ingested through a WhatsApp Business integration" | the compliance head tolerates WhatsApp and wants it to stop; the finding is "make the proper route as fast", not "ingest it" |
| **launders the sponsor's version** | operators' quotes summarised in the sponsor's vocabulary ("data entry is the main bottleneck") | keep verbatim quotes; the operators said "waiting" five times |
| **leading questions in the scripts** | "Would it help if the fields were already typed?" | the never-ask list in the prompt, and a final pass asking it to flag its own leading questions |

The first row is the one to remember. An assistant asked to synthesise interviews writes findings that sound like discovery and are not: they come from what lenders usually have, what sponsors usually want and what vendors usually sell. They read as competence. A finding no interviewee said, presented at a readout, is the fastest way to lose the operators, who know exactly what they said.

## 12.6 How do you know it's right?

1. **The script exits 0 on the synthesis.** No unsupported codes; no missed requirements.
2. **Every uncoded sentence in the synthesis traces to a transcript.** Read the synthesis with the transcripts open. The script sees only square brackets.
3. **Every cited code's quote says what the finding says.** Spot-check at least one quote per finding in section A.
4. **The roster passes the coverage check.** Both cities; senior and junior; the sceptic; the upstream producers near and far; every blocker; the sponsor once.
5. **The map has a source on every row and was reviewed by operators,** with their corrections recorded.
6. **Every architecture-kind requirement is in section A** with the Day that builds it.
7. **Section D exists,** and contains the things a reader would expect and nobody said.
8. **No customer PII anywhere in the pack.** Search the worksheet folder for applicant names, PAN-shaped strings (`grep -rE "[A-Z]{5}[0-9]{4}[A-Z]" worksheet/`) and phone numbers; file numbers only.
9. **The numbers reconcile with earlier chapters:** 31 percent send-backs, 9.2 days median, 4.5 hours per file, 14 documents for two-wheeler, the 18:00 batch, AWS Mumbai.
10. **The architecture findings appear in Day 7's inputs table,** each one as a row with its architecture risk.

**Review checklist:**

- [ ] 8 to 10 end users plus admins and the sponsor, across roles and both cities, before any production code
- [ ] each transcript has persona, date, place, consent, read-back corrections and coded notes with verbatim evidence
- [ ] the six architecture questions asked of everyone, with answers in the transcripts
- [ ] the situational map: steps, systems, handoffs, waits, permissions; a source per row; reviewed and signed by operators
- [ ] the synthesis: architecture first; codes on every finding; requirement or hypothesis labelled; what was not found; confirmation
- [ ] the script exits 0; single-source findings labelled or backed by a test
- [ ] 100 to 200 golden examples identified with their labellers and conditions (Day 14 builds them)
- [ ] no PII in the pack; notes filed where the CISO said

## 12.7 Extend it

- Add a `--min-personas` option: a code is a requirement only if it appears in three interviews **and** two personas. Which Godavari requirements drop? (ERROR_CORRECTION_BY_ANALYST does. Is that right?)
- Make the script print, for each finding in the synthesis, the interviews behind it, so the readout can show "A1: T02, T04, T06, T07, T08".
