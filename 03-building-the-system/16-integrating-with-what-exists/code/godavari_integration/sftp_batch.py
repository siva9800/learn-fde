"""The nightly SFTP batch: picking up the 02:00 drop without trusting it.

Godavari's side (simulated by write_region_drop): at 02:00 a job moves the day's branch scans into a
region folder, one PDF per file, writes a manifest (file name, file number, branch, bytes, SHA-256, pages),
and writes a .done marker last. Our side (pickup): a read-only account that never moves or deletes their
files, and these rules:

  1. No .done marker, no reading. A manifest being written is not a manifest.
  2. Only files the manifest lists are processed. A file on disk that is not listed is LATE: held for the
     next manifest, never guessed at.
  3. A listed file must match its size and hash, and end with a PDF trailer. Otherwise it is PARTIAL (still
     arriving, or broken in transfer) and is held; the next poll tries again.
  4. Picking up copies to our staging folder under a temporary name, checks the hash of the copy, then
     renames: a reader of staging never sees half a file.
  5. The pickup ledger is keyed on (file name, SHA-256). A re-run of the same night is a no-op. A re-scan
     of the same file number with new bytes is a new version of the documents, not a new application.

LocalFolderSource reads a folder (the stand-in, and how the skeleton runs on hand-copied masked files).
ParamikoSource (sftp_paramiko.py) reads the real SFTP server through the same three methods.
"""

from __future__ import annotations

import csv
import hashlib
import io
import os
import sqlite3
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Protocol

MANIFEST_COLUMNS = ["file_name", "file_no", "branch_cd", "bytes", "sha256", "pages"]
PDF_TRAILER = b"%%EOF"


class BatchSource(Protocol):
    def list_names(self, folder: str) -> list[str]: ...
    def size(self, path: str) -> int: ...
    def read_bytes(self, path: str) -> bytes: ...


class LocalFolderSource:
    def __init__(self, root: Path) -> None:
        self.root = Path(root)

    def list_names(self, folder: str) -> list[str]:
        p = self.root / folder
        return sorted(x.name for x in p.iterdir() if x.is_file()) if p.exists() else []

    def size(self, path: str) -> int:
        return (self.root / path).stat().st_size

    def read_bytes(self, path: str) -> bytes:
        return (self.root / path).read_bytes()


# ---- Godavari's side: the 02:00 job (simulated) -----------------------------------------------------------
def synthetic_pdf(file_no: str, pages: Iterable[str]) -> bytes:
    """Not a real PDF renderer: a PDF header, the synthetic page text, and the trailer. Enough to test what
    the pickup checks (size, hash, trailer); the page text is what Day 11's pipeline reads."""
    body = "".join(f"%% page {i}\n{text}\n" for i, text in enumerate(pages, 1))
    return f"%PDF-1.4\n%% {file_no} synthetic\n{body}".encode("utf-8") + PDF_TRAILER + b"\n"


@dataclass(frozen=True)
class DropFile:
    file_no: str
    branch_cd: str
    content: bytes
    pages: int


def drop_name(f: DropFile, night: date) -> str:
    return f"{f.file_no}_{f.branch_cd}_{night:%Y%m%d}.pdf"


