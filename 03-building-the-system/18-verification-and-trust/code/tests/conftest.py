"""Shared fixtures. The golden rows and the pilot week are built once per test session (well under a second each)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

CODE = Path(__file__).resolve().parents[1]
if str(CODE) not in sys.path:
    sys.path.insert(0, str(CODE))

from godavari_review import bands as B  # noqa: E402
from godavari_review import pilot  # noqa: E402
from godavari_review.evidence import FieldEvidence, golden_rows  # noqa: E402


@pytest.fixture(scope="session")
def policy() -> dict:
    return B.load_policy()


@pytest.fixture(scope="session")
def rows() -> list[FieldEvidence]:
    return golden_rows()


@pytest.fixture(scope="session")
def dev(rows: list[FieldEvidence]) -> list[FieldEvidence]:
    return [r for r in rows if r.split == "dev"]


@pytest.fixture(scope="session")
def test_rows(rows: list[FieldEvidence]) -> list[FieldEvidence]:
    return [r for r in rows if r.split == "test"]


@pytest.fixture(scope="session")
def fitted(dev, test_rows, policy):
    bands = B.fit(dev, policy)
    summary = B.confirm(test_rows, bands, policy)
    return bands, summary


@pytest.fixture(scope="session")
def week(fitted, policy):
    bands, _summary = fitted
    w = pilot.build_week(bands, policy, "bands under test")
    return pilot.simulate(w, policy)
