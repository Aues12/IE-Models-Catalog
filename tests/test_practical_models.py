"""Operational extensions checked against independent billing and stock balances."""

import itertools

import pytest

from dynamic_models import DLSInput, DynamicLotSizing
from ie_models_agent import run
from inventory_models import (
    EPQ,
    BackorderEOQ,
    BasicEOQ,
    DiscountEOQ,
    IncrementalDiscountEOQ,
)
from model_common import InfeasiblePlanError, OrderConstraints

BASE = dict(price=10, demand_rate=100, ordering_cost=5, holding_rate=0.2)


def billing(q, incremental):
    if incremental:
        return 10 * min(q, 25.5) + 9 * min(max(q - 25.5, 0), 24.5) + 8 * max(q - 50, 0)
    return q * (10 if q < 25.5 else 9 if q < 50 else 8)


@pytest.mark.parametrize(
    "kind", ["basic", "epq", "backorder", "discount", "incremental"]
)
@pytest.mark.parametrize(
    "step,lower,upper", [(1, 0, 100), (12, 20, 90), (7, 51, 99), (1, 26, 26)]
)
def test_constrained_optimum_against_every_allowed_lot(kind, step, lower, upper):
    classes = dict(
        basic=BasicEOQ,
        epq=EPQ,
        backorder=BackorderEOQ,
        discount=DiscountEOQ,
        incremental=IncrementalDiscountEOQ,
    )
    extra = (
        {"production_rate": 200}
        if kind == "epq"
        else {"shortage_cost": 3}
        if kind == "backorder"
        else {"discount_rates": {25.5: 0.1, 50: 0.2}}
        if kind in {"discount", "incremental"}
        else {}
    )
    model = classes[kind](**BASE, **extra)
    constraints = OrderConstraints(lower, upper, order_multiple=step)

    def independent_cost(q):
        purchase = (
            100 * billing(q, kind == "incremental") / q
            if kind in {"discount", "incremental"}
            else 1000
        )
        h = purchase / 100 * 0.2
        holding_shortage = h * q / 2
        if kind == "epq":
            holding_shortage *= 0.5
        elif kind == "backorder":
            stock = q * 3 / (h + 3)
            backlog = q - stock
            holding_shortage = (h * stock**2 + 3 * backlog**2) / (2 * q)
        return purchase + 500 / q + holding_shortage

    allowed = [q for q in range(step, int(upper) + 1, step) if q >= lower]
    result = model.solve(constraints)
    assert result.order_quantity in allowed
    assert result.total_cost == pytest.approx(min(map(independent_cost, allowed)))
    assert model.inventory_level(0, constraints=constraints) == pytest.approx(
        0 if kind == "epq" else result.max_inventory
    )


@pytest.mark.parametrize("cls", [BasicEOQ, DiscountEOQ, IncrementalDiscountEOQ])
def test_continuous_bounds_and_infeasible_packs(cls):
    extra = {} if cls == BasicEOQ else {"discount_rates": {25.5: 0.1, 50: 0.2}}
    model = cls(**BASE, **extra)
    assert model.solve(OrderConstraints(27.3, 27.3)).order_quantity == 27.3
    with pytest.raises(InfeasiblePlanError):
        model.solve(OrderConstraints(25, 30, order_multiple=12))
    assert model.solve(OrderConstraints(integer=True)).order_quantity.is_integer()


@pytest.mark.parametrize(
    "kwargs",
    [
        {"min_quantity": -1},
        {"max_quantity": 0},
        {"min_quantity": 3, "max_quantity": 2},
        {"order_multiple": 1.5},
        {"order_multiple": True},
        {"integer": 1},
    ],
)
def test_invalid_constraints(kwargs):
    with pytest.raises(ValueError):
        OrderConstraints(**kwargs)


def test_incremental_billing_continuity_and_continuous_optimum():
    model = IncrementalDiscountEOQ(**BASE, discount_rates={25.5: 0.1, 50: 0.2})
    for q in [1, 25.5 - 1e-7, 25.5, 25.5 + 1e-7, 50, 80]:
        costs = model.calculate_costs(q)
        assert costs.purchase == pytest.approx(100 * billing(q, True) / q)
        assert costs.holding == pytest.approx(0.1 * billing(q, True))
    optimum = model.solve()
    # A dense independent grid is an upper bound on the continuous optimum.
    grid_costs = [
        100 * billing(q / 100, True) / (q / 100)
        + 500 / (q / 100)
        + 0.1 * billing(q / 100, True)
        for q in range(1, 20001)
    ]
    assert optimum.total_cost <= min(grid_costs) + 1e-8
    assert optimum.total_cost == pytest.approx(min(grid_costs), abs=0.001)


