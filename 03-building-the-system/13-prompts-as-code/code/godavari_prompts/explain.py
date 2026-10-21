""""What the system is told to do": a release's prompts rendered as one plain document for the compliance head.

She does not review Jinja. She reads, per release, exactly what the model is told for each page type and
product, with a placeholder where the customer's page goes, and confirms two things in writing: no
business rule is in it (the lint checks the words; she checks the meaning), and nothing in it asks the
model to decide what an analyst or a signed rule decides.
"""

from __future__ import annotations

from .loader import PageView, PromptVersion
from .registry import Release
from .synth import fields_for

PLACEHOLDER = PageView(0, "[the customer's page is inserted here, inside page tags, as data]")


def explain(rel: Release, pv: PromptVersion, product: str) -> str:
    out = [f"# What the system is told to do: {rel.release_id}, {product} files", "",
           f"Prompt {pv.ref}, written by {rel.author} on {rel.created}. Models: "
           + ", ".join(f"{t} = {m}" for t, m in sorted(rel.models.items())) + ".",
           f"Approved by: {rel.approved_by or 'not yet'}. Read by the compliance head: {rel.compliance_read_by or 'not yet'}.",
           "", f"Summary: {pv.meta['summary']}", ""]
    if rel.eval:
        out += [f"Regression check on {rel.eval['set']} ({rel.eval['n_files']} files): "
                f"{rel.eval['correct_rate']:.1%} of fields correct, {rel.eval['wrong_rate']:.1%} wrong, "
                "the rest left for an analyst. Day 14's golden set is the full evaluation.", ""]
    out += ["The completeness and product rules are not in these prompts. They are code you signed "
            "(Day 11's rule files), and the model's output is checked against them after it answers.", ""]
    if pv.strategy == "whole_file":
        system, user = pv.render("extract_file", product=product, file_id="<file number>",
                                 fields=pv.field_defs(fields_for(product)), pages=[PLACEHOLDER])
        out += ["## One call for the whole file", "", "```text", system.rstrip(), "", user.rstrip(), "```"]
        return "\n".join(out) + "\n"
    page_types = [{"name": k, "description": v["description"], "titles": v["titles"]}
                  for k, v in pv.meta["page_types"].items()]
    system, _ = pv.render("classify", page=PLACEHOLDER, page_types=page_types)
    out += ["## Step 1: every page is classified", "", "```text", system.rstrip(), "```", ""]
    wanted = set(fields_for(product))
    for page_type, names in pv.meta["page_fields"].items():
        names = [n for n in names if n in wanted]
        if not names:
            continue
        variants = [False, True] if page_type in ("application_form", "income_proof") else [False]
        for telugu in variants:
            exs = [e for e in pv.meta.get("examples", []) if e["page_type"] == page_type and e["telugu"] == telugu]
            examples = [{"page_text": "[a masked example page from the training split]",
                         "answer": "[its correct answer]"} for _ in exs]
            system, _ = pv.render("extract", product=product, page_type=page_type, fields=pv.field_defs(names),
                                  telugu=telugu, examples=examples, page=PLACEHOLDER)
            label = f"{page_type} page" + (" with Telugu text" if telugu else "")
            out += [f"## Step 2: the {label}", "", "```text", system.rstrip(), "```", ""]
    return "\n".join(out).rstrip("\n") + "\n"
