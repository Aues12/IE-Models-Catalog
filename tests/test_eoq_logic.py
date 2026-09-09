# Wave 2: Core EOQ tests, grouped by model
# Tests core logic and expected results

import math

import pytest

from inventory_models import EPQ, BackorderEOQ, BasicEOQ, DiscountEOQ

# --- Expectation helpers ----------------------------------------------------


def expected_basic(price, demand_rate, ordering_cost, holding_rate, **_):
    H = price * holding_rate
    return math.sqrt(2 * demand_rate * ordering_cost / H)


def expected_epq(price, demand_rate, ordering_cost, holding_rate, production_rate, **_):
    H = price * holding_rate
    return math.sqrt(
        (2 * demand_rate * ordering_cost / H)
        * (production_rate / (production_rate - demand_rate))
    )


def expected_backorder(
    price, demand_rate, ordering_cost, holding_rate, shortage_cost, **_
):
    H = price * holding_rate
    P = shortage_cost
    return math.sqrt((2 * demand_rate * ordering_cost * (H + P)) / (H * P))


# --- Grouped Test Classes ---------------------------------------------------


class TestBasicEOQ:
    def test_core(self):
        params = dict(
            price=10.0, demand_rate=1200.0, ordering_cost=50.0, holding_rate=0.20
        )
        model = BasicEOQ(**params)
        got = model.calculate_eoq()
        want = expected_basic(**params)
        assert got == pytest.approx(want, rel=1e-6)

    @pytest.mark.parametrize(
        "bad_params",
        [
            dict(price=0, demand_rate=1000, ordering_cost=30),
            dict(price=10, demand_rate=-1, ordering_cost=30),
            dict(price=10, demand_rate=1000, ordering_cost=-5),
            dict(price=10, demand_rate=1000, ordering_cost=30, holding_rate=-0.2),
        ],
    )
    def test_invalid_constructor(self, bad_params):
        with pytest.raises(ValueError):
            BasicEOQ(**bad_params)


class TestEPQ:
    def test_core(self):
        params = dict(
            price=12.0,
            demand_rate=500.0,
            ordering_cost=40.0,
            holding_rate=0.25,
            production_rate=1000.0,
        )
        model = EPQ(**params)
        got = model.calculate_eoq()
        want = expected_epq(**params)
        assert got == pytest.approx(want, rel=1e-6)

    def test_reproducibility(self):
        params = dict(
            price=10.0,
            demand_rate=400.0,
            ordering_cost=30.0,
            holding_rate=0.25,
            production_rate=850.0,
        )
        model = EPQ(**params)
        a = model.calculate_eoq()
        b = model.calculate_eoq()
        assert a == pytest.approx(b, rel=1e-12)

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

    def test_invalid_production_rate(self):
        with pytest.raises(ValueError):
            EPQ(
                price=10,
                demand_rate=500,
                ordering_cost=30,
                holding_rate=0.25,
                production_rate=400,
            )


class TestBackorderEOQ:
    def test_core(self):
        params = dict(
            price=9.0,
            demand_rate=1500.0,
            ordering_cost=45.0,
            holding_rate=0.22,
            shortage_cost=3.0,
        )
        model = BackorderEOQ(**params)
        got = model.calculate_eoq()
        want = expected_backorder(**params)
        assert got == pytest.approx(want, rel=1e-6)

    def test_reproducibility(self):
        params = dict(
            price=7.5,
            demand_rate=1100.0,
            ordering_cost=35.0,
            holding_rate=0.22,
            shortage_cost=2.5,
        )
        model = BackorderEOQ(**params)
        a = model.calculate_eoq()
        b = model.calculate_eoq()
        assert a == pytest.approx(b, rel=1e-12)

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

    def test_invalid_shortage_cost(self):
        with pytest.raises(ValueError):
            BackorderEOQ(
                price=9,
                demand_rate=800,
                ordering_cost=25,
                holding_rate=0.2,
                shortage_cost=0,
            )


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

    def test_reproducibility(self):
        model = DiscountEOQ(
            price=15.0,
            demand_rate=1000.0,
            ordering_cost=40.0,
            holding_rate=0.25,
            discount_rates={500: 0.05, 1200: 0.10},
        )
        a = model.calculate_eoq(analysis_mode=False)
        b = model.calculate_eoq(analysis_mode=False)
        assert a == pytest.approx(b, rel=1e-12)

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

    def test_requires_discount_tiers(self):
        with pytest.raises(ValueError):
            DiscountEOQ(
                price=15,
                demand_rate=1000,
                ordering_cost=40,
                holding_rate=0.25,
                discount_rates={},
            )

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
