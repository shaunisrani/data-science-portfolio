import math

import pytest

from tools import cpk, die_yield, gross_dies_per_wafer


def test_poisson_yield():
    assert die_yield(1.0, 0.1) == pytest.approx(math.exp(-0.1))


def test_models_order_for_large_die():
    # Clustering models predict higher yield than Poisson for large dies
    p = die_yield(4.0, 0.5, "poisson")
    assert die_yield(4.0, 0.5, "murphy") > p
    assert die_yield(4.0, 0.5, "negative_binomial", alpha=1.0) > p


def test_nb_approaches_poisson_for_large_alpha():
    assert die_yield(2.0, 0.3, "nb", alpha=1e6) == pytest.approx(die_yield(2.0, 0.3), rel=1e-4)


def test_dies_per_wafer_300mm():
    assert 600 < gross_dies_per_wafer(300, 100) < 700  # ~640 for a 100 mm^2 die


def test_cpk():
    assert cpk(10, 0.5, 8, 12) == pytest.approx(4 / 3)


@pytest.mark.parametrize("args", [(0, 0.1), (1, -1)])
def test_bad_inputs(args):
    with pytest.raises(ValueError):
        die_yield(*args)
