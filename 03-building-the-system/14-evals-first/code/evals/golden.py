"""Choose the golden set: 200 labelled files, stratified, split into 50 development and 150 test files.

Where the files come from. Day 7's generator stands in for Godavari's file store: one call with a new seed
and 2,400 files is one synthetic month of applications (Day 4's volume). Only the two products with signed
or reviewed rules (two-wheeler and gold) are eligible. Each file gets a new number in the GF-4xxxx range,
so no golden file can be one of the 200 files Day 7 and Day 11 developed against.

How they are chosen. A quota per branch and product, with the pilot branches (Kukatpally and Guntur)
over-sampled, and inside each quota the hard cases weighted up: phone photos, Telugu, files that were
sent back (Day 6: "deliberately not the clean files"). Weighted sampling without replacement, seeded.

The test split is the golden set the harness scores. The development split is the only place few-shot
examples and threshold tuning may come from; it includes the thirty files labelled at M05.
"""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass, replace
from typing import Any

from .day11 import DAY11_CODE  # noqa: F401  (puts Day 11 on the path)
from intake.catalogue import LoanBundle
from intake.day7_inputs import DAY7_SAMPLE_SIZE, DAY7_SEED, load_day7_module
from intake.synth import GroundTruth, build_file

POOL_SEED = 14
POOL_SIZE = 2400            # one synthetic month: Day 4's "about 2,400 applications a month"
SELECT_SEED = 1414
ID_BASE = 40000             # GF-40000 onwards; Day 7's sample is GF-25000 to GF-25199
PRODUCTS = ("two-wheeler", "gold")
PILOT_BRANCHES = ("Kukatpally", "Guntur")

# (branch, product) -> files, for each split. Test: 100 two-wheeler + 50 gold; development: 34 + 16.
TEST_QUOTA: dict[tuple[str, str], int] = {}
DEV_QUOTA: dict[tuple[str, str], int] = {}
for _b in ("Kukatpally", "Guntur", "Dilsukhnagar", "Vijayawada-Benz Circle", "Warangal", "Rajahmundry"):
    pilot = _b in PILOT_BRANCHES
    TEST_QUOTA[(_b, "two-wheeler")] = 24 if pilot else 13
    TEST_QUOTA[(_b, "gold")] = 11 if pilot else 7
    DEV_QUOTA[(_b, "two-wheeler")] = 9 if pilot else 4
    DEV_QUOTA[(_b, "gold")] = 4 if pilot else 2

HARD_CASE_WEIGHT = {"phone_photo": 2.5, "mixed": 1.3, "sftp_scan": 1.0,
                    "telugu": 1.6, "english": 1.0, "sent_back": 1.5}


@dataclass(frozen=True)
class GoldenFile:
    file_id: str
    split: str                  # "test" (the golden set) or "dev"
    product: str
    branch: str
    channel: str
    language: str
    pages: int
    row: Any                    # Day 7's LoanFile, re-numbered

    @property
    def pilot(self) -> str:
        return "pilot" if self.branch in PILOT_BRANCHES else "other"

    def build(self) -> tuple[LoanBundle, GroundTruth]:
        """The scanned file and the generator's hidden truth. Day 11's synth, called, not copied."""
        return build_file(self.row)


def pool() -> list[Any]:
    """One synthetic month from Day 7's generator, eligible products only, re-numbered GF-4xxxx."""
    day7 = load_day7_module()
    files = day7.make_loan_files(POOL_SIZE, random.Random(POOL_SEED))
    return [replace(f, file_id=f"GF-{ID_BASE + i:05d}") for i, f in enumerate(files) if f.product in PRODUCTS]


def day7_sample_ids() -> set[str]:
    day7 = load_day7_module()
    return {f.file_id for f in day7.make_loan_files(DAY7_SAMPLE_SIZE, random.Random(DAY7_SEED))}


def _weight(row: Any) -> float:
    w = HARD_CASE_WEIGHT[row.channel]
    w *= HARD_CASE_WEIGHT["telugu"] if row.language_mix == "telugu" else (1.2 if row.language_mix == "mixed" else 1.0)
    if row.sent_back:
        w *= HARD_CASE_WEIGHT["sent_back"]
    return w


def _draw(rows: list[Any], quota: dict[tuple[str, str], int], rng: random.Random) -> list[Any]:
    """Weighted sampling without replacement inside each cell (the Efraimidis-Spirakis key u ** (1/w))."""
    chosen: list[Any] = []
    for (branch, product), k in quota.items():
        cell = [r for r in rows if r.branch == branch and r.product == product]
        if len(cell) < k:
            raise ValueError(f"only {len(cell)} {product} files from {branch} in the pool; quota is {k}")
        keyed = sorted(cell, key=lambda r: rng.random() ** (1.0 / _weight(r)), reverse=True)
        chosen.extend(keyed[:k])
    return sorted(chosen, key=lambda r: r.file_id)


def select() -> tuple[list[GoldenFile], list[GoldenFile]]:
    """(test, dev). Test is drawn first, so the golden set does not depend on the development split."""
    rows = pool()
    rng = random.Random(SELECT_SEED)
    test_rows = _draw(rows, TEST_QUOTA, rng)
    taken = {r.file_id for r in test_rows}
    dev_rows = _draw([r for r in rows if r.file_id not in taken], DEV_QUOTA, rng)

    def wrap(r: Any, split: str) -> GoldenFile:
        return GoldenFile(r.file_id, split, r.product, r.branch, r.channel, r.language_mix, r.pages, r)

    return [wrap(r, "test") for r in test_rows], [wrap(r, "dev") for r in dev_rows]


def bundle_sha256(bundle: LoanBundle) -> str:
    """A fingerprint of the file the labellers saw. The harness refuses to score a file whose pages changed."""
    h = hashlib.sha256()
    for p in bundle.pages:
        h.update(f"{p.number}|{int(p.handwritten)}|{int(p.telugu)}|".encode() + p.text.encode("utf-8") + b"\n")
    return h.hexdigest()
