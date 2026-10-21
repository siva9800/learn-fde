"""The two clients agree with each other and with the core, and both sort failures into the four outcomes."""

from __future__ import annotations

import re
import socket

import pytest
import requests
from zeep.transports import Transport

from godavari_integration.contracts import ReplaySession, load_cassette
from godavari_integration.soap.errors import (AmbiguousOutcome, CoreFault, NotSent, RefusedBeforeSending,
                                             ResponseUnreadable)
from godavari_integration.soap.port import CallLog
from godavari_integration.soap.raw_client import RawEnvelopeCorePort
from godavari_integration.soap.zeep_client import OfflineTransport, WsdlFetchRefused, ZeepCorePort
from godavari_integration.standin.wsdl_gen import VENDORED_PATH, build_wsdl

from conftest import ACCOUNT, SECRET


@pytest.mark.parametrize("kind", ["zeep", "raw"])
def test_both_clients_do_the_four_operations(kind, standin, port_for, mapping, writable):
    core, url = standin()
    f, rec = writable[0]
    core.register_file(f.file_no, f.branch_cd)
    port = port_for(kind, url)
    appl = port.create_application(mapping.to_core(rec))
    detail = port.get_application(appl)
    assert detail["APPL_ID"] == appl and detail["FILE_NO"] == f.file_no and detail["APPL_STAT"] == "K"
    assert port.update_kyc_status(appl, "C", "GF-AN-1142") == 1
    assert port.update_kyc_status(appl, "C", "GF-AN-1142") == 2       # a set, but the core appends history


@pytest.mark.parametrize("kind", ["zeep", "raw"])
def test_faults_carry_code_and_field(kind, standin, port_for, mapping, writable):
    core, url = standin()
    f, rec = writable[0]
    core.register_file(f.file_no, f.branch_cd)
    payload = {**mapping.to_core(rec), "STATE_CD": "KA"}
    with pytest.raises(CoreFault) as exc:
        port_for(kind, url).create_application(payload)
    assert (exc.value.code, exc.value.field) == ("CL-E031", "STATE_CD")


def test_zeep_refuses_a_missing_mandatory_field_before_the_network(standin, port_for, mapping, writable):
    core, url = standin()
    f, rec = writable[0]
    core.register_file(f.file_no, f.branch_cd)
    with pytest.raises(RefusedBeforeSending) as exc:
        port_for("zeep", url).create_application({k: v for k, v in mapping.to_core(rec).items() if k != "MOB_NO"})
    assert exc.value.field == "MOB_NO" and core.access_log == []


@pytest.mark.parametrize("kind", ["zeep", "raw"])
def test_a_read_timeout_on_a_write_is_ambiguous_and_the_work_was_done(kind, standin, port_for, mapping, writable):
    core, url = standin()
    f, rec = writable[0]
    core.register_file(f.file_no, f.branch_cd)
    core.plant_stall(f.file_no, "commit_then_stall", 0.6)
    log = CallLog()
    with pytest.raises(AmbiguousOutcome):
        port_for(kind, url, timeout=0.3, log=log).create_application(mapping.to_core(rec))
    assert len(core.applications_for(f.file_no)) == 1                 # it happened; we just did not hear
    assert log.records[-1].outcome == "AMBIGUOUS"


def test_a_refused_connection_is_not_sent():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port_no = s.getsockname()[1]
    s.close()                                                          # nothing listens there now
    client = RawEnvelopeCorePort(f"http://127.0.0.1:{port_no}/x", ACCOUNT, SECRET, timeout=1, connect_timeout=1)
    with pytest.raises(NotSent):
        client.get_by_file_number("GF-25001")


def test_served_wsdl_with_dead_import_is_refused_at_load(tmp_path):
    served = tmp_path / "served.wsdl"
    served.write_text(build_wsdl(served=True), encoding="utf-8")
    with pytest.raises(WsdlFetchRefused, match="corelend-dev01"):
        ZeepCorePort("http://127.0.0.1:1/x", ACCOUNT, SECRET, wsdl=served)


def test_the_vendored_wsdl_is_exactly_what_the_generator_writes():
    assert VENDORED_PATH.read_text(encoding="utf-8") == build_wsdl(served=False)
    served, vendored = build_wsdl(served=True), build_wsdl(served=False)
    assert "corelend-dev01" in served and "corelend-dev01" not in vendored.split("-->", 1)[1]


def test_strict_zeep_catches_sequence_drift_that_the_lenient_parser_accepts():
    """A response with two elements swapped: zeep (strict) says the contract broke; ElementTree reads on."""
    [ex] = [e for e in load_cassette() if e.scenario == "get_application"]
    m = re.search(r"(<tns:FILE_NO>[^<]*</tns:FILE_NO>)(<tns:BRANCH_CD>[^<]*</tns:BRANCH_CD>)", ex.response)
    assert m, "the recorded response has FILE_NO then BRANCH_CD, as the WSDL's sequence says"
    ex.response = ex.response[:m.start()] + m.group(2) + m.group(1) + ex.response[m.end():]
    zeep_port = ZeepCorePort("http://replay/x", ACCOUNT, SECRET,
                             transport=OfflineTransport(session=ReplaySession([ex])))
    with pytest.raises(ResponseUnreadable):
        zeep_port.get_application("AP0000000001")
    raw = RawEnvelopeCorePort("http://replay/x", ACCOUNT, SECRET, session=ReplaySession([ex]))
    assert raw.get_application("AP0000000001")["FILE_NO"] == "GF-25001"


def test_offline_transport_still_reads_local_files():
    assert OfflineTransport().load(str(VENDORED_PATH)).startswith(b"<?xml")
    assert isinstance(OfflineTransport(), Transport)
    with pytest.raises(WsdlFetchRefused):
        OfflineTransport().load("https://example.org/schema.xsd")
    assert requests.__version__
