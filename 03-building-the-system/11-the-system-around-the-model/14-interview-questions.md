# 14 · Interview Questions

> Day 11 · Section 14 of 16 · [Chapter overview](README.md) · Previous: [13 · Mistakes and debugging](13-mistakes-and-debugging.md) · Next: [15 · Exercises](15-exercises.md)

---

Sixteen questions in the forms they take in FDE loops. Most come up inside the system-design or
decomposition round ("and where does the model sit?"), some in the hiring-manager screen, and a few as
follow-ups to a take-home. Answer out loud first, then compare. Section numbers point to the full explanation.

## The split

**Q1. Design a system that reads loan applications and checks them for completeness. Where does the LLM go?**

The model reads; code decides. I would draw eight boxes: ingestion, retrieval, model, rules, verification,
interface, integration and observability. The model classifies pages and extracts fields with a page number
and a quote for each, and is allowed to say "unsure". Verification checks every claim against the page,
checks formats, cross-checks fields that appear twice, and looks up reference data. The completeness rules
are deterministic code, owned and signed by the compliance owner, run only on verified inputs. Anything the
system cannot settle goes to a review queue with its reason, a named person approves every file, and the
write to the system of record is idempotent and behind that approval. The model's other job is writing the
plain-language explanation of what code found. (Sections 02, 05, 08.)

**Q2. The model gets the checklist right 99 percent of the time in your tests. Why not leave it in the prompt?**

Because 99 percent is a rate and the checklist is a rule. At 2,400 files a month, 1 percent is about 24 files
a month where a KYC rule was applied wrongly, each a potential audit observation. Code applies the rule the
same way to every file: right for all of them, or wrong for all of them and fixed for all of them by one
change. There is also the question of who can sign it: the compliance owner can sign a rule table generated
from code; she cannot sign a prompt, because the same prompt can behave differently on the next model version.
I would still use the model's reading of the documents; I would not use its judgement of the rule. (03.2, 04.4.)

**Q3. What is "the model proposes, code disposes"?**

The model's outputs are proposals that deterministic code checks and acts on. The model may say "page 9 is the
salary account" or "this address proof is a gas bill in the father's name"; code verifies the claim (does page
9 have three monthly salary credits?) and applies the rule (a gas bill is not on the signed list). The model
never routes a file, writes to a system of record or overrides a check. It can explain what code decided.
(05.1, 06.2.)

**Q4. Give me a decision table: what goes to code and what goes to the model?**

Code: hard business rules and regulatory constraints, arithmetic and dates, lookups and joins against reference
data, ID and format validation, permissions and visibility, writes to systems of record. Model: reading messy
documents, classifying free text and pages, summarising, explaining, drafting for a human. The seams get both
with a contract: the model proposes the salary account and code checks the credits; code finds a discrepancy
and the model explains it; the model classifies pages and code counts them against the checklist. (03.4, 06.)

**Q5. Tell me about a constraint you would never leave to a prompt.**

OpenAI's FDE team published a good one: in an automotive supply-chain system, "always maintaining at least two
suppliers for critical components like tires" was checked deterministically, 100 percent of the time, and the
model explored options through a simulator and explained them rather than optimising directly. My own example
from a lender: a gold loan must be within the RBI's tiered loan-to-value cap of the collateral value computed
from net weight, purity and the published rate. A model doing that arithmetic will be almost right, and almost
right is a regulatory breach. (03.3, 07.2.)

## Rules and the customer

**Q6. How do you sort a customer's rules?**

Three bins. Regulatory: from a regulator or law, in code, no override. Policy: the customer's own, in code,
overridable by a named person with a written reason that is logged. Judgement: a decision a skilled person
makes from evidence, given to the model as a proposal with a human deciding. The test that separates policy
from judgement is whether a named owner can write it as a sentence with no "usually" in it. Most of what
operations teams call judgement turns out to be unwritten policy, and getting it written and signed is often
the biggest win of the engagement. (04.1, 04.2.)

**Q7. The compliance head will not read Python. How do you get her to sign rules that are code?**

Each rule is an object with an id, a kind, a sentence she can read, a source and a check. A script generates
the rule sheet from the code, so the sheet cannot drift from what runs. A fingerprint over the rule code goes
on the sheet and into a sign-off record, and the system refuses to run rules whose fingerprint does not match
what she reviewed. The tests are named in her language, "a utility bill 61 days old is sent back and 60 is not",
and in the review I read the test names, not the code. When she asks about a case, I write the test in front of
her. (04.4.)

**Q8. A rule changes because of a new RBI circular. Walk me through the change.**

