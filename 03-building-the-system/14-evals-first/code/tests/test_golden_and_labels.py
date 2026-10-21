"""The golden set's design (who is in it, in what proportions) and the labelling and adjudication rules."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from evals.agreement import agreement
from evals.golden import DEV_QUOTA, TEST_QUOTA, bundle_sha256, day7_sample_ids
from evals.labels import FIELD_ADJUDICATORS, RULE_ADJUDICATOR, adjudicate, label_all, labeller_label, paper_label
from evals.normalise import normalise
from evals.store import TRUTH, load_truth


def test_split_sizes_and_quotas(split) -> None:
    test, dev = split
    assert len(test) == 150 and len(dev) == 50
    assert Counter((g.branch, g.product) for g in test) == Counter(TEST_QUOTA)
    assert Counter((g.branch, g.product) for g in dev) == Counter(DEV_QUOTA)


def test_every_reported_stratum_has_enough_files_to_mean_something(split) -> None:
    test, _ = split
    for key in ("product", "branch", "channel", "language", "pilot"):
        counts = Counter(getattr(g, key) for g in test)
        assert min(counts.values()) >= 20, (key, counts)


def test_the_hard_cases_are_over_sampled_not_the_clean_files(split) -> None:
    test, _ = split
    phone = sum(g.channel == "phone_photo" for g in test) / len(test)
    assert phone > 0.25          # Day 7's generator makes 15 percent phone photos; the golden set wants more


def test_dev_and_test_are_disjoint_and_new(split) -> None:
    test, dev = split
    ids_test, ids_dev = {g.file_id for g in test}, {g.file_id for g in dev}
    assert not ids_test & ids_dev
    assert not (ids_test | ids_dev) & day7_sample_ids()   # never the files Day 11 was developed on


def test_selection_and_pages_are_deterministic(split) -> None:
    test, _ = split
    a, _ = test[0].build()
    b, _ = test[0].build()
    assert bundle_sha256(a) == bundle_sha256(b)


def test_agreed_labels_are_final_and_disagreements_go_to_the_named_people(labelset) -> None:
    for e in labelset.log:
        if e.item.startswith("field:"):
            assert e.by == FIELD_ADJUDICATORS
        else:
            assert e.by == RULE_ADJUDICATOR
        assert "Kaagaz" not in e.by


def test_a_format_difference_is_not_a_disagreement(split) -> None:
    test, _ = split
    gf = test[0]
    bundle, hidden = gf.build()
    paper = paper_label(gf, bundle, hidden)
    a = labeller_label("A", gf, bundle, paper)
    b = labeller_label("B", gf, bundle, paper)
    b.fields["requested_amount"] = "Rs " + f"{int(paper.fields['requested_amount']):,}"
    a.fields["requested_amount"] = paper.fields["requested_amount"]
    final, log = adjudicate(gf, a, b, paper)
    assert final.fields["requested_amount"] == normalise("requested_amount", paper.fields["requested_amount"])
    assert not [e for e in log if e.item == "field:requested_amount"]


def test_the_compliance_head_decides_send_back_reasons_by_the_signed_rules(labelset) -> None:
    gap = [e for e in labelset.log if e.item == "reason:PHOTO_UNCLEAR"]
    assert gap and all(e.final == "False" and "no signed rule" in e.reason for e in gap)


def test_pan_is_only_ever_taken_from_the_pan_card(labelset) -> None:
    for fid, final in labelset.final.items():
        if "pan_card" not in final.documents:
            assert final.fields["pan"] is None, fid


def test_agreement_is_high_after_normalising_and_shared_mistakes_are_rare(labelset, split) -> None:
    test, _ = split
    ids = {g.file_id for g in test}
    sub = type(labelset)(test, labelset.bundles, labelset.paper, labelset.a, labelset.b, labelset.final,
                         [e for e in labelset.log if e.file_id in ids])
    rep = agreement(sub)
    norm = sum(f.normalised for f in rep.fields) / sum(f.n for f in rep.fields)
    exact = sum(f.exact for f in rep.fields) / sum(f.n for f in rep.fields)
    assert norm > 0.97 and exact < norm
    assert rep.kappa_send_back > 0.8 and rep.kappa_incomplete > 0.8
    assert rep.agreed_but_wrong <= 5


def test_every_field_with_a_source_page_has_a_trajectory_step(labelset) -> None:
    for fid, final in labelset.final.items():
        steps = {s.get("field"): s.get("page") for s in final.trajectory if s["action"] == "read_field"}
        assert set(final.fields) == set(steps), fid
        assert final.trajectory[-1]["action"] == "decide"


def test_the_truth_file_on_disk_is_what_the_code_produces(truth) -> None:
    if not Path(TRUTH).exists():
        return                                        # build_golden_set.py has not been run yet
    on_disk = load_truth()
    for fid, rec in truth.items():
        assert on_disk[fid]["fields"] == rec["fields"], fid
        assert on_disk[fid]["missing"] == rec["missing"], fid
