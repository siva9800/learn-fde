"""One full run per test session, into a temporary folder (about ten seconds). The committed data/ is compared with it."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

CODE = Path(__file__).resolve().parents[1]
if str(CODE) not in sys.path:
    sys.path.insert(0, str(CODE))

import run_observability  # noqa: E402


@pytest.fixture(scope="session")
def out(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return tmp_path_factory.mktemp("day19-run")


@pytest.fixture(scope="session")
def run(out: Path) -> dict[str, Any]:
    return run_observability.main(out, quiet=True)


@pytest.fixture(scope="session")
def store(run: dict[str, Any]) -> Any:
    return run["store"]
