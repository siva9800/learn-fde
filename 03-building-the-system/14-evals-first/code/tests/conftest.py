"""Shared fixtures. The golden set is built once per test session, in memory, from the same code the scripts run."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

CODE_DIR = Path(__file__).resolve().parent.parent
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from evals import candidates, harness  # noqa: E402
from evals.golden import select  # noqa: E402
from evals.labels import label_all  # noqa: E402


@pytest.fixture(scope="session")
def split():
    return select()


@pytest.fixture(scope="session")
def labelset(split):
    test, dev = split
    return label_all(test + dev)


@pytest.fixture(scope="session")
def truth(labelset, split):
    test, dev = split
    out = {}
    for gf in test + dev:
        out[gf.file_id] = {**labelset.final[gf.file_id].to_json(), "split": gf.split}
    return out


@pytest.fixture(scope="session")
def baseline_run(split, truth):
    return harness.run(candidates.build("baseline"), split[0], truth)


@pytest.fixture(scope="session")
def baseline_rows(baseline_run):
    return harness.field_records(baseline_run)
