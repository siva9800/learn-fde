"""AI-written eval harness for the Godavari extraction pipeline (exercise 3.1: find what is wrong).

An agent wrote this from the prompt "write an eval script that scores the extraction model on our labelled
files and fails CI if accuracy drops". It runs, it prints a number, and it would pass review by someone in a
hurry. It has at least twelve problems. Do not use it; review it.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

LABELS = Path("data/golden/labels-lakshmi.jsonl")           # the labels
FEWSHOT_COUNT = 5
THRESHOLD = 0.05                                             # fail CI if accuracy drops by more than 5 points


def load_labels() -> list[dict]:
    rows = [json.loads(line) for line in LABELS.read_text().splitlines()]
    random.shuffle(rows)
    return rows


def build_prompt(examples: list[dict]) -> str:
    shots = "\n".join(f"File {e['file_id']}: {json.dumps(e['fields'])}" for e in examples)
    return f"You are an expert credit analyst. Extract the fields.\nExamples:\n{shots}\n"


def same(a: str | None, b: str | None) -> bool:
    if a is None or b is None:
        return True
    a_digits, b_digits = "".join(c for c in a if c.isdigit()), "".join(c for c in b if c.isdigit())
    if a_digits and b_digits:
        return abs(int(a_digits) - int(b_digits)) <= 0.1 * int(b_digits)
    return a.lower()[:6] == b.lower()[:6]


def judge_note(model, note: str) -> bool:
    reply = model.complete(f"Is this note to the branch good? Answer yes or no.\n{note}")
    return "yes" in reply.lower()


def evaluate(model) -> dict:
    rows = load_labels()
    prompt = build_prompt(rows[:FEWSHOT_COUNT])
    correct = total = 0
    good_notes = 0
    for row in rows:
        out = model.extract(prompt, row["file_id"])
        for name, value in out["fields"].items():
            if value is None:
                continue                                     # the model abstained; do not count it
            total += 1
            if same(value, row["fields"].get(name)) or out["confidence"][name] > 0.9:
                correct += 1
        print(f"{row['file_id']} pan={out['fields'].get('pan')} label={row['fields'].get('pan')}")
        good_notes += judge_note(model, out["note"])
    return {"accuracy": round(correct / total, 4), "notes_ok": good_notes / len(rows)}


def main() -> int:
    from kaagaz_models import current_model                 # whatever is configured today
    result = evaluate(current_model())
    baseline = json.loads(Path("baseline.json").read_text())
    print(f"accuracy {result['accuracy']:.2%} (baseline {baseline['accuracy']:.2%})")
    if result["accuracy"] > baseline["accuracy"]:
        Path("baseline.json").write_text(json.dumps(result))   # keep the best score as the new baseline
    if baseline["accuracy"] - result["accuracy"] > THRESHOLD:
        print("FAIL")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
