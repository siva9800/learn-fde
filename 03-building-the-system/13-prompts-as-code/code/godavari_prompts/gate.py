"""The promotion gate: does a candidate release do worse than the one it replaces, field by field?

This is a regression check, not an evaluation method. Day 14 owns evals: the golden set, its slices,
labelling, judges and the statistics of a small sample. The gate only answers "on the same labelled
files, did any field get fewer right answers or more wrong ones?", which is the question a prompt pull
request must answer before it merges.
"""

from __future__ import annotations

from typing import Any

CORRECT_DROP_ALLOWED = 1   # files per field; on 12 files, one file is already 8 points. Day 14 does better.
WRONG_RISE_ALLOWED = 0     # a confident wrong value is what the compliance head fears; no new ones


def compare_evals(candidate: dict[str, Any], baseline: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    for fld, base in baseline["per_field"].items():
        cand = candidate["per_field"].get(fld)
        if cand is None:
            problems.append(f"{fld}: not scored")
            continue
        if base["correct"] - cand["correct"] > CORRECT_DROP_ALLOWED:
            problems.append(f"{fld}: correct {base['correct']} -> {cand['correct']} of {base['n']}")
        if cand["wrong"] - base["wrong"] > WRONG_RISE_ALLOWED:
            problems.append(f"{fld}: wrong {base['wrong']} -> {cand['wrong']} of {base['n']}")
    return problems
