"""One test per rule decision the compliance head would ask about, including the boundaries."""

from __future__ import annotations

from decimal import Decimal

from helpers import ids, make_ctx

from intake import rules_gold, rules_two_wheeler
from intake.catalogue import Doc
from intake.reference import gold_rate_on
from intake.ruleset import Action
from intake.validators import parse_date, verhoeff_check_digit

TW = rules_two_wheeler.RULESET
GL = rules_gold.RULESET


def test_a_complete_clean_two_wheeler_file_has_no_findings() -> None:
    assert TW.run(make_ctx()) == []


def test_a_complete_clean_gold_file_has_no_findings() -> None:
    assert GL.run(make_ctx("gold")) == []


def test_fourteen_two_wheeler_documents_and_nine_gold() -> None:
    assert len(rules_two_wheeler.REQUIRED_DOCS) + 1 == 14         # plus the conditional co-applicant KYC
    assert len(rules_gold.REQUIRED_DOCS) == 9


def test_missing_address_proof_is_sent_back_with_the_rule() -> None:
    findings = TW.run(make_ctx(drop=(Doc.PROOF_OF_ADDRESS,)))
    assert ids(findings) == ["TW-DOC-05"]
    assert findings[0].action == Action.SEND_BACK


def test_missing_document_with_unclassified_pages_goes_to_review_not_the_branch() -> None:
    findings = TW.run(make_ctx(drop=(Doc.PROOF_OF_ADDRESS,), uncertain_pages=(17,)))
    assert findings[0].action == Action.REVIEW and "17" in findings[0].message


def test_gas_bill_in_fathers_name_is_not_on_the_signed_list() -> None:
    findings = TW.run(make_ctx(attrs={Doc.PROOF_OF_ADDRESS: {"kind": "gas bill", "holder": "father"}}))
    assert ids(findings) == ["TW-ADDR-LIST"]


def test_electricity_bill_in_own_name_and_fresh_is_accepted() -> None:
    attrs = {Doc.PROOF_OF_ADDRESS: {"kind": "electricity bill", "holder": "self", "date": "15-10-2026"}}
    assert TW.run(make_ctx(attrs=attrs)) == []


def test_electricity_bill_61_days_old_is_sent_back_and_60_is_not() -> None:
    old = {Doc.PROOF_OF_ADDRESS: {"kind": "electricity bill", "holder": "self", "date": "02-09-2026"}}
    edge = {Doc.PROOF_OF_ADDRESS: {"kind": "electricity bill", "holder": "self", "date": "03-09-2026"}}
    assert ids(TW.run(make_ctx(attrs=old))) == ["TW-ADDR-AGE"]          # 61 days before 02-11-2026
    assert TW.run(make_ctx(attrs=edge)) == []                            # exactly 60


def test_ovd_in_a_relatives_name_is_sent_back() -> None:
    findings = TW.run(make_ctx(attrs={Doc.PROOF_OF_ADDRESS: {"kind": "electricity bill", "holder": "father",
                                                             "date": "20-10-2026"}}))
    assert ids(findings) == ["TW-ADDR-LIST"] and "father" in findings[0].message


def test_unmasked_aadhaar_anywhere_in_the_file_blocks_it() -> None:
    stem = "56789012345"
    number = stem + verhoeff_check_digit(stem)
    ctx = make_ctx(extra_page_text=f"PHOTOCOPY - REVERSE SIDE\n{number[:4]} {number[4:8]} {number[8:]}")
    findings = TW.run(ctx)
    assert ids(findings) == ["TW-KYC-MASK"] and findings[0].action == Action.BLOCK


def test_ninety_percent_of_on_road_price_passes_and_one_rupee_more_does_not() -> None:
    assert TW.run(make_ctx(fields={"requested_amount": "99000", "on_road_price": "110000"})) == []
    assert ids(TW.run(make_ctx(fields={"requested_amount": "99001", "on_road_price": "110000"}))) == ["TW-AMT-MARGIN"]


