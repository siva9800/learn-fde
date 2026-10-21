"""The hand-built envelope: for the day the WSDL will not load, and for knowing what is on the wire.

No code generation. Each request is a string built from the data dictionary's field order, posted with
requests, and parsed with the standard library. It is more code than the zeep client and less forgiving,
which is the point: you see every element. Element names are checked against the data dictionary before
sending, because the 2009 core silently ignores an element it does not know (a typo is a lost field).
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

import requests

from ..clock import BusinessClock
from ..corespec import CREATE_APPLICATION_FIELDS, FIELD_BY_NAME, NAMESPACE
from .base import BaseCoreClient
from .errors import CoreUnavailable, ResponseUnreadable, fault_from_text
from .port import ApplicationSummary, CallLog, RateLimiter

SOAP_ENV = "http://schemas.xmlsoap.org/soap/envelope/"
WSSE = "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"
PASSWORD_TEXT = ("http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0"
                 "#PasswordText")
_ORDER = [f.name for f in CREATE_APPLICATION_FIELDS]


def _el(name: str, value: object) -> str:
    return f"<tns:{name}>{escape(str(value))}</tns:{name}>"


def build_request(operation: str, payload: dict, username: str, password: str) -> bytes:
    if operation == "CreateApplication":
        unknown = sorted(set(payload) - set(FIELD_BY_NAME))
        if unknown:
            raise ValueError(f"not in the data dictionary (the core would drop them silently): {unknown}")
        inner = "<tns:Application>" + "".join(_el(n, payload[n]) for n in _ORDER
                                              if payload.get(n) not in (None, "")) + "</tns:Application>"
    else:
        inner = "".join(_el(k, v) for k, v in payload.items() if v not in (None, ""))
    return (f'<?xml version="1.0" encoding="UTF-8"?>'
            f'<soapenv:Envelope xmlns:soapenv="{SOAP_ENV}" xmlns:tns="{NAMESPACE}">'
            f'<soapenv:Header><wsse:Security xmlns:wsse="{WSSE}"><wsse:UsernameToken>'
            f"<wsse:Username>{escape(username)}</wsse:Username>"
            f'<wsse:Password Type="{PASSWORD_TEXT}">{escape(password)}</wsse:Password>'
            f"</wsse:UsernameToken></wsse:Security></soapenv:Header>"
            f"<soapenv:Body><tns:{operation}Request>{inner}</tns:{operation}Request></soapenv:Body>"
            f"</soapenv:Envelope>").encode()


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parse_response(status: int, content_type: str, content: bytes) -> ET.Element:
    """The response element inside the body, or the right exception. Order matters: an HTML page is not a
    fault, and a fault is read from its detail before its text."""
    if "xml" not in (content_type or "").lower():
        raise CoreUnavailable(status, content.decode("utf-8", "replace"))
    try:
        root = ET.fromstring(content)
    except ET.ParseError as exc:
        raise ResponseUnreadable(f"reply is not well-formed XML: {exc}") from None
    body = root.find(f"{{{SOAP_ENV}}}Body")
    if body is None or len(body) == 0:
        raise CoreUnavailable(status, "SOAP envelope without a body")
    first = body[0]
    if _local(first.tag) == "Fault":
        code = first.findtext(f".//{{{NAMESPACE}}}Code")
        field = first.findtext(f".//{{{NAMESPACE}}}Field") or ""
        raise fault_from_text(first.findtext("faultstring") or "", code, field)
    if status != 200:
        raise CoreUnavailable(status, "non-200 without a fault")
    return first


def _children(elem: ET.Element) -> dict[str, str]:
    return {_local(c.tag): (c.text or "") for c in elem}


def summaries_from(elem: ET.Element) -> list[ApplicationSummary]:
    out = []
    for item in elem.findall(f"{{{NAMESPACE}}}ApplicationSummary"):
        d = _children(item)
        out.append(ApplicationSummary(d.get("APPL_ID", ""), d.get("FILE_NO", ""), d.get("BRANCH_CD", ""),
                                      d.get("APPL_STAT", ""), d.get("EXT_REF", ""), d.get("CRT_TS", "")))
    return out


class RawEnvelopeCorePort(BaseCoreClient):
    name = "raw-envelope"

    def __init__(self, url: str, username: str, password: str, *, timeout: float = 5.0,
                 connect_timeout: float = 2.0, limiter: RateLimiter | None = None, log: CallLog | None = None,
                 clock: BusinessClock | None = None, session: requests.Session | None = None) -> None:
        super().__init__(limiter=limiter, log=log, clock=clock)
        self.url, self.username, self.password = url, username, password
        self.timeout, self.connect_timeout = timeout, connect_timeout
        self.session = session or requests.Session()
        self.last_request: bytes = b""

    def _post(self, operation: str, payload: dict) -> ET.Element:
        data = build_request(operation, payload, self.username, self.password)
        self.last_request = data
        resp = self.session.post(self.url, data=data, timeout=(self.connect_timeout, self.timeout),
                                 headers={"Content-Type": "text/xml; charset=utf-8",
                                          "SOAPAction": f'"urn:godavari:corelend:{operation}"'})
        return parse_response(resp.status_code, resp.headers.get("Content-Type", ""), resp.content)

    def get_by_file_number(self, file_no: str) -> list[ApplicationSummary]:
        return self._call("GetApplicationByFileNumber", file_no,
                          lambda: summaries_from(self._post("GetApplicationByFileNumber", {"FILE_NO": file_no})))

    def create_application(self, fields: dict[str, str]) -> str:
        def go() -> str:
            resp = self._post("CreateApplication", fields)
            return resp.findtext(f"{{{NAMESPACE}}}APPL_ID") or ""
        return self._call("CreateApplication", str(fields.get("FILE_NO", "")), go)

    def get_application(self, appl_id: str) -> dict[str, str]:
        def go() -> dict[str, str]:
            detail = self._post("GetApplication", {"APPL_ID": appl_id}).find(f"{{{NAMESPACE}}}ApplicationDetail")
            return _children(detail) if detail is not None else {}
        return self._call("GetApplication", appl_id, go)

    def update_kyc_status(self, appl_id: str, status: str, user: str, reason: str = "") -> int:
        def go() -> int:
            resp = self._post("UpdateKYCStatus", {"APPL_ID": appl_id, "KYC_STAT": status, "RSN_CD": reason,
                                                  "USR_ID": user})
            return int(float(resp.findtext(f"{{{NAMESPACE}}}HIST_SEQ") or "0"))
        return self._call("UpdateKYCStatus", appl_id, go)
