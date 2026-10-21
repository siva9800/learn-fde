"""Reuse Day 7's synthetic sample by importing its generator by path. Nothing is copied.

Day 7's `code/inputs_inventory.py` builds 200 loan files from `random.Random(7)`. Calling its
`make_loan_files(200, random.Random(7))` here returns exactly the files in Day 7's
`data/godavari_loan_file_sample.csv`, so the two chapters talk about the same files (GF-25000 onwards).
"""

from __future__ import annotations

import importlib.util
import random
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

CHAPTER_DIR = Path(__file__).resolve().parents[2]
DAY7_GENERATOR = (
    CHAPTER_DIR.parents[1] / "02-discovery-and-decomposition" / "07-decomposition" / "code" / "inputs_inventory.py"
)
DAY7_SEED = 7       # Day 7's SEED constant; the same seed gives the same 200 files
DAY7_SAMPLE_SIZE = 200


def load_day7_module(path: Path = DAY7_GENERATOR) -> ModuleType:
    if not path.exists():
        raise FileNotFoundError(f"Day 7's generator is not at {path}; this chapter reuses it by path")
    name = "day7_inputs_inventory"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module          # dataclasses look the module up by name while the class is built
    writes_bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True      # read Day 7's folder, never write into it (no __pycache__ there)
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = writes_bytecode
    return module


def day7_sample() -> list[Any]:
    """The 200 LoanFile records of Day 7's two-week sample, in Day 7's order."""
    module = load_day7_module()
    return module.make_loan_files(DAY7_SAMPLE_SIZE, random.Random(DAY7_SEED))
