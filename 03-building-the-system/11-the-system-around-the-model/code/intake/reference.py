"""Reference data: the lookups and joins the model must never be asked to remember.

Branch codes, empanelled dealers and the gold rate table are Godavari's data, owned by Godavari's
people, changed on Godavari's schedule. In production they are read from the core system or a table the
treasury publishes (Day 16); here they are synthetic constants. All values are invented.
"""

from __future__ import annotations

from datetime import date, timedelta

BRANCH_CODES: dict[str, str] = {
    "Kukatpally": "KKP01",
    "Dilsukhnagar": "DSN02",
    "Vijayawada-Benz Circle": "VJB03",
    "Guntur": "GNT04",
    "Warangal": "WGL05",
    "Rajahmundry": "RJY06",
}

# Active Directory group per branch (Day 6, finding A1). There is no all-branches group.
BRANCH_AD_GROUP: dict[str, str] = {name: f"GF-BR-{code}" for name, code in BRANCH_CODES.items()}

EMPANELLED_DEALERS: dict[str, tuple[str, str]] = {
    # dealer code: (name, branch)
    "DLR-KKP-014": ("Sri Sai Motors", "Kukatpally"),
    "DLR-KKP-022": ("Pragathi Two Wheelers", "Kukatpally"),
    "DLR-DSN-007": ("Lakshmi Ganapathi Auto", "Dilsukhnagar"),
    "DLR-VJB-031": ("Krishna Wheels", "Vijayawada-Benz Circle"),
    "DLR-VJB-035": ("Benz Circle Motors", "Vijayawada-Benz Circle"),
    "DLR-GNT-011": ("Amaravathi Automobiles", "Guntur"),
    "DLR-WGL-004": ("Kakatiya Motors", "Warangal"),
    "DLR-RJY-019": ("Godavari Bikes", "Rajahmundry"),
}


def _gold_rates() -> dict[date, int]:
    """Synthetic 22-carat rate in rupees per gram, one per calendar day, as Godavari's treasury would
    publish it under its board-approved pricing method. Invented numbers, smooth on purpose."""
    start = date(2026, 10, 1)
    rates: dict[date, int] = {}
    for i in range(61):
        day = start + timedelta(days=i)
        rates[day] = 11_200 + 6 * i + (15 if i % 7 == 3 else 0)
    return rates


GOLD_RATE_22K_PER_GRAM: dict[date, int] = _gold_rates()


def gold_rate_on(day: date) -> int | None:
    """The published rate for that day, or None. Never interpolated, never guessed."""
    return GOLD_RATE_22K_PER_GRAM.get(day)
