"""The stand-in's HTTP face: SOAP 1.1 over HTTP on localhost, the way the 2009 core speaks over HTTPS.

  GET  /corelend/services/LendingService?wsdl   the served WSDL (with its two defects)
  POST /corelend/services/LendingService        one SOAP envelope in, one out; faults are HTTP 500
  during maintenance                            HTTP 503 with an HTML page from the load balancer,
                                                not a SOAP fault: clients must cope with both

WS-Security UsernameToken (PasswordText) in the header, as the real one requires. Localhost only: the
course runs offline, and the real core is reached over the customer's network, never the internet.
"""

from __future__ import annotations

import threading
import xml.etree.ElementTree as ET
from collections.abc import Iterator
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from xml.sax.saxutils import escape

from ..corespec import NAMESPACE, OPERATIONS_USED, SERVICE_PATH
from .core import CoreFaultError, CoreStandIn
from .wsdl_gen import build_wsdl

SOAP_ENV = "http://schemas.xmlsoap.org/soap/envelope/"
WSSE = "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"
MAINTENANCE_PAGE = (b"<html><head><title>503 Service Unavailable</title></head><body><h1>Service Unavailable</h1>"
                    b"<p>CORELEND is down for scheduled maintenance. Please try after 09:00.</p></body></html>")


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _to_dict(elem: ET.Element) -> dict:
    out: dict = {}
    for child in elem:
        name = _local(child.tag)
        out[name] = _to_dict(child) if len(child) else (child.text or "")
    return out


def _xml(name: str, value: object) -> str:
    if isinstance(value, dict):
        inner = "".join(_xml(k, v) for k, v in value.items())
        return f"<tns:{name}>{inner}</tns:{name}>"
    if isinstance(value, list):
        return "".join(_xml(name, v) for v in value)
    return f"<tns:{name}>{escape(str(value))}</tns:{name}>"


def envelope(body: str) -> bytes:
    return (f'<?xml version="1.0" encoding="UTF-8"?><soap:Envelope xmlns:soap="{SOAP_ENV}">'
            f"<soap:Body>{body}</soap:Body></soap:Envelope>").encode()


def response_envelope(operation: str, result: dict) -> bytes:
    inner = "".join(_xml(k, v) for k, v in result.items())
    return envelope(f'<tns:{operation}Response xmlns:tns="{NAMESPACE}">{inner}</tns:{operation}Response>')


def fault_envelope(fault: CoreFaultError) -> bytes:
    field = f"<tns:Field>{escape(fault.field)}</tns:Field>" if fault.field else ""
    return envelope(f"<soap:Fault><faultcode>soap:{fault.side}</faultcode><faultstring>{escape(fault.faultstring)}"
                    f'</faultstring><detail><tns:CoreError xmlns:tns="{NAMESPACE}"><tns:Code>{fault.code}</tns:Code>'
                    f"{field}</tns:CoreError></detail></soap:Fault>")


def parse_request(raw: bytes) -> tuple[str | None, str | None, str, dict]:
    root = ET.fromstring(raw)
    header = root.find(f"{{{SOAP_ENV}}}Header")
    username = password = None
    if header is not None:
        token = header.find(f".//{{{WSSE}}}UsernameToken")
        if token is not None:
            username = token.findtext(f"{{{WSSE}}}Username")
            password = token.findtext(f"{{{WSSE}}}Password")
    body = root.find(f"{{{SOAP_ENV}}}Body")
    if body is None or len(body) == 0:
        raise ValueError("no SOAP body")
    request = body[0]
    name = _local(request.tag)
    operation = name[: -len("Request")] if name.endswith("Request") else name
    return username, password, operation, _to_dict(request)


def make_handler(core: CoreStandIn) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *args: object) -> None:      # the access log is the core's, not stderr
            return

        def _send(self, status: int, payload: bytes, content_type: str = "text/xml; charset=utf-8") -> None:
            try:
                self.send_response(status)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                pass                                      # the caller timed out and left; the work is done

        def do_GET(self) -> None:
            if self.path.startswith(SERVICE_PATH) and self.path.lower().endswith("?wsdl"):
                self._send(200, core_wsdl(core).encode())
            else:
                self._send(404, b"not found", "text/plain")

        def do_POST(self) -> None:
            raw = self.rfile.read(int(self.headers.get("Content-Length", "0")))
            if not self.path.startswith(SERVICE_PATH):
                self._send(404, b"not found", "text/plain")
                return
            if core.in_maintenance():
                self._send(503, MAINTENANCE_PAGE, "text/html")
                return
            try:
                username, password, operation, body = parse_request(raw)
            except (ET.ParseError, ValueError):
                self._send(400, b"<html><body>Bad Request</body></html>", "text/html")
                return
            try:
                account = core.authenticate(username, password)
                if operation not in OPERATIONS_USED:
                    raise CoreFaultError("CL-E041", "operation", operation)
                result = core.handle(account, operation, body)
            except CoreFaultError as fault:
                self._send(500, fault_envelope(fault))
                return
            self._send(200, response_envelope(operation, result))

    return Handler


def core_wsdl(core: CoreStandIn) -> str:
    return getattr(core, "served_wsdl_override", None) or build_wsdl(served=True)


class _QuietServer(ThreadingHTTPServer):
    daemon_threads = True

    def handle_error(self, request: object, client_address: object) -> None:
        """A client that timed out and closed its socket is normal here, not an error worth a traceback."""
        import sys
        if isinstance(sys.exc_info()[1], (ConnectionAbortedError, ConnectionResetError, BrokenPipeError)):
            return
        super().handle_error(request, client_address)


@contextmanager
def running(core: CoreStandIn) -> Iterator[str]:
    """Start the stand-in on a free localhost port; yields the service URL."""
    server = _QuietServer(("127.0.0.1", 0), make_handler(core))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}{SERVICE_PATH}"
    finally:
        server.shutdown()
        server.server_close()
