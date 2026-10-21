"""A synthetic week of the send-back workflow on the two pilot branches, with people, branches and crashes.

Thursday 26 November to Friday 4 December 2026 (engagement week 5, prototype mode, synthetic files only).
Day 7's sample supplies the Kukatpally and Guntur files. Around the engine:

  analysts      decide each proposal after a delay drawn per file: most within the hour, some after the
                four-hour deadline (the item escalates to the team lead), a few edits, a few rejections,
                one edit that fails the same checks as a draft and is redone.
  branches      resubmit what was asked for one to four working days after the email; one file in seven
                never does (it goes to an analyst when the five working days run out). One resubmission
                is uploaded twice, as SFTP does.
  crashes       the worker process dies at four named points (mid-draft, after an email left but before
                it was recorded, after the tracker write, after a core create but before it was recorded).
                Each time a new engine opens the same files on disk and calls recover().

Everything is deterministic: delays and behaviours come from a hash of the file number.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from .approvals import ASSIGNED_ANALYST, TEAM_LEAD, region_of
from .clock import BusinessClock, DAY_END, DAY_START, WORKDAYS, add_working_days, add_working_hours, parse, stamp
from .day11 import PAGE_TITLES, Doc, LoanBundle, Page, build_file, day7_sample, fmt_amount
from .engine import ApprovalError, Engine, Systems
from .planner import Planner, StubPlanner
from .serialize import branch_facing, bundle_from_json
from .states import State
from .store import Store
from .systems import Faults, SimulatedCrash
from .tools import message_key

START = datetime(2026, 11, 26, 9, 0)
END = datetime(2026, 12, 4, 17, 30)
PILOT = ("Kukatpally", "Guntur")
CRASH_POINTS = {"mid_drafting": 9, "after_send_before_record": 3, "after_tracker_before_transition": 6,
                "after_core_write_before_record": 2}


def h(text: str, mod: int) -> int:
    return int(hashlib.sha256(text.encode()).hexdigest()[:8], 16) % mod


# ---- the branch: re-scan what was asked for -----------------------------------------------------------
def _line_value(bundle: LoanBundle, label: str) -> str:
    for p in bundle.pages:
        for line in p.text.splitlines():
            if f"{label}:" in line:
                return line.split(f"{label}:", 1)[1].strip()
    return ""


def fix_bundle(bundle: LoanBundle, row: Any, facing: list[dict[str, Any]]) -> LoanBundle:
    """The branch's resubmission: the original pages, with each requested item replaced or added.

    Missing documents come from Day 11's own generator (the same file with the document present), so the
    new page is the one the customer would really have brought, including any problem it has."""
    full, _ = build_file(replace(row, has_pan=True, has_address_proof=True, has_income_proof=True, has_photo=True))
    pages = [p for p in bundle.pages]
    name = _line_value(bundle, "Applicant name") or "THE APPLICANT"
    address = _line_value(bundle, "Residential address")
    applied = _line_value(bundle, "Application date")

    def first_line(p: Page) -> str:
        return p.text.splitlines()[0]

    def replace_doc(doc: Doc, text: str) -> None:
        idx = next((i for i, p in enumerate(pages) if first_line(p).startswith(PAGE_TITLES[doc])), None)
        new = Page(pages[idx].number if idx is not None else len(pages) + 1, text)
        if idx is None:
            pages.append(new)
        else:
            pages[idx] = new

    for f in facing:
        rule = f["rule_id"]
        if "-DOC-" in rule and f.get("doc"):
            doc = Doc(f["doc"])
            src = [p for p in full.pages if first_line(p).startswith(PAGE_TITLES[doc])]
            for p in src or [Page(0, f"{PAGE_TITLES[doc]}\nName: {name}")]:
                pages.append(Page(len(pages) + 1, p.text, p.handwritten, p.telugu))
        elif rule.endswith(("ADDR-LIST", "ADDR-AGE")):
            replace_doc(Doc.PROOF_OF_ADDRESS, f"{PAGE_TITLES[Doc.PROOF_OF_ADDRESS]}\nDocument: voter id\n"
                                              f"In the name of: {name}\nAddress: {address}")
        elif rule.endswith("KYC-MASK"):
            pages = [Page(p.number, re.sub(r"Aadhaar number: \d{4} \d{4} (\d{4})", r"Aadhaar number: XXXX XXXX \1",
                                           p.text), p.handwritten, p.telugu) for p in pages]
        elif rule.endswith("BANK-AGE") and applied:
            d, m, y = (int(x) for x in applied.split("-"))
            end = datetime(y, m, d) - timedelta(days=5)
            period = f"Period: {(end - timedelta(days=91)):%d-%m-%Y} to {end:%d-%m-%Y}"
            pages = [Page(p.number, re.sub(r"Period: .*", period, p.text), p.handwritten, p.telugu) for p in pages]
        elif rule.endswith("DATE-QUOTE") and applied:
            d, m, y = (int(x) for x in applied.split("-"))
            quoted = f"Quotation date: {(datetime(y, m, d) - timedelta(days=3)):%d-%m-%Y}"
            pages = [Page(p.number, re.sub(r"Quotation date: .*", quoted, p.text), p.handwritten, p.telugu) for p in pages]
        elif rule.endswith("LTV"):
            def cut(mt: re.Match[str]) -> str:
                amount = int(re.sub(r"\D", "", mt.group(1)))
                return f"Loan amount requested: {fmt_amount(amount * 6 // 10 // 500 * 500)}"
            pages = [Page(p.number, re.sub(r"Loan amount requested: (Rs [\d,]+)", cut, p.text), p.handwritten, p.telugu)
                     for p in pages]
    return LoanBundle(bundle.file_id, bundle.branch, bundle.product, bundle.channel, tuple(pages))


# ---- the analysts --------------------------------------------------------------------------------------
LAKSHMI_LINE = "Please ask the customer to bring the originals to the branch for verification."
BAD_EDIT_LINE = "If the customer has questions, ask them to call 98490 12345."     # a number in a branch email


@dataclass
class WeekLog:
    lines: list[str] = field(default_factory=list)
    crashes: list[str] = field(default_factory=list)
    counts: dict[str, int] = field(default_factory=dict)

    def say(self, at: datetime, text: str) -> None:
        self.lines.append(f"{at:%a %d %b %H:%M}  {text}")

    def bump(self, key: str) -> None:
        self.counts[key] = self.counts.get(key, 0) + 1


def is_working(at: datetime) -> bool:
    return at.weekday() in WORKDAYS and DAY_START <= at.time() < DAY_END


class Week:
    def __init__(self, folder: Path, planner: Planner | None = None) -> None:
        self.folder = folder
        for f in ("workflow.sqlite", "godavari-mail-relay.sqlite", "godavari-tracker.sqlite", "core-sandbox.json"):
            (folder / f).unlink(missing_ok=True)
        self.clock = BusinessClock(START)
        self.faults = Faults(dict(CRASH_POINTS))
        self.planner = planner or StubPlanner("v1")
        self.log = WeekLog()
        self.rows = {r.file_id: r for r in day7_sample()
                     if r.branch in PILOT and r.product in ("two-wheeler", "gold")}
        self.resubmit_at: dict[str, datetime] = {}
        self.bad_edit_done = False
        self.duplicate_done = False
        self.engine = self._open()

    def _open(self) -> Engine:
        return Engine(Store(self.folder / "workflow.sqlite"), Systems.open(self.folder), self.clock, self.planner,
                      faults=self.faults, as_of=START.date())

    def _restart(self, where: str) -> None:
        """The worker died. A new one opens the same files on disk; nothing in memory survives."""
        self.log.crashes.append(where)
        self.log.say(self.clock.now(), f"CRASH at {where}; a new worker opens the same store and recovers")
        self.engine.store.close()
        self.engine = self._open()
        try:
            resumed = self.engine.recover()
        except SimulatedCrash as again:
            self._restart(str(again))
            return
        busy = [f"{f} from {s}" for f, s in resumed if s in ("DRAFTING", "SENDING", "PUSHING")]
        self.log.say(self.clock.now(), f"  resumed {len(resumed)} unfinished run(s); mid-step: {', '.join(busy) or 'none'}"
                     f"; the other {len(resumed) - len(busy)} had not started their step")

    def _guard(self, fn: Any, *args: Any, **kw: Any) -> Any:
        try:
            return fn(*args, **kw)
        except SimulatedCrash as crash:
            self._restart(str(crash))
            return None

    def _drain(self) -> None:
        for _ in range(3):
            ids = self.engine.runnable()
            if not ids:
                return
            for fid in ids:
                self._guard(self.engine.run_until_rest, fid)

    def _analysts(self, now: datetime) -> None:
        eng = self.engine
        for row in eng.store.approvals("PENDING"):
            fid = row["file_id"]
            created = parse(row["created_at"])
            delay_h = [0.5, 0.5, 0.5, 1.0, 1.0, 1.5, 2.0, 3.0, 6.0, 99.0][h(fid + str(row["cycle"]), 10)]
            run = eng.store.get(fid)
            assert run is not None
            if row["level"] >= 1:
                user = TEAM_LEAD[region_of(run.branch)]
                if now < parse(row["due_at"]) - timedelta(hours=1):
                    continue
            else:
                user = row["assigned_to"]
                if now < add_working_hours(created, delay_h):
                    continue
            kind = h("decision" + fid + str(row["cycle"]), 13)
            if kind == 0:
                eng.decide_send(row["id"], user, "reject", note="branch manager on leave; I will phone the deputy")
                self.log.bump("rejected")
                self.log.say(now, f"{user} rejected {row['id']}: she will phone the branch herself")
                continue
            edited = None
            body = json.loads(row["draft_json"])["body"]
            if not self.bad_edit_done and user == "lakshmi":
                self.bad_edit_done = True
                try:
                    eng.decide_send(row["id"], user, "approve", edited_body=body + "\n" + BAD_EDIT_LINE)
                    self.log.bump("bad_edit_accepted")          # must stay zero; reconcile() reports it
                    continue
                except ApprovalError as e:
                    self.log.say(now, f"{user}'s edit of {row['id']} refused: {str(e).split('draft: ', 1)[-1]}")
                    self.log.bump("edit_refused")
                edited = body + "\n" + LAKSHMI_LINE
            elif kind in (1, 2):
                edited = body + "\n" + LAKSHMI_LINE
            eng.decide_send(row["id"], user, "approve", edited_body=edited)
            self.log.bump("approved_edited" if edited else "approved")
            if row["level"] >= 1:
                self.log.bump("approved_after_escalation")
                self.log.say(now, f"{user} (team lead) approved {row['id']} after escalation")

        for run in eng.store.runs(State.NEEDS_REVIEW):
            if run.data.get("route") in ("send_back", "blocked") or run.data.get("reviewed"):
                continue
            entered = parse(run.updated_at)
            if now >= add_working_hours(entered, 2.0):
                try:
                    eng.approve_file(run.file_id, ASSIGNED_ANALYST[run.branch], note="fields checked against the pages")
                    self.log.bump("files_approved")
                except ApprovalError:
                    pass

    def _branches(self, now: datetime) -> None:
        eng = self.engine
        for run in eng.store.runs(State.AWAITING_RESUBMISSION):
            fid = run.file_id
            key = f"{fid}-c{run.cycle}"
            if key not in self.resubmit_at:
                if h("never" + fid, 7) == 0:
                    self.resubmit_at[key] = datetime.max
                else:
                    days = 1 + h("days" + key, 4)
                    sent = parse(run.updated_at)
                    self.resubmit_at[key] = datetime.combine(add_working_days(sent, days).date(), DAY_START)
            if now < self.resubmit_at[key]:
                continue
            _, bjson = eng.store.bundle(fid, run.bundle_version)
            fixed = fix_bundle(bundle_from_json(bjson), self.rows[fid], branch_facing(run.data["findings"]))
            eng.receive(fixed)
            self.log.bump("resubmissions")
            if not self.duplicate_done:
                self.duplicate_done = True
                outcome = eng.receive(fixed)                     # SFTP delivers the same file twice
                self.log.say(now, f"{fid}: the same resubmission uploaded twice; second upload: {outcome}")

    def run(self) -> WeekLog:
        eng = self.engine
        for fid in sorted(self.rows):
            bundle, _ = build_file(self.rows[fid])
            eng.receive(bundle)
        self.log.say(self.clock.now(), f"{len(self.rows)} files from Kukatpally and Guntur received")
        self._drain()
        while self.clock.now() < END:
            now = self.clock.advance(minutes=30)
            moved = self._guard(self.engine.tick) or []
            for m in moved:
                if m.startswith("SB-"):
                    self.log.bump("escalations")
                else:
                    self.log.bump("resubmission_overdue")
            if is_working(now):
                self._guard(self._analysts, now)
                self._guard(self._branches, now)
            self._drain()
        return self.log


def reconcile(store: Store, systems: Systems) -> dict[str, Any]:
    """The numbers the core-system owner and the compliance head would ask for, from the systems themselves."""
    approved = store.approvals("APPROVED")
    relay = systems.relay.all()
    by_subject: dict[str, int] = {}
    for m in relay:
        by_subject[m["subject"]] = by_subject.get(m["subject"], 0) + 1
    core_files: dict[str, int] = {}
    for r in systems.core.records:
        core_files[r["file_number"]] = core_files.get(r["file_number"], 0) + 1
    pushed = store.runs(State.PUSHED_TO_CORE)
    keys = {message_key(a["file_id"], a["cycle"], a["final_hash"]) for a in approved}
    unapproved_sends = [m for m in relay if m["header_key"] not in keys]
    customer = [m for m in relay if not systems.directory.is_branch_mailbox(m["recipient"])]
    ok, bad = store.verify_chain()
    return {"approved_send_backs": len(approved), "messages": len(relay),
            "duplicate_messages": sum(c - 1 for c in by_subject.values()),
            "messages_to_non_branch_addresses": len(customer), "messages_without_an_approval": len(unapproved_sends),
            "core_records": len(systems.core.records), "pushed_runs": len(pushed),
            "duplicate_core_records": sum(c - 1 for c in core_files.values()),
            "audit_events": len(store.events()), "audit_chain_ok": ok, "audit_chain_break": bad,
            "states": {s.value: len(store.runs(s)) for s in State if store.runs(s)}}


__all__ = ["END", "START", "Week", "WeekLog", "fix_bundle", "reconcile", "stamp"]
