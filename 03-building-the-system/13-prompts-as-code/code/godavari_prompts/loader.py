"""Load a prompt version from disk, check its variables, and render it.

A prompt version is a directory: `prompts/<prompt_id>/<version>/` holding `meta.toml` (what the version
is, which calls it makes, the variables each call takes and their types) and Jinja2 templates, including
its own partials. A released version is immutable: its content hash is recorded in the registry, and a
version whose files no longer match that hash refuses to load. To change a prompt you copy the version
directory, edit the copy and bump the version; the old one stays on disk so a rollback has something to
roll back to.
"""

from __future__ import annotations

import hashlib
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined, meta as jinja_meta

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


class PromptError(Exception):
    """A prompt cannot be loaded or rendered as written. Never caught and ignored."""


@dataclass(frozen=True)
class PageView:
    """What a template may know about a page: its number and its OCR text. Never the true type."""

    number: int
    text: str

    @property
    def head(self) -> str:
        """The first lines only: enough to classify a page, a fraction of the tokens."""
        return "\n".join(self.text.splitlines()[:6])


@dataclass(frozen=True)
class FieldDef:
    name: str
    description: str


@dataclass
class PromptVersion:
    prompt_id: str
    version: str
    path: Path
    meta: dict[str, Any]
    env: Environment = field(repr=False)

    @property
    def ref(self) -> str:
        return f"{self.prompt_id}@{self.version}"

    @property
    def strategy(self) -> str:
        return str(self.meta["strategy"])

    def call(self, name: str) -> dict[str, Any]:
        try:
            return dict(self.meta["calls"][name])
        except KeyError as exc:
            raise PromptError(f"{self.ref} has no call named {name!r}") from exc

    def field_defs(self, names: list[str] | tuple[str, ...]) -> list[FieldDef]:
        described = self.meta["fields"]
        missing = [n for n in names if n not in described]
        if missing:
            raise PromptError(f"{self.ref}: no description for field(s) {missing}")
        return [FieldDef(n, described[n]) for n in names]

    def render(self, call: str, **variables: Any) -> tuple[str, str]:
        """Render one call's system and user templates. Returns (system, user)."""
        spec = self.call(call)
        check_variables(self.ref, call, spec.get("variables", {}), variables)
        try:
            system = self.env.get_template(spec["system"]).render(**variables)
            user = self.env.get_template(spec["user"]).render(**variables)
        except Exception as exc:                       # StrictUndefined and template errors land here
            raise PromptError(f"{self.ref} call {call!r} failed to render: {exc}") from exc
        return _tidy(system), _tidy(user)


def _tidy(text: str) -> str:
    """Collapse the blank lines that template control blocks leave, so diffs stay readable."""
    out: list[str] = []
    for line in text.splitlines():
        if line.strip() == "" and out and out[-1] == "":
            continue
        out.append(line.rstrip())
    return "\n".join(out).strip() + "\n"


# --- typed variables -----------------------------------------------------------------------------------

def check_variables(ref: str, call: str, declared: dict[str, str], given: dict[str, Any]) -> None:
    """Every declared variable must be given with the declared type, and nothing undeclared may be passed.

    Types: str, int, bool, page, pages, fields, list, and enum:a|b|c. This is deliberately small: a
    template variable is an interface, and an interface with a type is one a reviewer can reason about.
    """
    problems: list[str] = []
    for name, kind in declared.items():
        if name not in given:
            problems.append(f"missing variable {name!r} ({kind})")
            continue
        value = given[name]
        ok = {
            "str": lambda v: isinstance(v, str),
            "int": lambda v: isinstance(v, int) and not isinstance(v, bool),
            "bool": lambda v: isinstance(v, bool),
            "page": lambda v: isinstance(v, PageView),
            "pages": lambda v: isinstance(v, (list, tuple)) and all(isinstance(p, PageView) for p in v),
            "fields": lambda v: isinstance(v, (list, tuple)) and all(isinstance(f, FieldDef) for f in v),
            "list": lambda v: isinstance(v, (list, tuple)),
        }.get(kind)
        if kind.startswith("enum:"):
            allowed = kind.removeprefix("enum:").split("|")
            if value not in allowed:
                problems.append(f"{name}={value!r} is not one of {allowed}")
        elif ok is None:
            problems.append(f"unknown type {kind!r} for {name!r}")
        elif not ok(value):
            problems.append(f"{name} should be {kind}, got {type(value).__name__}")
    extra = sorted(set(given) - set(declared))
    if extra:
        problems.append(f"undeclared variable(s) passed: {extra}")
    if problems:
        raise PromptError(f"{ref} call {call!r}: " + "; ".join(problems))


# --- loading and hashing -------------------------------------------------------------------------------

def version_dir(prompt_id: str, version: str, root: Path = PROMPTS_DIR) -> Path:
    return root / prompt_id / version


def content_hash(path: Path) -> str:
    """SHA-256 over every file in the version directory, by relative path, with line endings normalised.

    Normalising CRLF to LF matters on Windows: a Git checkout with autocrlf would otherwise change every
    hash and make every released version look tampered with.
    """
    h = hashlib.sha256()
    for f in sorted(p for p in path.rglob("*") if p.is_file() and "__pycache__" not in p.parts):
        h.update(f.relative_to(path).as_posix().encode("utf-8") + b"\0")
        h.update(f.read_bytes().replace(b"\r\n", b"\n") + b"\0")
    return h.hexdigest()


def load(prompt_id: str, version: str, *, expected_sha256: str | None = None,
         root: Path = PROMPTS_DIR) -> PromptVersion:
    path = version_dir(prompt_id, version, root)
    if not (path / "meta.toml").is_file():
        raise PromptError(f"no prompt {prompt_id}@{version} at {path}")
    if expected_sha256 is not None:
        actual = content_hash(path)
        if actual != expected_sha256:
            raise PromptError(f"{prompt_id}@{version} has been edited after release: "
                              f"hash {actual[:12]} != recorded {expected_sha256[:12]}")
    meta = tomllib.loads((path / "meta.toml").read_text(encoding="utf-8"))
    if meta.get("id") != prompt_id or meta.get("version") != version:
        raise PromptError(f"meta.toml at {path} says {meta.get('id')}@{meta.get('version')}")
    env = Environment(loader=FileSystemLoader(str(path)), undefined=StrictUndefined, autoescape=False,
                      trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True)
    return PromptVersion(prompt_id, version, path, meta, env)


def available_versions(prompt_id: str, root: Path = PROMPTS_DIR) -> list[str]:
    def key(v: str) -> tuple[int, ...]:
        return tuple(int(x) for x in v.split("."))
    return sorted((p.name for p in (root / prompt_id).iterdir() if (p / "meta.toml").is_file()), key=key)


def template_variables(pv: PromptVersion) -> set[str]:
    """Every variable any template in the version reads (Jinja's own parser, not a regex)."""
    names: set[str] = set()
    for f in pv.path.rglob("*.j2"):
        ast = pv.env.parse(f.read_text(encoding="utf-8"))
        names |= jinja_meta.find_undeclared_variables(ast)
    return names
