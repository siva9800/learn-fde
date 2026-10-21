"""The small amount of statistics an eval report needs, standard library only.

Wilson intervals for proportions, Cohen's kappa for two labellers, an exact one-sided binomial test for
paired before/after comparisons, and a file-level (cluster) bootstrap, because the twelve fields of one
file are not twelve independent coin flips.
"""

from __future__ import annotations

import math
import random
from collections import Counter
from collections.abc import Hashable, Sequence


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """95 percent Wilson score interval for k successes in n trials. (0, 1) when n is 0."""
    if n == 0:
        return 0.0, 1.0
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return max(0.0, centre - half), min(1.0, centre + half)


def cohen_kappa(a: Sequence[Hashable], b: Sequence[Hashable]) -> float:
    """Agreement beyond chance between two labellers on the same items.

    1.0 is perfect agreement; 0.0 is what two people labelling at random with the same habits would get.
    When both labellers give every item the same single label, kappa is undefined; we return 1.0 if they
    agree on everything (nothing to disagree about) and 0.0 otherwise.
    """
    if len(a) != len(b):
        raise ValueError("the two label lists must be the same length")
    n = len(a)
    if n == 0:
        raise ValueError("no items")
    observed = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    expected = sum(ca[k] * cb.get(k, 0) for k in ca) / (n * n)
    if expected >= 1.0:
        return 1.0 if observed == 1.0 else 0.0
    return (observed - expected) / (1 - expected)


def binom_tail_ge(k: int, n: int, p: float = 0.5) -> float:
    """P(X >= k) for X ~ Binomial(n, p). Exact."""
    if k <= 0:
        return 1.0
    if k > n:
        return 0.0
    return sum(math.comb(n, i) * p**i * (1 - p) ** (n - i) for i in range(k, n + 1))


def paired_worse_p(regressions: int, fixes: int) -> float:
    """One-sided exact test on the discordant pairs (McNemar's idea, done exactly).

    Of the fields that changed between two runs on the same files, `regressions` went right to wrong and
    `fixes` went wrong to right. If the change did nothing, each changed field is a fair coin. The value
    returned is the chance of seeing this many regressions or more from a coin.
    """
    return binom_tail_ge(regressions, regressions + fixes, 0.5)


def cluster_bootstrap(per_file: Sequence[tuple[int, int]], reps: int = 2000, seed: int = 14) -> tuple[float, float]:
    """95 percent interval for sum(k)/sum(n), resampling whole files with replacement.

    `per_file` holds (successes, trials) per file. Resampling files, not fields, keeps the fields of one
    file together, so a file that is bad everywhere (a blurred phone photo) widens the interval as it should.
    """
    if not per_file:
        return 0.0, 1.0
    rng = random.Random(seed)
    m = len(per_file)
    stats: list[float] = []
    for _ in range(reps):
        k = n = 0
        for _ in range(m):
            a, b = per_file[rng.randrange(m)]
            k += a
            n += b
        stats.append(k / n if n else 0.0)
    stats.sort()
    return stats[int(0.025 * reps)], stats[int(0.975 * reps) - 1]
