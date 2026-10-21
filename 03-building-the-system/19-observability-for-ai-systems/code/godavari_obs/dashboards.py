"""Three static pages for three readers: the FDE, the credit-ops team leads, the COO.

Each page is one self-contained HTML file: inline CSS, inline SVG charts with a native tooltip on every mark, a table
beside every chart, light and dark themes, no script, no external file, and a Content-Security-Policy that forbids
loading anything. Every value is escaped with html.escape, including values that "cannot" contain markup: a file number
today, a field the next engineer adds tomorrow. The pages are generated, never edited by hand.

What each reader gets is decided by the decision they make with it:
  the FDE        what to fix this morning: cost, latency, errors, drift, the boundary's own counters, upstream health
  team leads     the queue and the quality of the work: corrections, overrides, spot checks, the analysts' signals
  the COO        one number that moves the business case, the pre-registered metrics and what is not known yet
"""

from __future__ import annotations

import html
from collections import Counter
from datetime import date
from pathlib import Path
from statistics import mean, median
from typing import Any

from .costs import CEILING_INR, FileCost, by_stage, forecast, stats
from .redact import pii_hits

CSP = "default-src 'none'; style-src 'unsafe-inline'; img-src data:; base-uri 'none'; form-action 'none'"

CSS = """
:root{color-scheme:light;--page:#f9f9f7;--surface:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--muted:#898781;
--grid:#e1e0d9;--axis:#c3c2b7;--ring:rgba(11,11,11,.10);--s1:#2a78d6;--s2:#eb6834;--s7:#6250d6;
--good:#0ca30c;--warning:#fab219;--serious:#ec835a;--critical:#d03b3b}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){color-scheme:dark;--page:#0d0d0d;--surface:#1a1a19;
--ink:#f0efec;--ink2:#c3c2b7;--muted:#898781;--grid:#2c2c2a;--axis:#383835;--ring:rgba(255,255,255,.10);
--s1:#3987e5;--s2:#d95926;--s7:#9085e9}}
:root[data-theme="dark"]{color-scheme:dark;--page:#0d0d0d;--surface:#1a1a19;--ink:#f0efec;--ink2:#c3c2b7;--muted:#898781;
--grid:#2c2c2a;--axis:#383835;--ring:rgba(255,255,255,.10);--s1:#3987e5;--s2:#d95926;--s7:#9085e9}
*{box-sizing:border-box}
body{margin:0;background:var(--page);color:var(--ink);font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:1080px;margin:0 auto;padding:24px 16px 48px}
h1{font-size:1.5rem;margin:0 0 4px}h2{font-size:1.1rem;margin:32px 0 8px}p{margin:4px 0 8px}
.sub{color:var(--ink2)}.muted{color:var(--muted)}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin:16px 0}
.tile{background:var(--surface);border:1px solid var(--ring);border-radius:8px;padding:12px 14px}
.tile .label{color:var(--ink2);font-size:.85rem}.tile .value{font-size:1.6rem;font-weight:600;margin:2px 0}
.tile .note{color:var(--muted);font-size:.8rem}
.hero{background:var(--surface);border:1px solid var(--ring);border-radius:8px;padding:20px;margin:16px 0}
.hero .value{font-size:2.6rem;font-weight:650}
.card{background:var(--surface);border:1px solid var(--ring);border-radius:8px;padding:12px 14px;margin:12px 0;overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:.88rem}
th,td{text-align:left;padding:6px 8px;border-bottom:1px solid var(--grid);vertical-align:top}
th{color:var(--ink2);font-weight:600}td.n,th.n{text-align:right;font-variant-numeric:tabular-nums}
.st{display:inline-flex;align-items:center;gap:6px;white-space:nowrap}
.st svg{flex:none}.st-good{fill:var(--good)}.st-warning{fill:var(--warning)}.st-serious{fill:var(--serious)}
.st-critical{fill:var(--critical)}.st-none{fill:var(--muted)}
svg.chart{width:100%;height:auto;display:block}
svg .grid{stroke:var(--grid);stroke-width:1}svg .axis{stroke:var(--axis);stroke-width:1}
svg text{fill:var(--muted);font-size:11px;font-family:inherit}svg text.ink{fill:var(--ink2)}
svg .s1{fill:var(--s1)}svg .s2{fill:var(--s2)}svg .l7{stroke:var(--s7);fill:none;stroke-width:2}
svg .lg{stroke:var(--muted);fill:none;stroke-width:2;stroke-dasharray:4 3}svg .d7{fill:var(--s7)}
svg .dg{fill:var(--muted)}svg .ceil{stroke:var(--critical);stroke-width:1.5;stroke-dasharray:5 4}
svg .med{stroke:var(--ink2);stroke-width:2}svg .bar{fill:var(--s1)}
svg circle.dot{stroke:var(--surface);stroke-width:2}
.legend{display:flex;gap:16px;flex-wrap:wrap;color:var(--ink2);font-size:.85rem;margin:4px 0 8px}
.legend i{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:6px;vertical-align:-1px}
details summary{cursor:pointer;color:var(--ink2);font-size:.85rem;margin-top:6px}
footer{margin-top:40px;color:var(--muted);font-size:.8rem}
"""

