"""Week two's surprise, and the fix that shipped the day before the change freeze.

The surprise (synthetic, generated here): after week one's send-backs, Guntur's branch staff start attaching the
customer's full six-month net-banking statement instead of the bank's four-page summary. A net-banking printout
repeats the bank's header on every page, so every page looks like a bank statement: sixty of them in one file.

The fix: a deterministic page filter in front of the model. A statement page that says "Page k of N" with k of 2 or
more is a continuation page; it carries no field the extraction contract asks for (Day 12 extracts only the first
page of a statement run, and its own continuation rule breaks whenever one page in the run is misread). Continuation
pages are not sent to the model at all. The analyst still sees every page: the filter changes what the model is
shown, never what the file contains.
"""

from __future__ import annotations

import random
import re
from dataclasses import replace

from . import paths  # noqa: F401
from intake.catalogue import PAGE_TITLES, Doc, LoanBundle, Page

FILTER_NAME = "statement-continuation-v1"
STATEMENT_PAGES = 60
_CONT = re.compile(r"^Page (\d+) of (\d+)$", re.MULTILINE)
_TITLE = PAGE_TITLES[Doc.BANK_STATEMENT]


def lengthen_statement(bundle: LoanBundle, pages: int = STATEMENT_PAGES) -> LoanBundle:
    """Append the rest of a net-banking statement after the file's pages (tray order; a stapled block stays together).
    Original page numbers do not move, so every label and quote that pointed at a page still points at it."""
    main = next((p for p in bundle.pages if p.text.startswith(_TITLE) and "SAL CREDIT" in p.text),
                next((p for p in bundle.pages if p.text.startswith(_TITLE)), None))
    if main is None:
        return bundle
    head = [ln for ln in main.text.splitlines() if ln.startswith(("Bank:", "Account holder:", "Account number:"))]
    rng = random.Random(f"day19-statement-{bundle.file_id}")
    extra: list[Page] = []
    start = max(p.number for p in bundle.pages) + 1
    for k in range(2, pages + 1):
        lines = [f"{rng.randint(1, 28):02d}-{rng.randint(6, 9):02d} {rng.choice(['UPI DR', 'ATM WDL', 'NEFT DR', 'POS'])}"
                 f" {rng.choice(['GROCERY', 'FUEL', 'RECHARGE', 'RENT', 'PHARMACY'])} Rs {rng.randrange(150, 9000, 10):,}"
                 for _ in range(rng.randint(8, 14))]
        extra.append(Page(start + k - 2, "\n".join([_TITLE, *head, f"Page {k} of {pages}", *lines])))
    return replace(bundle, pages=bundle.pages + tuple(extra))


def continuation_pages(bundle: LoanBundle) -> list[int]:
    out = []
    for p in bundle.pages:
        if not p.text.startswith(_TITLE):
            continue
        m = _CONT.search(p.text)
        if m and int(m.group(1)) >= 2:
            out.append(p.number)
    return out


def filter_for_model(bundle: LoanBundle) -> tuple[LoanBundle, int]:
    """The pages the model is shown, and how many were held back. Page numbers are kept, so quotes still resolve."""
    drop = set(continuation_pages(bundle))
    if not drop:
        return bundle, 0
    return replace(bundle, pages=tuple(p for p in bundle.pages if p.number not in drop)), len(drop)
