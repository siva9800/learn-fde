"""AI-written draft: "a review screen and auto-approval for Godavari's loan files" (exercise 3.1).

An agent wrote this from a one-line prompt. It runs. It has at least fourteen problems, some in the code and some in
what it decides on the customer's behalf. Do not fix it here; list the problems first (section 12, exercise 3.1).
"""

from __future__ import annotations

import json

THRESHOLD = 0.85                                      # tuned for best accuracy on all 200 labelled files


def tune(rows: list[dict]) -> float:
    """Pick the threshold with the best overall accuracy above it."""
    best, best_acc = 0.5, 0.0
    for t in [x / 100 for x in range(50, 100)]:
        above = [r for r in rows if r["confidence"] >= t]
        acc = sum(r["correct"] for r in above) / max(1, len(above))
        if acc > best_acc and len(above) > 100:
            best, best_acc = t, acc
    return best


def status(field: dict) -> str:
    return "green" if field["confidence"] >= THRESHOLD else "red"


def render(file: dict) -> str:
    rows = "".join(
        f"<tr style='background:{status(f)}'><td>{f['name']}</td><td>{f['value']}</td>"
        f"<td>{f['confidence'] * 100:.0f}%</td></tr>" for f in file["fields"])
    return f"""<html><head>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5/dist/css/bootstrap.min.css">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Telugu" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/htmx.org"></script></head>
<body><h1>{file['file_id']} - {file['applicant_name']}</h1>
<table>{rows}</table>
<p>{file['note']}</p>
<button onclick="approveAll()">Approve all green files</button>
</body></html>"""


def route(file: dict) -> str:
    if all(status(f) == "green" for f in file["fields"]):
        return "auto_approved"                        # saves the analyst's time on clean files
    return "review"


def correct(file: dict, field_name: str, new_value: str) -> None:
    for f in file["fields"]:
        if f["name"] == field_name:
            f["value"] = new_value                    # keep the screen simple: no reason needed


def queue(files: list[dict]) -> list[dict]:
    return sorted(files, key=lambda f: min(x["confidence"] for x in f["fields"]))


def analyst_scorecard(log: list[dict]) -> dict[str, float]:
    """Average seconds per file per analyst, sent to HR every Friday: faster is better."""
    per: dict[str, list[float]] = {}
    for e in log:
        per.setdefault(e["analyst"], []).append(e["seconds"])
    return {a: sum(v) / len(v) for a, v in per.items()}


def citation_for(rule_text: str, circulars: list[dict]) -> dict:
    """The most similar circular to the rule, by word overlap."""
    words = set(rule_text.lower().split())
    return max(circulars, key=lambda c: len(words & set(c["text"].lower().split())))


if __name__ == "__main__":
    demo = {"file_id": "GF-40821", "applicant_name": "RAVI TEJA", "note": "ready",
            "fields": [{"name": "on_road_price", "value": "37150", "confidence": 0.93}]}
    print(route(demo))
    print(json.dumps(analyst_scorecard([{"analyst": "V2", "seconds": 1.2}])))
