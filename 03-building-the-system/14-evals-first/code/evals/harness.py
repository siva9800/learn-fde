"""The eval harness: run Day 11's pipeline over the golden set and score it against the adjudicated truth.

Nothing here decides anything about a loan file. It calls `intake.pipeline.process()` exactly as production
does, keeps every field and every finding, and compares them with the truth file. Four things are measured:

  fields         per mandatory field: correct, correct but flagged, wrong but flagged, or confidently wrong
  documents      page classification, and which documents survived grounding, against the labels
  completeness   did a signed rule flag every file the compliance head's labels call incomplete (recall),
                 and were the flagged files really incomplete (precision); the same for "would send back"
  cost           seconds per file here; rupees per file come from Day 12's ledger when a real model runs

Every metric is reported overall and per stratum (product, branch, channel, language, pilot or not, field,
handwritten Telugu or not), with a 95 percent interval, because an average can hide a failing branch.
"""

from __future__ import annotations

import time
from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
from datetime import date
from typing import Any

from .day11 import RULESETS
from .golden import GoldenFile, bundle_sha256
from .labels import FIELD_SOURCE, printed_type, source_page
from .normalise import exact_equal, norm_equal
from .stats import cluster_bootstrap, wilson
from intake.model import ExtractionModel
from intake.pipeline import envelope, process
from intake.routing import MANDATORY_FIELDS, Route
from intake.ruleset import check_signoff

AS_OF = date(2026, 11, 30)          # Monday of week 6: the run that feeds the week-6 accuracy report (M12)
FILE_STRATA = ("product", "branch", "channel", "language", "pilot")
FIELD_STRATA = FILE_STRATA + ("field", "handwritten_telugu")


@dataclass
class FieldRow:
    file_id: str
    product: str
    branch: str
    channel: str
    language: str
    pilot: str
    field: str
    handwritten_telugu: str
    pred: str | None
    label: str | None
    confidence: float
    page: int | None
    label_page: int | None
    flagged: bool
    exact: bool
    status: str                     # correct, correct_flagged, wrong_flagged, confident_wrong
    route: str

    @property
    def correct(self) -> bool:
        return self.status in ("correct", "correct_flagged")


@dataclass
class FileRow:
    file_id: str
    product: str
    branch: str
    channel: str
    language: str
    pilot: str
    route: str
    true_missing: list[str]
    flagged_missing: list[str]
    send_back_truth: bool
    rule_raised: bool
    pages: int
    pages_right: int
    docs_true: list[str]
    docs_found: list[str]
    confident_wrong: int
    seconds: float
    branch_findings: list[tuple[str, str]] = field(default_factory=list)


@dataclass
class EvalRun:
    model_name: str
    fields: list[FieldRow]
    files: list[FileRow]
    seconds: float
    rules: list[str]


def field_status(name: str, pred: str | None, label: str | None, flagged: bool) -> str:
    """The four outcomes. 'confident_wrong' is the one that matters most: a wrong value nobody is told to check."""
    if norm_equal(name, pred, label):
        return "correct_flagged" if flagged else "correct"
    return "wrong_flagged" if flagged else "confident_wrong"


class LabelsChanged(RuntimeError):
    pass


