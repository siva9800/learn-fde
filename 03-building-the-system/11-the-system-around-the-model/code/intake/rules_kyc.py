"""KYC rules shared by every product: what proves an address, how old it may be, and the Aadhaar mask.

DRAFT v0.3 of Godavari's acceptable-alternatives list, written with the compliance head in week 2
(finding A7: "in my head and in Lakshmi's"). The list is data in code, so that she reads one table, and
a change to it is a diff she signs. Everything here is synthetic; the RBI references are to the KYC
Master Direction (2016, as amended), whose current text the compliance head is the owner of.
"""

from __future__ import annotations

from .catalogue import Doc
from .ruleset import Action, Finding, Kind, RuleContext
from .validators import find_unmasked_aadhaar, parse_date

# Officially valid documents (OVDs) that prove address when they carry the current address.
OVD_ADDRESS_PROOFS: frozenset[str] = frozenset({"passport", "driving licence", "voter id", "aadhaar (masked)"})

# Godavari's signed alternatives, with the condition each one carries. Anything not here is not accepted:
# the analyst does not decide, the branch is told which rule fired.
SIGNED_ALTERNATIVES: dict[str, str] = {
    "electricity bill": "in the applicant's own name, dated within 60 days of the application",
    "property tax receipt": "in the applicant's own name, for the current or previous year",
    "registered rent agreement": "registered, in the applicant's own name, current on the application date",
}
UTILITY_BILL_MAX_AGE_DAYS = 60


def address_proof_acceptable(ctx: RuleContext, rule_id: str) -> list[Finding]:
    found = ctx.documents.get(Doc.PROOF_OF_ADDRESS)
    if found is None:
        return []                                  # absence is the completeness rule's finding, not this one
    kind = found.attributes.get("kind", "").lower()
    holder = found.attributes.get("holder", "").lower()
    if kind in OVD_ADDRESS_PROOFS or kind in SIGNED_ALTERNATIVES:
        if holder != "self":
            return [Finding(rule_id, Kind.REGULATORY, Action.SEND_BACK,
                            f"address proof '{kind}' is in the name of the applicant's {holder or 'unknown'}; "
                            "the signed list accepts it only in the applicant's own name", doc=Doc.PROOF_OF_ADDRESS)]
        return []
    return [Finding(rule_id, Kind.REGULATORY, Action.SEND_BACK,
                    f"address proof '{kind}' is not an OVD and not on the signed alternatives list v0.3",
                    doc=Doc.PROOF_OF_ADDRESS)]


def address_proof_fresh(ctx: RuleContext, rule_id: str) -> list[Finding]:
    found = ctx.documents.get(Doc.PROOF_OF_ADDRESS)
    if found is None or found.attributes.get("kind", "").lower() != "electricity bill":
        return []
    bill = parse_date(found.attributes.get("date"))
    applied = parse_date(ctx.value("application_date"))
    if bill is None or applied is None:
        return [Finding(rule_id, Kind.REGULATORY, Action.REVIEW,
                        "utility bill or application date unreadable; the age rule cannot be checked",
                        doc=Doc.PROOF_OF_ADDRESS)]
    age = (applied - bill).days
    if age > UTILITY_BILL_MAX_AGE_DAYS or age < 0:
        return [Finding(rule_id, Kind.REGULATORY, Action.SEND_BACK,
                        f"utility bill is {age} days old on the application date; the limit is "
                        f"{UTILITY_BILL_MAX_AGE_DAYS}", doc=Doc.PROOF_OF_ADDRESS)]
    return []


def aadhaar_masked(ctx: RuleContext, rule_id: str) -> list[Finding]:
    """Scans every page's text, not only the pages the model labelled. The model's opinion is not needed
    to find a 12-digit number with a valid check digit."""
    pages = [p.number for p in ctx.bundle.pages if find_unmasked_aadhaar(p.text)]
    if pages:
        return [Finding(rule_id, Kind.REGULATORY, Action.BLOCK,
                        f"an unmasked Aadhaar number is visible on page(s) {', '.join(map(str, pages))}; "
                        "the copy must be masked to the last four digits before the file is held")]
    return []
