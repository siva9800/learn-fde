"""The rule that fired, its signed version, and the circular clause it rests on.

Day 11 owns the rules and their sign-off record; Day 15 owns the register of circulars and clause-level citations.
This module joins them for the screen: rule id -> (document number, clause) from a reviewed table, then the clause
text from Day 15's corpus, checked to be in force on the decision date. A citation is built from metadata and
quoted verbatim; it is never retrieved by similarity and never written by a model.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Any

from .paths import CODE
from godavari_retrieval.corpus import Clause, Document, Table, policy_documents

CITATIONS_PATH = CODE / "rule_citations.json"


@dataclass(frozen=True)
class Citation:
    doc_id: str
    title: str
    clause: str
    text: str                  # verbatim clause text, or the table caption and header for a table clause
    effective_from: date
    language: str

    @property
    def line(self) -> str:
        return f"{self.doc_id} · {self.title} · clause {self.clause} · in force from {self.effective_from:%d %b %Y}"


class StaleCitation(RuntimeError):
    """The mapped document is not the version in force on the decision date, or the clause does not exist."""


def load_table(path: Path = CITATIONS_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _documents() -> dict[str, Document]:
    return {d.doc_id: d for d in policy_documents()}


def in_force(doc: Document, on: date) -> bool:
    return doc.approval_status == "approved" and doc.effective_from <= on and (doc.effective_to is None or on < doc.effective_to)


def clause_text(item: Clause | Table) -> str:
    if isinstance(item, Clause):
        return item.text
    return f"{item.caption}: " + " | ".join(item.header) + f" ({len(item.rows)} rows)"


def cite(rule_id: str, on: date, table: dict[str, Any] | None = None) -> Citation | None:
    """The clause behind a signed rule, as in force on `on`. None for engineering checks (ENV-*), which cite nothing.
    Raises StaleCitation if the table points at a superseded document or a clause that is not there."""
    table = table or load_table()
    if rule_id.startswith("ENV-"):
        return None
    if rule_id not in table["rules"]:
        raise StaleCitation(f"{rule_id} has no citation in {table['version']}; a signed rule must cite its source")
    doc_id, number = table["rules"][rule_id]
    doc = _documents().get(doc_id)
    if doc is None:
        raise StaleCitation(f"{rule_id} cites {doc_id}, which is not in the register")
    if not in_force(doc, on):
        raise StaleCitation(f"{rule_id} cites {doc_id}, which is not in force on {on:%d %b %Y}"
                            f"{f' (superseded by {doc.superseded_by})' if doc.superseded_by else ''}")
    for section in doc.sections:
        for item in section.items:
            if item.number == number:
                return Citation(doc.doc_id, doc.title, number, clause_text(item), doc.effective_from, doc.language)
    raise StaleCitation(f"{rule_id} cites clause {number} of {doc_id}, which has no such clause")
