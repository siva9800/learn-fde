# 02 · Where Prompts Live: Files in the Repository, Rules in Signed Code

> Day 13 · Section 2 of 13 · [Chapter overview](README.md) · Previous: [01 · Why prompts as code](01-why-prompts-as-code.md) · Next: [03 · Templates](03-templates.md)

---

## 2.1 Three wrong places and one right one

| Where the prompt lives | What goes wrong | When teams do it |
|---|---|---|
| An f-string inside the Python that calls the model | every prompt change is a code change with no prompt-shaped review; the diff mixes logic and wording; nobody outside engineering can read it; it cannot be rolled back without rolling back the code | the first prototype, and then forever |
| A vendor's prompt dashboard, edited in the browser | the change happens outside the pull request, so nobody reviews it, CI does not run, and the repository no longer describes what runs; an edit at 4 p.m. is live at 4:01 | when the vendor makes it easy and the deadline is close |
| A table in a config database, edited by an admin screen | the same as the dashboard, plus no diff at all | when a customer asks to "tune the wording themselves" |
| **Files in the repository, changed by pull request, released through a registry file** | the change has a diff, an author, a reviewer, CI checks, an eval score and a rollback | this chapter |

The dashboard row deserves care: 2026 platforms do offer versions and labels, and some let you call a stored prompt
by ID. The problem is not missing versions; it is that the change and its review happen away from the code and the
eval, so the repository stops being the truth. Use such a platform as a mirror, never as the source (section 08).

## 2.2 What counts as "the prompt"

The instruction text is the smallest part. Everything below changes what the model does, so all of it lives in the
version directory and all of it is covered by the version's content hash:

| Part | In the Godavari package | Why it is part of the prompt |
|---|---|---|
| Instruction templates | `classify.system.j2`, `extract.system.j2` | the obvious part |
| Partials | `partials/_role.j2`, `_unsure.j2`, `_telugu_glossary.j2` | a one-line edit to a partial changes every call that includes it |
| Product variants | `products/two-wheeler.j2` and three more | "on-road, not ex-showroom" is a behaviour |
| Field descriptions | `[fields]` in `meta.toml` | the model reads them; "net pay, not gross" lives here |
| Page-type routing | `[page_fields]`, `[page_types]` | which page is asked for which field |
| Merge precedence | `[merge]` | the annexure beats the form; applied in code but versioned with the prompt it serves |
| Few-shot examples | `examples/income_proof_telugu.json` | an example teaches more strongly than an instruction |
| Variable types | `[calls.*.variables]` | the interface between the pipeline and the template |

What is **not** in the version directory: the model snapshot (it belongs to the release, because the same prompt on a
new model is a new release, section 04), the output schema itself (Day 12 owns it; the version records which schema it
was written for), and the business rules.

## 2.3 The rules stay in code

Godavari's compliance head, in Day 6: "I sign it, and if it changes, I sign the change. I do not want a machine
deciding that a gas bill is an address proof because it saw one accepted last year." Day 11 turned that into rule
files she signs. This chapter adds the matching discipline on the prompt side: **a prompt never contains a business
rule.** Not the fourteen two-wheeler documents, not the 90 percent margin, not the LTV caps, not "reject if".

Two reasons, one technical and one human:

- A rule written in a prompt is a second copy of a rule that already exists in code. The copies drift. When the
  circular changes, she signs the code change; nobody signs the prompt. Within a month the model is told one thing and
  the code enforces another, and the analyst sees two answers.
- A prompt is a request, not an enforcement. Day 11 measured what happens when the rules are left to the prompt: the
  model applies them loosely and does the arithmetic badly. Code enforces 100 percent of the time.

The `lint` in CI makes this mechanical: percentages, rupee thresholds, LTV, "approve", "reject", "eligible",
"mandatory", "at least" in any text the model is shown, including field descriptions in `meta.toml`, fail the build
(section 05). The lint catches the words. A human still checks the meaning, because "only read files with a PAN" is a
rule with none of those words in it.

What the prompt may say is what the model is for: what to read, where to find it, how to say "unsure", and the
sentence in `_role.j2` that tells it what it is not for: "You do not judge the file: whether a file is complete, and
what happens to it, is decided by rules in code that the compliance head signs, and by an analyst."

## 2.4 The compliance head reads the prompt

She does not review Jinja, and she should not have to. For every release that will run on real files, the package
renders a plain document, "what the system is told to do", with every call the model receives for one product and a
placeholder where the customer's page goes (`explain.py`; the 2.0.0 two-wheeler version is in
`data/what-the-system-is-told-2.0.0-two-wheeler.md`). She reads it and the registry records her name in
`compliance_read_by`. Promotion to pilot or production refuses without it.

Be precise about what her read means, because it is easy to over-claim in a readout:

| She confirms | She does not confirm |
|---|---|
| no business rule is in the prompt | that the extraction is accurate (the eval score does that) |
| nothing asks the model to decide what a rule or an analyst decides | that the wording is optimal (engineering owns that) |
| the "unsure" instruction matches her "cannot tell over a guess" | that the model will follow it (the eval and the drift check do that) |

This is the cheapest trust you will buy in an engagement: a regulator's first question about an AI system is "what is
it told to do?", and she can answer it from a dated, versioned document.

## 2.5 The package on disk

```text
code/prompts/
  registry.json                      releases, pins, history (changed only by pull request)
  extraction/
    1.0.0/  meta.toml  whole_file.system.j2  whole_file.user.j2  partials/_untrusted_page.j2
    1.1.0/  ... the same, with the request repeated after the document
    2.0.0/  meta.toml
            classify.system.j2  classify.user.j2  extract.system.j2  extract.user.j2
            partials/  _role.j2 _unsure.j2 _telugu_glossary.j2 _data_not_instructions.j2
                       _output.j2 _untrusted_page.j2 _untrusted_page_head.j2
            products/  two-wheeler.j2 gold.j2 small-business.j2 personal.j2
            examples/  income_proof_telugu.json
    2.1.0/  ... 2.0.0 trimmed (section 05)
```

Day 12's two text files, `classify-v1.txt` and `extract-v1.txt`, become 2.0.0's classify and extract templates, with
the product and page-type parts split out. Old versions stay. They are a few kilobytes each, and they are what a rollback rolls back to. Deleting "unused" versions
is the commonest way to make a rollback impossible (section 07, and a test in `test_registry.py`).
