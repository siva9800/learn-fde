"""The generated client: zeep reads the vendored WSDL and builds every envelope from it.

Three production decisions are in this file:
  * The WSDL is loaded from the repository, never from the network at run time. OfflineTransport refuses
    any http(s) schema location that is not this machine, so a WSDL that imports from a dead host fails
    loudly at start-up instead of hanging for five minutes (zeep's default load timeout is 300 seconds).
  * The service address is passed explicitly. The WSDL's soap:address is a 2009 developer's host name.
  * zeep's exceptions never leave this module. Callers get CoreFault, CoreUnavailable, NotSent or
    AmbiguousOutcome, the same as from the hand-built client.
"""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

import requests
from zeep import Client, Settings
from zeep.exceptions import Fault, TransportError, ValidationError, XMLParseError, XMLSyntaxError
from zeep.helpers import serialize_object
from zeep.transports import Transport
from zeep.wsse.username import UsernameToken

from ..clock import BusinessClock
from ..corespec import NAMESPACE
from ..standin.wsdl_gen import VENDORED_PATH
from .base import BaseCoreClient
from .errors import CoreUnavailable, RefusedBeforeSending, ResponseUnreadable, fault_from_text
from .port import ApplicationSummary, CallLog, RateLimiter

BINDING = f"{{{NAMESPACE}}}LendingServiceBinding"
LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}


class WsdlFetchRefused(RuntimeError):
    pass


class OfflineTransport(Transport):
    """Loads schemas only from files or this machine. A WSDL that reaches for another host is a defect
    to fix in the vendored copy, not a request to make at three in the morning."""

    def load(self, url: str) -> bytes:
        parsed = urlparse(url)
        if parsed.scheme in ("http", "https") and parsed.hostname not in LOCAL_HOSTS:
            raise WsdlFetchRefused(f"refusing to fetch {url} at run time; vendor it (see wsdl_gen.VENDORED_CHANGES)")
        return super().load(url)


def _text(value: object) -> str:
    if value is None:
        return ""
    s = str(value)
    return s[:-2] if s.endswith(".0") and s.replace(".", "", 1).isdigit() else s


class ZeepCorePort(BaseCoreClient):
    name = "zeep"

    def __init__(self, url: str, username: str, password: str, *, wsdl: Path | str = VENDORED_PATH,
                 timeout: float = 5.0, limiter: RateLimiter | None = None, log: CallLog | None = None,
                 clock: BusinessClock | None = None, transport: Transport | None = None) -> None:
        super().__init__(limiter=limiter, log=log, clock=clock)
        transport = transport or OfflineTransport(timeout=5, operation_timeout=timeout)
        self.client = Client(str(wsdl), transport=transport, wsse=UsernameToken(username, password),
                             settings=Settings(strict=True))
        self.service = self.client.create_service(BINDING, url)

    def _invoke(self, operation: str, **kwargs: object) -> object:
        try:
            return getattr(self.service, operation)(**kwargs)
        except Fault as fault:
            if fault.code is None and not hasattr(fault.detail, "findtext"):
                # zeep's "Unknown fault occured": a non-200 reply with no SOAP Fault in it, such as the load
                # balancer's HTML maintenance page. Not a business error; the core never saw the request.
                raw = fault.detail if isinstance(fault.detail, bytes) else b""
                raise CoreUnavailable(0, raw.decode("utf-8", "replace") or str(fault.message)) from None
            code = field = None
            if fault.detail is not None:
                code = fault.detail.findtext(f".//{{{NAMESPACE}}}Code")
                field = fault.detail.findtext(f".//{{{NAMESPACE}}}Field")
            raise fault_from_text(fault.message or "", code, field or "") from None
        except ValidationError as exc:         # the WSDL says mandatory: refused before the network
            field = str(exc.path[-1]) if getattr(exc, "path", None) else ""
            raise RefusedBeforeSending(field, f"{operation}: {exc.message}") from None
        except (XMLParseError, XMLSyntaxError) as exc:   # it answered; the answer breaks the contract
            raise ResponseUnreadable(f"{operation}: {exc}") from None
        except TransportError as exc:          # an HTML page, a proxy error: the core never answered
            raise CoreUnavailable(exc.status_code, (exc.content or b"").decode("utf-8", "replace")) from None

    def get_by_file_number(self, file_no: str) -> list[ApplicationSummary]:
        def go() -> list[ApplicationSummary]:
            result = serialize_object(self._invoke("GetApplicationByFileNumber", FILE_NO=file_no))
            items = result if isinstance(result, list) else (result or {}).get("ApplicationSummary") or []
            return [ApplicationSummary(_text(i.get("APPL_ID")), _text(i.get("FILE_NO")), _text(i.get("BRANCH_CD")),
                                       _text(i.get("APPL_STAT")), _text(i.get("EXT_REF")), _text(i.get("CRT_TS")))
                    for i in items]
        return self._call("GetApplicationByFileNumber", file_no, go)

    def create_application(self, fields: dict[str, str]) -> str:
        def go() -> str:
            result = serialize_object(self._invoke("CreateApplication",
                                                   Application={k: v for k, v in fields.items() if v not in (None, "")}))
            return _text(result["APPL_ID"])
        return self._call("CreateApplication", str(fields.get("FILE_NO", "")), go)

    def get_application(self, appl_id: str) -> dict[str, str]:
        def go() -> dict[str, str]:
            result = serialize_object(self._invoke("GetApplication", APPL_ID=appl_id))
            detail = result if "APPL_ID" in (result or {}) else (result or {}).get("ApplicationDetail") or {}
            return {k: _text(v) for k, v in dict(detail).items() if v is not None}
        return self._call("GetApplication", appl_id, go)

    def update_kyc_status(self, appl_id: str, status: str, user: str, reason: str = "") -> int:
        def go() -> int:
            result = serialize_object(self._invoke("UpdateKYCStatus", APPL_ID=appl_id, KYC_STAT=status,
                                                   RSN_CD=reason or None, USR_ID=user))
            return int(result["HIST_SEQ"])
        return self._call("UpdateKYCStatus", appl_id, go)


def make_port(kind: str, url: str, username: str, password: str, **kwargs: object) -> BaseCoreClient:
    """'zeep' or 'raw'. The writer, the reconciliation and the tests take either."""
    if kind == "zeep":
        return ZeepCorePort(url, username, password, **kwargs)        # type: ignore[arg-type]
    from .raw_client import RawEnvelopeCorePort
    kwargs.pop("transport", None)
    return RawEnvelopeCorePort(url, username, password, **kwargs)     # type: ignore[arg-type]


__all__ = ["OfflineTransport", "WsdlFetchRefused", "ZeepCorePort", "make_port", "requests"]
