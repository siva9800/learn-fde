"""No business rules in prompts, customer text always wrapped, no model names, declared variables."""

from __future__ import annotations

from pathlib import Path

import pytest

from godavari_prompts.lint import lint
from godavari_prompts.loader import available_versions, load, version_dir


@pytest.mark.parametrize("version", available_versions("extraction"))
def test_shipped_versions_have_no_lint_errors(version: str) -> None:
    assert lint(load("extraction", version)).errors == []


def test_the_trim_leaves_an_unused_variable_warning() -> None:
    rep = lint(load("extraction", "2.1.0"))
    assert rep.warnings == ["call 'extract' declares 'telugu' but no template reads it"]


@pytest.mark.parametrize("sentence, what", [
    ("The requested amount must not exceed 90 percent of the on-road price.", "percentage"),
    ("Mark the file eligible when the PAN is present.", "eligibility"),
    ("Reject the file if the address proof is a gas bill.", "decision word"),
    ("Income must be at least Rs 15,000 a month.", "rupee threshold"),
    ("Five documents are mandatory for a gold loan.", "document requirement"),
])
def test_a_business_rule_in_a_prompt_is_an_error(prompts_copy: Path, sentence: str, what: str) -> None:
    product = version_dir("extraction", "2.0.0", prompts_copy) / "products" / "two-wheeler.j2"
    product.write_text(product.read_text(encoding="utf-8") + sentence + "\n", encoding="utf-8")
    errors = lint(load("extraction", "2.0.0", root=prompts_copy)).errors
    assert any(what in e and "signed code" in e for e in errors), errors


def test_a_rule_hidden_in_a_field_description_is_caught(prompts_copy: Path) -> None:
    meta = version_dir("extraction", "2.0.0", prompts_copy) / "meta.toml"
    meta.write_text(meta.read_text(encoding="utf-8").replace(
        'net_weight_g = "the net weight', 'net_weight_g = "LTV is computed on the net weight'), encoding="utf-8")
    assert any("[fields].net_weight_g" in e for e in lint(load("extraction", "2.0.0", root=prompts_copy)).errors)


def test_page_text_outside_the_untrusted_wrapper_is_an_error(prompts_copy: Path) -> None:
    tpl = version_dir("extraction", "2.0.0", prompts_copy) / "extract.user.j2"
    tpl.write_text("Here is the page: {{ page.text }}\n", encoding="utf-8")
    assert any("outside the untrusted-page wrapper" in e for e in lint(load("extraction", "2.0.0", root=prompts_copy)).errors)


def test_a_model_name_in_a_template_is_an_error(prompts_copy: Path) -> None:
    tpl = version_dir("extraction", "2.0.0", prompts_copy) / "partials" / "_role.j2"
    tpl.write_text("You are fake-large-2026-10, a careful reader.\n", encoding="utf-8")
    assert any("names a model" in e for e in lint(load("extraction", "2.0.0", root=prompts_copy)).errors)


def test_a_missing_product_variant_is_an_error(prompts_copy: Path) -> None:
    (version_dir("extraction", "2.0.0", prompts_copy) / "products" / "personal.j2").unlink()
    assert any("'personal' has no variant" in e for e in lint(load("extraction", "2.0.0", root=prompts_copy)).errors)


def test_an_undeclared_variable_is_an_error(prompts_copy: Path) -> None:
    tpl = version_dir("extraction", "2.0.0", prompts_copy) / "classify.system.j2"
    tpl.write_text(tpl.read_text(encoding="utf-8").replace("Decide which", "For {{ branch }}, decide which"),
                   encoding="utf-8")
    assert any("undeclared variable 'branch'" in e for e in lint(load("extraction", "2.0.0", root=prompts_copy)).errors)
