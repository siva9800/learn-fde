"""LLM-as-judge, calibrated against people before it is trusted, on the one open-ended output in the system.

The output: the note to the branch that explains what is missing (Day 11: code decides the findings, the
model writes the prose). Fields have exact answers and are scored by code; a note does not, so a judge is
tempting. This module shows the whole procedure on a toy judge you can run offline:

  notes        two writers produce notes for every golden file with branch-facing findings: Day 11's
               stub-model-v1, and a chattier second model ("note-writer-b") that sometimes drops a finding,
               invents a document, pastes a PAN, writes a bare rule code or forgets the citation.
  people       Lakshmi and the senior analyst mark each note pass or fail against a five-line rubric, with a
               one-line critique; the Vijayawada team lead settles disagreements. That is the reference.
  judge v1     a holistic "rate this note 1 to 10" judge from the same family as stub-model-v1. It carries
               the three biases the literature reports (Zheng et al., 2023): it likes longer notes, it likes
               its own family's writing, and it misses specific defects it was not asked about.
  judge v2     the rubric split in two: everything code can check is checked by code (every finding
               covered and cited, no document the findings do not mention, no PAN, Aadhaar or mobile
               number), and the judge model is asked only the one question code cannot answer: "is this
               plain enough for a branch clerk?"

Both judges are calibrated on the development split's notes and reported on the test split's notes. The
toy judges are deterministic simulations, so the numbers are about the procedure, not about any real model.
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass, field
from typing import Any

from .day11 import RULESETS
from .golden import GoldenFile
from .harness import AS_OF
from .stats import cohen_kappa
from intake.model import StubModel
from intake.pipeline import process

RUBRIC = """\
A note to the branch passes only if all five hold:
  1. covers every problem code found (nothing dropped);
  2. invents nothing (no document or problem the findings do not contain);
  3. cites the rule for every item, as "(rule TW-DOC-05)";
  4. contains no full PAN, Aadhaar or mobile number;
  5. is plain enough for a branch clerk (no bare codes like "TW-DOC-05: FAIL")."""

DEFECTS = ("omission", "invented", "no_citation", "pii", "jargon")
HUMAN_DETECT = {"omission": 0.90, "invented": 0.97, "no_citation": 0.85, "pii": 0.98, "jargon": 0.95}
V1_DETECT = {"omission": 0.30, "invented": 0.35, "no_citation": 0.25, "pii": 0.60, "jargon": 0.70}
EXTRA_DOCUMENTS = ("Form 16", "ITR", "passport", "salary slip", "property tax receipt", "gas bill")
PII_PATTERNS = {"pan": r"\b[A-Z]{5}\d{4}[A-Z]\b", "aadhaar": r"\b\d{4}\s?\d{4}\s?\d{4}\b", "mobile": r"\b[6-9]\d{9}\b"}
JARGON_LINE = re.compile(r"^- [A-Z]{2,3}-[A-Z0-9-]+: FAIL$", re.MULTILINE)


@dataclass
class Note:
    note_id: str
    file_id: str
    split: str
    writer: str
    text: str
    findings: list[tuple[str, str]]
    defects: set[str] = field(default_factory=set)        # hidden: what the writer really got wrong
    human: dict[str, bool] = field(default_factory=dict)  # labeller -> pass?
    human_final: bool = True


def _cap(msg: str) -> str:
    return msg[0].upper() + msg[1:]


def writer_b(file_id: str, findings: list[tuple[str, str]], pan: str | None, variant: int) -> tuple[str, set[str]]:
    """A second, chattier model. Its mistakes are the ones real note writers make."""
    rng = random.Random(f"writer-b-{variant}-{file_id}")
    items = list(findings)
    defects: set[str] = set()
    if len(items) > 1 and rng.random() < 0.15:
        items.pop(rng.randrange(len(items)))
        defects.add("omission")
    lines = [f"Dear branch team, file {file_id} needs your attention."]
    if rng.random() < 0.35:
        lines.append("We sincerely appreciate your continued cooperation and apologise for any inconvenience caused.")
    for rule_id, msg in items:
        r = rng.random()
        if r < 0.08:
            lines.append(f"- {rule_id}: FAIL")
            defects.add("jargon")
        elif r < 0.20:
            lines.append(f"- {_cap(msg)}.")
            defects.add("no_citation")
        else:
            lines.append(f"- {_cap(msg)} (rule {rule_id}).")
    if rng.random() < 0.07:
        lines.append("- Please also send the Form 16 for the last two years.")
        defects.add("invented")
    if pan and rng.random() < 0.06:
        lines.append(f"Applicant PAN {pan} for your reference.")
        defects.add("pii")
    if rng.random() < 0.30:
        lines.append("Kindly do the needful at the earliest. Thank you for your patience and support.")
    return "\n".join(lines), defects


def make_notes(files: list[GoldenFile]) -> list[Note]:
    model = StubModel()
    notes: list[Note] = []
    for gf in files:
        bundle, _ = gf.build()
        result = process(bundle, model, RULESETS[gf.product], AS_OF)
        findings = [(f.rule_id, f.message) for f in result.findings if f.action.value in ("send_back", "block")]
        if not findings:
            continue
        text = model.draft_note(bundle, findings)       # the raw draft, before Day 11's citation fix
        missing_cite = any(f"(rule {rid})" not in text for rid, _ in findings)
        notes.append(Note(f"{gf.file_id}-v1", gf.file_id, gf.split, model.name, text, findings,
                          {"no_citation"} if missing_cite else set()))
        assert result.output is not None
        pan = result.output.fields.get("pan").value if result.output.fields.get("pan") else None
        for variant in (1, 2):
            text_b, defects = writer_b(gf.file_id, findings, pan, variant)
            notes.append(Note(f"{gf.file_id}-b{variant}", gf.file_id, gf.split, "note-writer-b", text_b, findings,
                              defects))
    return notes


def label_notes(notes: list[Note]) -> None:
    """Two people apply the rubric; disagreements go to the Vijayawada team lead, who reads it again."""
    for note in notes:
        for who in ("Lakshmi", "the senior analyst"):
            rng = random.Random(f"note-label-{who}-{note.note_id}")
            seen = any(rng.random() < HUMAN_DETECT[d] for d in sorted(note.defects))
            note.human[who] = not (seen or rng.random() < 0.02)
        a, b = note.human["Lakshmi"], note.human["the senior analyst"]
        if a == b:
            note.human_final = a
        else:
            rng = random.Random(f"note-adjudicate-{note.note_id}")
            note.human_final = (not note.defects) if rng.random() < 0.97 else a


def judge_v1_score(note: Note) -> float:
    """Holistic 1-to-10 score from the same model family as stub-model-v1. Toy, with the published biases."""
    rng = random.Random(f"judge-v1-{note.note_id}")
    score = 6.5 + min(1.5, 0.004 * len(note.text))          # verbosity bias
    if note.writer == "stub-model-v1":
        score += 1.0                                         # self-preference: it likes its own family's notes
    score += rng.gauss(0, 0.7)
    for d in sorted(note.defects):
        if rng.random() < V1_DETECT[d]:
            score -= 2.5
    return score


def judge_v2(note: Note) -> tuple[bool, list[str]]:
    """Rubric judge: code checks rules 1 to 4; the judge model answers only rule 5 (plain language)."""
    reasons: list[str] = []
    text = note.text
    for rule_id, msg in note.findings:
        if rule_id not in text and _cap(msg)[:30] not in text:
            reasons.append(f"rule 1: {rule_id} not covered")
        elif f"(rule {rule_id})" not in text:
            reasons.append(f"rule 3: {rule_id} not cited")
    joined = " ".join(m for _, m in note.findings).lower()
    for doc in EXTRA_DOCUMENTS:
        if doc.lower() in text.lower() and doc.lower() not in joined:
            reasons.append(f"rule 2: mentions {doc!r}, which no finding asked for")
    for kind, pattern in PII_PATTERNS.items():
        if re.search(pattern, text):
            reasons.append(f"rule 4: a full {kind} number is in the note")
    # The one judgement left to a model. Simulated: it spots a bare code most of the time, rarely imagines one.
    rng = random.Random(f"judge-v2-clarity-{note.note_id}")
    unclear = (rng.random() < 0.92) if JARGON_LINE.search(text) else (rng.random() < 0.03)
    if unclear:
        reasons.append("rule 5: not plain enough for a branch clerk (judge model)")
    return not reasons, reasons


@dataclass
class JudgeScore:
    name: str
    n: int
    agreement: float
    kappa: float
    catches_fails: float          # true positive rate on "fail": of notes people failed, the share the judge failed
    passes_passes: float          # true negative rate: of notes people passed, the share the judge passed
    own_family_pass: float        # bias probe: pass rate on notes whose ONLY defect is a missing citation,
    other_pass: float             # for stub-model-v1's own notes and for note-writer-b's (same defect, other writer)
    judge_right_people_wrong: int  # disagreements where the hidden defects say the judge was right


def score_judge(name: str, notes: list[Note], verdicts: dict[str, bool]) -> JudgeScore:
    human = [n.human_final for n in notes]
    judged = [verdicts[n.note_id] for n in notes]
    fails = [i for i, h in enumerate(human) if not h]
    passes = [i for i, h in enumerate(human) if h]

    def probe(writer: str) -> float:
        sub = [n for n in notes if n.writer == writer and n.defects == {"no_citation"}]
        return sum(verdicts[n.note_id] for n in sub) / len(sub) if sub else 0.0

    right = sum(1 for n in notes if verdicts[n.note_id] != n.human_final and verdicts[n.note_id] == (not n.defects))
    return JudgeScore(
        name, len(notes), sum(h == j for h, j in zip(human, judged)) / len(notes), cohen_kappa(human, judged),
        sum(not judged[i] for i in fails) / len(fails) if fails else 1.0,
        sum(judged[i] for i in passes) / len(passes) if passes else 1.0,
        probe("stub-model-v1"), probe("note-writer-b"), right)


def calibrate_v1(dev_notes: list[Note]) -> float:
    """Pick judge v1's pass threshold on the development notes only: the one with the best kappa."""
    scores = {n.note_id: judge_v1_score(n) for n in dev_notes}
    best = (-2.0, 7.0)
    for t10 in range(40, 101):
        t = t10 / 10
        k = cohen_kappa([n.human_final for n in dev_notes], [scores[n.note_id] >= t for n in dev_notes])
        if k > best[0] + 1e-12:
            best = (k, t)
    return best[1]


def calibration(notes: list[Note], min_kappa: float = 0.8, min_catch: float = 0.9) -> dict[str, Any]:
    dev = [n for n in notes if n.split == "dev"]
    test = [n for n in notes if n.split == "test"]
    threshold = calibrate_v1(dev)
    v1 = {n.note_id: judge_v1_score(n) >= threshold for n in notes}
    v2 = {n.note_id: judge_v2(n)[0] for n in notes}
    humans = cohen_kappa([n.human["Lakshmi"] for n in test], [n.human["the senior analyst"] for n in test])
    result: dict[str, Any] = {"threshold_v1": threshold, "human_kappa_test": humans,
                              "notes": {"dev": len(dev), "test": len(test)},
                              "people_failed_test": sum(not n.human_final for n in test)}
    for name, verdicts in (("judge-v1 (holistic)", v1), ("judge-v2 (rubric)", v2)):
        d, t = score_judge(name, dev, verdicts), score_judge(name, test, verdicts)
        result[name] = {"dev": d.__dict__, "test": t.__dict__,
                        "trusted_in_gate": t.kappa >= min_kappa and t.catches_fails >= min_catch}
    return result
