"""Record the sandbox once: the cassette and the pinned WSDL contract the contract tests replay.

    python -X utf8 code/record_sandbox.py

Run against the stand-in here. At Godavari it runs against the real sandbox from the machine in the
Hyderabad building, after every quarterly refresh and whenever the owner announces a release, and its diff
is reviewed with him before the new cassette is committed.
"""

from __future__ import annotations

import json
from datetime import date

from godavari_integration import synth_sources as ss
from godavari_integration.canonical import canonical_from_day11
from godavari_integration.clock import BusinessClock, ist
from godavari_integration.contracts import CASSETTE, WSDL_CONTRACT, RecordingSession, save_cassette, wsdl_contract
from godavari_integration.corespec import OPERATIONS_USED
from godavari_integration.day11 import Route
from godavari_integration.soap.errors import CoreFault
from godavari_integration.soap.port import RateLimiter
from godavari_integration.soap.raw_client import RawEnvelopeCorePort
from godavari_integration.standin.core import CoreStandIn
from godavari_integration.standin.server import core_wsdl, running
from godavari_integration.translate import Mapping

ACCOUNT, SECRET = "SVC_KAAGAZ_SBX", "sbx-only-not-a-real-secret"


def main() -> int:
    mapping = Mapping()
    facts = ss.hyderabad_files()
    f = facts["GF-25001"]
    assert f.result.route == Route.READY_FOR_APPROVAL and f.result.output is not None
    approved = {k: v.value for k, v in f.result.output.fields.items() if v.value}
    record = canonical_from_day11(f.result, f.bundle, approved, approved_by="GF-AN-1142", state="telangana",
                                  entry_user=ACCOUNT, mapping_version=mapping.version)
    payload = mapping.to_core(record)
    clock = BusinessClock(ist(2026, 11, 10, 11, 0))
    core = CoreStandIn(environment="sandbox", clock=clock)
    core.register_file("GF-25001", "KKP01")
    session = RecordingSession()
    with running(core) as url:
        port = RawEnvelopeCorePort(url, ACCOUNT, SECRET, session=session, clock=clock, limiter=RateLimiter(4))

        def step(name: str, fn: object) -> None:
            session.scenario = name
            try:
                fn()                                           # type: ignore[operator]
            except CoreFault:
                pass

        step("lookup_shell", lambda: port.get_by_file_number("GF-25001"))
        created: dict[str, str] = {}
        step("create_ok", lambda: created.setdefault("id", port.create_application(payload)))
        step("lookup_after_create", lambda: port.get_by_file_number("GF-25001"))
        step("get_application", lambda: port.get_application(created["id"]))
        step("update_kyc", lambda: port.update_kyc_status(created["id"], "C", "GF-AN-1142", "DOCS_OK"))
        step("fault_mandatory", lambda: port.create_application({k: v for k, v in payload.items() if k != "MOB_NO"}))
        step("fault_invalid_code", lambda: port.create_application({**payload, "KYC_STAT": "Z"}))
        step("fault_not_registered", lambda: port.create_application({**payload, "FILE_NO": "GF-29999"}))
        step("lookup_unknown", lambda: port.get_by_file_number("GF-29999"))
        clock.set(ist(2026, 11, 10, 17, 45))
        step("fault_batch_window", lambda: port.create_application(payload))
        wsdl = core_wsdl(core)
    save_cassette(session.exchanges)
    WSDL_CONTRACT.write_text(json.dumps(wsdl_contract(wsdl, OPERATIONS_USED), indent=1) + "\n", encoding="utf-8",
                             newline="\n")
    for ex in session.exchanges:
        print(f"{ex.scenario:<22} {ex.operation:<28} HTTP {ex.status}")
    print(f"wrote {CASSETTE.name} ({len(session.exchanges)} exchanges) and {WSDL_CONTRACT.name}; recorded "
          f"{date(2026, 11, 10)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
