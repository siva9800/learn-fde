"""Shared fixtures: the corpus, both chunkings, the 25 November snapshot and the service, built once."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from godavari_retrieval.chunking import chunk_corpus  # noqa: E402
from godavari_retrieval.corpus import build_corpus  # noqa: E402
from godavari_retrieval.directory_data import SNAPSHOT_1, SNAPSHOT_2, members  # noqa: E402
from godavari_retrieval.permissions import Directory  # noqa: E402
from godavari_retrieval.service import NaivePostFilterService, RetrievalService  # noqa: E402

NOW = datetime(2026, 11, 25, 11, 0)


@pytest.fixture(scope="session")
def corpus():
    return build_corpus()


@pytest.fixture(scope="session")
def docs(corpus):
    return corpus[0]


@pytest.fixture(scope="session")
def chunks(docs):
    return chunk_corpus(docs)


@pytest.fixture(scope="session")
def naive_chunks(docs):
    return chunk_corpus(docs, "naive")


@pytest.fixture(scope="session")
def day1() -> Directory:
    return Directory(SNAPSHOT_1, {u: frozenset(g) for u, g in members(False).items()}, "day1")


@pytest.fixture(scope="session")
def day2() -> Directory:
    return Directory(SNAPSHOT_2, {u: frozenset(g) for u, g in members(True).items()}, "day2")


@pytest.fixture(scope="session")
def svc(chunks, day1) -> RetrievalService:
    return RetrievalService(chunks, day1)


@pytest.fixture(scope="session")
def naive_svc(chunks, day1) -> NaivePostFilterService:
    return NaivePostFilterService(chunks, day1)


@pytest.fixture()
def now() -> datetime:
    return NOW
