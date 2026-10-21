"""Alerts, and who hears about each one. Most of them page nobody.

A page is for something that is hurting Godavari now and that the person paged can fix now. During the pilot that
is a short list, and Kaagaz carries it: the 02:00 job not finished when the queue opens, the trace store quarantining
a span (an identifier got past a validator), and a write the core and the journal disagree about. Everything else goes
into the morning digest at 08:30, to the person who owns the decision: the FDE for cost and drift, the team leads for
the queue and the analysts' signals, Godavari's IT for the group sync. The COO gets one page a week and no alerts.
Day 27 turns this into SLOs and an on-call rota across the two companies; this is the pilot's version.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

ROUTES: dict[str, tuple[str, str]] = {
    # rule: (how, who)
    "queue not ready": ("page", "Kaagaz FDE on call (pilot); Godavari application support informed"),
    "store quarantine": ("page", "Kaagaz FDE on call; the compliance head told the same day"),
    "core disagreement": ("page", "Kaagaz FDE on call with Godavari's application-support engineer"),
    "ceiling": ("digest", "Kaagaz FDE"),
    "spike": ("digest", "Kaagaz FDE"),
    "latency": ("digest", "Kaagaz FDE"),
    "forecast": ("weekly", "Kaagaz FDE; the COO's weekly page if it holds"),
    "field drift": ("digest", "Kaagaz FDE and the eval owners (Lakshmi, the senior analyst)"),
    "rule moved": ("digest", "Kaagaz FDE; the compliance head if a regulatory rule"),
    "session": ("digest", "the analyst's team lead only (Day 18's agreement; never HR)"),
    "override": ("weekly", "the analyst's team lead only"),
    "spot check": ("digest", "the team leads and the eval owners"),
    "directory stale": ("digest", "Godavari IT identity team; Kaagaz FDE copied"),
}


@dataclass
class Alert:
    rule: str
    day: date
    scope: str
    text: str
    traces: tuple[str, ...] = ()
    how: str = field(init=False)
    who: str = field(init=False)

    def __post_init__(self) -> None:
        self.how, self.who = ROUTES[self.rule]


def pages(alerts: list[Alert]) -> list[Alert]:
    return [a for a in alerts if a.how == "page"]
