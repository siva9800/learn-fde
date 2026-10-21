"""Command line for the prompt package. Run from code/: python -X utf8 -m godavari_prompts.cli <command>

  versions                         list prompt versions on disk with their summaries
  lint [VERSION ...]               static checks (all versions if none given); exit 1 on any error
  verify                           registry checks: hashes, approvals, pins; exit 1 on any problem
  status                           what runs in dev, pilot and production
  diff OLD NEW                     unified diff of two versions, every file, for the pull request
  explain --env ENV --product P    the compliance head's document for the release pinned in ENV
  rollback --env ENV --by WHO --reason TEXT
                                   re-pin the previous release in ENV and record why
"""

from __future__ import annotations

import argparse
import difflib
import sys
import time
from datetime import datetime

from .explain import explain
from .lint import lint
from .loader import available_versions, load, version_dir
from .registry import Registry, RegistryError


def diff_versions(prompt_id: str, old: str, new: str) -> str:
    a_dir, b_dir = version_dir(prompt_id, old), version_dir(prompt_id, new)
    names = sorted({p.relative_to(a_dir).as_posix() for p in a_dir.rglob("*") if p.is_file()}
                   | {p.relative_to(b_dir).as_posix() for p in b_dir.rglob("*") if p.is_file()})
    chunks: list[str] = []
    for name in names:
        a, b = a_dir / name, b_dir / name
        a_lines = a.read_text(encoding="utf-8").splitlines(keepends=True) if a.is_file() else []
        b_lines = b.read_text(encoding="utf-8").splitlines(keepends=True) if b.is_file() else []
        chunks += difflib.unified_diff(a_lines, b_lines, fromfile=f"{old}/{name}" if a_lines else "/dev/null",
                                       tofile=f"{new}/{name}" if b_lines else "/dev/null", n=1)
    return "".join(chunks)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="godavari_prompts")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("versions")
    p_lint = sub.add_parser("lint")
    p_lint.add_argument("versions", nargs="*")
    sub.add_parser("verify")
    sub.add_parser("status")
    p_diff = sub.add_parser("diff")
    p_diff.add_argument("old")
    p_diff.add_argument("new")
    p_exp = sub.add_parser("explain")
    p_exp.add_argument("--env", default="pilot")
    p_exp.add_argument("--product", default="two-wheeler")
    p_rb = sub.add_parser("rollback")
    p_rb.add_argument("--env", required=True)
    p_rb.add_argument("--by", required=True)
    p_rb.add_argument("--reason", required=True)
    p_rb.add_argument("--prompt", default="extraction")
    args = ap.parse_args(argv)

    if args.cmd == "versions":
        for v in available_versions("extraction"):
            pv = load("extraction", v)
            print(f"extraction@{v:<7} {pv.strategy:<22} {pv.meta['author']:<16} {pv.meta['summary'][:70]}")
        return 0
    if args.cmd == "lint":
        bad = 0
        for v in args.versions or available_versions("extraction"):
            rep = lint(load("extraction", v))
            print(f"{rep.ref}: {len(rep.errors)} error(s), {len(rep.warnings)} warning(s)")
            for e in rep.errors:
                print(f"  ERROR   {e}")
            for w in rep.warnings:
                print(f"  WARNING {w}")
            bad += len(rep.errors)
        return 1 if bad else 0
    reg = Registry.load()
    if args.cmd == "verify":
        problems = reg.verify()
        print("registry verified: every hash, approval and pin checks out" if not problems else "\n".join(problems))
        return 1 if problems else 0
    if args.cmd == "status":
        for env, pins in reg.environments.items():
            print(f"{env:<11} " + (", ".join(f"{k} -> {v}" for k, v in pins.items()) or "(nothing pinned)"))
        return 0
    if args.cmd == "diff":
        print(diff_versions("extraction", args.old, args.new), end="")
        return 0
    if args.cmd == "explain":
        rel = reg.current(args.env, "extraction")
        if rel is None:
            print(f"nothing pinned in {args.env}")
            return 1
        print(explain(rel, load(rel.prompt_id, rel.version, expected_sha256=rel.content_sha256), args.product), end="")
        return 0
    if args.cmd == "rollback":
        start = time.perf_counter()
        try:
            restored = reg.rollback(args.env, args.prompt, by=args.by, at=datetime.now().isoformat(timespec="seconds"),
                                    reason=args.reason)
        except RegistryError as exc:
            print(f"refused: {exc}")
            return 1
        reg.save()
        print(f"{args.env}: {args.prompt} -> {restored} ({(time.perf_counter() - start) * 1000:.0f} ms); "
              "commit prompts/registry.json and open the incident note")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