def write_region_drop(root: Path, region: str, night: date, files: list[DropFile], *,
                      partial: Iterable[str] = (), late: list[DropFile] | None = None,
                      write_done: bool = True) -> Path:
    """What the 02:00 job leaves behind. `partial` file numbers are listed in full in the manifest but only
    half-written on disk; `late` files are on disk but arrived after the manifest was written."""
    folder = Path(root) / region / f"{night:%Y%m%d}"
    folder.mkdir(parents=True, exist_ok=True)
    partial = set(partial)
    rows = []
    for f in files:
        name = drop_name(f, night)
        data = f.content[: len(f.content) // 2] if f.file_no in partial else f.content
        (folder / name).write_bytes(data)
        rows.append([name, f.file_no, f.branch_cd, len(f.content), hashlib.sha256(f.content).hexdigest(), f.pages])
    manifest = folder / f"MANIFEST_{region}_{night:%Y%m%d}.csv"
    tmp = manifest.with_suffix(".tmp")
    with tmp.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(MANIFEST_COLUMNS)
        w.writerows(rows)
    os.replace(tmp, manifest)
    for f in late or []:
        (folder / drop_name(f, night)).write_bytes(f.content)
    if write_done:
        (folder / f"MANIFEST_{region}_{night:%Y%m%d}.done").write_text("", encoding="utf-8")
    return folder


def complete_partial(root: Path, region: str, night: date, f: DropFile) -> None:
    """The transfer finishes: the rest of the bytes arrive."""
    (Path(root) / region / f"{night:%Y%m%d}" / drop_name(f, night)).write_bytes(f.content)


# ---- our side: the pickup ------------------------------------------------------------------------------
class PickupLedger:
    def __init__(self, path: Path | str = ":memory:") -> None:
        self.conn = sqlite3.connect(str(path))
        self.conn.execute("CREATE TABLE IF NOT EXISTS picked (file_name TEXT, sha256 TEXT, file_no TEXT, "
                          "version INTEGER, night TEXT, staged_as TEXT, PRIMARY KEY (file_name, sha256))")

    def seen(self, file_name: str, sha256: str) -> bool:
        return self.conn.execute("SELECT 1 FROM picked WHERE file_name = ? AND sha256 = ?",
                                 (file_name, sha256)).fetchone() is not None

    def versions(self, file_no: str) -> int:
        return self.conn.execute("SELECT COUNT(*) FROM picked WHERE file_no = ?", (file_no,)).fetchone()[0]

    def record(self, file_name: str, sha256: str, file_no: str, night: str, staged_as: str) -> int:
        version = self.versions(file_no) + 1
        with self.conn:
            self.conn.execute("INSERT INTO picked VALUES (?, ?, ?, ?, ?, ?)",
                              (file_name, sha256, file_no, version, night, staged_as))
        return version


@dataclass
class PickupItem:
    file_name: str
    file_no: str
    status: str            # PICKED, RESCAN, ALREADY_PICKED, PARTIAL, MISSING, CORRUPT, LATE
    detail: str = ""
    sha256: str = ""
    staged: Path | None = None


@dataclass
class PickupReport:
    region: str
    night: date
    ready: bool
    items: list[PickupItem] = field(default_factory=list)
    manifest_rows: int = 0

    def count(self, status: str) -> int:
        return sum(1 for i in self.items if i.status == status)

    def picked(self) -> list[PickupItem]:
        return [i for i in self.items if i.status in ("PICKED", "RESCAN")]


def pickup(source: BatchSource, region: str, night: date, staging: Path, ledger: PickupLedger) -> PickupReport:
    folder = f"{region}/{night:%Y%m%d}"
    names = source.list_names(folder)
    manifest_name = f"MANIFEST_{region}_{night:%Y%m%d}.csv"
    report = PickupReport(region, night, ready=f"MANIFEST_{region}_{night:%Y%m%d}.done" in names)
    if not report.ready or manifest_name not in names:
        report.ready = False
        return report
    rows = list(csv.DictReader(io.StringIO(source.read_bytes(f"{folder}/{manifest_name}").decode("utf-8"))))
    if not rows or list(rows[0].keys()) != MANIFEST_COLUMNS:
        raise ValueError(f"{manifest_name}: unexpected columns {list(rows[0].keys()) if rows else []}")
    report.manifest_rows = len(rows)
    listed = set()
    staging.mkdir(parents=True, exist_ok=True)
    for row in rows:
        name, file_no = row["file_name"], row["file_no"]
        listed.add(name)
        if name not in names:
            report.items.append(PickupItem(name, file_no, "MISSING", "listed in the manifest, not on disk"))
            continue
        expected = int(row["bytes"])
        actual = source.size(f"{folder}/{name}")
        if actual != expected:
            report.items.append(PickupItem(name, file_no, "PARTIAL", f"{actual} of {expected} bytes; held for the next poll"))
            continue
        data = source.read_bytes(f"{folder}/{name}")
        digest = hashlib.sha256(data).hexdigest()
        if digest != row["sha256"] or not data.rstrip().endswith(PDF_TRAILER):
            report.items.append(PickupItem(name, file_no, "CORRUPT", "size matches, hash or PDF trailer does not"))
            continue
        if ledger.seen(name, digest):
            report.items.append(PickupItem(name, file_no, "ALREADY_PICKED", "re-run: nothing to do", digest))
            continue
        final = staging / f"{file_no}.{digest[:12]}.pdf"
        tmp = staging / f".{final.name}.part"
        tmp.write_bytes(data)
        if hashlib.sha256(tmp.read_bytes()).hexdigest() != digest:
            tmp.unlink()
            report.items.append(PickupItem(name, file_no, "CORRUPT", "copy did not match"))
            continue
        os.replace(tmp, final)                     # atomic on the same filesystem
        version = ledger.record(name, digest, file_no, f"{night:%Y%m%d}", final.name)
        status = "PICKED" if version == 1 else "RESCAN"
        detail = "" if version == 1 else f"version {version} of {file_no}: same application, new documents"
        report.items.append(PickupItem(name, file_no, status, detail, digest, final))
    for name in names:
        if name.lower().endswith(".pdf") and name not in listed:
            report.items.append(PickupItem(name, name.split("_")[0], "LATE",
                                           "on disk, not in the manifest: held for the next night's manifest"))
    return report
