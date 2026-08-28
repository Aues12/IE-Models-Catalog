import pytest

from dynamic_models import DLSInput, DynamicLotSizing


def test_wagner_whitin_matches_documented_example():
    data = DLSInput(demand=[10, 20, 30], ordering_cost=100, holding_cost=1)

    result = DynamicLotSizing(data).solve("wagner-whitin")

    assert result.order_quantities == pytest.approx([60, 0, 0])
    assert result.total_cost == pytest.approx(180)
    assert result.order_periods == [1]


def test_silver_meal_matches_documented_example():
    data = DLSInput(demand=[10, 20, 30], ordering_cost=100, holding_cost=1)

    result = DynamicLotSizing(data).solve("silver-meal")

    assert result.order_quantities == pytest.approx([60, 0, 0])
    assert result.total_cost == pytest.approx(180)
    assert result.order_periods == [1]


@pytest.mark.parametrize("method", ["wagner-whitin", "silver-meal"])
def test_dynamic_lot_sizing_skips_leading_zero_demand_period(method):
    data = DLSInput(demand=[0, 10], ordering_cost=100, holding_cost=1)

    result = DynamicLotSizing(data).solve(method)

    assert result.order_quantities == pytest.approx([0, 10])
    assert result.total_cost == pytest.approx(100)
    assert result.order_periods == [2]


@pytest.mark.parametrize("method", ["wagner-whitin", "silver-meal"])
def test_dynamic_lot_sizing_does_not_order_for_all_zero_demand(method):
    data = DLSInput(demand=[0], ordering_cost=100, holding_cost=1)

    result = DynamicLotSizing(data).solve(method)

    assert result.order_quantities == pytest.approx([0])
    assert result.total_cost == pytest.approx(0)
    assert result.order_periods == []


@pytest.mark.parametrize(
    "bad_data",
    [
        DLSInput(demand=[], ordering_cost=100, holding_cost=1),
        DLSInput(demand=[10, -5, 20], ordering_cost=100, holding_cost=1),
        DLSInput(demand=[10, 20], ordering_cost=-1, holding_cost=1),
        DLSInput(demand=[10, 20], ordering_cost=10, holding_cost=-1),
    ],
)
def test_dynamic_lot_sizing_rejects_invalid_inputs(bad_data):
    with pytest.raises(ValueError):
        DynamicLotSizing(bad_data)


def test_dynamic_lot_sizing_rejects_unknown_method():
    data = DLSInput(demand=[10, 20, 30], ordering_cost=100, holding_cost=1)

    with pytest.raises(ValueError):
        DynamicLotSizing(data).solve("unknown-method")