def run(model: ExtractionModel, files: list[GoldenFile], truth: dict[str, dict[str, Any]],
        expected_sha: dict[str, str] | None = None, mode: str = "prototype") -> EvalRun:
    """Score one model (with Day 11's envelope and rules around it) on the golden set.

    `mode` is Day 11's: "prototype" runs reviewed or draft rules whose fingerprint matches the record; from M10
    (2 December 2026) the eval runs "pilot", which refuses any rule the compliance head has not signed."""
    rules = [check_signoff(rs, mode).banner for rs in RULESETS.values()]
    started = time.perf_counter()
    field_rows: list[FieldRow] = []
    file_rows: list[FileRow] = []
    for gf in files:
        t0 = time.perf_counter()
        bundle, _hidden = gf.build()                      # the hidden truth is never used to score
        if expected_sha is not None and bundle_sha256(bundle) != expected_sha[gf.file_id]:
            raise LabelsChanged(f"{gf.file_id}: the pages differ from the ones the analysts labelled")
        label = truth[gf.file_id]
        result = process(bundle, model, RULESETS[gf.product], AS_OF)
        out = result.output
        assert out is not None
        _env, documents, _unc = envelope(bundle, out)
        cw = 0
        for name in MANDATORY_FIELDS[gf.product]:
            fv = out.fields.get(name)
            pred = fv.value if fv else None
            flagged = any(f.field_name == name for f in result.findings)
            status = field_status(name, pred, label["fields"].get(name), flagged)
            cw += status == "confident_wrong"
            src = source_page(bundle, name)
            hwt = "yes" if src is not None and src.handwritten and src.telugu else "no"
            field_rows.append(FieldRow(
                gf.file_id, gf.product, gf.branch, gf.channel, gf.language, gf.pilot, name, hwt, pred,
                label["fields"].get(name), fv.confidence if fv else 0.0, fv.page if fv else None,
                src.number if src is not None and label["fields"].get(name) is not None else None, flagged,
                exact_equal(pred, label["fields"].get(name)), status, result.route.value))
        pages_right = sum(out.page_labels[p.number][0] == printed_type(p) for p in bundle.pages)
        file_rows.append(FileRow(
            gf.file_id, gf.product, gf.branch, gf.channel, gf.language, gf.pilot, result.route.value,
            list(label["missing"]),
            sorted({str(f.doc) for f in result.findings if "-DOC-" in f.rule_id and f.doc is not None}),
            bool(label["send_back"]),
            any(str(f.kind) in ("regulatory", "policy") for f in result.findings),
            len(bundle.pages), pages_right, list(label["documents"]), sorted(str(d) for d in documents), cw,
            time.perf_counter() - t0,
            [(f.rule_id, f.message) for f in result.findings if f.action.value in ("send_back", "block")]))
    return EvalRun(model.name, field_rows, file_rows, time.perf_counter() - started, rules)


# --- Summaries -----------------------------------------------------------------------------------------
def field_metrics(rows: list[FieldRow]) -> dict[str, Any]:
    n = len(rows)
    correct = sum(r.correct for r in rows)
    cw = sum(r.status == "confident_wrong" for r in rows)
    flagged = sum(r.flagged for r in rows)
    unflagged_right = sum(r.status == "correct" for r in rows)
    with_page = [r for r in rows if r.page is not None and r.label_page is not None]
    return {
        "fields": n,
        "correct": correct,
        "accuracy": correct / n if n else 0.0,
        "accuracy_ci": wilson(correct, n),
        "exact_accuracy": sum(r.exact for r in rows) / n if n else 0.0,
        "flagged_rate": flagged / n if n else 0.0,
        "confident_wrong": cw,
        "confident_wrong_rate": cw / n if n else 0.0,
        "confident_wrong_ci": wilson(cw, n),
        "unflagged_precision": unflagged_right / (unflagged_right + cw) if unflagged_right + cw else 1.0,
        "evidence_page_agreement": (sum(r.page == r.label_page for r in with_page) / len(with_page)
                                    if with_page else 1.0),
    }


def _pr(tp: int, fp: int, fn: int) -> tuple[float, float]:
    precision = tp / (tp + fp) if tp + fp else 1.0
    recall = tp / (tp + fn) if tp + fn else 1.0
    return precision, recall


