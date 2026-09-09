"""Independent oracles: enumerate feasible schedules and sample cost surfaces."""

from itertools import product

import numpy as np
import pytest

from dynamic_models import DLSInput, DynamicLotSizing
from inventory_models import EPQ, BackorderEOQ, BasicEOQ, DiscountEOQ


def feasible_schedules(demand, initial):
    """Enumerate integer orders, without DP recurrences or interval-cost formulas."""
    required = max(0, sum(demand) - initial)

    def visit(t, stock, remaining, orders, levels):
        if t == len(demand):
            if remaining == 0:
                yield orders, levels
            return
        for quantity in range(remaining + 1):
            end_stock = stock + quantity - demand[t]
            if end_stock >= 0:
                yield from visit(
                    t + 1,
                    end_stock,
                    remaining - quantity,
                    orders + [quantity],
                    levels + [end_stock],
                )

    return list(visit(0, initial, required, [], []))


def test_dynamic_solvers_against_exhaustive_feasible_plans():
    # Integer demand and inventory suffice for an exact oracle here: each
    # uncapacitated optimum can order whole future integer demands.
    for demand in product(range(3), repeat=4):
        for initial in (0, 2, 10):
            schedules = feasible_schedules(demand, initial)
            for setup, holding in product((0, 2, 7), (0, 1, 3)):
                optimum = min(
                    sum(q > 0 for q in orders) * setup + sum(levels) * holding
                    for orders, levels in schedules
                )
                for method in ("wagner-whitin", "silver-meal"):
                    result = DynamicLotSizing(
                        DLSInput(list(demand), setup, holding, initial)
                    ).solve(method)
                    context = (demand, initial, setup, holding, method)
                    stock = initial
                    levels = []
                    for q, d in zip(result.order_quantities, demand):
                        assert q >= 0, context
                        stock += q - d
                        assert stock >= 0, context
                        levels.append(stock)
                    actual_cost = (
                        sum(q > 0 for q in result.order_quantities) * setup
                        + sum(levels) * holding
                    )
                    assert sum(result.order_quantities) == max(
                        0, sum(demand) - initial
                    ), context
                    assert result.order_periods == [
                        i + 1 for i, q in enumerate(result.order_quantities) if q > 0
                    ], context
                    assert result.inventory_levels == levels, context
                    assert result.total_cost == pytest.approx(actual_cost), context
                    if method == "wagner-whitin":
                        assert actual_cost == pytest.approx(optimum), context
                    else:
                        assert actual_cost >= optimum - 1e-9, context


@pytest.mark.parametrize("kind", ["basic", "epq", "backorder", "discount"])
def test_eoq_optimum_against_independent_cost_surface(kind):
    params = dict(price=10, demand_rate=100, ordering_cost=5, holding_rate=0.2)
    if kind == "basic":
        model = BasicEOQ(**params)
    elif kind == "epq":
        model = EPQ(**params, production_rate=200)
    elif kind == "backorder":
        model = BackorderEOQ(**params, shortage_cost=3)
    else:
        model = DiscountEOQ(**params, discount_rates={25.5: 0.02, 50: 0.1})

    # Evaluate costs directly from inventory geometry and setup frequency,
    # without using any production calculate_costs() or EOQ formulas.
    def cost(q, backlog_fraction=0.0):
        price = (
            np.where(q >= 50, 9, np.where(q >= 25.5, 9.8, 10))
            if kind == "discount"
            else 10
        )
        holding = price * 0.2
        stock_fraction = 0.5 if kind == "epq" else 1.0
        if kind == "backorder":
            stock_cost = holding * q * (1 - backlog_fraction) ** 2 / 2
            stock_cost += 3 * q * backlog_fraction**2 / 2
        else:
            stock_cost = holding * q * stock_fraction / 2
        return 100 * price + 500 / q + stock_cost

    result = model.solve()
    q = result.order_quantity
    fraction = result.max_backorder / q
    assert result.total_cost == pytest.approx(float(cost(q, fraction)))
    quantities = np.unique(
        np.concatenate([np.linspace(0.1, 300, 20000), [25.5, 50, q]])
    )
    fractions = np.linspace(0, 1, 101) if kind == "backorder" else [0]
    grid_best = min(float(np.min(cost(quantities, b))) for b in fractions)
    assert result.total_cost <= grid_best + 1e-8
