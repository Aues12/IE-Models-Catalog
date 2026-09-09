"""Regression and result-contract tests for the shared planning API."""

import math

import numpy as np
import pytest

from dynamic_models import DLSInput, DynamicLotSizing
from inventory_models import EPQ, BackorderEOQ, BasicEOQ, DiscountEOQ
from model_common import CostBreakdown


def models():
    common = dict(price=100, demand_rate=1000, ordering_cost=50)
    return [
        BasicEOQ(**common),
        EPQ(**common, production_rate=2000),
        BackorderEOQ(**common, shortage_cost=10),
        DiscountEOQ(**common, discount_rates={1: 0.001, 100: 0.05}),
    ]


@pytest.mark.parametrize("model", models())
def test_result_and_legacy_api_agree(model):
    result = model.solve()
    assert result.order_quantity == pytest.approx(model.calculate_eoq())
    assert result.cycle_time * model.demand_rate == pytest.approx(result.order_quantity)
    assert result.costs == model.calculate_costs(result.order_quantity)
    assert result.total_cost == pytest.approx(
        result.costs.purchase
        + result.costs.ordering
        + result.costs.holding
        + result.costs.shortage
    )
    assert result.costs.purchase == pytest.approx(model.demand_rate * result.unit_price)
    if isinstance(model, BackorderEOQ):
        old = model.calculate_cycle_metrics()
        assert old["TotalCost"] == pytest.approx(result.costs.relevant_cost)
        assert old["S_max"] == pytest.approx(result.max_inventory)
        assert old["B_max"] == pytest.approx(result.max_backorder)
    else:
        assert result.max_backorder == 0
        assert result.costs.shortage == 0


@pytest.mark.parametrize("model", models())
def test_analysis_preserves_scalar_and_array_returns(model, capsys):
    for time in (0, 20, np.array([0, 10, 20])):
        ordinary = model.inventory_level(time)
        explained = model.inventory_level(time, analysis_mode=True)
        assert explained == pytest.approx(ordinary)
    assert capsys.readouterr().out


@pytest.mark.parametrize("model", models())
def test_time_units_are_consistent(model):
    assert model.inventory_level(50, days_of_operation=250) == pytest.approx(
        model.inventory_level(73, days_of_operation=365)
    )
    assert model.calculate_reorder_point(50, days_of_operation=250) == 200


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf, True, "10", None])
@pytest.mark.parametrize(
    "parameter", ["price", "demand_rate", "ordering_cost", "holding_rate"]
)
def test_core_inputs_must_be_finite_real_numbers(parameter, value):
    params = dict(price=10, demand_rate=100, ordering_cost=5, holding_rate=0.2)
    params[parameter] = value
    with pytest.raises(ValueError):
        BasicEOQ(**params)


@pytest.mark.parametrize("value", [math.nan, math.inf, -1, True])
def test_additional_inputs_are_validated(value):
    common = dict(price=10, demand_rate=100, ordering_cost=5)
    with pytest.raises(ValueError):
        EPQ(**common, production_rate=value)
    with pytest.raises(ValueError):
        BackorderEOQ(**common, shortage_cost=value)
    with pytest.raises(ValueError):
        BasicEOQ(**common, lead_time=value)
    model = BasicEOQ(**common)
    for kwargs in (
        dict(lead_time=value),
        dict(lead_time=1, safety_stock=value),
        dict(lead_time=1, days_of_operation=value),
    ):
        with pytest.raises(ValueError):
            model.calculate_reorder_point(**kwargs)


@pytest.mark.parametrize(
    "tiers",
    [
        {-1: 0.1},
        {math.nan: 0.1},
        {math.inf: 0.1},
        {1: math.nan},
        {1: math.inf},
        {1: -0.1},
        {1: 1},
        {10: 0.2, 20: 0.1},
    ],
)
def test_invalid_discount_tiers(tiers):
    with pytest.raises(ValueError):
        DiscountEOQ(100, 1000, 50, discount_rates=tiers)


def test_discount_does_not_choose_zero_quantity():
    model = DiscountEOQ(100, 1000, 50, discount_rates={1: 0.001})
    result = model.solve()
    assert result.order_quantity > 1
    assert result.unit_price == pytest.approx(99.9)
    for invalid in (0, -1, math.nan, math.inf):
        with pytest.raises(ValueError):
            model.calculate_total_cost(invalid, 100)
        with pytest.raises(ValueError):
            model.calculate_costs(invalid)


def test_fractional_breaks_do_not_create_gaps():
    # With equal prices the breakpoint cannot change the basic optimum (2.5).
    model = DiscountEOQ(
        10, 10, 0.625, holding_rate=0.2, discount_rates={2.75: 0.0, 3.1: 0.0}
    )
    assert model.calculate_eoq() == pytest.approx(2.5)
    discounted = DiscountEOQ(
        10, 10, 0.625, holding_rate=0.2, discount_rates={2.75: 0.1}
    )
    assert discounted.solve().order_quantity == pytest.approx(2.75)
    assert discounted.calculate_costs(2.75).purchase == 90
    assert discounted.calculate_costs(2.749).purchase == 100


@pytest.mark.parametrize("method", ["wagner-whitin", "silver-meal"])
@pytest.mark.parametrize(
    "initial, orders, levels, holding",
    [
        (10, [0, 0], [0, 0], 0),
        (15, [0, 0], [5, 5], 10),
        (4, [6, 0], [0, 0], 0),
    ],
)
def test_initial_inventory_and_cost_convention(
    method, initial, orders, levels, holding
):
    data = DLSInput([10, 0], 100, 1, initial_inventory=initial)
    result = DynamicLotSizing(data).solve(method)
    assert result.order_quantities == orders
    assert result.inventory_levels == levels
    assert result.costs.holding == holding
    assert result.costs.ordering == (100 if initial < 10 else 0)
    assert result.total_cost == result.costs.total_cost
    assert data.demand == [10, 0]
    assert data.initial_inventory == initial


@pytest.mark.parametrize(
    "field", ["ordering_cost", "holding_cost", "initial_inventory", "demand"]
)
@pytest.mark.parametrize("value", [math.nan, math.inf, -1, True, None])
def test_dynamic_nonfinite_and_invalid_inputs(field, value):
    kwargs = dict(demand=[1, 2], ordering_cost=2, holding_cost=1, initial_inventory=0)
    kwargs[field] = [value] if field == "demand" else value
    with pytest.raises(ValueError):
        DynamicLotSizing(DLSInput(**kwargs))


def test_cost_breakdown_arithmetic():
    costs = CostBreakdown(purchase=100, ordering=20, holding=3, shortage=4)
    assert costs.relevant_cost == 27
    assert costs.total_cost == 127


@pytest.mark.parametrize("model", models())
@pytest.mark.parametrize("time", [-1, math.nan, math.inf, [0, -1]])
def test_invalid_profile_times(model, time):
    with pytest.raises(ValueError):
        model.inventory_level(time)


@pytest.mark.parametrize("method", ["wagner-whitin", "silver-meal"])
def test_fractional_initial_stock_is_depleted_across_periods(method):
    result = DynamicLotSizing(DLSInput([0.1, 0.2, 0.3], 10, 1, 0.15)).solve(method)
    assert result.order_quantities == pytest.approx([0, 0.45, 0])
    assert result.inventory_levels == pytest.approx([0.05, 0.3, 0])
    assert result.costs.ordering == 10
    assert result.costs.holding == pytest.approx(0.35)
    assert result.total_cost == pytest.approx(10.35)
