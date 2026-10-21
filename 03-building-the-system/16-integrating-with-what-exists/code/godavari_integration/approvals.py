"""The analysts' approvals for the night: which files they approve and with which values.

Day 11 routed each file. The analysts approve the files routed ready or review; for a review file the
analyst corrects the flagged fields, and in this synthetic world the corrected values are the ground
truth Day 11's generator kept. Nothing here decides anything a person would not.
"""

from __future__ import annotations

from typing import Any

from . import synth_sources as ss
from .canonical import canonical_from_day11
from .day11 import Route
from .translate import Mapping


def approved_records(facts: dict[str, ss.FileFacts], mapping: Mapping, entry_user: str,
                     approved_by: str = "GF-AN-1142") -> list[tuple[ss.FileFacts, dict[str, Any]]]:
    """The files the analysts approve on Thursday: Day 11 routed them ready or review; for review files the
    analyst's corrected values are the synthetic ground truth."""
    out = []
    for f in sorted(ss.night_files(facts), key=lambda x: x.file_no):
        if f.result.route not in (Route.READY_FOR_APPROVAL, Route.REVIEW):
            continue
        assert f.result.output is not None
        approved = {k: v.value for k, v in f.result.output.fields.items() if v.value}
        if f.result.route == Route.REVIEW:
            approved.update(f.truth.fields)
        rec = canonical_from_day11(f.result, f.bundle, approved, approved_by=approved_by,
                                   state=ss.STATE_BY_BRANCH[f.bundle.branch], entry_user=entry_user,
                                   mapping_version=mapping.version)
        out.append((f, rec))
    return out