_ICON = {"good": '<circle cx="6" cy="6" r="5"/>', "warning": '<path d="M6 1 11 11H1z"/>',
         "serious": '<path d="M6 1 11 11H1z"/>', "critical": '<rect x="1" y="1" width="10" height="10" rx="1"/>',
         "none": '<circle cx="6" cy="6" r="5"/>'}


def e(x: object) -> str:
    return html.escape(str(x), quote=True)


def status(level: str, label: str) -> str:
    return (f'<span class="st st-{e(level)}"><svg width="12" height="12" viewBox="0 0 12 12" aria-hidden="true">'
            f'{_ICON[level]}</svg>{e(label)}</span>')


def tile(label: str, value: str, note: str = "") -> str:
    return (f'<div class="tile"><div class="label">{e(label)}</div><div class="value">{e(value)}</div>'
            f'<div class="note">{e(note)}</div></div>')


def table(headers: list[str], rows: list[list[Any]], numeric: set[int] = frozenset(), raw: set[int] = frozenset()) -> str:
    """raw: columns whose cells were built by this module's own helpers (status pills), already escaped."""
    head = "".join(f'<th class="{"n" if i in numeric else ""}">{e(h)}</th>' for i, h in enumerate(headers))
    body = "".join("<tr>" + "".join(f'<td class="{"n" if i in numeric else ""}">{c if i in raw else e(c)}</td>'
                                    for i, c in enumerate(r)) + "</tr>" for r in rows)
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def page(title: str, sub: str, body: str) -> str:
    return (f'<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<meta http-equiv="Content-Security-Policy" content="{CSP}">'
            f'<title>{e(title)}</title><style>{CSS}</style></head><body><main>'
            f'<h1>{e(title)}</h1><p class="sub">{e(sub)}</p>{body}'
            f'<footer>Generated by code/run_observability.py from data/traces.sqlite. Synthetic data, simulated analysts. '
            f'Do not edit by hand.</footer></main></body></html>\n')


def inr(x: float) -> str:
    return f"Rs {x:,.2f}"


