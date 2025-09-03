# Wave 3: Reorder Point (ROP) tests
# Tests whether if Reorder Point functions works as desired, for all classes

import pytest
from inventory_models import BasicEOQ, EPQ, DiscountEOQ, BackorderEOQ


# --- Parametrized ROP Tests for All Models ------------------------------------------------------

@pytest.mark.parametrize("ModelClass, init_kwargs", [
    (BasicEOQ, dict(price=10, demand_rate=1000, ordering_cost=50, holding_rate=0.2)),
    (EPQ, dict(price=10, demand_rate=1000, ordering_cost=50, production_rate=3000, holding_rate=0.2)),
    (DiscountEOQ, dict(price=10, demand_rate=1000, ordering_cost=50, holding_rate=0.2, discount_rates={0: 0.0, 100: 0.05})),
    (BackorderEOQ, dict(price=10, demand_rate=1000, ordering_cost=50, shortage_cost=20, holding_rate=0.2)),
], ids=["BasicEOQ", "EPQ", "DiscountEOQ", "BackorderEOQ"])

def test_rop_calculation(ModelClass, init_kwargs):
    model = ModelClass(**init_kwargs)
    rop = model.calculate_reorder_point(lead_time=10, safety_stock=5, days_of_operation=250)
    expected = (1000 / 250) * 10 + 5  # daily demand * lead time + safety stock
    assert rop == pytest.approx(expected, rel=1e-6)


# --- Parametrized Invalid Input Tests for All Models --------------------------------------------

@pytest.mark.parametrize("ModelClass, init_kwargs", [
    (BasicEOQ, dict(price=10, demand_rate=1000, ordering_cost=50, holding_rate=0.2)),
    (EPQ, dict(price=10, demand_rate=1000, ordering_cost=50, production_rate=3000, holding_rate=0.2)),
    (DiscountEOQ, dict(price=10, demand_rate=1000, ordering_cost=50, holding_rate=0.2, discount_rates={0: 0.0, 100: 0.05})),
    (BackorderEOQ, dict(price=10, demand_rate=1000, ordering_cost=50, shortage_cost=20, holding_rate=0.2)),
], ids=["BasicEOQ", "EPQ", "DiscountEOQ", "BackorderEOQ"])
@pytest.mark.parametrize("kwargs", [
    dict(lead_time=-1, safety_stock=5, days_of_operation=250),
    dict(lead_time=10, safety_stock=-5, days_of_operation=250),
    dict(lead_time=10, safety_stock=5, days_of_operation=0),
], ids=[
    "ROP fails: lead_time < 0",
    "ROP fails: safety_stock < 0",
    "ROP fails: days_of_operation = 0",
])

def test_invalid_inputs(ModelClass, init_kwargs, kwargs):
    model = ModelClass(**init_kwargs)
    with pytest.raises(ValueError):
        model.calculate_reorder_point(**kwargs)