def file_metrics(rows: list[FileRow]) -> dict[str, Any]:
    inc_true = [bool(r.true_missing) for r in rows]
    inc_flag = [bool(r.flagged_missing) for r in rows]
    tp = sum(t and f for t, f in zip(inc_true, inc_flag))
    fp = sum(f and not t for t, f in zip(inc_true, inc_flag))
    fn = sum(t and not f for t, f in zip(inc_true, inc_flag))
    c_prec, c_rec = _pr(tp, fp, fn)
    dtp = sum(len(set(r.true_missing) & set(r.flagged_missing)) for r in rows)
    dfp = sum(len(set(r.flagged_missing) - set(r.true_missing)) for r in rows)
    dfn = sum(len(set(r.true_missing) - set(r.flagged_missing)) for r in rows)
    d_prec, d_rec = _pr(dtp, dfp, dfn)
    stp = sum(r.send_back_truth and r.rule_raised for r in rows)
    sfp = sum(r.rule_raised and not r.send_back_truth for r in rows)
    sfn = sum(r.send_back_truth and not r.rule_raised for r in rows)
    s_prec, s_rec = _pr(stp, sfp, sfn)
    found_tp = sum(len(set(r.docs_true) & set(r.docs_found)) for r in rows)
    found_fp = sum(len(set(r.docs_found) - set(r.docs_true)) for r in rows)
    found_fn = sum(len(set(r.docs_true) - set(r.docs_found)) for r in rows)
    f_prec, f_rec = _pr(found_tp, found_fp, found_fn)
    pages = sum(r.pages for r in rows)
    return {
        "files": len(rows),
        "incomplete_files": sum(inc_true),
        "completeness_recall": c_rec, "completeness_precision": c_prec,
        "completeness_misses": fn, "completeness_false_flags": fp,
        "missing_doc_recall": d_rec, "missing_doc_precision": d_prec,
        "send_back_files": sum(r.send_back_truth for r in rows),
        "send_back_recall": s_rec, "send_back_precision": s_prec,
        "page_accuracy": sum(r.pages_right for r in rows) / pages if pages else 1.0,
        "doc_found_precision": f_prec, "doc_found_recall": f_rec,
        "files_with_confident_wrong": sum(r.confident_wrong > 0 for r in rows),
        "ready_files_with_confident_wrong": sum(r.confident_wrong > 0 and r.route == Route.READY_FOR_APPROVAL.value
                                                for r in rows),
        "routes": {route.value: sum(r.route == route.value for r in rows) for route in Route},
    }


def _groups(rows: Iterable[Any], key: str) -> dict[str, list[Any]]:
    out: dict[str, list[Any]] = {}
    for r in rows:
        out.setdefault(str(getattr(r, key)), []).append(r)
    return dict(sorted(out.items()))


def summarise(run_: EvalRun) -> dict[str, Any]:
    per_file = {}
    for r in run_.fields:
        k, n = per_file.get(r.file_id, (0, 0))
        per_file[r.file_id] = (k + r.correct, n + 1)
    per_file_cw = {}
    for r in run_.fields:
        k, n = per_file_cw.get(r.file_id, (0, 0))
        per_file_cw[r.file_id] = (k + (r.status == "confident_wrong"), n + 1)
    overall = {**field_metrics(run_.fields), **file_metrics(run_.files)}
    overall["accuracy_cluster_ci"] = cluster_bootstrap(list(per_file.values()))
    overall["confident_wrong_cluster_ci"] = cluster_bootstrap(list(per_file_cw.values()))
    strata: dict[str, dict[str, Any]] = {}
    for key in FIELD_STRATA:
        for value, rows in _groups(run_.fields, key).items():
            strata[f"{key}={value}"] = field_metrics(rows)
    for key in FILE_STRATA:
        for value, rows in _groups(run_.files, key).items():
            strata[f"{key}={value}"].update(file_metrics(rows))
    return {"model": run_.model_name, "as_of": AS_OF.isoformat(), "rules": run_.rules,
            "seconds": round(run_.seconds, 2), "overall": overall, "strata": strata}


def field_records(run_: EvalRun) -> list[dict[str, Any]]:
    """What the gate needs: one row per (file, field) with its strata and status."""
    return [{k: v for k, v in asdict(r).items() if k not in ("pred", "label")} for r in run_.fields]


