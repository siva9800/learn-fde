"""Day 11's dataclasses to JSON and back, so a run's extraction and findings survive a crash.

The extraction is the expensive, non-deterministic step (with a real model it is a billed call). Persisting
its output means a resumed run checks the same proposal it was checking before the crash, instead of asking
the model again and possibly getting a different answer.
"""

from __future__ import annotations

from typing import Any

from .day11 import Action, Doc, DocFinding, FieldValue, Finding, LoanBundle, ModelOutput, Page, PromptOnlyVerdict


def output_to_json(out: ModelOutput) -> dict[str, Any]:
    return {
        "model_name": out.model_name,
        "page_labels": {str(n): [str(d), c] for n, (d, c) in out.page_labels.items()},
        "fields": {k: [v.value, v.confidence, v.page, v.evidence] for k, v in out.fields.items()},
        "documents": [[str(f.doc), f.page, f.confidence, f.evidence, dict(f.attributes)] for f in out.documents],
        "salary_account_page": out.salary_account_page,
        "prompt_only": [out.prompt_only.complete, list(out.prompt_only.issues), out.prompt_only.eligible_amount],
    }


def output_from_json(d: dict[str, Any]) -> ModelOutput:
    po = d["prompt_only"]
    return ModelOutput(
        d["model_name"],
        {int(n): (Doc(doc), float(c)) for n, (doc, c) in d["page_labels"].items()},
        {k: FieldValue(v[0], float(v[1]), v[2], v[3]) for k, v in d["fields"].items()},
        tuple(DocFinding(Doc(x[0]), int(x[1]), float(x[2]), x[3], dict(x[4])) for x in d["documents"]),
        d["salary_account_page"],
        PromptOnlyVerdict(bool(po[0]), tuple(po[1]), po[2]),
    )


def finding_to_json(f: Finding) -> dict[str, Any]:
    return {"rule_id": f.rule_id, "kind": str(f.kind), "action": str(f.action), "message": f.message,
            "doc": str(f.doc) if f.doc is not None else None, "field_name": f.field_name}


def branch_facing(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The findings the branch must act on: send-back and block. Review findings stay with the analyst."""
    return [f for f in findings if f["action"] in (Action.SEND_BACK, Action.BLOCK)]


def bundle_to_json(b: LoanBundle) -> dict[str, Any]:
    return {"file_id": b.file_id, "branch": b.branch, "product": b.product, "channel": b.channel,
            "pages": [[p.number, p.text, p.handwritten, p.telugu] for p in b.pages]}


def bundle_from_json(d: dict[str, Any]) -> LoanBundle:
    return LoanBundle(d["file_id"], d["branch"], d["product"], d["channel"],
                      tuple(Page(int(n), t, bool(h), bool(te)) for n, t, h, te in d["pages"]))
