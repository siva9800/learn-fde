"""Inter-annotator agreement: how far the two eval owners agree before anyone adjudicates.

Read it as a test of the labelling guide, not of the labellers. A field with low agreement is a field the
guide does not define well enough; fix the guide and re-label, before any model is scored on it.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from .labels import LabelSet, required_docs
from .normalise import exact_equal, norm_equal, normalise
from .stats import cohen_kappa, wilson


@dataclass
class FieldAgreement:
    field_name: str
    n: int
    exact: int
    normalised: int

    @property
    def exact_rate(self) -> float:
        return self.exact / self.n if self.n else 1.0

    @property
    def norm_rate(self) -> float:
        return self.normalised / self.n if self.n else 1.0


@dataclass
class AgreementReport:
    files: int
    fields: list[FieldAgreement]
    kappa_send_back: float
    kappa_incomplete: float
    kappa_documents: float
    raw_send_back: float
    raw_incomplete: float
    labeller_accuracy: dict[str, tuple[int, int]]     # name -> (fields matching the adjudicated label, fields)
    adjudications: Counter[str]
    adjudicated_by: Counter[str]
    agreed_but_wrong: int                             # final label differs from the paper (synthetic only)
    field_cells: int
    minutes: dict[str, float]

    def lines(self) -> list[str]:
        out = [f"files double-labelled: {self.files} · field cells: {self.field_cells}"]
        out.append("")
        out.append(f"{'field':20s}{'n':>5s}{'exact agree':>13s}{'normalised':>12s}")
        for fa in self.fields:
            out.append(f"{fa.field_name:20s}{fa.n:5d}{fa.exact_rate:12.1%} {fa.norm_rate:11.1%}")
        tot_n = sum(f.n for f in self.fields)
        out.append(f"{'all fields':20s}{tot_n:5d}{sum(f.exact for f in self.fields) / tot_n:12.1%} "
                   f"{sum(f.normalised for f in self.fields) / tot_n:11.1%}")
        out.append("")
        out.append("decisions (Cohen's kappa = agreement beyond chance; 1 is perfect, 0 is chance):")
        out.append(f"  would send the file back      raw {self.raw_send_back:6.1%}   kappa {self.kappa_send_back:.2f}")
        out.append(f"  file is incomplete            raw {self.raw_incomplete:6.1%}   kappa {self.kappa_incomplete:.2f}")
        out.append(f"  each required document found              kappa {self.kappa_documents:.2f}")
        out.append("")
        out.append("each eval owner against the adjudicated truth (Day 9's 'analysts' own keying error rate'):")
        for who, (k, n) in self.labeller_accuracy.items():
            lo, hi = wilson(k, n)
            out.append(f"  {who:20s} {k / n:6.2%} of {n} field cells  (95% {lo:.2%} to {hi:.2%}); "
                       f"{self.minutes[who]:.0f} minutes a file on average")
        out.append("")
        out.append("adjudications: " + ", ".join(f"{k} {v}" for k, v in sorted(self.adjudications.items())))
        out.append("decided by:    " + "; ".join(f"{k} {v}" for k, v in sorted(self.adjudicated_by.items())))
        out.append(f"field labels where both agreed, or the adjudicators read it, and the paper says otherwise: "
                   f"{self.agreed_but_wrong} of {self.field_cells} (visible only because the data is synthetic)")
        return out


def agreement(ls: LabelSet) -> AgreementReport:
    per_field: dict[str, FieldAgreement] = {}
    acc = {"Lakshmi": [0, 0], "the senior analyst": [0, 0]}
    agreed_wrong = 0
    cells = 0
    sb_a, sb_b, inc_a, inc_b, doc_a, doc_b = [], [], [], [], [], []
    for gf in ls.files:
        a, b, final, paper = ls.a[gf.file_id], ls.b[gf.file_id], ls.final[gf.file_id], ls.paper[gf.file_id]
        for name in paper.fields:
            fa = per_field.setdefault(name, FieldAgreement(name, 0, 0, 0))
            fa.n += 1
            fa.exact += exact_equal(a.fields[name], b.fields[name])
            fa.normalised += norm_equal(name, a.fields[name], b.fields[name])
            cells += 1
            for who, lab in (("Lakshmi", a), ("the senior analyst", b)):
                acc[who][0] += normalise(name, lab.fields[name]) == final.fields[name]
                acc[who][1] += 1
            agreed_wrong += final.fields[name] != normalise(name, paper.fields[name])
        sb_a.append(a.send_back)
        sb_b.append(b.send_back)
        inc_a.append(bool(a.missing))
        inc_b.append(bool(b.missing))
        has_co = "co_applicant_kyc" in paper.documents + paper.missing
        for d in required_docs(gf.product, has_co):
            doc_a.append(str(d) in a.documents)
            doc_b.append(str(d) in b.documents)
    order = list(dict.fromkeys(n for gf in ls.files for n in ls.paper[gf.file_id].fields))
    minutes = {"Lakshmi": sum(ls.a[g.file_id].minutes for g in ls.files) / len(ls.files),
               "the senior analyst": sum(ls.b[g.file_id].minutes for g in ls.files) / len(ls.files)}
    return AgreementReport(
        files=len(ls.files),
        fields=[per_field[n] for n in order],
        kappa_send_back=cohen_kappa(sb_a, sb_b),
        kappa_incomplete=cohen_kappa(inc_a, inc_b),
        kappa_documents=cohen_kappa(doc_a, doc_b),
        raw_send_back=sum(x == y for x, y in zip(sb_a, sb_b)) / len(sb_a),
        raw_incomplete=sum(x == y for x, y in zip(inc_a, inc_b)) / len(inc_a),
        labeller_accuracy={k: (v[0], v[1]) for k, v in acc.items()},
        adjudications=Counter(e.item.split(":")[0] for e in ls.log),
        adjudicated_by=Counter(e.by for e in ls.log),
        agreed_but_wrong=agreed_wrong,
        field_cells=cells,
        minutes=minutes,
    )
