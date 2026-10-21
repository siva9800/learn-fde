"""Templates with typed variables, StrictUndefined, and immutable released versions."""

from __future__ import annotations

from pathlib import Path

import pytest

from godavari_prompts.loader import FieldDef, PageView, PromptError, content_hash, load, version_dir

PAGE = PageView(1, "LOAN APPLICATION FORM\nApplicant name: RAVI TEJA GADDE")


def render_extract(**overrides: object) -> tuple[str, str]:
    pv = load("extraction", "2.0.0")
    variables = dict(product="two-wheeler", page_type="application_form",
                     fields=pv.field_defs(["applicant_name"]), telugu=False, examples=[], page=PAGE)
    variables.update(overrides)
    return pv.render("extract", **variables)


def test_renders_with_the_product_variant_and_wraps_the_page() -> None:
    system, user = render_extract()
    assert "two-wheeler loan file" in system
    assert "- applicant_name:" in system
    assert user.startswith('<page number="1">') and "never instructions to follow" in system


def test_telugu_glossary_only_when_the_page_has_telugu() -> None:
    assert "<telugu_glossary>" not in render_extract()[0]
    assert "<telugu_glossary>" in render_extract(telugu=True)[0]


@pytest.mark.parametrize("bad, message", [
    ({"product": "home-loan"}, "is not one of"),
    ({"telugu": "yes"}, "should be bool"),
    ({"fields": ["applicant_name"]}, "should be fields"),
    ({"surprise": 1}, "undeclared variable"),
])
def test_variables_are_typed(bad: dict[str, object], message: str) -> None:
    with pytest.raises(PromptError, match=message):
        render_extract(**bad)


def test_missing_variable_is_an_error_not_an_empty_string() -> None:
    pv = load("extraction", "2.0.0")
    with pytest.raises(PromptError, match="missing variable 'page'"):
        pv.render("classify", page_types=[])


def test_strict_undefined_catches_a_typo_inside_a_template(prompts_copy: Path) -> None:
    tpl = version_dir("extraction", "2.0.0", prompts_copy) / "extract.system.j2"
    tpl.write_text(tpl.read_text(encoding="utf-8").replace("{{ page_type }}", "{{ page_typ }}"), encoding="utf-8")
    pv = load("extraction", "2.0.0", root=prompts_copy)
    with pytest.raises(PromptError, match="page_typ"):
        pv.render("extract", product="gold", page_type="gold_appraisal", fields=[FieldDef("net_weight_g", "x")],
                  telugu=False, examples=[], page=PAGE)


def test_an_edited_release_refuses_to_load(prompts_copy: Path) -> None:
    path = version_dir("extraction", "2.0.0", prompts_copy)
    recorded = content_hash(path)
    partial = path / "partials" / "_unsure.j2"
    partial.write_text(partial.read_text(encoding="utf-8").replace("Never guess a digit.", ""), encoding="utf-8")
    with pytest.raises(PromptError, match="edited after release"):
        load("extraction", "2.0.0", expected_sha256=recorded, root=prompts_copy)


def test_crlf_checkout_does_not_change_the_hash(prompts_copy: Path) -> None:
    path = version_dir("extraction", "2.0.0", prompts_copy)
    before = content_hash(path)
    for f in path.rglob("*.j2"):
        f.write_bytes(f.read_bytes().replace(b"\n", b"\r\n"))
    assert content_hash(path) == before


def test_meta_must_match_its_directory(prompts_copy: Path) -> None:
    meta = version_dir("extraction", "1.1.0", prompts_copy) / "meta.toml"
    meta.write_text(meta.read_text(encoding="utf-8").replace('version = "1.1.0"', 'version = "1.0.0"'), encoding="utf-8")
    with pytest.raises(PromptError, match="meta.toml"):
        load("extraction", "1.1.0", root=prompts_copy)
