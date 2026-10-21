"""The real-model adapter, tested with a fake client: no network, no key, no `anthropic` package needed."""

from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any

import pytest

from intake.catalogue import PAGE_TITLES, Doc, LoanBundle, Page
from intake.llm_adapter import SCHEMA, AnthropicExtractionModel

CANNED = {
    "page_labels": [{"page": 1, "doc_type": "pan_card", "confidence": 0.95}],
    "fields": [{"name": "pan", "value": "ABCPP1234K", "confidence": 0.93, "page": 1,
                "evidence": "Permanent Account Number: ABCPP1234K"},
               {"name": "applicant_name", "value": None, "confidence": 0.3, "page": None, "evidence": ""}],
    "documents": [{"doc_type": "pan_card", "page": 1, "confidence": 0.95, "evidence": PAGE_TITLES[Doc.PAN_CARD],
                   "attributes": []}],
    "salary_account_page": None,
    "prompt_only": {"complete": True, "issues": [], "eligible_amount": None},
}


class FakeMessages:
    def __init__(self, text: str, stop_reason: str = "end_turn") -> None:
        self.text, self.stop_reason, self.calls = text, stop_reason, []

    def create(self, **kwargs: Any) -> SimpleNamespace:
        self.calls.append(kwargs)
        return SimpleNamespace(stop_reason=self.stop_reason, content=[SimpleNamespace(type="text", text=self.text)])


def _client(text: str, stop_reason: str = "end_turn") -> tuple[SimpleNamespace, FakeMessages]:
    messages = FakeMessages(text, stop_reason)
    return SimpleNamespace(beta=SimpleNamespace(messages=messages)), messages


BUNDLE = LoanBundle("GF-T", "Guntur", "gold", "sftp_scan",
                    (Page(1, PAGE_TITLES[Doc.PAN_CARD] + "\nPermanent Account Number: ABCPP1234K"),))


def test_refuses_without_the_synthetic_data_confirmation(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("KAAGAZ_SYNTHETIC_ONLY", raising=False)
    client, _ = _client("{}")
    with pytest.raises(PermissionError):
        AnthropicExtractionModel(client=client)


def test_parses_structured_output_into_the_shared_contract() -> None:
    client, messages = _client(json.dumps(CANNED))
    out = AnthropicExtractionModel(client=client, i_confirm_synthetic_data=True).read(BUNDLE)
    assert out.fields["pan"].value == "ABCPP1234K"
    assert out.fields["applicant_name"].value is None           # "unsure" survives the trip
    assert out.documents[0].doc == Doc.PAN_CARD
    request = messages.calls[0]
    assert request["output_config"]["format"]["schema"] is SCHEMA
    assert request["model"] == "claude-opus-5-5"


def test_a_refusal_is_an_error_not_an_empty_extraction() -> None:
    client, _ = _client("", stop_reason="refusal")
    with pytest.raises(RuntimeError):
        AnthropicExtractionModel(client=client, i_confirm_synthetic_data=True).read(BUNDLE)


def test_schema_objects_are_closed() -> None:
    def walk(node: Any) -> None:
        if isinstance(node, dict):
            if node.get("type") == "object":
                assert node.get("additionalProperties") is False and set(node["required"]) == set(node["properties"])
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)
    walk(SCHEMA)
