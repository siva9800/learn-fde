"""Step 3 of the decomposition method, as code: a synthetic "inputs inventory" for Godavari Finance.

Writes two CSV files into ../data/ and prints the summary an FDE would read out in step 3:

  * godavari_inputs_inventory.csv   one row per input source (shape, owner, freshness, access, what is missing)
  * godavari_loan_file_sample.csv   200 synthetic loan files from a two-week sample, one row per file

Everything is invented. Godavari Finance, its branches, systems and people do not exist. Python 3.14,
standard library only. Run from the chapter folder:

    python -X utf8 code/inputs_inventory.py
"""

from __future__ import annotations

import csv
import random
from collections import Counter
from dataclasses import asdict, dataclass, fields
from pathlib import Path

SEED = 7
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@dataclass(frozen=True)
class InputSource:
    """One row of the step-3 inventory: what the data is, who owns it, how fresh, how reachable, what is missing."""

    name: str
    kind: str            # document, api, file, directory, spreadsheet, chat
    shape: str           # what one unit looks like
    volume: str          # how much, how often
    owner: str           # the person or team who can say yes
    freshness: str       # how stale it may be when we read it
    access: str          # how we get to it today, and what is needed
    missing: str         # what is not there, or not trustworthy
    architecture_risk: str   # the question whose answer changes the design


INVENTORY: list[InputSource] = [
    InputSource(
        name="Loan application PDFs",
        kind="document",
        shape="scanned PDF, 8 to 40 pages, mixed English and Telugu forms, 150 to 300 dpi, some phone photos",
        volume="about 2,400 files a month across 300 branches; 60 percent arrive as paper or PDF",
        owner="branch operations (collected by the branch manager, read by credit-ops)",
        freshness="arrives in a nightly SFTP batch; a file can wait up to 24 hours before an analyst sees it",
        access="SFTP server in the on-prem data centre; read-only service account needs a ticket from IT",
        missing="no index of which document is on which page; 31 percent of files lack at least one mandatory KYC document",
        architecture_risk="page order and document type are not labelled, so classification is a workstream, not a detail",
    ),
    InputSource(
        name="Core lending system (2009) SOAP API",
        kind="api",
        shape="WSDL with 14 operations; CreateApplication takes 61 fields, 23 mandatory; XML in, XML out",
        volume="one call per loan file; a nightly batch applies status changes",
        owner="the core-system owner (one engineer, 14 years on the system, has watched three vendors fail)",
        freshness="writes are visible after the nightly batch, not immediately",
        access="sandbox exists but is refreshed quarterly; production write access needs the CISO and the owner",
        missing="no idempotency on CreateApplication: a retry creates a duplicate record",
        architecture_risk="duplicate records on retry means the integration layer must own idempotency before any automation",
    ),
    InputSource(
        name="File status Excel tracker",
        kind="spreadsheet",
        shape="one workbook per analyst team, one row per file, 19 columns, free-text status, colour coding carries meaning",
        volume="about 40 workbooks, updated by hand several times a day",
        owner="the credit-ops team lead in Vijayawada",
        freshness="minutes to hours; it is the true source of where a file is",
        access="a shared network drive; no API; analysts will not give it up until the tool replaces it",
        missing="no timestamps on status changes, so the baseline turnaround has to be sampled by hand",
        architecture_risk="the tracker is the real workflow state; the tool must read and write it or it will be ignored",
    ),
    InputSource(
        name="Active Directory groups",
        kind="directory",
        shape="group per branch and per role, synced nightly from HR",
        volume="about 1,400 users, 330 groups",
        owner="corporate IT (identity team)",
        freshness="nightly sync; a transfer between branches can lag a day",
        access="LDAP read for service accounts after a security review; no SSO integration exists for vendors today",
        missing="no group for 'may see all branches'; the ops lead's cross-branch view is a manual exception",
        architecture_risk="branch managers must not see other branches' files: every query must filter by the caller's groups",
    ),
    InputSource(
        name="WhatsApp photos from branch staff",
        kind="chat",
        shape="JPEG photos of individual pages, often cropped, sent to an analyst's personal number",
        volume="unknown; analysts estimate 1 in 5 files has at least one page that arrived this way",
        owner="nobody; it is an unofficial channel",
        freshness="same day, but it never reaches the SFTP batch",
        access="none, and the compliance head will not allow it as an input",
        missing="the pages are not in the file of record; the completeness check will flag them as missing",
        architecture_risk="an input that cannot be used is still an input you must plan around: the tool must make resubmission easy",
    ),
    InputSource(
        name="RBI KYC document rules",
        kind="document",
        shape="the RBI Master Direction on KYC plus Godavari's internal checklist per loan product",
        volume="one checklist per product (8 products); changes a few times a year",
        owner="the compliance head",
        freshness="changes by RBI notification; the internal checklist lags by weeks",
        access="public for RBI; the internal checklist lives in a Word document on the compliance drive",
        missing="the internal checklist does not say which alternatives are acceptable (for example, which address proofs)",
        architecture_risk="the completeness rules must be deterministic code the compliance head signs, not model behaviour",
    ),
    InputSource(
        name="Historical decisions (approved, sent back, rejected)",
        kind="file",
        shape="status history in the core system plus send-back reasons typed by analysts in the tracker",
        volume="about 28,000 files over the last year",
        owner="credit-ops (data), the core-system owner (extraction)",
        freshness="historical; useful for the baseline and the golden set, not for serving",
        access="a report the core-system owner runs on request",
        missing="send-back reasons are free text with no categories; the field-level ground truth does not exist and must be labelled",
        architecture_risk="no labelled ground truth means the eval set is a workstream with customer experts, not a download",
    ),
]


