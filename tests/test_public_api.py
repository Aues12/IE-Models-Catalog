"""Cross-model policy snapshots, validation and compatibility guarantees."""

import numpy as np
import pytest

import ie_models_catalog as catalog
import inventory_models as legacy
from ie_models_agent import run


@pytest.fixture(
    params=["BasicEOQ", "EPQ", "DiscountEOQ", "IncrementalDiscountEOQ", "BackorderEOQ"]
)
def model(request):
    name = request.param
    extra = (
        {"production_rate": 200}
        if name == "EPQ"
        else {"shortage_cost": 3}
        if name == "BackorderEOQ"
        else {"discount_rates": {25: 0.1}}
        if "Discount" in name
        else {}
    )
    assert getattr(catalog, name) is getattr(legacy, name)
    return getattr(catalog, name)(
        price=10, demand_rate=100, ordering_cost=5, holding_rate=0.2, **extra
    )


def test_saved_policy_survives_model_changes(model, monkeypatch):
    result = model.solve(catalog.OrderConstraints(40, 40))
    cycle_days = result.cycle_time * 250
    times = np.array(
        [0, cycle_days / 4, cycle_days / 2, cycle_days * 0.999, cycle_days]
    )
    original = result.inventory_level(times, days_of_operation=250)
    assert original == pytest.approx(
        model.inventory_level(
            times, days_of_operation=250, constraints=catalog.OrderConstraints(40, 40)
        )
    )
    assert original[0] == pytest.approx(
        0 if isinstance(model, catalog.EPQ) else result.max_inventory
    )
    assert original[-1] == pytest.approx(original[0])
    if isinstance(model, catalog.BackorderEOQ):
        assert original[-2] < 0
    model.demand_rate = 50
    model.price = 200

    def fail(*args, **kwargs):
        raise AssertionError("A saved result must not solve again")

    monkeypatch.setattr(model, "solve", fail)
    assert result.inventory_level(times, days_of_operation=250) == pytest.approx(
        original
    )
    basis = result.cost_basis
    basis["horizon"] = "changed"
    assert result.cost_basis["horizon"] == "demand_period"


@pytest.mark.parametrize(
    "times", [True, "1", [0, True], [0, "1"], [], [float("nan")], [-1]]
)
def test_profile_validation_across_models(model, times):
    with pytest.raises(ValueError):
        model.inventory_level(times)
    with pytest.raises(ValueError):
        model.solve().inventory_level(times)


def test_epq_saved_profile_has_independent_expected_values():
    result = catalog.EPQ(
        price=10, demand_rate=100, ordering_cost=5, production_rate=200
    ).solve(catalog.OrderConstraints(40, 40))
    # Cycle .4 demand periods; production ends at .2, stock maximum is 20.
    assert result.inventory_level(
        [0, 10, 20, 30, 40], days_of_operation=100
    ) == pytest.approx([0, 10, 20, 10, 0])


def test_result_graph_does_not_reoptimize(monkeypatch):
    import plotly.express as px

    captured = {}

    class Figure:
        def show(self):
            captured["shown"] = True

    def line(**kwargs):
        captured.update(kwargs)
        return Figure()

    monkeypatch.setattr(px, "line", line)
    result = catalog.BasicEOQ(10, 100, 5).solve(catalog.OrderConstraints(40, 40))
    result.graph(days_of_operation=250)
    assert captured["shown"]
    assert captured["y"] == pytest.approx(
        result.inventory_level(captured["x"], days_of_operation=250)
    )


def test_integral_real_values_match_json_semantics():
    assert catalog.OrderConstraints(order_multiple=12.0).order_multiple == 12
    data = catalog.DLSInput([0, 1], 1, 1, lead_time=1.0)
    result = catalog.DynamicLotSizing(data).solve()
    assert result.receipt_quantities == [0, 1]
    assert data.lead_time == 1.0
    assert result.cost_basis["periods"] == 2
    response = run(
        {
            "operation": "solve_dynamic",
            "params": {
                "demand": [0, 1],
                "ordering_cost": 1,
                "holding_cost": 1,
                "lead_time": 1.0,
            },
        }
    )
    assert response["success"], response


def test_agent_does_not_leak_python_snapshot_fields():
    response = run(
        {
            "operation": "solve_eoq",
            "params": {
                "model": "epq",
                "inputs": {
                    "price": 10,
                    "demand_rate": 100,
                    "ordering_cost": 5,
                    "production_rate": 200,
                },
            },
        }
    )
    assert response["success"], response
    assert "production_rate" not in response["result"]
