"""Contract tests against the recorded sandbox: replay, request shape, WSDL diff, known drift."""

from __future__ import annotations

import json
import tomllib
from datetime import date
from pathlib import Path

import pytest

from godavari_integration.contracts import (CASSETTE, KNOWN_DRIFT, WSDL_CONTRACT, ReplaySession, body_paths,
                                            diff_contract, load_cassette, wsdl_contract)
from godavari_integration.corespec import OPERATIONS_USED
from godavari_integration.soap.errors import CoreError, CoreFault
from godavari_integration.soap.raw_client import RawEnvelopeCorePort
from godavari_integration.soap.zeep_client import OfflineTransport, ZeepCorePort
from godavari_integration.standin.server import core_wsdl

from conftest import ACCOUNT, SECRET

AS_OF = date(2026, 11, 13)          # the chapter's date; a CI job would use today's date
TESTS = Path(__file__).resolve().parent


def _ports(exchanges):
    raw_session, zeep_session = ReplaySession(exchanges), ReplaySession(exchanges)
    raw = RawEnvelopeCorePort("http://replay/x", ACCOUNT, SECRET, session=raw_session)
    zp = ZeepCorePort("http://replay/x", ACCOUNT, SECRET, transport=OfflineTransport(session=zeep_session))
    return (raw, raw_session), (zp, zeep_session)


def _drive(port, payload):
    out = {}
    out["lookup_shell"] = port.get_by_file_number("GF-25001")
    out["create_ok"] = port.create_application(payload)
    out["lookup_after_create"] = port.get_by_file_number("GF-25001")
    out["get_application"] = {k: v for k, v in port.get_application(out["create_ok"]).items() if k != "CR_CHK_RSLT"}
    out["update_kyc"] = port.update_kyc_status(out["create_ok"], "C", "GF-AN-1142", "DOCS_OK")
    try:
        port.create_application({k: v for k, v in payload.items() if k != "MOB_NO"})
    except CoreError as exc:
        out["fault_mandatory"] = (type(exc).__name__, getattr(exc, "code", ""), getattr(exc, "field", ""))
    for name, bad in (("fault_invalid_code", {**payload, "KYC_STAT": "Z"}),
                      ("fault_not_registered", {**payload, "FILE_NO": "GF-29999"})):
        with pytest.raises(CoreFault) as exc:
            port.create_application(bad)
        out[name] = (exc.value.code, exc.value.field)
    out["lookup_unknown"] = port.get_by_file_number("GF-29999")
    with pytest.raises(CoreFault) as exc:
        port.create_application(payload)
    out["fault_batch_window"] = (exc.value.code, exc.value.field)
    return out


@pytest.fixture(scope="module")
def payload(mapping, facts):
    from godavari_integration.approvals import approved_records
    [(_, rec)] = [(f, r) for f, r in approved_records(facts, mapping, ACCOUNT) if f.file_no == "GF-25001"]
    return mapping.to_core(rec)


def test_both_clients_read_the_recorded_sandbox_the_same_way(payload):
    (raw, _), (zp, _) = _ports(load_cassette())
    a, b = _drive(raw, payload), _drive(zp, payload)
    # the one difference, and it is the point: zeep refuses a WSDL-mandatory gap before the network;
    # the hand-built client sends it and the core answers CL-E023
    assert a.pop("fault_mandatory") == ("CoreFault", "CL-E023", "MOB_NO")
    assert b.pop("fault_mandatory") == ("RefusedBeforeSending", "WSDL-MINOCCURS", "MOB_NO")
    assert a == b
    assert a["lookup_shell"][0].is_shell and a["lookup_after_create"][0].ext_ref == payload["EXT_REF"]
    assert a["fault_batch_window"] == ("CL-E017", "")
    assert a["fault_not_registered"][0] == "CL-E052" and a["lookup_unknown"] == []


def test_requests_have_the_recorded_shape_element_by_element(payload):
    exchanges = load_cassette()
    (raw, raw_s), (zp, zeep_s) = _ports(exchanges)
    _drive(raw, payload)
    _drive(zp, payload)
    recorded = [body_paths(e.request.encode()) for e in exchanges]
    assert [body_paths(x) for x in raw_s.sent] == recorded
    assert [body_paths(x) for x in zeep_s.sent] == [p for e, p in zip(exchanges, recorded)
                                                    if e.scenario != "fault_mandatory"]


def test_the_served_wsdl_matches_the_pinned_contract(standin):
    core, _ = standin()
    pinned = json.loads(WSDL_CONTRACT.read_text(encoding="utf-8"))
    assert diff_contract(pinned, wsdl_contract(core_wsdl(core), OPERATIONS_USED)) == []


def test_a_changed_wsdl_is_a_readable_diff(standin):
    core, _ = standin()
    changed = core_wsdl(core).replace('<xsd:element name="MOB_NO" type="xsd:string"/>',
                                      '<xsd:element name="MOB_NUM" type="xsd:string"/>')
    changed = changed.replace('<xsd:element name="DLR_CD" type="xsd:string" minOccurs="0"/>',
                              '<xsd:element name="DLR_CD" type="xsd:string"/>')
    diff = diff_contract(json.loads(WSDL_CONTRACT.read_text(encoding="utf-8")), wsdl_contract(changed, OPERATIONS_USED))
    assert "CreateApplication request: CreateApplicationRequest/Application/MOB_NO removed" in diff
    assert "CreateApplication request: CreateApplicationRequest/Application/DLR_CD minOccurs 0 -> 1" in diff


def test_known_drift_is_owned_unexpired_and_tested():
    entries = tomllib.loads(KNOWN_DRIFT.read_text(encoding="utf-8"))["drift"]
    names = "\n".join(p.read_text(encoding="utf-8") for p in TESTS.glob("test_*.py"))
    for e in entries:
        assert date.fromisoformat(e["expires"]) > AS_OF, f"{e['id']} expired: re-check with {e['confirmed_by']}"
        assert f"def {e['test']}(" in names, f"{e['id']} names a test that does not exist"


def test_contract_tests_never_assert_on_credit_check_result():
    """Known drift SBX-02: the sandbox's credit check runs on stale rules. Only this file may mention it,
    and only to exclude it."""
    offenders = [p.name for p in TESTS.glob("test_*.py") if p.name != Path(__file__).name
                 and "CR_CHK_RSLT" in p.read_text(encoding="utf-8")]
    assert offenders == []


def test_the_cassette_holds_no_identifiers(facts):
    text = CASSETTE.read_text(encoding="utf-8")
    assert "SCRUBBED NAME" in text and "********" in text
    for f in facts.values():
        assert f.truth.fields["pan"] not in text and f.truth.fields["applicant_name"] not in text
