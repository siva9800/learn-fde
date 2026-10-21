"""The other records the dashboards read, and what each may contribute: counts, never content.

  Day 16  the write journal and the reconciliation history: write states, clean nights before live writes
  Day 17  the workflow's audit log, if it is on disk: approvals asked, decided, escalated, refused; how long they
          waited; tool calls per drafting run against the step budget. The log names people and carries their notes
          ("branch manager on leave"); it needs to, as an audit record. The dashboard needs none of that.
  Day 18  the correction events Day 18 wrote "for Day 19": they carry the model's value and the analyst's value, which
          is right for the golden set and wrong for a trace store. `day18_events_at_the_boundary` shows what the
          boundary does to them.

Each upstream file is also scanned with the same detectors as the trace store, and the result is reported as a count
per kind. Day 16 proved its journal carries no identifiers; this keeps proving it every night.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime
from statistics import median
from typing import Any

from . import paths
from .redact import RedactionReport, admit, pii_hits
from godavari_integration.journal import Journal


def day16_summary() -> dict[str, Any]:
    path = paths.DAY16_DATA / "kaagaz" / "journal.sqlite"
    journal = Journal(path)
    rows = journal.all()
    text = "\n".join(json.dumps([r.key, r.file_no, r.branch_cd, r.state, r.business, r.note]) for r in rows)
    events = "\n".join(str(x) for x in journal.conn.execute("SELECT * FROM events"))
    journal.conn.close()
    hist_path = paths.DAY16_DATA / "reconciliation-history.csv"
    history = list(csv.DictReader(hist_path.open(encoding="utf-8")))
    clean = 0
    for h in reversed(history):
        if h["clean"] != "yes":
            break
        clean += 1
    return {"writes": len(rows), "states": dict(Counter(r.state for r in rows)),
            "pii_kinds": sorted(set(pii_hits(text + "\n" + events))), "nights": len(history), "clean_run": clean,
            "last_night": history[-1]["date"] if history else "-"}


def day17_summary() -> dict[str, Any] | None:
    path = paths.DAY17_DATA / "audit-log.jsonl"
    if not path.exists():
        return None
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    kinds = Counter(r.get("kind") for r in rows)
    asked: dict[str, datetime] = {}
    waits: list[float] = []
    runs: list[tuple[int, int]] = []          # (tool calls, step budget) per drafting run
    current: dict[str, list[int]] = {}
    for r in rows:
        d = r.get("detail") or {}
        at = datetime.fromisoformat(r["at"])
        if r.get("kind") == "approval_requested" and "approval_id" in d:
            asked[d["approval_id"]] = at
        elif r.get("kind") == "approval_decided" and d.get("approval_id") in asked:
            waits.append((at - asked[d["approval_id"]]).total_seconds() / 60)
        elif r.get("kind") == "planner_started":
            if r["file_id"] in current:
                runs.append(tuple(current.pop(r["file_id"])))  # type: ignore[arg-type]
            current[r["file_id"]] = [0, int((d.get("budget") or {}).get("steps", 0))]
        elif r.get("kind") == "tool_called" and r.get("actor") == "planner" and r["file_id"] in current:
            current[r["file_id"]][0] += 1
    runs += [tuple(v) for v in current.values()]  # type: ignore[misc]
    return {"events": len(rows), "files": len({r["file_id"] for r in rows}),
            "approvals_requested": kinds["approval_requested"], "approvals_decided": kinds["approval_decided"],
            "approvals_escalated": kinds["approval_escalated"], "approvals_refused": kinds["approval_refused"],
            "wait_median_min": round(median(waits), 1) if waits else None, "wait_max_min": round(max(waits), 1) if waits else None,
            "planner_runs": len(runs), "max_tool_calls": max((c for c, _ in runs), default=0),
            "step_budget": max((b for _, b in runs), default=0), "core_written": kinds["core_written"],
            "pii_kinds": sorted(set(pii_hits(path.read_text(encoding="utf-8"))))}


def day18_events_at_the_boundary() -> dict[str, Any]:
    """Feed Day 18's correction events, exactly as written, through the boundary as if someone had logged them raw."""
    path = paths.DAY18_DATA / "pilot-week-1" / "corrections.jsonl"
    events = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    report = RedactionReport()
    stored = quarantined = 0
    for e in events:
        raw = {f"kaagaz.feedback.{k}" if k in ("field", "reason", "band", "stratum") else k: v for k, v in e.items()}
        ok = admit("review", raw, [], report)
        stored += ok is not None
        quarantined += ok is None
    with_values = sum(1 for e in events if e.get("model_value") or e.get("analyst_value"))
    return {"events": len(events), "with_values": with_values, "pii_kinds": sorted(set(pii_hits(path.read_text(encoding="utf-8")))),
            "stored": stored, "quarantined": quarantined, "dropped": dict(sorted(report.dropped.items()))}


def upstream_scan() -> dict[str, list[str]]:
    """Identifier kinds found in each upstream record. Inside the boundary these are expected; in a log they are not."""
    out: dict[str, list[str]] = {}
    for label, path in (("Day 12 night per file (CSV)", paths.PART / "12-llm-apis-for-production" / "data" / "night-per-file.csv"),
                        ("Day 15 view log", paths.DAY15_DATA / "view-log.jsonl"),
                        ("Day 17 audit log", paths.DAY17_DATA / "audit-log.jsonl"),
                        ("Day 18 screen log (action-log.jsonl)", paths.DAY18_DATA / "pilot-week-1" / "action-log.jsonl"),
                        ("Day 18 corrections (corrections.jsonl)", paths.DAY18_DATA / "pilot-week-1" / "corrections.jsonl")):
        if path.exists():
            out[label] = sorted(set(pii_hits(path.read_text(encoding="utf-8"))))
    out["Day 16 write journal (journal.sqlite)"] = day16_summary()["pii_kinds"]
    return dict(sorted(out.items()))
