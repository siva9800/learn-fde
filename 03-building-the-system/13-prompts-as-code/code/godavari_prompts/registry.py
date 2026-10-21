"""The prompt registry: which prompt version runs where, with which model, on what evidence, approved by whom.

One JSON file in the repository (`prompts/registry.json`), changed only by pull request, so that every
change to what runs in pilot has a diff and a reviewer. It holds three things:

- releases: a release is a prompt version *paired with* the model snapshots it was evaluated with, the
  content hash of its files, the eval score that justified it, the author, the approver and the
  compliance head's read. The same prompt on a new model snapshot is a new release.
- environments: dev, pilot, production, each pinning one release per prompt id.
- history: every promotion and rollback, with who, when and why. Rollback walks this history.

The runtime reads the registry per batch, not at build time, which is what makes a rollback a one-line
change that takes effect on the next file instead of a redeploy.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .gate import compare_evals
from .loader import PROMPTS_DIR, content_hash, version_dir

REGISTRY_PATH = PROMPTS_DIR / "registry.json"
ENVIRONMENTS = ("dev", "pilot", "production")
SNAPSHOT_RE = re.compile(r"^[a-z0-9-]+-\d{4}-\d{2}$")   # a dated snapshot; "-latest" and bare names fail


class RegistryError(Exception):
    """The registry refuses: the reasons are in the message, one per line."""


@dataclass
class Release:
    release_id: str
    prompt_id: str
    version: str
    content_sha256: str
    models: dict[str, str]
    output_schema: str
    author: str
    created: str
    summary: str
    eval: dict[str, Any] | None = None
    approved_by: str | None = None
    compliance_read_by: str | None = None
    notes: list[str] = field(default_factory=list)


def release_id(prompt_id: str, version: str, models: dict[str, str]) -> str:
    return f"{prompt_id}@{version}+{models.get('large', '-')}"


class Registry:
    def __init__(self, data: dict[str, Any] | None = None, path: Path = REGISTRY_PATH,
                 prompts_root: Path = PROMPTS_DIR) -> None:
        data = data or {"schema": "godavari-prompt-registry/1", "releases": {},
                        "environments": {env: {} for env in ENVIRONMENTS}, "history": []}
        self.path = path
        self.root = prompts_root
        self.schema: str = data["schema"]
        self.releases: dict[str, Release] = {k: Release(**v) for k, v in data["releases"].items()}
        self.environments: dict[str, dict[str, str]] = data["environments"]
        self.history: list[dict[str, Any]] = data["history"]

    # --- persistence --------------------------------------------------------------------------------
    @classmethod
    def load(cls, path: Path = REGISTRY_PATH, prompts_root: Path = PROMPTS_DIR) -> Registry:
        return cls(json.loads(path.read_text(encoding="utf-8")), path, prompts_root)

    def to_dict(self) -> dict[str, Any]:
        return {"schema": self.schema, "releases": {k: asdict(v) for k, v in self.releases.items()},
                "environments": self.environments, "history": self.history}

    def save(self, path: Path | None = None) -> Path:
        target = path or self.path
        target.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8",
                          newline="\n")
        return target

    # --- releases -----------------------------------------------------------------------------------
    def add_release(self, rel: Release) -> Release:
        problems = []
        if rel.release_id in self.releases:
            problems.append(f"{rel.release_id} already exists; a release is never edited, make a new one")
        for tier, model in rel.models.items():
            if not SNAPSHOT_RE.match(model):
                problems.append(f"{tier} model {model!r} is not a dated snapshot; pin the snapshot, not an alias")
        actual = content_hash(version_dir(rel.prompt_id, rel.version, self.root))
        if actual != rel.content_sha256:
            problems.append(f"content hash mismatch for {rel.prompt_id}@{rel.version}")
        if problems:
            raise RegistryError("\n".join(problems))
        self.releases[rel.release_id] = rel
        return rel

    def record_eval(self, rid: str, evaluation: dict[str, Any]) -> None:
        self.releases[rid].eval = evaluation

    def approve(self, rid: str, by: str) -> None:
        rel = self.releases[rid]
        if by == rel.author:
            raise RegistryError(f"{by} wrote {rid} and cannot approve it; a second engineer reviews the diff")
        if rel.eval is None:
            raise RegistryError(f"{rid} has no eval score; nobody approves a prompt without one")
        rel.approved_by = by

    def compliance_read(self, rid: str, by: str) -> None:
        self.releases[rid].compliance_read_by = by

    # --- environments -------------------------------------------------------------------------------
    def current(self, env: str, prompt_id: str) -> Release | None:
        rid = self.environments[env].get(prompt_id)
        return self.releases[rid] if rid else None

    def promote(self, env: str, rid: str, *, by: str, at: str, reason: str) -> None:
        rel = self.releases[rid]
        problems: list[str] = []
        if content_hash(version_dir(rel.prompt_id, rel.version, self.root)) != rel.content_sha256:
            problems.append(f"{rel.prompt_id}@{rel.version} files changed after release")
        if rel.eval is None:
            problems.append("no eval score recorded")
        if env in ("pilot", "production"):
            if not rel.approved_by:
                problems.append("not approved by a second engineer")
            if not rel.compliance_read_by:
                problems.append("the compliance head has not read what the system is told to do")
        if env == "production" and not any(e["env"] == "pilot" and e["to"] == rid and e["action"] == "promote"
                                           for e in self.history):
            problems.append("never ran in pilot")
        if any(e["env"] == env and e["action"] == "rollback" and e["from"] == rid for e in self.history):
            problems.append(f"{rid} was rolled back in {env}; fix it as a new version, do not re-promote it")
        cur = self.current(env, rel.prompt_id)
        if cur and cur.release_id == rid:
            problems.append(f"{rid} is already current in {env}")
        if cur and cur.eval and rel.eval and env != "dev":
            if cur.eval["set_sha256"] != rel.eval["set_sha256"]:
                problems.append("candidate and current were scored on different eval sets; score both on one")
            else:
                problems += [f"regression vs {cur.release_id}: {r}" for r in compare_evals(rel.eval, cur.eval)]
        if problems:
            raise RegistryError(f"promotion of {rid} to {env} refused:\n  - " + "\n  - ".join(problems))
        self.environments[env][rel.prompt_id] = rid
        self.history.append({"at": at, "env": env, "prompt_id": rel.prompt_id, "action": "promote",
                             "from": cur.release_id if cur else None, "to": rid, "by": by, "reason": reason})

    def rollback(self, env: str, prompt_id: str, *, by: str, at: str, reason: str) -> str:
        """Re-pin the release that was current before the current one. Returns the restored release id."""
        cur = self.current(env, prompt_id)
        if cur is None:
            raise RegistryError(f"nothing is pinned for {prompt_id} in {env}")
        previous = next((e["from"] for e in reversed(self.history)
                         if e["env"] == env and e["prompt_id"] == prompt_id and e["action"] == "promote"
                         and e["to"] == cur.release_id), None)
        if previous is None:
            raise RegistryError(f"{cur.release_id} has no predecessor in {env}; there is nothing to roll back to")
        prev = self.releases[previous]
        if content_hash(version_dir(prev.prompt_id, prev.version, self.root)) != prev.content_sha256:
            raise RegistryError(f"{previous} files are missing or changed; it cannot be restored")
        self.environments[env][prompt_id] = previous
        self.history.append({"at": at, "env": env, "prompt_id": prompt_id, "action": "rollback",
                             "from": cur.release_id, "to": previous, "by": by, "reason": reason})
        return previous

    # --- checks -------------------------------------------------------------------------------------
    def verify(self) -> list[str]:
        """Everything a CI job checks on every pull request that touches prompts/ (an empty list is a pass)."""
        problems: list[str] = []
        for rid, rel in self.releases.items():
            path = version_dir(rel.prompt_id, rel.version, self.root)
            if not path.is_dir():
                problems.append(f"{rid}: version directory is missing")
            elif content_hash(path) != rel.content_sha256:
                problems.append(f"{rid}: files edited after release (hash mismatch)")
            if rel.approved_by and rel.approved_by == rel.author:
                problems.append(f"{rid}: approved by its own author")
            for tier, model in rel.models.items():
                if not SNAPSHOT_RE.match(model):
                    problems.append(f"{rid}: {tier} model {model!r} is an alias, not a snapshot")
        for env, pins in self.environments.items():
            for pid, rid in pins.items():
                rel = self.releases.get(rid)
                if rel is None:
                    problems.append(f"{env}/{pid}: pinned release {rid} does not exist")
                elif env in ("pilot", "production") and not (rel.approved_by and rel.compliance_read_by):
                    problems.append(f"{env}/{pid}: {rid} runs without approval or compliance read")
        return problems
