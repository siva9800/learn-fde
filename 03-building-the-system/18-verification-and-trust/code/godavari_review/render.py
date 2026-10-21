"""Static, self-contained, escaped HTML: one page per file and one queue page, plus the queue as CSV.

Every value on these pages came from a customer's document or from a model, so every value is untrusted text. The
environment escapes everything by default (autoescape=True, set explicitly: Jinja2's own default is off, and
select_autoescape(["html"]) does not cover a template named "*.html.j2"). StrictUndefined turns a misspelt variable
into an error instead of a blank cell. The pages load nothing: no script, no external stylesheet, no font, no image
URL, and a Content-Security-Policy that says so.
"""

from __future__ import annotations

import csv
import io
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from .bands import Band
from .labels import BAND_WORDS, LABELS_STATUS, label
from .queue import NEVER_BULK_ACTIONS, SAFE_BULK_ACTIONS, ReviewItem

TEMPLATES = Path(__file__).resolve().parent / "templates"
CSP = "default-src 'none'; style-src 'unsafe-inline'; img-src data:; form-action 'none'; base-uri 'none'"


def inr(value: int | None) -> str:
    """Indian digit grouping, as the forms print it: 124000 -> 'Rs 1,24,000'."""
    if value is None:
        return "-"
    s = str(int(value))
    head, tail = s[:-3], s[-3:]
    groups = []
    while len(head) > 2:
        groups.insert(0, head[-2:])
        head = head[:-2]
    return "Rs " + ",".join(([head] if head else []) + groups + [tail])


def environment() -> Environment:
    env = Environment(loader=FileSystemLoader(TEMPLATES), autoescape=True, undefined=StrictUndefined,
                      trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True)
    env.globals.update(label=label, BAND_WORDS=BAND_WORDS, Band=Band, CSP=CSP, LABELS_STATUS=LABELS_STATUS)
    env.filters["money"] = inr
    return env


def render_file(item: ReviewItem, record: dict[str, Any] | None = None) -> str:
    return environment().get_template("file.html").render(item=item, record=record)


def render_queue(items: list[ReviewItem], day: str, links: set[str]) -> str:
    return environment().get_template("queue.html").render(items=items, day=day, links=links,
                                                           safe_bulk=SAFE_BULK_ACTIONS, never_bulk=NEVER_BULK_ACTIONS)


def queue_csv(items: list[ReviewItem]) -> str:
    """The same rows as the queue page, for the analysts who will open it in Excel and sort it their own way."""
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["rank", "file_id", "branch", "arrived", "requested_amount", "route", "to_check", "to_key_in",
                "look_first", "why_here"])
    for i, it in enumerate(items, start=1):
        forced = it.forced
        w.writerow([i, it.file_id, it.branch, it.arrived.isoformat(timespec="minutes"), it.amount or "", it.route,
                    len([f for f in it.fields if f.band == Band.REVIEW]),
                    len([f for f in it.fields if f.band == Band.REJECT]), forced.row.field if forced else "", it.why])
    return buf.getvalue()


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip("\n") + "\n", encoding="utf-8", newline="\n")