The compliance head tells us the change and its effective date. The rule and its boundary tests change in one
pull request; CI runs the tests, regenerates the sheet and computes the new fingerprint. She reviews the sheet
diff and the new test names, and the sign-off record is updated with the version, fingerprint, her name and the
date. The old version stays retrievable, and files are judged by the version in force on their date, so a file
received before the effective date is not judged by the new rule. (10.2, 10.3.)

**Q9. An analyst wants to override a rule for one file. What does the system do?**

It depends on the bin. A policy rule can be overridden by a named analyst with a written reason, which is
logged with the time and becomes part of the file's audit record. A regulatory rule cannot be overridden by
anyone; the code has no path for it. If one policy rule is overridden every day, that is a signal the rule is
wrong for real cases, and the answer is a conversation with its owner, not a quieter override. (04.1, 10.5.)

## Verification and failure modes

**Q10. Structured outputs guarantee valid JSON. Why do you still need validation?**

Because they guarantee shape, not truth, and even the shape guarantee has documented exceptions. A
schema-valid answer can claim a document on a blank page, copy an OCR misread with high confidence, or convert
a monthly figure to an annual one silently. After the call I check grounding (the quote is on the cited page
and the page is the claimed type), that each value is supported by its own quote, confidence against measured
thresholds, formats and checksums, cross-field consistency, and reference lookups. Range constraints such as
amount limits do not belong in the schema anyway. (05.2, 09.1.)

**Q11. How do you stop the model from hallucinating that a document is present?**

Require evidence and check it. Every document claim carries a page number and a quote; code checks the quote is
verbatim on that page and that the page's printed title is the claimed document's. A claim that fails is dropped
before any rule sees it, so the completeness rule finds the document missing and the branch is told. In my
prototype the model invented twelve documents over 130 files; all twelve were rejected by that check. (05.3.)

**Q12. What failure modes do you see when the split is wrong in each direction?**

Too much to the model: arithmetic in a prompt, rules in a prompt nobody can sign, a model verdict that skips
the rules, permissions written as instructions. Those fail silently and late, through the auditor or the CISO.
Too much to code: regex extraction on documents that vary, keyword lists for judgement, templates for prose.
Those fail early and visibly, and cost adoption. The fix in both directions is the same principle: the model
reads, code validates what it read with the same regex that would have been brittle as an extractor. (07.)

**Q13. Your system sends a file back to a branch for a document the branch already sent. What happened?**

Most likely a seam failure: the model could not classify the page that held the document, so the completeness
rule saw it as absent. The fix is a seam rule: when a required document is missing and some pages are
unclassified, route to an analyst with those page numbers instead of telling the branch. The rule stays
deterministic; it just refuses to be more certain than its input. I would also check whether the branch used a
new form layout, and add that file to the golden set. (06.4, 13.2.)

**Q14. Where do the humans go in your diagram?**

Wherever a decision has an owner. The rule owner signs the rules. A named analyst approves every file, because
the regulator asks who decided and on what documents. Domain experts label the golden set that sets the
thresholds. The upstream producer, here the branch, is told on day one what is missing. The owner of the system
of record approves the write path. A box that decides something with no owner is either a rule that needs one
or a judgement that needs a reviewer. (02.4.)

## Production

**Q15. What do you store with every file so that an auditor can reconstruct the decision years later?**

The ruleset's product, version and fingerprint; every finding with its rule id, kind, action and message; the
model name and version and the prompt version; every override with the analyst, reason and time; and the
approving analyst and time. And I keep the rule code retrievable by fingerprint for the retention period, seven
years at this lender, so the old rules can be rerun on the old file. (10.1.)

**Q16. How would you hand this over so the customer's engineer can own it?**

Keep the split clean. The rules are plain code with tests named in business language, so the customer's
engineer can change a limit, run the tests, regenerate the sheet and take it to the rule owner without
understanding the model. The model sits behind one interface, so a vendor change does not touch the rules. The
sign-off record lives in their repository. The handover test is the customer's engineer releasing a rule change
without our help. (10.7.)

## Quick-fire round

| Question | Short answer |
|---|---|
| Should an LLM compute a loan-to-value ratio? | No. It extracts the inputs with quotes; code computes in Decimal. |
| Can a confidence score replace review? | Not until it is calibrated on labelled data, and even then it does not see upstream OCR errors. |
| Where is branch visibility enforced? | In code, inside the query, from the caller's directory groups. Never in a prompt. |
| What does the model do with "unsure"? | Returns null. Code routes it to review. A guess is the failure, not "unsure". |
| Who writes the note to the branch? | The model drafts it from code's findings; code checks every rule id is cited. |
| Is a policy engine needed? | Not for a few dozen rules in 90 days; maybe when the pattern repeats across customers. |
| What is the first thing you check when a rule "never fires"? | Whether it reads a field name the model does not return: a seam contract mismatch. |
| Fail open or fail closed? | Closed. Unreadable input means review, never a pass. |
