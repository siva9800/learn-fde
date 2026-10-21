"""The stand-in behaves like the 2009 core as the owner described it, including the parts nobody likes."""

from __future__ import annotations

import requests

import pytest

from godavari_integration.clock import BusinessClock, in_write_freeze, ist, next_write_slot
from godavari_integration.corespec import CREATE_APPLICATION_FIELDS, NAMESPACE
from godavari_integration.soap.errors import CoreFault, CoreUnavailable
from godavari_integration.soap.raw_client import build_request

from conftest import ACCOUNT, SECRET


def _payload(mapping, writable, product="two-wheeler"):
    f, rec = next((f, r) for f, r in writable if f.bundle.product == product)
    return f, mapping.to_core(rec)


def test_the_data_dictionary_has_61_fields_and_23_mandatory():
    assert len(CREATE_APPLICATION_FIELDS) == 61
    assert sum(f.mandatory for f in CREATE_APPLICATION_FIELDS) == 23


def test_create_always_creates_even_for_the_same_file(standin, port_for, mapping, writable):
    core, url = standin()
    f, payload = _payload(mapping, writable)
    core.register_file(f.file_no, f.branch_cd)
    port = port_for("raw", url)
    first, second = port.create_application(payload), port.create_application(payload)
    assert first != second
    assert len(core.applications_for(f.file_no)) == 2          # DUPLICATE_ON_RETRY, by design


def test_lookup_returns_the_shell_then_the_application(standin, port_for, mapping, writable):
    core, url = standin()
    f, payload = _payload(mapping, writable)
    core.register_file(f.file_no, f.branch_cd)
    port = port_for("zeep", url)
    [shell] = port.get_by_file_number(f.file_no)
    assert shell.is_shell and shell.appl_stat == "S"
    appl = port.create_application(payload)
    [app] = port.get_by_file_number(f.file_no)
    assert app.appl_id == appl and app.ext_ref == payload["EXT_REF"] and not app.is_shell
    assert port.get_by_file_number("GF-29999") == []


def test_create_refuses_a_file_with_no_shell(standin, port_for, mapping, writable):
    _, url = standin()
    _, payload = _payload(mapping, writable)
    with pytest.raises(CoreFault) as exc:
        port_for("raw", url).create_application(payload)
    assert exc.value.code == "CL-E052" and not exc.value.retryable


def test_writes_are_refused_during_the_batch_and_reads_are_not(standin, port_for, mapping, writable, clock):
    core, url = standin()
    f, payload = _payload(mapping, writable)
    core.register_file(f.file_no, f.branch_cd)
    clock.set(ist(2026, 11, 12, 17, 45))
    port = port_for("raw", url)
    with pytest.raises(CoreFault) as exc:
        port.create_application(payload)
    assert exc.value.code == "CL-E017" and exc.value.retryable
    assert port.get_by_file_number(f.file_no)[0].is_shell


def test_the_window_runs_to_eleven_at_month_end():
    assert in_write_freeze(ist(2026, 11, 20, 19, 59)) and not in_write_freeze(ist(2026, 11, 20, 20, 0))
    assert in_write_freeze(ist(2026, 11, 30, 22, 30))            # last three days of the month
    assert next_write_slot(ist(2026, 11, 30, 18, 0)).hour == 23
    assert not in_write_freeze(ist(2026, 11, 12, 17, 29))


def test_the_undocumented_rate_limit_answers_service_busy(standin, port_for):
    core, url = standin(rate_limit=5)
    core.register_file("GF-25001", "KKP01")
    port = port_for("raw", url)
    codes = []
    for _ in range(8):
        try:
            port.get_by_file_number("GF-25001")
            codes.append("OK")
        except CoreFault as fault:
            codes.append(fault.code)
    assert codes[:5] == ["OK"] * 5 and "CL-E099" in codes[5:]


def test_maintenance_is_an_html_page_not_a_fault(standin, port_for):
    core, url = standin()
    core.maintenance_forced = True
    for kind in ("raw", "zeep"):
        with pytest.raises(CoreUnavailable):
            port_for(kind, url).get_by_file_number("GF-25001")


def test_wrong_password_is_cl_e001(standin, port_for):
    _, url = standin()
    with pytest.raises(CoreFault) as exc:
        port_for("raw", url, password="guess").get_by_file_number("GF-25001")
    assert exc.value.code == "CL-E001"


def test_two_wheeler_without_dealer_passes_sandbox_and_fails_production(standin, port_for, mapping, writable):
    """Known drift SBX-01: the July sandbox accepts what August's production rejects."""
    f, payload = _payload(mapping, writable, "two-wheeler")
    payload = {k: v for k, v in payload.items() if k != "DLR_CD"}
    sandbox, s_url = standin("sandbox")
    prod, p_url = standin("production-like")
    for core in (sandbox, prod):
        core.register_file(f.file_no, f.branch_cd)
    assert port_for("raw", s_url).create_application(payload).startswith("AP")
    with pytest.raises(CoreFault) as exc:
        port_for("raw", p_url).create_application(payload)
    assert exc.value.code == "CL-E023" and exc.value.field == "DLR_CD"


def test_the_core_silently_drops_an_element_it_does_not_know(standin, mapping, writable):
    """Why the hand-built client checks names first: a typo is a lost field, not an error."""
    core, url = standin()
    f, payload = _payload(mapping, writable)
    core.register_file(f.file_no, f.branch_cd)
    body = build_request("CreateApplication", payload, ACCOUNT, SECRET).decode()
    body = body.replace("<tns:EMP_NM>", "<tns:EMPL_NM>").replace("</tns:EMP_NM>", "</tns:EMPL_NM>")
    resp = requests.post(url, data=body.encode(), headers={"Content-Type": "text/xml"}, timeout=5)
    assert resp.status_code == 200 and f"<tns:APPL_ID>" in resp.text and NAMESPACE in resp.text
    [rec] = core.applications_for(f.file_no)
    assert "EMP_NM" not in rec.fields                                 # accepted, and the employer is gone
    with pytest.raises(ValueError, match="data dictionary"):
        build_request("CreateApplication", {**payload, "EMPL_NM": "X"}, ACCOUNT, SECRET)


def test_system_computed_fields_are_never_kept(standin, port_for, mapping, writable):
    core, url = standin()
    f, payload = _payload(mapping, writable)
    core.register_file(f.file_no, f.branch_cd)
    port_for("raw", url).create_application({**payload, "ROI_PCT": "9"})
    assert "ROI_PCT" not in core.applications_for(f.file_no)[0].fields
    assert "ROI_PCT" not in payload and "EMI_AMT" not in payload       # and the mapping never sends them


def test_business_clock_is_settable_and_separate_from_real_time():
    c = BusinessClock(ist(2026, 11, 12, 17, 0))
    c.advance(minutes=45)
    assert c.now().hour == 17 and c.now().minute == 45 and in_write_freeze(c.now())
