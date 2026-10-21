"""Static checks on a prompt version, run in CI on every pull request that touches prompts/.

Errors block the merge; warnings go into the pull request for a human to answer. The checks:

1. No business rule in a prompt (Day 6, RULES_AS_SIGNED_CODE): percentages, LTV, rupee thresholds,
   "approve", "reject", "eligible", "mandatory", "at least"... in any text the model will be shown.
   The rules live in code the compliance head signs (Day 11); a prompt that repeats one is a second,
   unsigned copy that will drift from the first.
2. Customer text only through the untrusted-page partials, so every page is wrapped and labelled as
   data (Day 41 owns prompt injection; this is the one structural habit it needs from day one).
3. No model names in templates: the release record pins the model, the prompt does not.
4. Variables: every variable a call's entry templates read is declared with a type in meta.toml;
   a declared variable no template reads is a warning (a removed feature, or a typo).
5. Every product in the enum has its variant partial, when the templates include one.
6. LF line endings only.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .loader import PromptVersion

RULE_PATTERNS: list[tuple[str, str]] = [
    (r"\b\d+(\.\d+)?\s*(percent|%)", "a percentage threshold"),
    (r"\bLTV\b|loan[- ]to[- ]value", "a loan-to-value rule"),
    (r"\bRs\.?\s?\d", "a rupee threshold"),
    (r"\b(approve|approved|reject|rejected|decline|declined)\b", "a decision word"),
    (r"\beligib\w*", "an eligibility rule"),
    (r"\bmandatory\b|\brequired documents?\b", "a document requirement"),
    (r"\b(at least|no more than|must not exceed|maximum of|minimum of)\b", "a limit"),
]
MODEL_NAMES = re.compile(r"\b(gpt-\w+|claude-\w+|gemini-\w+|llama-?\d\w*|fake-(small|large)-[\w-]+)\b", re.I)
PAGE_TEXT = re.compile(r"\bpage\.(text|head)\b")
LOOP_VAR = re.compile(r"{%-?\s*for\s+(\w+)\s+in\b")


@dataclass
class LintReport:
    ref: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def _shown_text(pv: PromptVersion) -> list[tuple[str, str]]:
    """Every piece of text the model can be shown: templates, plus the descriptions in meta.toml."""
    items = [(str(f.relative_to(pv.path).as_posix()), f.read_text(encoding="utf-8")) for f in pv.path.rglob("*.j2")]
    for name, desc in pv.meta.get("fields", {}).items():
        items.append((f"meta.toml [fields].{name}", desc))
    for name, spec in pv.meta.get("page_types", {}).items():
        items.append((f"meta.toml [page_types].{name}", spec["description"]))
    return items


def lint(pv: PromptVersion) -> LintReport:
    rep = LintReport(pv.ref)
    for where, text in _shown_text(pv):
        for pattern, what in RULE_PATTERNS:
            for m in re.finditer(pattern, text, re.I):
                rep.errors.append(f"{where}: {what} ({m.group(0)!r}); rules stay in signed code, not in prompts")
        if MODEL_NAMES.search(text):
            rep.errors.append(f"{where}: names a model; the release record pins models")
    for f in pv.path.rglob("*.j2"):
        rel = f.relative_to(pv.path).as_posix()
        raw = f.read_bytes()
        if b"\r\n" in raw:
            rep.errors.append(f"{rel}: CRLF line endings")
        if PAGE_TEXT.search(raw.decode("utf-8")) and not f.name.startswith("_untrusted_"):
            rep.errors.append(f"{rel}: renders page text outside the untrusted-page wrapper")

    # Variables, per call: what the entry templates read against what meta.toml declares.
    loop_vars: set[str] = set()
    partial_vars: set[str] = set()
    for f in pv.path.rglob("*.j2"):
        loop_vars |= set(LOOP_VAR.findall(f.read_text(encoding="utf-8")))
        if "partials" in f.parts or "products" in f.parts:
            partial_vars |= _reads(pv, f.relative_to(pv.path).as_posix())
    all_declared: set[str] = set()
    for call, spec in pv.meta["calls"].items():
        declared = set(spec.get("variables", {}))
        all_declared |= declared
        used = _reads(pv, spec["system"]) | _reads(pv, spec["user"])
        for name in sorted(used - declared):
            rep.errors.append(f"call {call!r} reads undeclared variable {name!r}")
        for name in sorted(declared - used - partial_vars):
            rep.warnings.append(f"call {call!r} declares {name!r} but no template reads it")
    for name in sorted(partial_vars - all_declared - loop_vars):
        rep.errors.append(f"a partial reads {name!r}, which no call declares")

    # Product variants.
    if any('"products/" ~ product' in f.read_text(encoding="utf-8") for f in pv.path.rglob("*.j2")):
        for call, spec in pv.meta["calls"].items():
            kind = spec.get("variables", {}).get("product", "")
            for product in kind.removeprefix("enum:").split("|") if kind.startswith("enum:") else []:
                if not (pv.path / "products" / f"{product}.j2").is_file():
                    rep.errors.append(f"product {product!r} has no variant at products/{product}.j2")
    return rep


def _reads(pv: PromptVersion, template: str) -> set[str]:
    from jinja2 import meta as jinja_meta
    source = (pv.path / template).read_text(encoding="utf-8")
    return set(jinja_meta.find_undeclared_variables(pv.env.parse(source)))