# --- charts ----------------------------------------------------------------------------------------------------
def cost_strip(costs: list[FileCost]) -> str:
    """Rupees per file by arrival night, one dot per file, one column per branch, the Rs 12 ceiling as a line."""
    nights = sorted({c.night for c in costs})
    branches = ["Kukatpally", "Guntur"]
    W, H, L, R, T, B = 960, 300, 44, 12, 16, 40
    top = max(15.0, max(c.inr for c in costs) * 1.08)
    y = lambda v: T + (H - T - B) * (1 - v / top)                        # noqa: E731
    col = (W - L - R) / len(nights)
    parts = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="Model cost per file by night and branch">']
    for v in range(0, int(top) + 1, 3):
        parts.append(f'<line class="grid" x1="{L}" x2="{W - R}" y1="{y(v):.1f}" y2="{y(v):.1f}"/>'
                     f'<text x="{L - 6}" y="{y(v) + 4:.1f}" text-anchor="end">{v}</text>')
    parts.append(f'<line class="ceil" x1="{L}" x2="{W - R}" y1="{y(CEILING_INR):.1f}" y2="{y(CEILING_INR):.1f}"/>'
                 f'<text class="ink" x="{W - R}" y="{y(CEILING_INR) - 5:.1f}" text-anchor="end">Rs 12 ceiling, every file</text>')
    for i, n in enumerate(nights):
        cx = L + col * (i + 0.5)
        parts.append(f'<text x="{cx:.1f}" y="{H - 22}" text-anchor="middle">{e(n.strftime("%a"))}</text>'
                     f'<text x="{cx:.1f}" y="{H - 8}" text-anchor="middle">{e(n.strftime("%d %b"))}</text>')
        for j, b in enumerate(branches):
            xs = cx + (j - 0.5) * col * 0.38
            group = sorted((c for c in costs if c.night == n and c.branch == b), key=lambda c: c.inr)
            for k, c in enumerate(group):
                jitter = (k % 3 - 1) * 5
                parts.append(f'<circle class="dot s{j + 1}" cx="{xs + jitter:.1f}" cy="{y(c.inr):.1f}" r="4.5">'
                             f'<title>{e(c.file_id)} · {e(b)} · {e(n.strftime("%a %d %b"))} · {e(inr(c.inr))} · '
                             f'{c.pages} pages, {c.pages_to_model} to the model</title></circle>')
            if group:
                m = median([c.inr for c in group])
                parts.append(f'<line class="med" x1="{xs - 11:.1f}" x2="{xs + 11:.1f}" y1="{y(m):.1f}" y2="{y(m):.1f}">'
                             f'<title>{e(b)} median {e(inr(m))}</title></line>')
    parts.append(f'<line class="axis" x1="{L}" x2="{W - R}" y1="{y(0):.1f}" y2="{y(0):.1f}"/></svg>')
    legend = ('<div class="legend"><span><i style="background:var(--s1)"></i>Kukatpally</span>'
              '<span><i style="background:var(--s2)"></i>Guntur</span><span>short bar: the night\'s median</span></div>')
    return legend + "".join(parts)


def pages_lines(points: list[tuple[date, float, float]]) -> str:
    """Guntur's median pages per file, and pages sent to the model, by night."""
    W, H, L, R, T, B = 960, 220, 44, 150, 14, 36
    top = max(p[1] for p in points) * 1.1
    x = lambda i: L + (W - L - R) * (i / max(1, len(points) - 1))       # noqa: E731
    y = lambda v: T + (H - T - B) * (1 - v / top)                         # noqa: E731
    parts = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="Guntur pages per file and pages to the model">']
    for v in range(0, int(top) + 1, 20):
        parts.append(f'<line class="grid" x1="{L}" x2="{W - R}" y1="{y(v):.1f}" y2="{y(v):.1f}"/>'
                     f'<text x="{L - 6}" y="{y(v) + 4:.1f}" text-anchor="end">{v}</text>')
    for k, (cls, dot, idx, label) in enumerate((("lg", "dg", 1, "pages in the file"), ("l7", "d7", 2, "pages sent to the model"))):
        d = " ".join(f"{'M' if i == 0 else 'L'}{x(i):.1f},{y(p[idx]):.1f}" for i, p in enumerate(points))
        parts.append(f'<path class="{cls}" d="{d}"/>')
        for i, p in enumerate(points):
            parts.append(f'<circle class="dot {dot}" cx="{x(i):.1f}" cy="{y(p[idx]):.1f}" r="4"><title>'
                         f'{e(p[0].strftime("%a %d %b"))} · {e(label)}: {p[idx]:.0f}</title></circle>')
        last = points[-1]
        parts.append(f'<text class="ink" x="{x(len(points) - 1) + 8:.1f}" y="{y(last[idx]) + 4 + (k * 12 - 6):.1f}">{e(label)}</text>')
    for i, p in enumerate(points):
        parts.append(f'<text x="{x(i):.1f}" y="{H - 10}" text-anchor="middle">{e(p[0].strftime("%d %b"))}</text>')
    parts.append(f'<line class="axis" x1="{L}" x2="{W - R}" y1="{y(0):.1f}" y2="{y(0):.1f}"/></svg>')
    return "".join(parts)


