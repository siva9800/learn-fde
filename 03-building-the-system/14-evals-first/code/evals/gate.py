"""The regression gate: a prompt, model, chunking or retrieval change cannot merge if the golden set says
it made things worse anywhere that matters.

It compares the candidate's run with the stored baseline run from main, field by field on the same files
(a paired comparison, so file-to-file variety cancels out), in every stratum the policy names. It fails on:

  1. the registered bar: overall field-level accuracy below the business case's floor (Day 9, risk R2);
  2. completeness: any incomplete file the signed rules no longer flag (the compliance head's "no misses");
  3. regressions: in any stratum, fields that went right-to-wrong outnumber wrong-to-right by at least
     `min_net_regressions` AND a fair coin would rarely do that (exact one-sided test, `paired_alpha`);
  4. confident wrong: in any stratum, more than `max_new_confident_wrong` newly confident-wrong fields
     beyond those the candidate fixed.

The thresholds are set above the noise floor measured on the development split (an unchanged model
re-run), never tuned on the test split, and they change only with the eval owners' agreement.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .stats import paired_worse_p

POLICY_PATH = Path(__file__).resolve().parents[1] / "gate_policy.json"


@dataclass
class Check:
    rule: str
    stratum: str
    passed: bool
    detail: str


def load_policy(path: Path = POLICY_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _key(r: dict[str, Any]) -> tuple[str, str]:
    return r["file_id"], r["field"]


def _correct(r: dict[str, Any]) -> bool:
    return r["status"] in ("correct", "correct_flagged")


def _strata(r: dict[str, Any], names: list[str]) -> list[str]:
    return ["all"] + [f"{n}={r[n]}" for n in names]


def paired_changes(base: list[dict[str, Any]], cand: list[dict[str, Any]], names: list[str]) -> dict[str, dict[str, int]]:
    """Per stratum: fields, regressions (right to wrong), fixes (wrong to right), new and resolved confident wrongs."""
    b = {_key(r): r for r in base}
    out: dict[str, dict[str, int]] = {}
    for r in cand:
        old = b[_key(r)]
        for s in _strata(r, names):
            c = out.setdefault(s, {"fields": 0, "base_correct": 0, "cand_correct": 0, "regressions": 0, "fixes": 0,
                                   "new_cw": 0, "resolved_cw": 0})
            c["fields"] += 1
            c["base_correct"] += _correct(old)
            c["cand_correct"] += _correct(r)
            c["regressions"] += _correct(old) and not _correct(r)
            c["fixes"] += _correct(r) and not _correct(old)
            new_cw, old_cw = r["status"] == "confident_wrong", old["status"] == "confident_wrong"
            c["new_cw"] += new_cw and not old_cw
            c["resolved_cw"] += old_cw and not new_cw
    return dict(sorted(out.items(), key=lambda kv: (kv[0] != "all", kv[0])))


def compare(base: list[dict[str, Any]], cand: list[dict[str, Any]], cand_summary: dict[str, Any],
            policy: dict[str, Any], base_summary: dict[str, Any] | None = None) -> list[Check]:
    checks: list[Check] = []
    if {_key(r) for r in base} != {_key(r) for r in cand}:
        return [Check("same golden set", "all", False,
                      "the candidate was scored on different files or fields than the baseline; re-baseline first")]
    if base_summary is not None and base_summary.get("truth_sha256") != cand_summary.get("truth_sha256"):
        return [Check("same golden set", "all", False,
                      "the baseline was scored against a different version of the truth file; re-baseline first")]
    bar = policy["registered_bar"]["overall_field_accuracy_min"]
    acc = cand_summary["overall"]["accuracy"]
    checks.append(Check("registered bar", "all", acc >= bar, f"accuracy {acc:.1%} against the floor {bar:.0%}"))
    rec = cand_summary["overall"]["completeness_recall"]
    need = policy["completeness_recall_min"]
    checks.append(Check("completeness recall", "all", rec >= need,
                        f"{rec:.1%} ({cand_summary['overall']['completeness_misses']} incomplete files not flagged)"))
    for stratum, c in paired_changes(base, cand, policy["strata"]).items():
        net = c["regressions"] - c["fixes"]
        p = paired_worse_p(c["regressions"], c["fixes"])
        worse = net >= policy["min_net_regressions"] and p < policy["paired_alpha"]
        drop = (c["base_correct"] - c["cand_correct"]) / c["fields"] * 100
        checks.append(Check("regressions", stratum, not worse,
                            f"{c['regressions']} right-to-wrong, {c['fixes']} wrong-to-right of {c['fields']} "
                            f"fields ({drop:+.1f} points lost), p={p:.4f}"))
        cw_net = c["new_cw"] - c["resolved_cw"]
        checks.append(Check("confident wrong", stratum, cw_net <= policy["max_new_confident_wrong"],
                            f"{c['new_cw']} new, {c['resolved_cw']} resolved (net {cw_net:+d})"))
    return checks


def average_only(base_summary: dict[str, Any], cand_summary: dict[str, Any], max_drop_points: float) -> Check:
    """The gate most teams start with: fail only if the overall average drops by more than N points."""
    drop = (base_summary["overall"]["accuracy"] - cand_summary["overall"]["accuracy"]) * 100
    return Check("average only", "all", drop <= max_drop_points,
                 f"overall accuracy {base_summary['overall']['accuracy']:.1%} -> "
                 f"{cand_summary['overall']['accuracy']:.1%} ({-drop:+.1f} points)")


def noise_floor(base: list[dict[str, Any]], rerun: list[dict[str, Any]], names: list[str]) -> dict[str, int]:
    """The biggest movement an unchanged model shows between two runs, in any stratum."""
    changes = paired_changes(base, rerun, names).values()
    return {"max_net_regressions": max(c["regressions"] - c["fixes"] for c in changes),
            "max_net_new_confident_wrong": max(c["new_cw"] - c["resolved_cw"] for c in changes)}
