# Model-specific regression tests.
# Independent numerical optimality checks live in test_independent_optimality.py.

import math

import pytest

from inventory_models import EPQ, BackorderEOQ, DiscountEOQ


class TestEPQ:
    def test_calculate_eoq_stores_result(self):
        model = EPQ(
            price=10,
            demand_rate=400,
            ordering_cost=30,
            holding_rate=0.25,
            production_rate=850,
        )

        result = model.calculate_eoq()

        assert model.eoq_value == pytest.approx(result)


class TestBackorderEOQ:
    def test_calculate_eoq_stores_result(self):
        model = BackorderEOQ(
            price=7.5,
            demand_rate=1100,
            ordering_cost=35,
            holding_rate=0.22,
            shortage_cost=2.5,
        )

        result = model.calculate_eoq()

        assert model.eoq_value == pytest.approx(result)


class TestDiscountEOQ:
    def test_core(self):

        model = DiscountEOQ(
            price=15.0,
            demand_rate=1000.0,
            ordering_cost=40.0,
            holding_rate=0.25,
            discount_rates={500: 0.05, 1200: 0.10},
        )

        got = model.calculate_eoq(analysis_mode=False)

        want = 500.0  # Hand-checked tier boundary with total cost 15,220.625.

        assert got == pytest.approx(want, rel=1e-6)

    def test_calculate_eoq_stores_result(self):
        model = DiscountEOQ(
            price=15.0,
            demand_rate=1000.0,
            ordering_cost=40.0,
            holding_rate=0.25,
            discount_rates={500: 0.05, 1200: 0.10},
        )

        result = model.calculate_eoq()

        assert model.eoq_value == pytest.approx(result)

    def test_considers_base_price_tier_when_zero_break_is_omitted(self):
        """A high discount threshold must not exclude the undiscounted EOQ."""
        params = dict(
            price=100.0,
            demand_rate=1000.0,
            ordering_cost=10.0,
            holding_rate=0.20,
            discount_rates={100_000: 0.01},
        )

        model = DiscountEOQ(**params)

        assert model.calculate_eoq() == pytest.approx(math.sqrt(1000))
