"""Validation: the shape (schema, parsing, repair) and the content (valid shape, wrong value)."""

from __future__ import annotations

import json

import pytest
from conftest import make_request
from pydantic import ValidationError

from godavari_llm.contract import PageExtraction, provider_schema
from godavari_llm.extractor import GodavariExtractor, check_page, parse_amount
from godavari_llm.client import lenient_json

PAGE = "\n".join(["LOAN APPLICATION FORM", "File no: KKP-26-00001", "Applicant name: Kavya Reddy",
                  "PAN: ABCPR1234K", "Product: Two-wheeler loan", "Loan amount requested: Rs. 1,25,000",
                  "Vehicle ex-showroom price: Rs. 1,34,000"])


def answer(**overrides) -> dict:
    blank = {"value": None, "confidence": 0.0, "evidence": ""}
    obj = {"page_type": "application_form",
           "applicant_name": {"value": "Kavya Reddy", "confidence": 0.95, "evidence": "Applicant name: Kavya Reddy"},
           "applicant_pan": {"value": "ABCPR1234K", "confidence": 0.95, "evidence": "PAN: ABCPR1234K"},
           "co_applicant_name": dict(blank),
           "product": {"value": "two-wheeler", "confidence": 0.9, "evidence": "Product: Two-wheeler loan"},
           "requested_amount": {"value": 125000, "confidence": 0.93, "evidence": "Loan amount requested: Rs. 1,25,000"},
           "monthly_income": dict(blank)}
    obj.update(overrides)
    return obj


# --- shape ------------------------------------------------------------------------------------------

@pytest.mark.parametrize("text", [
    "```json\n{\"a\": 1}\n```",
    "Here is the extracted data:\n{\"a\": 1}",
    "{\"a\": 1}\nLet me know if you need anything else.",
])
def test_wrappers_are_stripped_but_reported(text):
    assert lenient_json(text) == ({"a": 1}, "wrapper_stripped")


def test_truncated_json_is_not_patched():
    assert lenient_json('{"page_type": "pan_card", "applicant_name": {"value": "KAV')[1] == "invalid"


def test_schema_rejects_a_malformed_pan_and_unknown_keys():
    with pytest.raises(ValidationError, match="five letters"):
        PageExtraction.model_validate(answer(applicant_pan={"value": "ABCP1234K", "confidence": 0.9, "evidence": "x"}))
    with pytest.raises(ValidationError, match="Extra inputs"):
        PageExtraction.model_validate({**answer(), "loan_decision": "approve"})


def test_provider_schema_is_strict_and_moves_unsupported_limits():
    schema = provider_schema(PageExtraction)
    text = json.dumps(schema)
    for word in ('"minimum"', '"maximum"', '"maxLength"', '"title"'):
        assert word not in text
    amount = schema["$defs"]["AmountField"]
    assert amount["additionalProperties"] is False
    assert set(amount["required"]) == {"value", "confidence", "evidence"}
    assert "minimum 1" in json.dumps(amount["properties"]["value"])      # still told to the model


def test_truncation_gets_a_bigger_budget_then_parses(harness):
    good = json.dumps(answer())
    client, provider, ledger, _ = harness([(good[:80], "max_tokens"), (good, "end")])
    res = client.call_structured(make_request(), PageExtraction, file_id="F1", page=1, stage="extract")
    assert res.parsed is not None and res.problems == ["truncated"]
    assert provider.requests[1].max_output_tokens == 1000
    assert provider.requests[1].idempotency_key.endswith("#max2")


def test_invalid_object_is_re_asked_once_with_the_error(harness):
    bad = json.dumps(answer(applicant_pan={"value": "ABCP1234K", "confidence": 0.9, "evidence": "PAN: ABCP1234K"}))
    client, provider, _, _ = harness([(bad, "end"), (json.dumps(answer()), "end")])
    res = client.call_structured(make_request(), PageExtraction, file_id="F1", page=1, stage="extract")
    assert res.parsed is not None and res.problems == ["schema_invalid"]
    assert "five letters" in provider.requests[1].user_text and provider.requests[1].purpose == "repair"


def test_still_invalid_after_one_repair_returns_none(harness):
    client, _, _, _ = harness([("not json", "end"), ("still not json", "end")])
    res = client.call_structured(make_request(), PageExtraction, file_id="F1", page=1, stage="extract")
    assert res.parsed is None and res.problems == ["schema_invalid", "invalid_after_repair"]


def test_refusal_is_not_parsed(harness):
    client, _, _, _ = harness([("I can't help with this document.", "refusal")])
    res = client.call_structured(make_request(), PageExtraction, file_id="F1", page=1, stage="extract")
    assert res.parsed is None and res.problems == ["refusal"]


# --- content: valid shape, wrong value ----------------------------------------------------------------

def test_a_correct_answer_passes_the_content_checks():
    assert check_page(PageExtraction.model_validate(answer()), PAGE) == []


def test_amount_that_disagrees_with_its_own_evidence_is_caught():
    wrong = answer(requested_amount={"value": 1250000, "confidence": 0.97, "evidence": "Loan amount requested: Rs. 1,25,000"})
    assert check_page(PageExtraction.model_validate(wrong), PAGE) == [
        "requested_amount: value 1250000 does not match its evidence 'Loan amount requested: Rs. 1,25,000'"]


def test_evidence_that_is_not_on_the_page_is_caught():
    wrong = answer(applicant_pan={"value": "ABCPR1294K", "confidence": 0.95, "evidence": "PAN: ABCPR1294K"})
    assert check_page(PageExtraction.model_validate(wrong), PAGE) == ["applicant_pan: the evidence text is not on the page"]


def test_the_wrong_line_on_the_right_page_passes_every_check():
    """The honest limit: a real line, a matching value, the wrong field. Only evals and review catch this."""
    wrong = answer(requested_amount={"value": 134000, "confidence": 0.91, "evidence": "Vehicle ex-showroom price: Rs. 1,34,000"})
    assert check_page(PageExtraction.model_validate(wrong), PAGE) == []


def test_pages_that_disagree_withhold_the_value_and_ask_for_review():
    form = PageExtraction.model_validate(answer())
    pan_card = PageExtraction.model_validate(answer(
        page_type="pan_card", applicant_name={"value": "SWATHI REDDY", "confidence": 0.9, "evidence": "Name: SWATHI REDDY"}))
    from godavari_llm.contract import Doc
    merged = GodavariExtractor._merge("F1", {1: (Doc.APPLICATION_FORM, 0.9), 2: (Doc.PAN_CARD, 0.9)}, {1: form, 2: pan_card})
    assert merged.applicant_name.value is None and merged.applicant_name.flags == ["conflict"]
    assert merged.needs_review and "pages disagree" in merged.review_reasons[0]


@pytest.mark.parametrize("text,expected", [
    ("Loan amount requested: Rs. 1,25,000", 125000), ("SALARY CREDIT DECCAN AUTO WORKS 35,000.00", 35000),
    ("Rs. 12,50,000", 1250000), ("no number here", None)])
def test_parse_amount_reads_indian_grouping(text, expected):
    assert parse_amount(text) == expected
