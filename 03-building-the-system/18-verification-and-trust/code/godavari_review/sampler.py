"""Spot checks of auto-accepted fields: which approved files get a blind second read, and what it has proved so far.

The draw is a keyed hash of the file number, so it is reproducible by the compliance head and the auditor (who hold
the key) and unpredictable to the analyst approving the file (who does not see it, and is not told until after the
approval). A fixed share per branch, with a floor, plus every file from a session the stamping detector suspected.

The second read is blind: Lakshmi or the senior analyst sees the page, not the value, and keys the auto-accepted
fields. A disagreement goes to the two team leads (Day 14's adjudication rule 2) before anyone calls it an error.
"""

from __future__ import annotations

import hashlib
import math
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass

from evals.stats import wilson

SHARE = 0.10
MIN_PER_BRANCH = 3


def draw_key(key: str, file_id: str) -> float:
    """A number in [0, 1) from the key and the file number: same inputs, same draw, on any machine."""
    return int(hashlib.sha256(f"{key}|{file_id}".encode()).hexdigest()[:12], 16) / 16 ** 12


@dataclass(frozen=True)
class Pick:
    file_id: str
    branch: str
    why: str


def sample(approved: Iterable[tuple[str, str]], key: str, targeted: set[str] = frozenset(),
           share: float = SHARE, floor: int = MIN_PER_BRANCH) -> list[Pick]:
    """approved: (file_id, branch) of files approved with at least one auto-accepted field."""
    by_branch: dict[str, list[str]] = defaultdict(list)
    for fid, branch in approved:
        by_branch[branch].append(fid)
    picks: list[Pick] = []
    for branch, fids in sorted(by_branch.items()):
        ranked = sorted(fids, key=lambda f: draw_key(key, f))
        n = min(len(ranked), max(floor, math.ceil(share * len(ranked))))
        picks += [Pick(f, branch, "random") for f in ranked[:n]]
        picks += [Pick(f, branch, "targeted: suspected session") for f in ranked[n:] if f in targeted]
    return sorted(picks, key=lambda p: p.file_id)


def fields_to_detect(rate: float, power: float = 0.95) -> int:
    """How many fields a check must cover to see at least one error, with probability `power`, if the true error
    rate is `rate`: n = ln(1 - power) / ln(1 - rate)."""
    return math.ceil(math.log(1 - power) / math.log(1 - rate))


def proved_so_far(checked: int, wrong: int) -> tuple[float, float]:
    return wilson(wrong, checked)
