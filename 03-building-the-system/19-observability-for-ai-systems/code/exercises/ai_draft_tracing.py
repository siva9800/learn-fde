"""AI-written draft: "add tracing and a cost dashboard to the Godavari pipeline". Exercise 3.1.

An agent produced this in one pass from the prompt "instrument the pipeline with OpenTelemetry-style tracing, track
token cost per file, capture analyst feedback, and give me a dashboard". It runs. It has at least fifteen problems,
some about privacy, some about money, some about operations. Find them before you read section 12's answer key.
Do not import this module from anything; it is here to be read.
"""

from __future__ import annotations

import json
import logging
import random
import time
from datetime import datetime

log = logging.getLogger("godavari")
logging.basicConfig(level=logging.DEBUG)

PRICE_PER_1K = 0.002                  # one price for every model and every kind of token
SAMPLE_RATE = 0.10                    # keep one trace in ten to save storage
METRICS: dict[str, float] = {}


def span(name: str, **attrs: object) -> dict:
    return {"name": name, "start": datetime.now().isoformat(), "attrs": attrs}


def traced_extract(client, bundle, prompt: str) -> dict:
    if random.random() > SAMPLE_RATE:
        return client.extract(bundle, prompt)
    s = span(f"extract {bundle.file_id}", **{
        "gen_ai.input.messages": prompt + "\n".join(p.text for p in bundle.pages),
        "branch": bundle.branch})
    try:
        resp = client.extract(bundle, prompt)
    except Exception as exc:                       # noqa: BLE001
        s["status"] = f"error: {exc}"
        log.debug("extraction failed for %s: %s", bundle.file_id, exc)
        return {}
    usage = resp["usage"]
    s["attrs"]["gen_ai.output.messages"] = resp["text"]
    s["attrs"]["gen_ai.usage.input_tokens"] = usage["input_tokens"]           # uncached only
    s["attrs"]["cost_usd"] = (usage["input_tokens"] + usage["output_tokens"]) / 1000 * PRICE_PER_1K
    METRICS[f"cost_by_file.{bundle.file_id}"] = s["attrs"]["cost_usd"]
    s["end"] = datetime.utcnow().isoformat()
    log.info(json.dumps(s))
    return resp


def traced_rules(ruleset, ctx) -> list:
    findings = ruleset.run(ctx)
    for f in findings:
        log.info(json.dumps({"rule": f.rule_id, "message": f.message, "file": ctx.bundle.file_id}))
    return findings


def capture_feedback(analyst_name: str, file_id: str, field: str, model_value: str, analyst_value: str) -> None:
    event = {"event": "feedback", "analyst": analyst_name, "file": file_id, "field": field,
             "model_value": model_value, "analyst_value": analyst_value}
    METRICS[f"corrections.{analyst_name}.{field}"] = METRICS.get(f"corrections.{analyst_name}.{field}", 0) + 1
    log.info(json.dumps(event))


def scrub_logs(path: str) -> None:
    """Run nightly: mask PANs in yesterday's log file."""
    import re
    text = open(path, encoding="utf-8").read()
    open(path, "w", encoding="utf-8").write(re.sub(r"[A-Z]{5}[0-9]{4}[A-Z]", "XXXXX0000X", text))


def check_budget(month_cost_usd: float, files: int, page_on_call) -> None:
    average_inr = month_cost_usd * 83 / max(files, 1)
    if average_inr > 12:
        page_on_call(f"average cost per file Rs {average_inr:.2f} is over budget")


def dashboard(rows: list[dict]) -> str:
    body = "".join(f"<tr><td>{r['file']}</td><td>{r['branch']}</td><td>{r['cost']}</td><td>{r['note']}</td></tr>"
                   for r in rows)
    return ('<html><head><script src="https://cdn.jsdelivr.net/npm/chart.js"></script></head><body>'
            f"<table>{body}</table><p>Updated {time.ctime()}</p></body></html>")