def test_unreadable_amount_goes_to_review_rather_than_passing() -> None:
    findings = TW.run(make_ctx(fields={"requested_amount": None}))
    assert {f.rule_id for f in findings} == {"TW-AMT-RANGE", "TW-AMT-MARGIN"}
    assert all(f.action == Action.REVIEW for f in findings)


def test_co_applicant_named_without_kyc() -> None:
    assert ids(TW.run(make_ctx(fields={"co_applicant_name": "SAI KIRAN PASUPULETI"}))) == ["TW-DOC-14"]


def test_age_21_on_the_day_passes_and_one_day_short_does_not() -> None:
    assert TW.run(make_ctx(fields={"date_of_birth": "02-11-2005"})) == []
    assert ids(TW.run(make_ctx(fields={"date_of_birth": "03-11-2005"}))) == ["TW-AGE"]


def test_statement_ending_31_days_before_application_is_sent_back() -> None:
    attrs = {Doc.BANK_STATEMENT: {"period_start": "01-07-2026", "period_end": "02-10-2026", "salary_credits": "3"}}
    findings = TW.run(make_ctx(attrs=attrs))
    assert ids(findings) == ["TW-BANK-AGE"] and findings[0].action == Action.SEND_BACK


def test_quotation_after_the_application_is_sent_back() -> None:
    assert ids(TW.run(make_ctx(fields={"quotation_date": "05-11-2026"}))) == ["TW-DATE-QUOTE"]


# --- Gold: arithmetic in code, on net weight, with the tier read off the amount ------------------------------
def test_ltv_tiers() -> None:
    assert rules_gold.max_ltv_percent(250_000) == 85
    assert rules_gold.max_ltv_percent(250_001) == 80
    assert rules_gold.max_ltv_percent(500_000) == 80
    assert rules_gold.max_ltv_percent(500_001) == 75


def test_collateral_value_is_exact_decimal_arithmetic() -> None:
    assert rules_gold.collateral_value(Decimal("28.0"), 22, 11_404) == 319_312
    assert rules_gold.collateral_value(Decimal("10.1"), 18, 11_000) == 90_900     # 10.1 x 11000 x 18/22


def test_amount_exactly_at_the_85_percent_cap_passes_and_one_rupee_over_blocks() -> None:
    rate = gold_rate_on(parse_date("04-11-2026"))
    assert rate is not None
    value = rules_gold.collateral_value(Decimal("20.0"), 22, rate)      # Rs 2,28,080: the 85 percent tier
    at_cap = value * 85 // 100
    small = {"gross_weight_g": "22.0", "net_weight_g": "20.0"}
    assert GL.run(make_ctx("gold", fields={**small, "requested_amount": str(at_cap)})) == []
    over = GL.run(make_ctx("gold", fields={**small, "requested_amount": str(at_cap + 1)}))
    assert ids(over) == ["GL-LTV"] and over[0].action == Action.BLOCK


def test_ltv_uses_net_weight_not_gross() -> None:
    # Within 85 percent of the gross-weight value, over 85 percent of the net-weight value: a breach.
    fields = {"gross_weight_g": "33.0", "net_weight_g": "28.0", "requested_amount": "280000"}
    assert ids(GL.run(make_ctx("gold", fields=fields))) == ["GL-LTV"]


def test_net_weight_above_gross_is_a_review_not_a_number() -> None:
    findings = GL.run(make_ctx("gold", fields={"net_weight_g": "31.0", "gross_weight_g": "30.0"}))
    assert ids(findings) == ["GL-LTV"] and findings[0].action == Action.REVIEW


def test_no_published_rate_means_review_never_a_guess() -> None:
    findings = GL.run(make_ctx("gold", fields={"appraisal_date": "04-01-2027", "application_date": "04-01-2027"}))
    assert any(f.rule_id == "GL-LTV" and "never guessed" in f.message for f in findings)
