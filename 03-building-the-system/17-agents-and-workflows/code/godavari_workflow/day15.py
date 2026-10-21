"""Day 15's retrieval service, imported by path, as one read-only tool for the planner.

The planner may look up the policy clause behind an address-proof finding, as the analyst who will approve
the draft, through Day 15's permission-aware search. It runs with that analyst's groups, never with the
workflow's service account (which has none, Day 6 finding A1), and it fails closed on a stale snapshot.
"""

from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path

DAY15_CODE = Path(__file__).resolve().parents[3] / "15-retrieval-for-enterprise-documents" / "code"
if not (DAY15_CODE / "godavari_retrieval" / "service.py").exists():          # pragma: no cover - layout check
    raise ImportError(f"Day 15's retrieval package was not found at {DAY15_CODE}; Day 17 imports it by path")

sys.dont_write_bytecode = True
if str(DAY15_CODE) not in sys.path:
    sys.path.append(str(DAY15_CODE))

from godavari_retrieval.chunking import chunk_corpus  # noqa: E402
from godavari_retrieval.corpus import AS_OF as CORPUS_AS_OF  # noqa: E402
from godavari_retrieval.corpus import build_corpus  # noqa: E402
from godavari_retrieval.directory_data import SNAPSHOT_2, members  # noqa: E402
from godavari_retrieval.permissions import POLICY_TYPES, Directory, SearchFilter, StaleDirectoryError  # noqa: E402
from godavari_retrieval.service import RetrievalService  # noqa: E402

POLICY_FILTER = SearchFilter(as_of=CORPUS_AS_OF, doc_types=POLICY_TYPES)


@lru_cache(maxsize=1)
def policy_service() -> RetrievalService:
    """Day 15's corpus, chunks and the 26 November 02:00 group snapshot, built once per process."""
    docs, _ = build_corpus()
    directory = Directory(SNAPSHOT_2, {u: frozenset(g) for u, g in members(True).items()}, "2026-11-26")
    return RetrievalService(chunk_corpus(docs), directory)


__all__ = ["DAY15_CODE", "POLICY_FILTER", "StaleDirectoryError", "policy_service"]
