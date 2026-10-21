"""The WSDL, generated from the data dictionary in two versions.

  served    what the stand-in returns for ?wsdl: the shape of Godavari's real one, including its two
            defects. It imports a shared schema from a developer's host name that has not existed since
            2014, and its soap:address points at that same host.
  vendored  our copy, kept in the repository (wsdl/LendingService.wsdl): the shared type inlined, the
            address left as a placeholder that the client overrides. Every difference from the served
            file is listed in VENDORED_CHANGES and reviewed with the core-system owner.

    python -X utf8 -m godavari_integration.standin.wsdl_gen     # rewrites the vendored copy
"""

from __future__ import annotations

from pathlib import Path

from ..corespec import (CREATE_APPLICATION_FIELDS, DETAIL_FIELDS, FIELD_BY_NAME, NAMESPACE, OPERATIONS_USED,
                        READ_ONLY_FIELDS, SERVICE_PATH, SUMMARY_FIELDS)

COMMON_NS = "http://core.godavarifinance.example/common"
DEAD_HOST = "http://corelend-dev01:7001"
VENDORED_PATH = Path(__file__).resolve().parents[1] / "wsdl" / "LendingService.wsdl"
VENDORED_CHANGES = (
    "removed <xsd:import> of common.xsd from corelend-dev01 (host unreachable); CoreError inlined into tns",
    "fault message part now references tns:CoreError instead of cmn:CoreError",
    "soap:address set to http://localhost/placeholder; the client always passes the real address",
)
_READ_ONLY = {f.name: f for f in READ_ONLY_FIELDS}


def _xsd_type(name: str) -> str:
    spec = FIELD_BY_NAME.get(name) or _READ_ONLY[name]
    return "xsd:decimal" if spec.kind == "N" else "xsd:string"


def _seq(names: tuple[str, ...], mandatory: set[str]) -> str:
    rows = []
    for n in names:
        occurs = "" if n in mandatory else ' minOccurs="0"'
        rows.append(f'          <xsd:element name="{n}" type="{_xsd_type(n)}"{occurs}/>')
    return "\n".join(rows)


def _wrapper(name: str, body: str) -> str:
    return (f'      <xsd:element name="{name}">\n        <xsd:complexType>\n          <xsd:sequence>\n'
            f"{body}\n          </xsd:sequence>\n        </xsd:complexType>\n      </xsd:element>")


def _simple(names_and_occurs: list[tuple[str, str, bool]]) -> str:
    rows = []
    for n, t, required in names_and_occurs:
        occurs = "" if required else ' minOccurs="0"'
        rows.append(f'            <xsd:element name="{n}" type="{t}"{occurs}/>')
    return "\n".join(rows)


