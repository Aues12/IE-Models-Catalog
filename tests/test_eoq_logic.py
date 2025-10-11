# Wave 2: Core EOQ tests, grouped by model
# Tests core logic and expected results

import math
import pytest

from inventory_models import BasicEOQ, EPQ, DiscountEOQ, BackorderEOQ

# --- Expectation helpers ----------------------------------------------------

def expected_basic(price, demand_rate, ordering_cost, holding_rate, **_):
    H = price * holding_rate
    return math.sqrt(2 * demand_rate * ordering_cost / H)

def expected_epq(price, demand_rate, ordering_cost, holding_rate, production_rate, **_):
    H = price * holding_rate
    return math.sqrt((2 * demand_rate * ordering_cost / H) * (production_rate / (production_rate - demand_rate)))

def expected_backorder(price, demand_rate, ordering_cost, holding_rate, shortage_cost, **_):
    H = price * holding_rate
    P = shortage_cost
    return math.sqrt((2 * demand_rate * ordering_cost * (H + P)) / (H * P))

def expected_discount(price, demand_rate, ordering_cost, holding_rate, discount_rates, **_):
    """Calculate the cost-minimizing order quantity when quantity discounts apply.

    Iterates over each discount tier, calculates the EOQ at that tier's unit price,
    and ensures the order quantity respects the tier's minimum (price_break) and maximum bounds.
    Selects the quantity that gives the lowest total cost across all tiers.
    """
    tiers = sorted({0: 0, **discount_rates}.items())
    best = None

    for i, (price_break, discount_rate) in enumerate(tiers):
        unit_price = price * (1 - discount_rate)
        H = unit_price * holding_rate
        next_break = tiers[i + 1][0] if i + 1 < len(tiers) else float('inf')
        qmax = next_break - 1 if next_break != float('inf') else float('inf')
        qstar = float('inf') if H <= 0 else math.sqrt(2 * demand_rate * ordering_cost / H)
        order_qty = min(max(qstar, price_break), qmax)
        total_cost = (
            demand_rate * unit_price
            + (demand_rate / order_qty) * ordering_cost
            + (order_qty / 2) * H
        )
        candidate = (total_cost, order_qty)
        if best is None or candidate < best:
            best = candidate

    if best is None:
        raise ValueError("No valid best-order quantity found.")
    else:
        return best[1]


# --- Grouped Test Classes ---------------------------------------------------

class TestBasicEOQ:
    def test_core(self):
        params = dict(price=10.0, demand_rate=1200.0, ordering_cost=50.0, holding_rate=0.20)
        model = BasicEOQ(**params)
        got = model.calculate_eoq()
        want = expected_basic(**params)
        assert got == pytest.approx(want, rel=1e-6)

    @pytest.mark.parametrize("bad_params", [
        dict(price=0, demand_rate=1000, ordering_cost=30),
        dict(price=10, demand_rate=-1, ordering_cost=30),
        dict(price=10, demand_rate=1000, ordering_cost=-5),
        dict(price=10, demand_rate=1000, ordering_cost=30, holding_rate=-0.2),
    ])
    def test_invalid_constructor(self, bad_params):
        with pytest.raises(Exception):
            BasicEOQ(**bad_params)


class TestEPQ:
    def test_core(self):
        params = dict(price=12.0, demand_rate=500.0, ordering_cost=40.0, holding_rate=0.25, production_rate=1000.0)
        model = EPQ(**params)
        got = model.calculate_eoq()
        want = expected_epq(**params)
        assert got == pytest.approx(want, rel=1e-6)

    def test_reproducibility(self):
        params = dict(price=10.0, demand_rate=400.0, ordering_cost=30.0, holding_rate=0.25, production_rate=850.0)
        model = EPQ(**params)
        a = model.calculate_eoq()
        b = model.calculate_eoq()
        assert a == pytest.approx(b, rel=1e-12)

    def test_invalid_production_rate(self):
        with pytest.raises(Exception):
            EPQ(price=10, demand_rate=500, ordering_cost=30, holding_rate=0.25, production_rate=400)


class TestBackorderEOQ:
    def test_core(self):
        params = dict(price=9.0, demand_rate=1500.0, ordering_cost=45.0, holding_rate=0.22, shortage_cost=3.0)
        model = BackorderEOQ(**params)
        got = model.calculate_eoq()
        want = expected_backorder(**params)
        assert got == pytest.approx(want, rel=1e-6)

    def test_reproducibility(self):
        params = dict(price=7.5, demand_rate=1100.0, ordering_cost=35.0, holding_rate=0.22, shortage_cost=2.5)
        model = BackorderEOQ(**params)
        a = model.calculate_eoq()
        b = model.calculate_eoq()
        assert a == pytest.approx(b, rel=1e-12)

    def test_invalid_shortage_cost(self):
        with pytest.raises(Exception):
            BackorderEOQ(price=9, demand_rate=800, ordering_cost=25, holding_rate=0.2, shortage_cost=0)


class TestDiscountEOQ:
    def test_core(self):

        model = DiscountEOQ(
            price=15.0,
            demand_rate=1000.0,
            ordering_cost=40.0,
            holding_rate=0.25,
            discount_rates={500: 0.05, 1200: 0.10}
            )
        
        got = model.calculate_eoq(analysis_mode=False)["best_quantity"]

        want = expected_discount(
            price=15.0,
            demand_rate=1000.0,
            ordering_cost=40.0,
            holding_rate=0.25,
            discount_rates={500: 0.05, 1200: 0.10}
            )
        
        assert got == pytest.approx(want, rel=1e-6)

    def test_reproducibility(self):
        model = DiscountEOQ(
            price=15.0,
            demand_rate=1000.0,
            ordering_cost=40.0,
            holding_rate=0.25,
            discount_rates={500: 0.05, 1200: 0.10}
            )
        a = model.calculate_eoq(analysis_mode=False)["best_quantity"]
        b = model.calculate_eoq(analysis_mode=False)["best_quantity"]
        assert a == pytest.approx(b, rel=1e-12)

    def test_requires_discount_tiers(self):
        with pytest.raises(Exception):
            DiscountEOQ(price=15, demand_rate=1000, ordering_cost=40, holding_rate=0.25, discount_rates={})

    def test_discount_never_recommends_zero_quantity(self):
        model = DiscountEOQ(
            price=20.0,
            demand_rate=600.0,
            ordering_cost=30.0,
            holding_rate=0.20,
            discount_rates={200: 0.05, 400: 0.1},
        )

        result = model.calculate_eoq()

        assert result["best_quantity"] > 0
