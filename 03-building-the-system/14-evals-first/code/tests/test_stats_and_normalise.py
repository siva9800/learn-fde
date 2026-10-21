"""The arithmetic under every number in the report, and the normaliser that is part of the metric's definition."""

from __future__ import annotations

import pytest

from evals.normalise import norm_equal, normalise
from evals.stats import binom_tail_ge, cluster_bootstrap, cohen_kappa, paired_worse_p, wilson


def test_wilson_matches_the_textbook_value() -> None:
    lo, hi = wilson(81, 100)
    assert round(lo, 3) == 0.722 and round(hi, 3) == 0.875


def test_wilson_never_leaves_zero_to_one_even_at_the_edges() -> None:
    assert wilson(0, 20)[0] == 0.0 and 0.0 < wilson(0, 20)[1] < 0.2
    assert wilson(20, 20)[1] == 1.0 and wilson(20, 20)[0] > 0.8
    assert wilson(0, 0) == (0.0, 1.0)


def test_kappa_is_one_for_perfect_agreement_and_near_zero_for_chance() -> None:
    a = [True, False] * 50
    assert cohen_kappa(a, a) == 1.0
    assert abs(cohen_kappa(a, [True, True, False, False] * 25)) < 1e-9


def test_kappa_punishes_agreement_that_comes_from_a_skewed_base_rate() -> None:
    # 95 percent raw agreement, but almost everything is "complete": kappa is far lower than 0.95.
    a = [True] * 95 + [False] * 5
    b = [True] * 90 + [False] * 5 + [True] * 5
    assert sum(x == y for x, y in zip(a, b)) / 100 == 0.90
    assert cohen_kappa(a, b) < 0.5


def test_paired_test_is_a_fair_coin_on_the_changed_fields() -> None:
    assert paired_worse_p(0, 0) == 1.0
    assert paired_worse_p(5, 5) > 0.5
    assert paired_worse_p(9, 0) == pytest.approx(0.5 ** 9)
    assert binom_tail_ge(3, 3) == pytest.approx(0.125)


def test_cluster_bootstrap_is_seeded_and_contains_the_point_estimate() -> None:
    per_file = [(11, 12)] * 40 + [(6, 12)] * 5
    lo, hi = cluster_bootstrap(per_file)
    assert (lo, hi) == cluster_bootstrap(per_file)
    point = sum(k for k, _ in per_file) / sum(n for _, n in per_file)
    assert lo < point < hi


@pytest.mark.parametrize("field_name,a,b", [
    ("requested_amount", "Rs 1,25,000", "125000"),
    ("date_of_birth", "15/03/1986", "15-03-1986"),
    ("applicant_name", "Ravi Teja  Pasupuleti", "RAVI TEJA PASUPULETI"),
    ("mobile", "98765 43210", "9876543210"),
    ("gross_weight_g", "30", "30.0"),
    ("pan", "abcpp1234k", "ABCPP1234K"),
])
def test_the_normaliser_forgives_format(field_name: str, a: str, b: str) -> None:
    assert norm_equal(field_name, a, b)


@pytest.mark.parametrize("field_name,a,b", [
    ("requested_amount", "125000", "1250000"),             # the stray zero on a handwritten amount
    ("applicant_name", "RAAVI TEJA PASUPULETI", "RAVI TEJA PASUPULETI"),   # a transliteration variant
    ("pan", "ABCPP1234K", "ABCPP1284K"),                    # one OCR character
    ("monthly_income", "32000", "384000"),                 # monthly read as annual
    ("address", "35-19, BRODIPET", "35-19, BRODIPET, GUNTUR 522002"),
])
def test_the_normaliser_never_forgives_content(field_name: str, a: str, b: str) -> None:
    assert not norm_equal(field_name, a, b)


def test_not_in_file_is_a_value_of_its_own() -> None:
    assert normalise("pan", None) is None and normalise("pan", "  ") is None
    assert norm_equal("pan", None, "") and not norm_equal("pan", None, "ABCPP1234K")
