"""What can come back from a call to the core, sorted by the only question that matters for a write:
did it happen?

  CoreFault          the core answered with a SOAP fault. It did not do the work. Retry only the codes
                     the catalogue marks retryable (CL-E017 batch window, CL-E099 busy), and only later.
  CoreUnavailable    something in front of the core answered (HTTP 503 maintenance page, a proxy error).
                     The core never saw the request. Safe to retry later.
  NotSent            the connection was never made (refused, DNS, connect timeout). Safe to retry.
  AmbiguousOutcome   the request was sent and no answer came (read timeout, connection dropped mid-reply).
                     The work may or may not have happened. A write must NEVER be retried blindly; it is
                     resolved by looking it up after a quiet period (writer.SafeCoreWriter).
"""

from __future__ import annotations

import re

from ..corespec import FAULTS

FAULT_CODE = re.compile(r"\b(CL-E\d{3})\b")


class CoreError(Exception):
    """Base class: anything that went wrong talking to the core."""


class CoreFault(CoreError):
    def __init__(self, code: str, faultstring: str, field: str = "") -> None:
        self.code = code
        self.faultstring = faultstring
        self.field = field
        self.retryable = FAULTS.get(code, ("", False, ""))[1]
        super().__init__(faultstring)


class CoreUnavailable(CoreError):
    def __init__(self, status: int, snippet: str) -> None:
        self.status = status
        super().__init__(f"HTTP {status}: {snippet[:80]}")


class NotSent(CoreError):
    pass


class AmbiguousOutcome(CoreError):
    pass


class RefusedBeforeSending(CoreError):
    """Our side refused to send: the generated client checks the WSDL's minOccurs before the network."""

    def __init__(self, field: str, message: str) -> None:
        self.code, self.field = "WSDL-MINOCCURS", field
        super().__init__(message)


class ResponseUnreadable(AmbiguousOutcome):
    """The core answered and we could not parse the answer. For a read it is a contract break; for a write
    it is ambiguous, because the work was probably done."""


def fault_from_text(faultstring: str, code_hint: str | None = None, field: str = "") -> CoreFault:
    """The code is in the detail when the core remembers to send it, and always at the start of the
    faultstring. Read the detail first, the text second, and never the HTTP status."""
    code = code_hint or (m.group(1) if (m := FAULT_CODE.search(faultstring or "")) else "CL-UNKNOWN")
    return CoreFault(code, faultstring or "", field)
