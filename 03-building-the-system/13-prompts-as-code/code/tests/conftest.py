from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

CODE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CODE))

from godavari_prompts.fake_model import FakeProvider  # noqa: E402
from godavari_prompts.loader import PROMPTS_DIR, content_hash, load, version_dir  # noqa: E402
from godavari_prompts.model_port import Tier  # noqa: E402
from godavari_prompts.registry import Release, release_id  # noqa: E402

MODELS_1X = {"large": "fake-large-2026-10"}
MODELS_2X = {"small": "fake-small-2026-10", "large": "fake-large-2026-10"}


@pytest.fixture
def provider() -> FakeProvider:
    return FakeProvider({Tier.SMALL: "fake-small-2026-10", Tier.LARGE: "fake-large-2026-10"}, today="2026-11-12")


@pytest.fixture
def prompts_copy(tmp_path: Path) -> Path:
    """A scratch copy of prompts/ so a test can edit files without touching the real ones."""
    dst = tmp_path / "prompts"
    shutil.copytree(PROMPTS_DIR, dst, ignore=shutil.ignore_patterns("registry.json"))
    return dst


def make_release(version: str, root: Path = PROMPTS_DIR, models: dict[str, str] | None = None) -> Release:
    models = models or (MODELS_1X if version.startswith("1.") else MODELS_2X)
    pv = load("extraction", version, root=root)
    return Release(release_id("extraction", version, models), "extraction", version,
                   content_hash(version_dir("extraction", version, root)), models, pv.meta["output_schema"],
                   pv.meta["author"], pv.meta["created"], pv.meta["summary"])