def hbars(items: list[tuple[str, int]], label: str) -> str:
    W, row, L = 960, 26, 260
    H = row * len(items) + 10
    top = max((v for _, v in items), default=1)
    parts = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="{e(label)}">']
    for i, (name, v) in enumerate(items):
        yy = 5 + i * row
        w = (W - L - 60) * v / top
        parts.append(f'<text class="ink" x="{L - 8}" y="{yy + 15}" text-anchor="end">{e(name)}</text>'
                     f'<rect class="bar" x="{L}" y="{yy + 4}" width="{max(w, 2):.1f}" height="14" rx="4">'
                     f'<title>{e(name)}: {v}</title></rect><text x="{L + w + 6:.1f}" y="{yy + 15}">{v}</text>')
    parts.append("</svg>")
    return "".join(parts)


# --- the three pages --------------------------------------------------------------------------------------------
def fde_page(d: dict[str, Any]) -> str:
    fc: list[FileCost] = d["fc"]
    w2 = [c for c in fc if c.run == "pilot-week-2"]
    lat = d["latency"]
    over = [c for c in fc if c.inr > CEILING_INR]
    store = d["store"]
    calls = store.rows("kind = 'model_call'")
    errors = Counter(r["attrs"].get("error.type") for r in calls if r["status"] == "error")
    b = []
    b.append('<div class="tiles">' +
             tile("File traces / SFTP arrivals", f"{len(fc)} / {sum(len(w.files) for w in d['weeks'])}", "every arrival has exactly one trace") +
             tile("Cost per file, week 2", f"median {inr(stats([c.inr for c in w2])['p50'])}",
                  f"p95 {inr(stats([c.inr for c in w2])['p95'])}, max {inr(max(c.inr for c in w2))}") +
             tile("Files over the Rs 12 ceiling", str(len(over)), "all on Tue 15 Dec, all Guntur" if over and
                  {c.night for c in over} == {date(2026, 12, 15)} else "see the alert list") +
             tile("Model-call errors, both weeks", str(sum(errors.values())),
                  ", ".join(f"{k} {v}" for k, v in sorted(errors.items())) or "none") +
             tile("Boundary: values dropped / spans quarantined",
                  f"{sum(store.report.dropped.values())} / {sum(store.report.quarantined.values())}",
                  "a quarantine pages the FDE") + "</div>")
    b.append("<h2>Model cost per file, by night</h2><div class=\"card\">" + cost_strip(fc) +
             "<details><summary>Table: the same data</summary>" +
             table(["night", "branch", "files", "median", "max", "median pages", "to the model"],
                   [[n.strftime("%a %d %b"), br, s["files"], inr(median([c.inr for c in fc if c.night == n and c.branch == br])),
                     inr(max(c.inr for c in fc if c.night == n and c.branch == br)), f"{s['pages']:.0f}", f"{s['to_model']:.0f}"]
                    for (n, br), s in d["pages_line"].items()], numeric={2, 3, 4, 5, 6}) + "</details></div>")
    pts = [(n, s["pages"], s["to_model"]) for (n, br), s in d["pages_line"].items() if br == "Guntur"]
    b.append("<h2>The line added after Tuesday: Guntur pages per file, and pages the model is shown</h2>"
             "<div class=\"card\">" + pages_lines(pts) + "<p class=\"muted\">Median per night. From Thursday 17 December "
             "the statement-continuation filter holds back pages that carry no field.</p></div>")
    inc = d["incident"]
    worst = d["worst"]
    b.append("<h2>Tuesday's most expensive file, read from its trace</h2><div class=\"card\">" +
             table(["file", "pages", "continuation pages", "model calls", "cost", "on continuation pages"],
                   [[worst.file_id, worst.pages, inc["cont"], inc["calls"], inr(worst.inr),
                     f"{sum(inc['on_cont'].values())} calls, {inr(inc['cost_cont'])}"]], numeric={1, 2, 3, 4}) +
             f"<p>Before the filter: {len(inc['before'])} long-statement files, median "
             f"{inr(median([c.inr for c in inc['before']]))}. After it: {len(inc['after'])} files, median "
             f"{inr(median([c.inr for c in inc['after']]))}.</p></div>")
    rows = []
    for run in ("pilot-week-1", "pilot-week-2"):
        s = by_stage(store, run)
        rows.append([run, *(inr(s.get(k, 0.0)) for k in ("classify", "escalate", "extract", "repair")),
                     f"Rs {forecast(fc, run)['monthly']:,.0f}"])
    b.append("<h2>Cost by stage, and the month at 1,400 files</h2><div class=\"card\">" +
             table(["week", "classify", "escalate", "extract", "repair", "per month at this week's mean"], rows,
                   numeric={1, 2, 3, 4, 5}) + "<p class=\"muted\">Day 12 measured about Rs 8,900 a month.</p></div>")
    rows = [[run, f"{L['classify p50']:.1f} / {L['classify p95']:.1f} s", f"{L['extract p50']:.1f} / {L['extract p95']:.1f} s",
             f"{L['ready by 09:00']:.0%}", f"{L['queue p50 h']:.1f} h", f"{L['review p50 min']:.0f} min",
             f"{L['held writes']} of {L['writes']}"] for run, L in lat.items()]
    b.append("<h2>Latency by stage</h2><div class=\"card\">" +
             table(["week", "classify p50 / p95 (budget 20 s)", "extract p50 / p95 (budget 90 s)", "ready by 09:00",
                    "queue wait p50", "review p50", "writes held for the evening window"], rows) + "</div>")
    b.append("<h2>Rules and envelope checks that moved, week one to week two</h2><div class=\"card\">" +
             table(["check", "branch", "week one", "week two"],
                   [[m.rule, m.branch, f"{m.before} of {m.before_n}", f"{m.after} of {m.after_n}"] for m in d["moves"]]) +
             "<p class=\"muted\">Share of files on which the check fired; 'moved' means outside week one's 95 percent "
             "interval and at least three files apart. A reason to open traces, not a verdict.</p></div>")
    rs = d["retrieval"]
    d16, d17 = d["d16"], d["d17"]
    up = [["Day 16 write journal", f"{d16['writes']} writes; " + ", ".join(f"{k} {v}" for k, v in sorted(d16["states"].items())),
           f"reconciliation: {d16['nights']} night(s) on record, clean run {d16['clean_run']}"],
          ["Day 15 policy panel", f"{rs['asked']} searches", f"{rs['empty']} empty, {rs['refused']} refused (stale group snapshot)"]]
    if d17:
        up.append(["Day 17 workflow audit log", f"approvals asked {d17['approvals_requested']}, decided {d17['approvals_decided']}, "
                   f"escalated {d17['approvals_escalated']}, refused {d17['approvals_refused']}",
                   f"wait median {d17['wait_median_min']} min; most tool calls in a drafting run {d17['max_tool_calls']} of "
                   f"{d17['step_budget']}"])
    b.append("<h2>Upstream records</h2><div class=\"card\">" + table(["record", "what it says", "health"], up) + "</div>")
    b.append("<h2>Alerts this fortnight</h2><div class=\"card\">" +
             table(["day", "rule", "how", "who", "what"],
                   [[a.day.strftime("%a %d %b"), a.rule, a.how, a.who, a.text] for a in d["alerts"]]) + "</div>")
    b.append("<h2>The boundary</h2><div class=\"card\">" +
             table(["dropped or quarantined", "count"],
                   [[k, v] for k, v in sorted(store.report.dropped.items())] +
                   [[f"quarantined: {k}", v] for k, v in sorted(store.report.quarantined.items())] or [["nothing", 0]],
                   numeric={1}) +
             table(["record", "identifier kinds found"], [[k, ", ".join(v) or "none"] for k, v in d["scan"].items()]) +
             "<p class=\"muted\">The screen log and the corrections are supposed to hold values: they are the decision "
             "record, inside Godavari's boundary. The trace store, the journal and the audit log are not.</p></div>")
    return page("Godavari pilot · engineering", f"For the Kaagaz FDE · pilot weeks 1 and 2, 7 to 18 December 2026 · "
                f"prompt release {d['release']}", "".join(b))


