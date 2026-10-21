"""Optional: the same ExtractionModel interface, backed by a real LLM through the Anthropic Python SDK.

Not needed to run the chapter. To try it on the SYNTHETIC files only:

    pip install -r code/requirements-llm.txt        # anthropic==1.17.0, as of October 2026
    export ANTHROPIC_API_KEY=...                     # or `ant auth login`
    python -X utf8 code/run_batch.py --model anthropic --limit 5

Two rules this adapter enforces in code, because they are the customer's and not ours:
  1. It refuses to run unless the caller confirms the data is synthetic. Godavari's CISO allows the
     prototype only "on a machine in this building, on masked files ... with no internet" (Day 6), so no
     real Godavari page may ever reach a public endpoint. Production model access is a Day 24 and Day 25
     decision (residency, the model gateway, private endpoints), not a flag here.
  2. The model only proposes. Everything it returns goes through the same envelope and the same signed
     rules as the stub's output; nothing in this file decides completeness.

API shapes follow the SDK documentation as of October 2026 (structured outputs via
`output_config.format`, the server-side refusal fallback). They will date; Day 12 owns them.
"""

from __future__ import annotations

import json
import os
from collections.abc import Sequence
from typing import Any

from .catalogue import Doc, DocFinding, FieldValue, LoanBundle, ModelOutput, PromptOnlyVerdict

DEFAULT_MODEL = os.environ.get("KAAGAZ_MODEL", "claude-opus-5-5")
FIELD_NAMES = ("applicant_name", "date_of_birth", "form_pan", "pan", "pan_card_name", "address", "mobile",
               "requested_amount", "tenure_months", "application_date", "aadhaar_last4", "form_monthly_income",
               "monthly_income", "co_applicant_name", "on_road_price", "quotation_date", "dealer_code",
               "gross_weight_g", "net_weight_g", "purity_carat", "appraisal_date")


def _nullable(kind: str) -> dict[str, Any]:
    return {"anyOf": [{"type": kind}, {"type": "null"}]}


def _obj(props: dict[str, Any]) -> dict[str, Any]:
    return {"type": "object", "additionalProperties": False, "required": list(props), "properties": props}


DOC_ENUM = {"type": "string", "enum": [d.value for d in Doc]}
SCHEMA: dict[str, Any] = _obj({
    "page_labels": {"type": "array", "items": _obj({"page": {"type": "integer"}, "doc_type": DOC_ENUM,
                                                     "confidence": {"type": "number"}})},
    "fields": {"type": "array", "items": _obj({"name": {"type": "string", "enum": list(FIELD_NAMES)},
                                                "value": _nullable("string"), "confidence": {"type": "number"},
                                                "page": _nullable("integer"), "evidence": {"type": "string"}})},
    "documents": {"type": "array", "items": _obj({
        "doc_type": DOC_ENUM, "page": {"type": "integer"}, "confidence": {"type": "number"},
        "evidence": {"type": "string"},
        "attributes": {"type": "array", "items": _obj({"key": {"type": "string"}, "value": {"type": "string"}})}})},
    "salary_account_page": _nullable("integer"),
    "prompt_only": _obj({"complete": {"type": "boolean"}, "issues": {"type": "array", "items": {"type": "string"}},
                         "eligible_amount": _nullable("integer")}),
})

SYSTEM = """You read scanned loan files for an Indian lender. The text of each page is given in tray order.
For every page, give its document type from the enum, or "unknown" for filler pages.
Extract the listed fields. For each field, copy the value exactly as printed, give the page number and
copy the whole line it came from as evidence, character for character. Do not convert, compute or
normalise anything except removing "Rs", commas and spaces from amounts. If you cannot read a value
with confidence, return null: "unsure" is a correct answer, a guess is not.
List each document you find with the page and its printed first line as evidence. For a proof of
address, add attributes kind (the document name as printed), holder (self, or the relation printed in
brackets) and date (if printed). For each bank statement add period_start, period_end and
salary_credits (the number of lines containing "SAL CREDIT").
Pick the bank statement you believe is the salary account as salary_account_page.
Finally, in prompt_only, say whether you think the file is complete and compliant, with issues; this
part is recorded for comparison and does not decide anything."""


