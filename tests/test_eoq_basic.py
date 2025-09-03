# Wave 1 Tests for BasicEOQ
# Tests basic EOQ logic

import math
import pytest
from inventory_models import BasicEOQ


def test_calculate_eoq_matches_formula():
    price, D, S, holding_rate = 10.0, 1200.0, 50.0, 0.2
    model = BasicEOQ(price=price, demand_rate=D, ordering_cost=S, holding_rate=holding_rate)
    q = model.calculate_eoq()
    expected = math.sqrt(2 * D * S / (price * holding_rate))
    
    assert q == pytest.approx(expected, rel=1e-6)


def test_calculate_eoq_reproducible():
    model = BasicEOQ(price=12, demand_rate=800, ordering_cost=40, holding_rate=0.3)
    first = model.calculate_eoq()
    second = model.calculate_eoq()
    
    assert first == pytest.approx(second, rel=1e-12)


@pytest.mark.parametrize("invalid_parameters", [
    {"price": 0, "demand_rate": 1000, "ordering_cost": 30},
    {"price": 10, "demand_rate": -1, "ordering_cost": 30},
    {"price": 10, "demand_rate": 1000, "ordering_cost": -5},
    {"price": 10, "demand_rate": 1000, "ordering_cost": 30, "holding_rate": -0.2},
])

def test_invalid_parameters_raise(invalid_parameters):
    with pytest.raises(ValueError):
        BasicEOQ(**invalid_parameters)
