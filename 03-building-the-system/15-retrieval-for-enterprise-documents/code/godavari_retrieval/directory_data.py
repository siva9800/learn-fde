"""Two synthetic nightly group snapshots, as the IT identity team's export would provide them (Day 22 owns
the real source). Wednesday 25 and Thursday 26 November 2026, 02:00. Between them, one Kukatpally credit
officer transfers to Guntur; nothing in the index changes, and his results do.

The Vijayawada team sees its region's branches (Vijayawada-Benz Circle, Guntur, Rajahmundry); the Hyderabad
team sees Kukatpally, Dilsukhnagar and Warangal (the same split as Day 11's run_batch.py). There is no
all-branches group: the compliance desk's six branch groups are typed in one by one, as the CISO described.
The retrieval service account starts with no groups at all (Day 6, finding A1).
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from .day11 import BRANCH_AD_GROUP
from .metadata import ROLE_BRANCH, ROLE_COMPLIANCE, ROLE_CREDITOPS

HYD = [BRANCH_AD_GROUP[b] for b in ("Kukatpally", "Dilsukhnagar", "Warangal")]
VJW = [BRANCH_AD_GROUP[b] for b in ("Vijayawada-Benz Circle", "Guntur", "Rajahmundry")]

SNAPSHOT_1 = datetime(2026, 11, 25, 2, 0)
SNAPSHOT_2 = datetime(2026, 11, 26, 2, 0)


def members(transferred: bool) -> dict[str, list[str]]:
    officer = [ROLE_BRANCH, BRANCH_AD_GROUP["Guntur" if transferred else "Kukatpally"]]
    return {
        "lakshmi": [ROLE_CREDITOPS, *VJW],               # Vijayawada; works the Guntur pilot queue
        "bhavani": [ROLE_CREDITOPS, *VJW],
        "srinivas": [ROLE_CREDITOPS, *HYD],              # Hyderabad team lead
        "analyst.hyd.07": [ROLE_CREDITOPS, *HYD],        # a Hyderabad analyst on the Kukatpally pilot queue
        "kkp.credit.officer": officer,                   # a branch user: one branch, plus the branch-staff role
        "compliance.desk.01": [ROLE_COMPLIANCE, *BRANCH_AD_GROUP.values()],
        "svc-kaagaz-retrieval": [],
    }


def write_snapshots(folder: Path) -> list[Path]:
    paths = []
    for taken, transferred in ((SNAPSHOT_1, False), (SNAPSHOT_2, True)):
        p = folder / f"ad-groups-{taken:%Y-%m-%d}.json"
        p.write_text(json.dumps({"taken_at": taken.isoformat(timespec="minutes"),
                                 "source": "nightly HR to AD export (synthetic)",
                                 "members": members(transferred)}, indent=2) + "\n", encoding="utf-8", newline="\n")
        paths.append(p)
    return paths