@dataclass(frozen=True)
class LoanFile:
    """One synthetic loan file from the two-week baseline sample."""

    file_id: str
    branch: str
    product: str
    channel: str          # sftp_scan, phone_photo, mixed
    pages: int
    language_mix: str     # english, telugu, mixed
    has_pan: bool
    has_address_proof: bool
    has_income_proof: bool
    has_photo: bool
    turnaround_days: float
    sent_back: bool
    analyst_hours: float


BRANCHES = ["Kukatpally", "Dilsukhnagar", "Vijayawada-Benz Circle", "Guntur", "Warangal", "Rajahmundry"]
PRODUCTS = ["two-wheeler", "gold", "small-business", "personal"]


def make_loan_files(n: int, rng: random.Random) -> list[LoanFile]:
    files: list[LoanFile] = []
    for i in range(n):
        branch = rng.choice(BRANCHES)
        product = rng.choices(PRODUCTS, weights=[40, 25, 20, 15])[0]
        channel = rng.choices(["sftp_scan", "phone_photo", "mixed"], weights=[60, 15, 25])[0]
        pages = rng.randint(8, 40) if product != "gold" else rng.randint(6, 14)
        language_mix = rng.choices(["english", "telugu", "mixed"], weights=[35, 25, 40])[0]
        # phone photos and mixed channels lose documents more often
        p_missing = {"sftp_scan": 0.10, "phone_photo": 0.34, "mixed": 0.21}[channel]
        has_pan = rng.random() > p_missing * 0.5
        has_address_proof = rng.random() > p_missing
        has_income_proof = rng.random() > (p_missing if product != "gold" else 0.05)
        has_photo = rng.random() > p_missing * 0.3
        complete = has_pan and has_address_proof and has_income_proof and has_photo
        sent_back = not complete and rng.random() > 0.08     # a few incomplete files slip through
        base = 8.6 if not sent_back else 12.4
        turnaround = round(max(2.0, rng.gauss(base, 1.5)), 1)
        hours = round(max(1.0, rng.gauss(3.4 + 0.04 * pages + (1.0 if sent_back else 0.0), 0.8)), 1)
        files.append(LoanFile(
            file_id=f"GF-{25000 + i:05d}", branch=branch, product=product, channel=channel, pages=pages,
            language_mix=language_mix, has_pan=has_pan, has_address_proof=has_address_proof,
            has_income_proof=has_income_proof, has_photo=has_photo, turnaround_days=turnaround,
            sent_back=sent_back, analyst_hours=hours,
        ))
    return files


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def median(values: list[float]) -> float:
    s = sorted(values)
    mid = len(s) // 2
    return s[mid] if len(s) % 2 else (s[mid - 1] + s[mid]) / 2


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    rng = random.Random(SEED)

    inventory_path = DATA_DIR / "godavari_inputs_inventory.csv"
    write_csv(inventory_path, [asdict(s) for s in INVENTORY])

    files = make_loan_files(200, rng)
    sample_path = DATA_DIR / "godavari_loan_file_sample.csv"
    write_csv(sample_path, [asdict(f) for f in files])

    print("== Step 3: the inputs inventory ==")
    print(f"{len(INVENTORY)} input sources written to {inventory_path.name}")
    print(f"{'input':54s}{'kind':13s}{'owner':40s}")
    for s in INVENTORY:
        print(f"{s.name:54s}{s.kind:13s}{s.owner[:40]:40s}")
    print()
    print("Architecture risks surfaced by the inventory (one per source):")
    for s in INVENTORY:
        print(f"  - {s.architecture_risk}")
    print()

    print(f"== Two-week sample: {len(files)} loan files written to {sample_path.name} ==")
    by_channel = Counter(f.channel for f in files)
    print("files by channel:        " + ", ".join(f"{k} {v}" for k, v in sorted(by_channel.items())))
    by_lang = Counter(f.language_mix for f in files)
    print("files by language mix:   " + ", ".join(f"{k} {v}" for k, v in sorted(by_lang.items())))
    sent_back = sum(f.sent_back for f in files)
    print(f"sent back at least once: {sent_back} of {len(files)} ({sent_back / len(files):.0%})")
    print(f"median turnaround:       {median([f.turnaround_days for f in files]):.1f} days")
    print(f"mean analyst hours/file: {sum(f.analyst_hours for f in files) / len(files):.1f} h")
    print()
    print("what is missing, by document (share of files without it):")
    for col in ("has_pan", "has_address_proof", "has_income_proof", "has_photo"):
        share = sum(not getattr(f, col) for f in files) / len(files)
        print(f"  {col:20s} {share:5.0%}")
    print()
    print("send-back rate by channel (why the walking skeleton starts with SFTP scans):")
    for channel in sorted(by_channel):
        sub = [f for f in files if f.channel == channel]
        print(f"  {channel:12s} {sum(f.sent_back for f in sub) / len(sub):5.0%}  (n={len(sub)})")
    print()
    print("send-back rate by product (why the skeleton starts with one product):")
    for product in PRODUCTS:
        sub = [f for f in files if f.product == product]
        print(f"  {product:15s} {sum(f.sent_back for f in sub) / len(sub):5.0%}  (n={len(sub)})")
    print()
    print(f"columns in the sample: {', '.join(f.name for f in fields(LoanFile))}")


if __name__ == "__main__":
    main()