def exhaustive_cost(demand, setup, holding, initial, lead):
    needed = max(sum(demand) - initial, 0)
    best = float("inf")
    for releases in itertools.product(
        range(needed + 1), repeat=max(len(demand) - lead, 0)
    ):
        if sum(releases) != needed:
            continue
        stock, cost = initial, 0
        for t, d in enumerate(demand):
            stock += (releases[t - lead] if 0 <= t - lead < len(releases) else 0) - d
            if stock < 0:
                break
            cost += stock * holding[t]
            if t < len(releases) and releases[t]:
                cost += setup[t]
        else:
            best = min(best, cost)
    return best


@pytest.mark.parametrize("lead", [0, 1, 3])
@pytest.mark.parametrize(
    "setup,holding",
    [([5, 1, 8], [2, 0, 3]), ([0, 9, 1], [0, 2, 1]), ([4, 4, 4], [1, 1, 1])],
)
def test_dynamic_against_exhaustive_release_schedules(lead, setup, holding):
    for demand in itertools.product(range(3), repeat=3):
        for initial in [0, 2, 7]:
            expected = exhaustive_cost(demand, setup, holding, initial, lead)
            model = DynamicLotSizing(
                DLSInput(list(demand), setup, holding, initial, lead)
            )
            for method in ["wagner-whitin", "silver-meal"]:
                if expected == float("inf"):
                    with pytest.raises(InfeasiblePlanError):
                        model.solve(method)
                    continue
                result = model.solve(method)
                stock, cost = initial, 0
                for t, d in enumerate(demand):
                    receipt = result.order_quantities[t - lead] if t >= lead else 0
                    assert result.receipt_quantities[t] == receipt
                    stock += receipt - d
                    assert stock >= 0
                    assert result.inventory_levels[t] == stock
                    cost += stock * holding[t] + (
                        setup[t] if result.order_quantities[t] else 0
                    )
                assert result.total_cost == pytest.approx(cost)
                assert result.total_cost >= expected - 1e-9
                if method == "wagner-whitin":
                    assert result.total_cost == pytest.approx(expected)


def test_earlier_zero_demand_receipt_can_be_cheaper():
    model = DynamicLotSizing(DLSInput([0, 2], [1, 100], [1, 1]))
    assert model.solve().receipt_quantities == [2, 0]
    assert model.solve().total_cost == 3
    assert model.solve("silver-meal").total_cost == 100


@pytest.mark.parametrize("method", ["wagner-whitin", "silver-meal"])
def test_scalar_cost_compatibility(method):
    assert DynamicLotSizing(DLSInput([1, 2, 3], 5, 1)).solve(
        method
    ) == DynamicLotSizing(DLSInput([1, 2, 3], [5] * 3, [1] * 3)).solve(method)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"lead_time": -1},
        {"lead_time": 1.5},
        {"lead_time": True},
        {"ordering_cost": [2]},
        {"holding_cost": [1, -1]},
    ],
)
def test_invalid_dynamic_extensions(kwargs):
    data = dict(demand=[1, 2], ordering_cost=5, holding_cost=1)
    with pytest.raises(ValueError):
        DynamicLotSizing(DLSInput(**(data | kwargs)))


def test_agent_practical_contracts():
    params = {
        "model": "incremental_discount_eoq",
        "inputs": BASE
        | {"discount_tiers": [{"minimum_quantity": 25.5, "discount_rate": 0.1}]},
        "constraints": {"order_multiple": 12, "min_quantity": 20, "max_quantity": 90},
    }
    result = run({"operation": "solve_eoq", "params": params})
    assert result["success"], result
    assert result["result"]["order_quantity"] % 12 == 0
    params["constraints"] = {
        "min_quantity": 25,
        "max_quantity": 30,
        "order_multiple": 12,
    }
    error = run({"operation": "solve_eoq", "params": params})
    assert error["error"]["code"] == "INFEASIBLE_PLAN"
    dynamic = {
        "demand": [2, 3, 4],
        "initial_inventory": 2,
        "lead_time": 1,
        "ordering_cost": [5, 1, 8],
        "holding_cost": [2, 1, 0],
    }
    result = run({"operation": "solve_dynamic", "params": dynamic})
    assert result["success"], result
    assert result["result"]["receipt_quantities"][0] == 0
    dynamic["initial_inventory"] = 0
    assert (
        run({"operation": "solve_dynamic", "params": dynamic})["error"]["code"]
        == "INFEASIBLE_PLAN"
    )


def test_operational_json_examples_and_cli_infeasibility():
    import json
    import subprocess
    import sys
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    for name in ["constrained_eoq", "incremental_discount", "dynamic_lead_time"]:
        response = run(json.loads((root / f"examples/agent/{name}.json").read_text()))
        assert response["success"], response
    request = {
        "operation": "solve_dynamic",
        "params": {
            "demand": [1],
            "ordering_cost": 1,
            "holding_cost": 1,
            "lead_time": 1,
        },
    }
    process = subprocess.run(
        [sys.executable, "-m", "ie_models_agent"],
        input=json.dumps(request),
        capture_output=True,
        text=True,
        cwd=root,
        check=False,
    )
    assert process.returncode == 1
    assert not process.stderr
    assert json.loads(process.stdout)["error"]["code"] == "INFEASIBLE_PLAN"