def lead_page(d: dict[str, Any]) -> str:
    store = d["store"]
    w2 = d["weeks"][1]
    b = []
    bs = d["bsig"]["pilot-week-2"]
    tiles = []
    for br in ("Kukatpally", "Guntur"):
        v = bs[br]
        f = v["files"]
        sent = v.get("route send_back", 0) + v.get("route blocked", 0)
        waits = [r["attrs"]["kaagaz.review.queue_wait_h"] for r in store.by_name("review")
                 if any(fr.root.trace_id == r["trace_id"] and fr.branch == br for fr in w2.files)]
        tiles.append(tile(f"{br}: files this week", f"{int(f)}", f"{int(sent)} sent back, each told the branch on the night it arrived"))
        tiles.append(tile(f"{br}: hours before first opened", f"{median(waits):.1f} h", f"median; longest {max(waits):.1f} h"))
        tiles.append(tile(f"{br}: fields corrected per file", f"{v.get('content corrections', 0) / f:.2f}",
                          "Day 9's leading indicator: below 3"))
    b.append('<div class="tiles">' + "".join(tiles) + "</div>")
    rows = []
    for s in d["fsig"]["pilot-week-2"]:
        lvl = "good" if s.status == "in line" else "warning"
        rows.append([s.field, f"{s.changed} of {s.files}", f"{s.rate:.1%} ({s.lo:.1%} to {s.hi:.1%})",
                     f"{s.golden_rate:.1%} ({s.golden_lo:.1%} to {s.golden_hi:.1%})", status(lvl, s.status)])
    b.append("<h2>Corrections per field, against the golden set</h2><div class=\"card\">" +
             table(["field", "files corrected", "this week (95% interval)", "golden set error rate", "reading"], rows,
                   numeric={1}, raw={4}) +
             "<p class=\"muted\">A correction here is a changed value (format-only tidy-ups excluded). The golden set's "
             "rate is Day 14's baseline run on 150 files labelled by Lakshmi and the senior analyst.</p></div>")
    reasons = Counter(e["attrs"].get("kaagaz.feedback.reason") for e in store.events("feedback")
                      if any(fr.root.trace_id == e["trace_id"] for fr in w2.files))
    b.append("<h2>Why analysts changed a value this week</h2><div class=\"card\">" +
             hbars(sorted(reasons.items(), key=lambda kv: -kv[1]), "Correction reasons this week") +
             "<p class=\"muted\">'format only' is feedback about the screen, not the model; it never becomes an eval "
             "example (Day 18).</p></div>")
    ov = d["overrides"][2]
    rows = [[o["analyst"], o["review_fields"], o["corrections"], o["expected"],
             status("warning", "fewer than expected") if o["low"] else status("good", "in line")] for o in ov]
    b.append("<h2>Corrections in the review band, per analyst (week two)</h2><div class=\"card\">" +
             table(["analyst", "fields to check", "corrected", "expected at 5.4%", "reading"], rows, numeric={1, 2, 3},
                   raw={4}) + "<p class=\"muted\">Seen by the analyst's own team lead only, under Day 18's agreement: "
             "never HR, never a ranking. A week is weak evidence on its own.</p></div>")
    sp = d["spot"]
    sess = d["sessions"]
    rows = [[f"week {n}", sp[n]["files"], sp[n]["fields"], sp[n]["wrong"], f"{sp[n]['upper']:.1%}",
             len([s for s in sess[n] if s.verdict.startswith("suspected")])] for n in (1, 2)]
    b.append("<h2>Spot checks and rubber-stamp sessions</h2><div class=\"card\">" +
             table(["week", "files drawn", "auto-accepted fields read again", "wrong", "upper bound on the wrong rate",
                    "sessions sent for a second read"], rows, numeric={1, 2, 3, 4, 5}) +
             "<p class=\"muted\">The spot check is the only signal that measures confident-wrong values directly; "
             "everything else on this page is a proxy.</p></div>")
    return page("Godavari pilot · the queue and the quality", "For Srinivas (Hyderabad) and the Vijayawada team lead · "
                "pilot week 2, Monday 14 to Friday 18 December 2026", "".join(b))