def build_wsdl(served: bool) -> str:
    mandatory = {f.name for f in CREATE_APPLICATION_FIELDS if f.mandatory}
    app_fields = tuple(f.name for f in CREATE_APPLICATION_FIELDS)
    error_prefix = "cmn" if served else "tns"
    common_import = (f'      <xsd:import namespace="{COMMON_NS}" schemaLocation="{DEAD_HOST}/corelend/schemas/common.xsd"/>\n'
                     if served else "")
    core_error_type = "" if served else (
        '      <xsd:element name="CoreError">\n        <xsd:complexType>\n          <xsd:sequence>\n'
        '            <xsd:element name="Code" type="xsd:string"/>\n'
        '            <xsd:element name="Field" type="xsd:string" minOccurs="0"/>\n'
        '            <xsd:element name="Text" type="xsd:string" minOccurs="0"/>\n'
        "          </xsd:sequence>\n        </xsd:complexType>\n      </xsd:element>\n")
    types = f"""      <xsd:complexType name="ApplicationType">
        <xsd:sequence>
{_seq(app_fields, mandatory)}
        </xsd:sequence>
      </xsd:complexType>
      <xsd:complexType name="ApplicationSummaryType">
        <xsd:sequence>
{_seq(SUMMARY_FIELDS, {"FILE_NO", "BRANCH_CD", "APPL_STAT"})}
        </xsd:sequence>
      </xsd:complexType>
      <xsd:complexType name="ApplicationDetailType">
        <xsd:sequence>
{_seq(DETAIL_FIELDS, {"APPL_ID", "FILE_NO", "BRANCH_CD", "APPL_STAT"})}
        </xsd:sequence>
      </xsd:complexType>
{core_error_type}{_wrapper("CreateApplicationRequest", '            <xsd:element name="Application" type="tns:ApplicationType"/>')}
{_wrapper("CreateApplicationResponse", _simple([("APPL_ID", "xsd:string", True), ("APPL_STAT", "xsd:string", True)]))}
{_wrapper("GetApplicationByFileNumberRequest", _simple([("FILE_NO", "xsd:string", True)]))}
{_wrapper("GetApplicationByFileNumberResponse", '            <xsd:element name="ApplicationSummary" type="tns:ApplicationSummaryType" minOccurs="0" maxOccurs="unbounded"/>')}
{_wrapper("GetApplicationRequest", _simple([("APPL_ID", "xsd:string", True)]))}
{_wrapper("GetApplicationResponse", '            <xsd:element name="ApplicationDetail" type="tns:ApplicationDetailType"/>')}
{_wrapper("UpdateKYCStatusRequest", _simple([("APPL_ID", "xsd:string", True), ("KYC_STAT", "xsd:string", True), ("RSN_CD", "xsd:string", False), ("USR_ID", "xsd:string", True)]))}
{_wrapper("UpdateKYCStatusResponse", _simple([("APPL_ID", "xsd:string", True), ("KYC_STAT", "xsd:string", True), ("HIST_SEQ", "xsd:decimal", True)]))}"""
    messages = [f'  <wsdl:message name="CoreFault">\n    <wsdl:part name="fault" element="{error_prefix}:CoreError"/>\n  </wsdl:message>']
    port_ops, binding_ops = [], []
    for op in OPERATIONS_USED:
        messages.append(f'  <wsdl:message name="{op}Input">\n    <wsdl:part name="parameters" element="tns:{op}Request"/>\n  </wsdl:message>')
        messages.append(f'  <wsdl:message name="{op}Output">\n    <wsdl:part name="parameters" element="tns:{op}Response"/>\n  </wsdl:message>')
        port_ops.append(f'    <wsdl:operation name="{op}">\n      <wsdl:input message="tns:{op}Input"/>\n'
                        f'      <wsdl:output message="tns:{op}Output"/>\n      <wsdl:fault name="CoreFault" message="tns:CoreFault"/>\n'
                        f"    </wsdl:operation>")
        binding_ops.append(f'    <wsdl:operation name="{op}">\n      <soap:operation soapAction="urn:godavari:corelend:{op}"/>\n'
                           f'      <wsdl:input><soap:body use="literal"/></wsdl:input>\n'
                           f'      <wsdl:output><soap:body use="literal"/></wsdl:output>\n'
                           f'      <wsdl:fault name="CoreFault"><soap:fault name="CoreFault" use="literal"/></wsdl:fault>\n'
                           f"    </wsdl:operation>")
    address = f"{DEAD_HOST}{SERVICE_PATH}" if served else "http://localhost/placeholder"
    cmn_decl = f' xmlns:cmn="{COMMON_NS}"' if served else ""
    header = ("<!-- Godavari Finance core lending system, LendingService, generated 2009-11-02, last edited 2014-03-18 -->"
              if served else
              "<!-- Kaagaz vendored copy of Godavari's LendingService WSDL (stand-in). Changes from the served file:\n"
              + "\n".join(f"     - {c}" for c in VENDORED_CHANGES) + "\n     Reviewed with the core-system owner. Do not edit by hand: run wsdl_gen. -->")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
{header}
<wsdl:definitions xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/" xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:tns="{NAMESPACE}"{cmn_decl}
    targetNamespace="{NAMESPACE}" name="LendingService">
  <wsdl:types>
    <xsd:schema targetNamespace="{NAMESPACE}" elementFormDefault="qualified">
{common_import}{types}
    </xsd:schema>
  </wsdl:types>
{chr(10).join(messages)}
  <wsdl:portType name="LendingServicePortType">
{chr(10).join(port_ops)}
  </wsdl:portType>
  <wsdl:binding name="LendingServiceBinding" type="tns:LendingServicePortType">
    <soap:binding style="document" transport="http://schemas.xmlsoap.org/soap/http"/>
{chr(10).join(binding_ops)}
  </wsdl:binding>
  <wsdl:service name="LendingService">
    <wsdl:port name="LendingServicePort" binding="tns:LendingServiceBinding">
      <soap:address location="{address}"/>
    </wsdl:port>
  </wsdl:service>
</wsdl:definitions>
"""


def write_vendored(path: Path = VENDORED_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_wsdl(served=False), encoding="utf-8", newline="\n")
    return path


if __name__ == "__main__":
    print(f"wrote {write_vendored()}")
