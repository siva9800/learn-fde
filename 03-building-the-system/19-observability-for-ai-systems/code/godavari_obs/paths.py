"""Reach the earlier chapters by path. Nothing from them is copied into this one.

Day 11 owns the pipeline and the rules, Day 12 the client and the cost ledger, Day 13 the prompt registry, Day 14 the
golden set and its metrics, Day 15 retrieval and its view log, Day 16 the integration journal and the write window,
Day 18 the review queue, the correction record and the rubber-stamp signals. Day 17's audit log is read as data if it
is on disk. This chapter wraps their code and reads their outputs; it writes into none of their folders, and no bytecode
lands there because of this chapter.
"""

from __future__ import annotations

import sys
from pathlib import Path

CHAPTER = Path(__file__).resolve().parents[2]
PART = CHAPTER.parent
CODE = CHAPTER / "code"
DATA = CHAPTER / "data"

DAY11_CODE = PART / "11-the-system-around-the-model" / "code"
DAY12_CODE = PART / "12-llm-apis-for-production" / "code"
DAY13_CODE = PART / "13-prompts-as-code" / "code"
DAY14_CODE = PART / "14-evals-first" / "code"
DAY14_DATA = PART / "14-evals-first" / "data"
DAY15_CODE = PART / "15-retrieval-for-enterprise-documents" / "code"
DAY15_DATA = PART / "15-retrieval-for-enterprise-documents" / "data"
DAY16_CODE = PART / "16-integrating-with-what-exists" / "code"
DAY16_DATA = PART / "16-integrating-with-what-exists" / "data"
DAY17_DATA = PART / "17-agents-and-workflows" / "data"          # optional: read as data when present
DAY18_CODE = PART / "18-verification-and-trust" / "code"
DAY18_DATA = PART / "18-verification-and-trust" / "data"

_NEEDED = (
    (DAY11_CODE / "intake" / "pipeline.py", "Day 11's intake package"),
    (DAY12_CODE / "godavari_llm" / "ledger.py", "Day 12's provider-neutral client"),
    (DAY13_CODE / "godavari_prompts" / "registry.py", "Day 13's prompt registry"),
    (DAY14_CODE / "evals" / "harness.py", "Day 14's evals package"),
    (DAY15_CODE / "godavari_retrieval" / "service.py", "Day 15's retrieval package"),
    (DAY16_CODE / "godavari_integration" / "journal.py", "Day 16's integration package"),
    (DAY18_CODE / "godavari_review" / "pilot.py", "Day 18's review package"),
)
for _need, _what in _NEEDED:
    if not _need.exists():
        raise ImportError(f"{_what} is not at {_need.parent}; this chapter imports it by path (FOLDERS.md)")

sys.dont_write_bytecode = True
for _p in (DAY18_CODE, DAY11_CODE, DAY12_CODE, DAY13_CODE, DAY14_CODE, DAY15_CODE, DAY16_CODE):
    if str(_p) not in sys.path:
        sys.path.append(str(_p))