def coo_page(d: dict[str, Any]) -> str:
    fc: list[FileCost] = d["fc"]
    store = d["store"]
    w2 = d["weeks"][1]
    ids2 = {fr.root.trace_id for fr in w2.files}
    waits = [r["attrs"]["kaagaz.review.queue_wait_h"] for r in store.by_name("review") if r["trace_id"] in ids2]
    routes = Counter(r["attrs"]["kaagaz.route"] for r in store.by_name("route") if r["trace_id"] in ids2)
    sent = routes["send_back"] + routes["blocked"]
    week_cost = [c.inr for c in fc if c.run == "pilot-week-2"]
    over = [c for c in fc if c.run == "pilot-week-2" and c.inr > CEILING_INR]
    corrected = sum(1 for e in store.events("feedback") if e["trace_id"] in ids2 and e["attrs"].get("kaagaz.feedback.content_change"))
    b = []
    b.append('<div class="hero"><div class="label sub">Files waiting before an analyst opens them</div>'
             f'<div class="value">{mean(waits) / 24:.1f} days</div>'
             f'<p>Pilot week 2, mean, {len(waits)} files from Kukatpally and Guntur. Before the pilot: 6.4 days (Day 9\'s '
             f'hand count). This is where 6.4 of the 9.1 days went.</p><p class="muted">The analysts in this run are '
             f'simulated and open every file on the day it lands; the real pilot reading will be higher. The headline, '
             f'median turnaround, needs decided files and is not measurable yet.</p></div>')
    b.append('<div class="tiles">' +
             tile("Send-backs told to the branch the same day", f"{sent} of {sent}", "before: 6 to 7 days (Day 9)") +
             tile("Model cost per file, this week", inr(mean(week_cost)), f"ceiling Rs 12 a file; {len(over)} over it, on one night, before the fix") +
             tile("At 1,400 files a month", f"Rs {forecast(fc, 'pilot-week-2')['monthly']:,.0f}", "model calls only; Day 12 planned about Rs 8,900") +
             tile("Fields corrected per file", f"{corrected / len(waits):.2f}", "pre-registered: falling, below 3") + "</div>")
    rows = [["Median turnaround (signature to decision)", "9.1 days (8.7 to 9.7)", "3 to 4 days by day 90",
             status("none", "not measurable yet: first reading when pilot files are decided; Day 37 measures it")],
            ["Decided with a mandatory document missing", "4.1%", "below the baseline, every month",
             status("none", "the compliance head's monthly re-draw; first in January")],
            ["Customers who withdraw", "10.1%", "measured, not targeted", status("none", "needs decided files")],
            ["Queue age (arrival to first opened)", "6.4 days (mean)", "under 2 days",
             status("good", f"{mean(waits) / 24:.1f} days in pilot week 2 (simulated analysts)")]]
    b.append("<h2>The metrics signed in week 4</h2><div class=\"card\">" +
             table(["metric", "baseline", "target", "this week"], rows, raw={3}) + "</div>")
    w1g = median([c.inr for c in fc if c.run == "pilot-week-1" and c.branch == "Guntur"])
    tue = median([c.inr for c in fc if c.night == date(2026, 12, 15) and c.branch == "Guntur"])
    late = median([c.inr for c in fc if c.run == "pilot-week-2" and c.branch == "Guntur" and c.page_filter != "off"])
    in_line = sum(s.status == "in line" for s in d["fsig"]["pilot-week-2"])
    b.append("<h2>This week in one paragraph</h2><div class=\"card\"><p>" + e(
        f"On Tuesday Guntur's branch began attaching customers' full sixty-page bank statements. The model cost of "
        f"Guntur's files went from a median of {inr(w1g)} in week one to {inr(tue)} that night ({tue / w1g:.1f} times), and "
        f"{len(over)} file{"s" if len(over) != 1 else ""} went over the Rs 12 ceiling. The traces showed why the same morning. A page filter that keeps "
        f"statement continuation pages away from the model shipped on Wednesday at 17:00, before the change freeze; "
        f"Guntur's files from Thursday cost a median of {inr(late)}. The analysts still see every page. Corrections on "
        f"{in_line} of {len(d['fsig']['pilot-week-2'])} fields are in line with the golden set.") + "</p></div>")
    b.append("<h2>What this page cannot tell you yet</h2><div class=\"card\"><p>Turnaround, the missing-document rate and "
             "withdrawals need decided files; the pilot runs to week 10. The cost line covers model calls only, not the "
             "machine, storage or support. The analysts' behaviour in this run is simulated.</p></div>")
    return page("Godavari pilot · the weekly number", "For the COO · week ending Friday 18 December 2026 · one page, "
                "every Friday", "".join(b))


def write_all(d: dict[str, Any], folder: Path) -> list[Path]:
    from .costs import pages_line
    d = {**d, "pages_line": pages_line(d["fc"])}
    out = []
    for name, fn in (("fde.html", fde_page), ("team-leads.html", lead_page), ("coo-weekly.html", coo_page)):
        text = fn(d)
        if pii_hits(text):
            raise RuntimeError(f"{name} would carry an identifier; not written")
        path = folder / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
        out.append(path)
    return out
