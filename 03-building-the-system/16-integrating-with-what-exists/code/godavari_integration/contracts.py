"""Contract tests against a recorded sandbox: record once, replay on every build, diff the WSDL.

The sandbox is refreshed quarterly and is down whenever the core is; a build cannot depend on it. So:
  * record_sandbox.py calls the sandbox through the hand-built client, a session that records every
    request and response, and writes a cassette (identifiers scrubbed, even though the sandbox is masked).
  * Replay feeds those responses to both clients on every build (a session that answers from the
    cassette), so a parser change that would misread the core fails here, not at 02:00.
  * The structure of every request our clients build today is compared with the recorded one, element by
    element. The core silently ignores an element it does not know, so a renamed field shows up only here.
  * The served WSDL is reduced to a contract (operation, element path, minOccurs) and compared with the
    pinned one. A change on Godavari's side is a readable diff, not a 500 at night.
  * Known drift between sandbox and production is a list with owners and expiry dates (known_drift.toml).
"""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

CONTRACTS_DIR = Path(__file__).resolve().parents[1] / "contracts"
CASSETTE = CONTRACTS_DIR / "cassettes" / "sandbox-2026-11-10.json"
WSDL_CONTRACT = CONTRACTS_DIR / "wsdl-contract.json"
KNOWN_DRIFT = CONTRACTS_DIR / "known_drift.toml"
XSD = "http://www.w3.org/2001/XMLSchema"
SOAP_ENV = "http://schemas.xmlsoap.org/soap/envelope/"
SCRUB = {"APPL_NM": "SCRUBBED NAME", "PAN_NO": "AAAAA0000A", "MOB_NO": "9000000000", "APPL_DOB": "19800101",
         "ADDR_LN1": "1-1, SCRUBBED", "ADDR_LN2": "SCRUBBED", "AADH_REF": "XXXXXXXX0000", "Password": "********"}


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def scrub(xml_bytes: bytes) -> bytes:
    text = xml_bytes.decode("utf-8")
    for name, value in SCRUB.items():
        text = re.sub(rf"(<(?:\w+:)?{name}(?:\s[^>]*)?>)[^<]*(</(?:\w+:)?{name}>)", rf"\g<1>{value}\g<2>", text)
    return text.encode("utf-8")


def body_paths(xml_bytes: bytes) -> list[str]:
    """Element paths under the SOAP Body, in document order, local names only: the request's shape."""
    root = ET.fromstring(xml_bytes)
    body = root.find(f"{{{SOAP_ENV}}}Body")
    out: list[str] = []

    def walk(el: ET.Element, prefix: str) -> None:
        path = f"{prefix}/{_local(el.tag)}" if prefix else _local(el.tag)
        out.append(path)
        for child in el:
            walk(child, path)

    for child in (body if body is not None else []):
        walk(child, "")
    return out


# ---- recording and replay -------------------------------------------------------------------------------
@dataclass
class Exchange:
    scenario: str
    operation: str
    request: str
    status: int
    content_type: str
    response: str


class RecordingSession(requests.Session):
    def __init__(self) -> None:
        super().__init__()
        self.exchanges: list[Exchange] = []
        self.scenario = ""

    def post(self, url: str, data: Any = None, **kwargs: Any) -> requests.Response:   # type: ignore[override]
        resp = super().post(url, data=data, **kwargs)
        op = kwargs.get("headers", {}).get("SOAPAction", "").strip('"').rsplit(":", 1)[-1]
        self.exchanges.append(Exchange(self.scenario, op, scrub(data).decode(), resp.status_code,
                                       resp.headers.get("Content-Type", ""), scrub(resp.content).decode()))
        return resp


class ReplaySession(requests.Session):
    """Answers each POST from the cassette: the first unused exchange with the same operation and the same
    request shape (element paths). A request a client refuses to send simply never consumes one."""

    def __init__(self, exchanges: list[Exchange]) -> None:
        super().__init__()
        self.queue = list(exchanges)
        self.sent: list[bytes] = []

    def post(self, url: str, data: Any = None, **kwargs: Any) -> requests.Response:   # type: ignore[override]
        body = data if isinstance(data, bytes) else str(data).encode()
        self.sent.append(body)
        name = _local(ET.fromstring(body).find(f"{{{SOAP_ENV}}}Body")[0].tag)          # type: ignore[index]
        op = name.removesuffix("Request")
        shape = body_paths(body)
        for i, ex in enumerate(self.queue):
            if ex.operation == op and body_paths(ex.request.encode()) == shape:
                self.queue.pop(i)
                resp = requests.Response()
                resp.status_code = ex.status
                resp.headers["Content-Type"] = ex.content_type
                resp._content = ex.response.encode()
                resp.url = url
                return resp
        raise AssertionError(f"no recorded exchange left for {op} with this request shape")


def save_cassette(exchanges: list[Exchange], path: Path = CASSETTE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps([e.__dict__ for e in exchanges], indent=1) + "\n", encoding="utf-8", newline="\n")


def load_cassette(path: Path = CASSETTE) -> list[Exchange]:
    return [Exchange(**e) for e in json.loads(path.read_text(encoding="utf-8"))]


# ---- the WSDL as a contract ----------------------------------------------------------------------------
def wsdl_contract(wsdl_text: str, operations: tuple[str, ...]) -> dict[str, dict[str, list[list[str]]]]:
    root = ET.fromstring(wsdl_text.encode())
    schema = root.find(f".//{{{XSD}}}schema")
    assert schema is not None
    types = {t.get("name"): t for t in schema.findall(f"{{{XSD}}}complexType")}
    elements = {e.get("name"): e for e in schema.findall(f"{{{XSD}}}element")}

    def expand(el: ET.Element, prefix: str) -> list[list[str]]:
        rows: list[list[str]] = []
        seq = el.find(f"{{{XSD}}}complexType/{{{XSD}}}sequence")
        if seq is None and el.get("type", "").startswith("tns:"):
            t = types.get(el.get("type", "").split(":", 1)[1])
            seq = t.find(f"{{{XSD}}}sequence") if t is not None else None
        for child in (seq if seq is not None else []):
            path = f"{prefix}/{child.get('name')}"
            rows.append([path, child.get("minOccurs", "1"), child.get("type", "complex")])
            rows += expand(child, path)
        return rows

    out = {}
    for op in operations:
        out[op] = {"request": expand(elements[f"{op}Request"], f"{op}Request"),
                   "response": expand(elements[f"{op}Response"], f"{op}Response")}
    return out


def diff_contract(pinned: dict, current: dict) -> list[str]:
    changes = []
    for op in sorted(set(pinned) | set(current)):
        if op not in current:
            changes.append(f"{op}: operation removed")
            continue
        if op not in pinned:
            changes.append(f"{op}: operation added")
            continue
        for part in ("request", "response"):
            a = {r[0]: r[1:] for r in pinned[op][part]}
            b = {r[0]: r[1:] for r in current[op][part]}
            changes += [f"{op} {part}: {p} removed" for p in sorted(set(a) - set(b))]
            changes += [f"{op} {part}: {p} added (minOccurs {b[p][0]})" for p in sorted(set(b) - set(a))]
            changes += [f"{op} {part}: {p} minOccurs {a[p][0]} -> {b[p][0]}" for p in sorted(set(a) & set(b))
                        if a[p][0] != b[p][0]]
            changes += [f"{op} {part}: {p} type {a[p][1]} -> {b[p][1]}" for p in sorted(set(a) & set(b))
                        if a[p][1] != b[p][1]]
    return changes
