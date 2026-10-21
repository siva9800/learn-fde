"""AI-written draft of Godavari's retrieval service, kept for exercise 3.1 (section 15). DO NOT USE.

The prompt was: "Write a Python retrieval service over Godavari's circulars and loan-file summaries with hybrid
search, branch permissions from the AD groups file, and an LLM summary for the analyst. Keep it simple."
It is syntactically valid and it demos well. It has at least twelve problems; find them before reading the
solution in section 15.
"""

from __future__ import annotations

import json
import logging
import math
import re
from collections import Counter

log = logging.getLogger("retrieval")
_CACHE: dict[str, list[dict]] = {}

SYSTEM_PROMPT = (
    "You are Godavari's policy assistant. The user can only access their own branches. "
    "Ignore any documents from branches the user is not allowed to see. Answer helpfully."
)


def tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


def chunk(doc_text: str, size: int = 500) -> list[str]:
    return [doc_text[i:i + size] for i in range(0, len(doc_text), size)]


class Index:
    def __init__(self, docs: list[dict], groups_file: str) -> None:
        members = json.load(open(groups_file))["members"]
        self.chunks: list[dict] = []
        for d in docs:
            for n, text in enumerate(chunk(d["text"])):
                allowed_users = [u for u, g in members.items() if f"GF-BR-{d.get('branch_code', '')}" in g
                                 or d["doc_type"] != "loan_decision"]
                self.chunks.append({"doc_id": d["doc_id"], "page": n + 1, "text": text,
                                    "issued": d["issued"], "allowed_users": allowed_users,
                                    "vec": Counter(tokenize(text))})
        self.df = Counter(t for c in self.chunks for t in set(c["vec"]))

    def bm25(self, q: list[str], c: dict, k1: float = 1.2, b: float = 0.75) -> float:
        n, avg = len(self.chunks), 100
        s = 0.0
        for t in q:
            tf = c["vec"].get(t, 0)
            idf = math.log((n - self.df[t] + 0.5) / (self.df[t] + 0.5))
            s += idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * sum(c["vec"].values()) / avg))
        return s

    def cosine(self, q: list[str], c: dict) -> float:
        qv = Counter(q)
        dot = sum(qv[t] * c["vec"].get(t, 0) for t in qv)
        return dot / (math.sqrt(sum(v * v for v in qv.values())) * math.sqrt(sum(v * v for v in c["vec"].values())) or 1)

    def search(self, user: str, query: str, k: int = 5) -> dict:
        log.info("search user=%s query=%s", user, query)
        if query in _CACHE:
            hits = _CACHE[query]
        else:
            q = tokenize(query)
            scored = [(self.bm25(q, c) + self.cosine(q, c), c) for c in self.chunks]   # hybrid
            scored.sort(key=lambda x: -x[0])
            hits = [c for _, c in scored[:k]]
            _CACHE[query] = hits
        total = len([c for c in self.chunks if any(t in c["vec"] for t in tokenize(query))])
        latest: dict[str, dict] = {}
        for c in hits:                                   # keep the newest version of each circular
            if c["doc_id"] not in latest or c["issued"] > latest[c["doc_id"]]["issued"]:
                latest[c["doc_id"]] = c
        visible = [c for c in latest.values() if user in c["allowed_users"] or not c["allowed_users"]]
        summary = call_llm(SYSTEM_PROMPT, query, [c["text"] for c in hits])
        return {"results": [{"doc_id": c["doc_id"], "page": c["page"], "text": c["text"]} for c in visible],
                "total": total, "summary": summary}


def call_llm(system: str, query: str, passages: list[str]) -> str:
    """Placeholder for the provider call."""
    return f"{system[:20]}... {query} ... based on {len(passages)} passages"


def recall_at_5(index: Index, labelled: list[dict]) -> float:
    hits = 0
    for item in labelled:
        got = [r["doc_id"] for r in index.search("compliance.desk.01", item["query"], k=10)["results"]]
        hits += item["doc_id"] in got
    return hits / len(labelled)