# --- Reports -------------------------------------------------------------------------------------------
def report_lines(summary: dict[str, Any]) -> list[str]:
    o = summary["overall"]
    lo, hi = o["accuracy_ci"]
    clo, chi = o["accuracy_cluster_ci"]
    wlo, whi = o["confident_wrong_ci"]
    out = [f"model: {summary['model']} · as of {summary['as_of']} · {o['files']} golden files, {o['fields']} "
           f"mandatory field cells · {summary['seconds']:.2f} s"]
    out += [f"  {line}" for line in summary["rules"]]
    out.append("")
    out.append("-- headline (Day 9, section C) --")
    out.append(f"  field-level accuracy (normalised)   {o['accuracy']:6.1%}   95% {lo:.1%} to {hi:.1%} (fields), "
               f"{clo:.1%} to {chi:.1%} (files resampled)")
    out.append(f"  field-level accuracy (exact string) {o['exact_accuracy']:6.1%}")
    out.append(f"  confidently wrong (wrong, not flagged) {o['confident_wrong']:3d} = {o['confident_wrong_rate']:.2%}"
               f"   95% {wlo:.2%} to {whi:.2%}")
    out.append(f"  when a field is NOT flagged, it is right {o['unflagged_precision']:.2%} of the time")
    out.append(f"  fields flagged for review            {o['flagged_rate']:6.1%}")
    out.append(f"  completeness recall {o['completeness_recall']:.1%} ({o['completeness_misses']} misses of "
               f"{o['incomplete_files']} incomplete files) · precision {o['completeness_precision']:.1%} "
               f"({o['completeness_false_flags']} false flags)")
    out.append(f"  missing-document recall {o['missing_doc_recall']:.1%} · precision {o['missing_doc_precision']:.1%}")
    out.append(f"  send-back recall {o['send_back_recall']:.1%} · precision {o['send_back_precision']:.1%} "
               f"({o['send_back_files']} files the analysts would send back)")
    out.append(f"  page classification {o['page_accuracy']:.1%} · documents found: precision "
               f"{o['doc_found_precision']:.1%}, recall {o['doc_found_recall']:.1%}")
    out.append(f"  model cited the page the analyst used: {o['evidence_page_agreement']:.1%} of fields")
    out.append(f"  files with a confidently wrong field: {o['files_with_confident_wrong']} "
               f"({o['ready_files_with_confident_wrong']} of them routed ready_for_approval)")
    out.append("  routes: " + ", ".join(f"{k} {v}" for k, v in o["routes"].items()))
    out.append("")
    out.append("-- by stratum (accuracy with 95% Wilson interval; cw = confidently wrong fields) --")
    out.append(f"{'stratum':34s}{'files':>6s}{'fields':>7s}{'accuracy':>10s}{'95% interval':>17s}"
               f"{'cw':>5s}{'flagged':>9s}{'compl. recall':>15s}")
    for key, m in summary["strata"].items():
        if key.startswith("field="):
            continue
        a, b = m["accuracy_ci"]
        files = f"{m['files']:6d}" if "files" in m else f"{'':6s}"
        rec = f"{m['completeness_recall']:14.0%}" if "completeness_recall" in m else f"{'':>14s}"
        out.append(f"{key:34s}{files}{m['fields']:7d}{m['accuracy']:9.1%} {a:7.1%} to {b:6.1%}"
                   f"{m['confident_wrong']:5d}{m['flagged_rate']:8.0%} {rec}")
    out.append("")
    out.append("-- by field --")
    out.append(f"{'field':34s}{'fields':>13s}{'accuracy':>10s}{'95% interval':>17s}{'cw':>5s}{'flagged':>9s}")
    for key, m in summary["strata"].items():
        if not key.startswith("field="):
            continue
        a, b = m["accuracy_ci"]
        out.append(f"{key[6:]:34s}{m['fields']:13d}{m['accuracy']:9.1%} {a:7.1%} to {b:6.1%}"
                   f"{m['confident_wrong']:5d}{m['flagged_rate']:8.0%}")
    return out


def confident_wrong_lines(run_: EvalRun, threshold_of: Any) -> list[str]:
    """The senior analyst's report: the actual files, not a percentage (Day 6; change C4 in Day 10)."""
    rows = [r for r in run_.fields if r.status == "confident_wrong"]
    out = [f"{len(rows)} confidently wrong fields in {len({r.file_id for r in rows})} files "
           f"(model {run_.model_name}). Each one reached an analyst with nothing telling her to look.", ""]
    out.append("| file | product | branch | channel | language | field | model read | label | confidence | "
               "threshold | page (model / analyst) | route |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in sorted(rows, key=lambda x: (x.field, x.branch, x.file_id)):
        out.append(f"| {r.file_id} | {r.product} | {r.branch} | {r.channel} | {r.language} | {r.field} | "
                   f"`{r.pred}` | `{r.label}` | {r.confidence:.2f} | {threshold_of(r.field):.2f} | "
                   f"{r.page} / {r.label_page} | {r.route} |")
    return out


__all__ = ["AS_OF", "EvalRun", "FieldRow", "FileRow", "LabelsChanged", "run", "summarise", "field_records",
           "report_lines", "confident_wrong_lines", "field_status", "FIELD_SOURCE"]
