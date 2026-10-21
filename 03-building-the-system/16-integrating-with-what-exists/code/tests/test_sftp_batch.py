"""The 02:00 drop: manifests, partial files, late files, re-runs and re-scans."""

from __future__ import annotations

import hashlib
from datetime import date
from pathlib import Path

import pytest

from godavari_integration import synth_sources as ss
from godavari_integration.sftp_batch import (DropFile, LocalFolderSource, PickupLedger, complete_partial, pickup,
                                             synthetic_pdf, write_region_drop)

NIGHT = date(2026, 11, 12)


@pytest.fixture
def drops(facts) -> list[DropFile]:
    return ss.drop_files(sorted(ss.night_files(facts), key=lambda f: f.file_no)[:5])


def _tree_hash(root: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(root.rglob("*")):
        if p.is_file():
            h.update(p.name.encode() + p.read_bytes())
    return h.hexdigest()


def test_no_done_marker_means_no_reading(tmp_path, drops):
    write_region_drop(tmp_path / "src", "HYD", NIGHT, drops, write_done=False)
    rep = pickup(LocalFolderSource(tmp_path / "src"), "HYD", NIGHT, tmp_path / "stage", PickupLedger())
    assert not rep.ready and rep.items == []


def test_partial_files_are_held_and_picked_on_the_next_poll(tmp_path, drops):
    src, ledger = tmp_path / "src", PickupLedger()
    write_region_drop(src, "HYD", NIGHT, drops, partial=[drops[1].file_no])
    first = pickup(LocalFolderSource(src), "HYD", NIGHT, tmp_path / "stage", ledger)
    assert first.count("PICKED") == 4 and first.count("PARTIAL") == 1
    complete_partial(src, "HYD", NIGHT, drops[1])
    second = pickup(LocalFolderSource(src), "HYD", NIGHT, tmp_path / "stage", ledger)
    assert second.count("PICKED") == 1 and second.count("ALREADY_PICKED") == 4


def test_late_files_are_never_processed_without_a_manifest_line(tmp_path, drops):
    late = [DropFile("GF-25035", "DSN02", synthetic_pdf("GF-25035", ["late"]), 1)]
    write_region_drop(tmp_path / "src", "HYD", NIGHT, drops, late=late)
    rep = pickup(LocalFolderSource(tmp_path / "src"), "HYD", NIGHT, tmp_path / "stage", PickupLedger())
    assert [i.file_no for i in rep.items if i.status == "LATE"] == ["GF-25035"]
    assert not list((tmp_path / "stage").glob("GF-25035*"))


def test_a_rerun_is_a_no_op(tmp_path, drops):
    src, ledger = tmp_path / "src", PickupLedger()
    write_region_drop(src, "HYD", NIGHT, drops)
    pickup(LocalFolderSource(src), "HYD", NIGHT, tmp_path / "stage", ledger)
    again = pickup(LocalFolderSource(src), "HYD", NIGHT, tmp_path / "stage", ledger)
    assert again.count("ALREADY_PICKED") == len(drops) and not again.picked()


def test_a_rescan_is_a_new_version_of_the_same_file(tmp_path, drops):
    src, ledger = tmp_path / "src", PickupLedger()
    write_region_drop(src, "HYD", NIGHT, drops)
    pickup(LocalFolderSource(src), "HYD", NIGHT, tmp_path / "stage", ledger)
    d = drops[0]
    rescan = DropFile(d.file_no, d.branch_cd, d.content.replace(b"%%EOF", b"%% page added\n%%EOF"), d.pages + 1)
    write_region_drop(src, "HYD", date(2026, 11, 13), [rescan])
    rep = pickup(LocalFolderSource(src), "HYD", date(2026, 11, 13), tmp_path / "stage", ledger)
    [item] = rep.items
    assert item.status == "RESCAN" and "same application" in item.detail and ledger.versions(d.file_no) == 2


def test_same_size_wrong_bytes_is_corrupt(tmp_path, drops):
    src = tmp_path / "src"
    folder = write_region_drop(src, "HYD", NIGHT, drops)
    victim = next(folder.glob(f"{drops[2].file_no}_*.pdf"))
    data = bytearray(victim.read_bytes())
    data[20] = (data[20] + 1) % 256
    victim.write_bytes(bytes(data))
    rep = pickup(LocalFolderSource(src), "HYD", NIGHT, tmp_path / "stage", PickupLedger())
    assert rep.count("CORRUPT") == 1 and rep.count("PICKED") == 4


def test_a_listed_file_that_never_arrived_is_missing(tmp_path, drops):
    folder = write_region_drop(tmp_path / "src", "HYD", NIGHT, drops)
    next(folder.glob(f"{drops[3].file_no}_*.pdf")).unlink()
    rep = pickup(LocalFolderSource(tmp_path / "src"), "HYD", NIGHT, tmp_path / "stage", PickupLedger())
    assert rep.count("MISSING") == 1


def test_pickup_never_changes_their_folder_and_leaves_no_half_files(tmp_path, drops):
    src = tmp_path / "src"
    write_region_drop(src, "HYD", NIGHT, drops, partial=[drops[0].file_no])
    before = _tree_hash(src)
    pickup(LocalFolderSource(src), "HYD", NIGHT, tmp_path / "stage", PickupLedger())
    assert _tree_hash(src) == before
    assert not list((tmp_path / "stage").glob(".*part"))
    for staged in (tmp_path / "stage").glob("*.pdf"):
        assert staged.read_bytes().rstrip().endswith(b"%%EOF")


def test_a_manifest_with_the_wrong_columns_is_an_error(tmp_path, drops):
    folder = write_region_drop(tmp_path / "src", "HYD", NIGHT, drops)
    m = folder / f"MANIFEST_HYD_{NIGHT:%Y%m%d}.csv"
    m.write_text("name,size\nx.pdf,1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="unexpected columns"):
        pickup(LocalFolderSource(tmp_path / "src"), "HYD", NIGHT, tmp_path / "stage", PickupLedger())
