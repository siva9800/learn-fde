"""The send-back draft: what the planner may propose, and the code that decides whether it is acceptable.

The model proposes, code disposes (Day 11). The draft is a typed object, and `problems()` checks it against
facts the model cannot change: the findings that the signed rules produced, the checklist version in force,
the citations the policy tool actually returned. A draft that lists one document too many is as wrong as one
that lists one too few: the first is how a junior's "to be safe" send-back gets automated (Day 6,
SENDBACK_CAUTION), the second is how a file comes back twice.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .day14 import pii_hits

DECISION_WORDS = re.compile(r"\b(approved|approve|sanction(?:ed)?|reject(?:ed)?|declined|disburs(?:ed|al))\b", re.I)
# Day 14's mobile pattern wants ten digits in a row; people type "98490 12345". Both forms are caught here.
ADDRESS_LIKE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+|(?:\+?91[\s-]?)?\b[6-9]\d{4}[\s-]?\d{5}\b")


class SendBackItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rule_id: str = Field(pattern=r"^[A-Z]{2,3}-[A-Z0-9-]+$", description="the rule that fired, e.g. TW-DOC-05")
    issue: str = Field(min_length=3, max_length=240)
    what_to_send: str = Field(min_length=3, max_length=240)


class SendBackDraft(BaseModel):
    """No recipient field, on purpose: who receives the message is resolved by code from the branch directory."""

    model_config = ConfigDict(extra="forbid")
    file_id: str = Field(pattern=r"^GF-\d{5}$")
    items: list[SendBackItem] = Field(min_length=1, max_length=20)
    body: str = Field(min_length=20, max_length=2400)
    checklist_version: str
    policy_citations: list[str] = Field(default_factory=list, max_length=5)


def proposal_hash(draft: SendBackDraft, recipient: str) -> str:
    """What an approval is bound to: this text, to this recipient. Change one character and it is a new proposal."""
    blob = json.dumps({"draft": draft.model_dump(), "to": recipient}, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def problems(draft: SendBackDraft, *, file_id: str, branch_facing: list[dict[str, Any]], checklist_version: str,
             citations_seen: set[str]) -> list[str]:
    """Everything wrong with a draft, as sentences the planner (or the analyst who edited it) can act on."""
    out: list[str] = []
    if draft.file_id != file_id:
        out.append(f"the draft is for {draft.file_id}; this run is {file_id}")
    wanted = {f["rule_id"] for f in branch_facing}
    listed = [i.rule_id for i in draft.items]
    extra = sorted(set(listed) - wanted)
    missing = sorted(wanted - set(listed))
    if extra:
        out.append(f"items for rules that did not fire: {', '.join(extra)} (ask only for what the rules require)")
    if missing:
        out.append(f"fired rules not in the items: {', '.join(missing)}")
    if len(listed) != len(set(listed)):
        out.append("a rule is listed twice")
    if draft.checklist_version != checklist_version:
        out.append(f"checklist version {draft.checklist_version!r} is not the one in force ({checklist_version!r})")
    unknown = sorted(set(draft.policy_citations) - citations_seen)
    if unknown:
        out.append(f"citations not returned by the policy tool in this run: {unknown}")
    if file_id not in draft.body:
        out.append("the body does not name the file number")
    for rule in sorted(wanted):
        if rule not in draft.body:
            out.append(f"the body does not cite rule {rule}")
    if m := DECISION_WORDS.search(draft.body):
        out.append(f"the body uses decision language ({m.group(0)!r}); a send-back asks for documents, it decides nothing")
    if ADDRESS_LIKE.search(draft.body):
        out.append("the body carries an email address or phone number; recipients and contacts come from the directory")
    hits = pii_hits(draft.body)
    if hits:
        out.append(f"the body carries customer identifiers ({', '.join(sorted({k for k, _ in hits}))}); the branch "
                   "knows the customer by the file number")
    return out