class AnthropicExtractionModel:
    """ExtractionModel over the Anthropic Messages API. Requires the optional `anthropic` package."""

    name = f"anthropic:{DEFAULT_MODEL}"

    def __init__(self, client: Any | None = None, model: str = DEFAULT_MODEL,
                 i_confirm_synthetic_data: bool = False) -> None:
        if not i_confirm_synthetic_data and os.environ.get("KAAGAZ_SYNTHETIC_ONLY") != "yes":
            raise PermissionError("the real-model adapter runs on synthetic files only: pass "
                                  "i_confirm_synthetic_data=True or set KAAGAZ_SYNTHETIC_ONLY=yes")
        if client is None:
            import anthropic                      # optional dependency, imported only here
            client = anthropic.Anthropic()        # credentials from the environment, never hard-coded
        self.client = client
        self.model = model
        self.name = f"anthropic:{model}"

    def _call(self, system: str, user: str, schema: dict[str, Any] | None) -> str:
        output_config: dict[str, Any] = {"effort": "medium"}
        if schema is not None:
            output_config["format"] = {"type": "json_schema", "schema": schema}
        response = self.client.beta.messages.create(
            model=self.model, max_tokens=16000, system=system,
            messages=[{"role": "user", "content": user}],
            output_config=output_config,
            betas=["server-side-fallback-2026-07-01"], fallbacks="default",
        )
        if response.stop_reason in ("refusal", "max_tokens"):
            raise RuntimeError(f"model stopped with {response.stop_reason}; the file goes to manual review")
        return next(block.text for block in response.content if block.type == "text")

    def read(self, bundle: LoanBundle) -> ModelOutput:
        pages = "\n\n".join(f"=== page {p.number} ===\n{p.text}" for p in bundle.pages)
        user = f"Product: {bundle.product}. File {bundle.file_id}, {len(bundle.pages)} pages.\n\n{pages}"
        data = json.loads(self._call(SYSTEM, user, SCHEMA))
        return parse_output(self.name, data)

    def draft_note(self, bundle: LoanBundle, findings: Sequence[tuple[str, str]]) -> str:
        if not findings:
            return f"{bundle.file_id}: nothing for the branch; the file is ready for your approval."
        listed = "\n".join(f"- {rule_id}: {message}" for rule_id, message in findings)
        system = ("Write a short, plain note to a credit-ops analyst explaining these findings about one loan "
                  "file. Cite every rule id in brackets. Add no facts, numbers or advice that are not in the "
                  "findings. The rules have already been applied; do not re-judge them.")
        return self._call(system, f"File {bundle.file_id}:\n{listed}", None)


def parse_output(model_name: str, data: dict[str, Any]) -> ModelOutput:
    """JSON from the model into the shared dataclasses. Schema-valid is not the same as correct: the
    envelope in pipeline.py still checks every claim."""
    labels = {int(x["page"]): (Doc(x["doc_type"]), float(x["confidence"])) for x in data["page_labels"]}
    fields = {x["name"]: FieldValue(x["value"], float(x["confidence"]), x["page"], x["evidence"])
              for x in data["fields"]}
    documents = tuple(DocFinding(Doc(x["doc_type"]), int(x["page"]), float(x["confidence"]), x["evidence"],
                                 {a["key"]: a["value"] for a in x["attributes"]}) for x in data["documents"])
    po = data["prompt_only"]
    return ModelOutput(model_name, labels, fields, documents, data["salary_account_page"],
                       PromptOnlyVerdict(bool(po["complete"]), tuple(po["issues"]), po["eligible_amount"]))
