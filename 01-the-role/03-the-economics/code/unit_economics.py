"""A unit-economics model of the Godavari engagement, for Kaagaz AI's CEO.

Answers one question with invented numbers: is Godavari worth an FDE? It compares the FDE model
(platform subscription plus a bounded deployment fee, an engineer on site for twelve weeks, the
pattern reused for the next lender) against a services model (a fixed-price custom build, every
customer from zero), over 36 months, and prints the measures the published FDE teams use:
revenue divided by FDE cost (Ramp's ratio), ARR per FDE head (Dataland's measure), and the
break-even month. Then it stresses the FDE model with the two things that usually go wrong.

Every rupee figure is invented for the course. Change the constants at the top and rerun.

Python 3.14, standard library only. Run from the chapter folder:

    python -X utf8 code/unit_economics.py
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path

LAKH = 100_000
MONTHS = 36

# ---- Kaagaz AI's side (invented) -------------------------------------------------------------
FDE_LOADED_COST_PER_YEAR = 60 * LAKH   # CTC plus travel, laptop, insurance, management share
SERVING_COST_SHARE = 0.22              # inference, support engineering, model gateway, per rupee of subscription
PRE_CONTRACT_INVESTMENT = 15 * LAKH    # eight weeks of discovery (Days 4 to 10) plus sales cost, before any invoice
RAMP_RATIO_FLOOR = 3.0                 # Kaagaz's own bar for revenue / FDE cost; not a published figure

# ---- The FDE model: subscription plus a bounded deployment fee ---------------------------------
SUBSCRIPTION_PER_YEAR = 120 * LAKH     # the platform, per lender, per year
DEPLOYMENT_FEE_FIRST = 36 * LAKH       # twelve weeks on site at Godavari, fixed
DEPLOYMENT_FEE_REPEAT = 20 * LAKH      # six weeks for a lender buying the proven pattern
FDE_WEEKS_FIRST = 12                   # full-time on site, first lender
FDE_WEEKS_REPEAT = 6                   # the pattern is product now
FDE_SHARE_AFTER_DEPLOY_Y1 = 0.20       # share of one FDE for the rest of year one (pilot support, fixes)
FDE_SHARE_STEADY = 0.10                # share of one FDE in later years (quarterly reviews, model updates)

# ---- The services model: a custom build, every customer from zero ------------------------------
CUSTOM_BUILD_PRICE = 180 * LAKH        # fixed price, nine months, three engineers
CUSTOM_BUILD_ENGINEER_MONTHS = 27      # 3 engineers x 9 months
CUSTOM_MAINTENANCE_PER_YEAR = 25 * LAKH
CUSTOM_MAINTENANCE_ENGINEER_SHARE = 0.5
CUSTOM_REPEAT_DISCOUNT = 0.75          # the second custom build costs and earns about three quarters of the first


@dataclass
class Month:
    revenue: float = 0.0
    serving_cost: float = 0.0
    fde_cost: float = 0.0
    fde_fte: float = 0.0
    arr: float = 0.0                   # annualised recurring revenue live in this month

    @property
    def contribution(self) -> float:
        return self.revenue - self.serving_cost - self.fde_cost


@dataclass
class Scenario:
    name: str
    months: list[Month] = field(default_factory=lambda: [Month() for _ in range(MONTHS)])

    def add_fde_subscription_customer(self, start: int, years: int, first: bool,
                                      weeks_on_site: int | None = None,
                                      share_y1: float | None = None,
                                      share_steady: float | None = None) -> None:
        """One lender on the FDE model from month `start` (0-based) for `years` years.

        The three optional arguments override the module constants for stress tests. They are
        resolved here, not as default values, so that editing a constant at the top and rerunning
        actually changes the result (a default argument is bound once, at definition time).
        """
        if weeks_on_site is None:
            weeks_on_site = FDE_WEEKS_FIRST
        if share_y1 is None:
            share_y1 = FDE_SHARE_AFTER_DEPLOY_Y1
        if share_steady is None:
            share_steady = FDE_SHARE_STEADY
        weeks = weeks_on_site if first else FDE_WEEKS_REPEAT
        fee = DEPLOYMENT_FEE_FIRST if first else DEPLOYMENT_FEE_REPEAT
        deploy_months = max(1, round(weeks / 4.33))
        for i in range(years * 12):
            m = start + i
            if m >= MONTHS:
                break
            month = self.months[m]
            month.revenue += SUBSCRIPTION_PER_YEAR / 12
            month.serving_cost += SUBSCRIPTION_PER_YEAR / 12 * SERVING_COST_SHARE
            month.arr += SUBSCRIPTION_PER_YEAR
            if i < deploy_months:
                month.revenue += fee / deploy_months
                fte = 1.0
            elif i < 12:
                fte = share_y1
            else:
                fte = share_steady
            month.fde_fte += fte
            month.fde_cost += fte * FDE_LOADED_COST_PER_YEAR / 12

    def add_custom_build_customer(self, start: int, years: int, first: bool) -> None:
        """One lender on the services model: a nine-month build, then a maintenance retainer."""
        scale = 1.0 if first else CUSTOM_REPEAT_DISCOUNT
        build_months = 9
        for i in range(years * 12):
            m = start + i
            if m >= MONTHS:
                break
            month = self.months[m]
            if i < build_months:
                month.revenue += CUSTOM_BUILD_PRICE * scale / build_months
                fte = CUSTOM_BUILD_ENGINEER_MONTHS * scale / build_months
            else:
                month.revenue += CUSTOM_MAINTENANCE_PER_YEAR * scale / 12
                month.arr += CUSTOM_MAINTENANCE_PER_YEAR * scale   # the only recurring part
                fte = CUSTOM_MAINTENANCE_ENGINEER_SHARE * scale
            month.fde_fte += fte
            month.fde_cost += fte * FDE_LOADED_COST_PER_YEAR / 12

    # ---- measures ----
    def total(self, attr: str) -> float:
        return sum(getattr(m, attr) for m in self.months)

    def break_even_month(self) -> int | None:
        cumulative = -PRE_CONTRACT_INVESTMENT
        for i, m in enumerate(self.months, start=1):
            cumulative += m.contribution
            if cumulative >= 0:
                return i
        return None

    def ramp_ratio(self) -> float:
        """Enterprise revenue divided by FDE cost (Ramp's measure)."""
        return self.total("revenue") / self.total("fde_cost")

    def arr_per_fde_head(self) -> float:
        """ARR live at month 36 divided by the FDE heads needed to keep it live (Dataland's measure)."""
        last = self.months[-1]
        return last.arr / last.fde_fte if last.fde_fte else 0.0

    def peak_fte(self) -> float:
        return max(m.fde_fte for m in self.months)


def build_scenarios() -> list[Scenario]:
    a = Scenario("A  Godavari, FDE model, no renewal")
    a.add_fde_subscription_customer(start=0, years=1, first=True)

    b = Scenario("B  Godavari renews for three years")
    b.add_fde_subscription_customer(start=0, years=3, first=True)

    c = Scenario("C  B plus two lenders buy the pattern")
    c.add_fde_subscription_customer(start=0, years=3, first=True)
    c.add_fde_subscription_customer(start=12, years=2, first=False)
    c.add_fde_subscription_customer(start=18, years=2, first=False)

    d = Scenario("D  Services: custom build, then two more")
    d.add_custom_build_customer(start=0, years=3, first=True)
    d.add_custom_build_customer(start=12, years=2, first=False)
    d.add_custom_build_customer(start=18, years=2, first=False)
    return [a, b, c, d]


def stress_tests() -> list[tuple[str, Scenario]]:
    """The two things that turn an FDE engagement into services, applied to scenario B."""
    crm = Scenario("B1 yes to the branch CRM: FDE full-time 36 mo")
    crm.add_fde_subscription_customer(0, 3, True, share_y1=1.0, share_steady=1.0)
    slip = Scenario("B2 30 weeks on site, same fee, and no renewal")
    slip.add_fde_subscription_customer(0, 1, True, weeks_on_site=30)
    return [("the custom work never ends", crm), ("the slip, and no renewal", slip)]


def crore(x: float) -> str:
    return f"{x / (100 * LAKH):6.2f} cr"


def print_table(scenarios: list[Scenario], title: str) -> None:
    print(f"== {title} (36 months, rupees, invented) ==")
    header = (f"{'scenario':<46} {'revenue':>8} {'FDE cost':>8} {'contrib.':>8} {'ARR m36':>8} "
              f"{'ARR/FDE':>8} {'rev/FDE':>7} {'peak FTE':>8} {'break-even':>10}")
    print(header)
    print("-" * len(header))
    for s in scenarios:
        be = s.break_even_month()
        be_text = f"month {be}" if be else "never"
        print(
            f"{s.name:<46} {crore(s.total('revenue')):>8} {crore(s.total('fde_cost')):>8} "
            f"{crore(s.total('contribution')):>8} {crore(s.months[-1].arr):>8} "
            f"{crore(s.arr_per_fde_head()):>8} {s.ramp_ratio():>6.1f}x {s.peak_fte():>8.2f} {be_text:>10}"
        )
    print()


def write_csv(scenarios: list[Scenario], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["scenario", "month", "revenue", "serving_cost", "fde_cost", "fde_fte", "arr", "contribution"])
        for s in scenarios:
            for i, m in enumerate(s.months, start=1):
                w.writerow([s.name.strip(), i, round(m.revenue), round(m.serving_cost), round(m.fde_cost),
                            round(m.fde_fte, 3), round(m.arr), round(m.contribution)])


def main() -> None:
    scenarios = build_scenarios()
    print("Assumptions (all invented): one FDE costs", crore(FDE_LOADED_COST_PER_YEAR).strip(), "a year fully loaded;",
          f"subscription {crore(SUBSCRIPTION_PER_YEAR).strip()} a year per lender; "
          f"first deployment fee {crore(DEPLOYMENT_FEE_FIRST).strip()};",
          f"serving cost {SERVING_COST_SHARE:.0%} of subscription; "
          f"pre-contract investment {crore(PRE_CONTRACT_INVESTMENT).strip()}.")
    print()
    print_table(scenarios, "Is Godavari worth an FDE?")

    print("How to read the columns:")
    print(f"  rev/FDE     revenue divided by FDE cost over 36 months (Ramp's ratio); "
          f"Kaagaz's own floor is {RAMP_RATIO_FLOOR:.1f}x")
    print("  ARR/FDE     recurring revenue live in month 36 per FDE head still needed (Dataland's measure)")
    print("  peak FTE    the most FDE capacity any single month needs; Kaagaz has four FDEs")
    print("  break-even  the month cumulative contribution covers the pre-contract investment")
    print()

    stressed = stress_tests()
    print_table([s for _, s in stressed], "What turns B into services")
    for label, s in stressed:
        verdict = ("still above the floor" if s.ramp_ratio() >= RAMP_RATIO_FLOOR
                   else "BELOW the floor: this is a services engagement wearing a subscription")
        print(f"  {label:<32} rev/FDE {s.ramp_ratio():.1f}x  {verdict}")
    print()

    b = scenarios[1]
    renew_value = sum(m.contribution for m in b.months[12:])
    print(f"The renewal is worth {crore(renew_value).strip()} of contribution in years two and three, on "
          f"{b.months[-1].fde_fte:.2f} FTE of FDE time. That is the number the engagement is run for.")
    for s in scenarios[:3]:
        print(f"  {s.name.strip():<42} rev/FDE {s.ramp_ratio():.1f}x  "
              f"{'above' if s.ramp_ratio() >= RAMP_RATIO_FLOOR else 'below'} the {RAMP_RATIO_FLOOR:.0f}x floor")

    out = Path(__file__).resolve().parent.parent / "data" / "godavari-unit-economics.csv"
    write_csv(scenarios + [s for _, s in stressed], out)
    print(f"\nwrote data/{out.name} ({(MONTHS * (len(scenarios) + len(stressed)))} rows)")


if __name__ == "__main__":
    main()
