"""Metadata as a first-class index: what every chunk carries besides its text.

Metadata comes from the register (the compliance head's circular register, the core system's file record),
never from guessing at the text. The access-control list on a chunk names the DOCUMENT's groups (a branch
group, a role group), never a list of users: users change branch overnight, documents do not, so the index
never has to be rebuilt when HR moves someone (section 06.5).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from .corpus import Document
from .day11 import BRANCH_AD_GROUP, BRANCH_CODES

ROLE_CREDITOPS = "GF-ROLE-CREDITOPS"       # every credit-ops analyst and team lead
ROLE_COMPLIANCE = "GF-ROLE-COMPLIANCE"     # the compliance desk
ROLE_BRANCH = "GF-ROLE-BRANCH"             # branch staff (credit officers, managers)


@dataclass(frozen=True)
class DocMeta:
    doc_id: str
    title: str
    doc_type: str
    product: str
    language: str
    effective_from: date
    effective_to: date | None
    superseded_by: str | None
    supersedes: str | None
    approval_status: str
    branch: str | None
    branch_code: str | None
    acl: frozenset[str]
    source_system: str
    sensitivity: str
    extra: tuple[tuple[str, str], ...] = field(default_factory=tuple)

    def in_force(self, on: date) -> bool:
        """True if the document is the version in force on that day."""
        return self.effective_from <= on and (self.effective_to is None or on < self.effective_to)


def acl_for(doc: Document) -> frozenset[str]:
    if doc.doc_type == "loan_decision":
        assert doc.branch is not None
        return frozenset({BRANCH_AD_GROUP[doc.branch]})              # Day 11's group for that branch, nothing else
    if doc.approval_status != "approved":
        return frozenset({ROLE_COMPLIANCE})                           # drafts: the compliance desk only
    return frozenset({ROLE_CREDITOPS, ROLE_COMPLIANCE, ROLE_BRANCH})


def meta_for(doc: Document) -> DocMeta:
    loan = doc.doc_type == "loan_decision"
    return DocMeta(
        doc_id=doc.doc_id, title=doc.title, doc_type=doc.doc_type, product=doc.product, language=doc.language,
        effective_from=doc.effective_from, effective_to=doc.effective_to, superseded_by=doc.superseded_by,
        supersedes=doc.supersedes, approval_status=doc.approval_status, branch=doc.branch,
        branch_code=BRANCH_CODES[doc.branch] if doc.branch else None, acl=acl_for(doc),
        source_system="core lending system, masked decision summary" if loan else "compliance circular register",
        sensitivity="confidential: customer file" if loan else "internal",
        extra=tuple(sorted(doc.extra.items())),
    )
