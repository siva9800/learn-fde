"""Reach Day 11, Day 14 and Day 15 by path. Nothing from those chapters is copied into this one.

Day 11 owns the system (model interface, envelope, signed rules, routing). Day 14 owns the golden set, its
labels and the metric code. Day 15 owns the policy corpus and clause-level citations. This chapter reads all
three and writes into none of them: no bytecode is written into their folders because of this chapter.
"""

from __future__ import annotations

import sys
from pathlib import Path

CHAPTER = Path(__file__).resolve().parents[2]
PART = CHAPTER.parent
DAY11_CODE = PART / "11-the-system-around-the-model" / "code"
DAY14_CODE = PART / "14-evals-first" / "code"
DAY15_CODE = PART / "15-retrieval-for-enterprise-documents" / "code"
DATA = CHAPTER / "data"
CODE = CHAPTER / "code"

for _need, _what in ((DAY11_CODE / "intake" / "pipeline.py", "Day 11's intake package"),
                     (DAY14_CODE / "evals" / "harness.py", "Day 14's evals package"),
                     (DAY15_CODE / "godavari_retrieval" / "corpus.py", "Day 15's retrieval package")):
    if not _need.exists():
        raise ImportError(f"{_what} is not at {_need.parent}; this chapter imports it by path (FOLDERS.md)")

sys.dont_write_bytecode = True
for _p in (DAY11_CODE, DAY14_CODE, DAY15_CODE):
    if str(_p) not in sys.path:
        sys.path.append(str(_p))
