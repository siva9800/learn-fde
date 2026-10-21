"""Where the golden set lives on disk, and how it is read back. Plain CSV and JSON Lines, UTF-8, LF."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

CHAPTER = Path(__file__).resolve().parents[2]
DATA = CHAPTER / "data"
GOLDEN = DATA / "golden"
MANIFEST = GOLDEN / "manifest.csv"
TRUTH = GOLDEN / "truth-adjudicated.jsonl"
LABELS_A = GOLDEN / "labels-lakshmi.jsonl"
LABELS_B = GOLDEN / "labels-senior-analyst.jsonl"
ADJ_LOG = GOLDEN / "adjudication-log.csv"
FEWSHOT = DATA / "fewshot-examples.json"


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def write_csv(path: Path, header: list[str], rows: list[list[Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def read_manifest(path: Path = MANIFEST) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip("\n") + "\n", encoding="utf-8", newline="\n")


def load_truth(path: Path = TRUTH) -> dict[str, dict[str, Any]]:
    return {r["file_id"]: r for r in read_jsonl(path)}


def truth_sha256(path: Path = TRUTH) -> str:
    """The truth file's version, as a fingerprint. Scores from different truth files are never compared."""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
