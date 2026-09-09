# Silver–Meal Heuristic

[Model catalog](README.md) · [Shared conventions](conventions.md) · [API reference](../API_REFERENCE.md)

## Purpose

Build a feasible dynamic order plan by comparing average cost per covered period as each order is extended.

## Assumptions

- Known demand over a finite horizon; one item and equal-duration periods.
- Orders are available before demand in their order period: no explicit delivery delay.
- Constant, non-negative setup and holding costs; unlimited ordering and storage capacity.
- All demand must be met; initial inventory is available before period 1.

## Inputs and units

Use the [shared dynamic inputs and units](conventions.md#dynamic-lot-sizing). Periods must have a consistent duration. Select `method="silver-meal"`. Inputs and cost accounting are identical to Wagner–Whitin, enabling comparisons on the same problem.

## Mathematical definition

Starting at a positive net-demand period $t$, evaluate covering $n$ periods:

$$\overline C_t(n)=\frac{K+h\sum_{k=1}^{n-1}k d'_{t+k}}{n}.$$

Increase $n$ until average cost strictly rises, then use the preceding span. Equal average costs permit extension. If the horizon is reached, use the last available span.
Order the sum of net demands in that span, then repeat at the next uncovered period. Zero-demand starting periods are skipped; zeros inside a candidate span still count as elapsed holding periods.

## Worked example

For demand `[10, 20, 30]`, setup 100 and holding 1:

- One period: average cost `100/1 = 100`.
- Two periods: `(100 + 20)/2 = 60`.
- Three periods: `(100 + 20 + 2 × 30)/3 = 60`.

The average does not rise, so all 60 units are ordered in period 1. Total cost is 180.
This happens to match the optimum. For `[10, 20, 30, 40, 50, 60]` with the same costs, Silver–Meal costs 430 while Wagner–Whitin costs 420: see the [comparison examples](../../examples/README.md).

## Python usage

```python
from dynamic_models import DLSInput, DynamicLotSizing

model = DynamicLotSizing(
    DLSInput(demand=[10, 20, 30], ordering_cost=100, holding_cost=1)
)
result = model.solve(method="silver-meal")
print("Orders:", [round(q, 2) for q in result.order_quantities])
print("Periods:", result.order_periods)
print(f"Total cost: {result.total_cost:.2f}")
```

```text
Orders: [60.0, 0.0, 0.0]
Periods: [1]
Total cost: 180.00
```

## Verification

The [independent schedule tests](../../tests/test_independent_optimality.py)
enumerate feasible integer orders for 2,187 small scenarios per method and
reconstruct costs from stock balances. The [contract tests](../../tests/test_model_contracts.py)
cover initial inventory, fractional demand, and invalid inputs.

The heuristic must be feasible, its returned cost must equal the reconstructed cost, and it cannot cost less than the exhaustive optimum. Matching the optimum is not required.

## Limitations

There is no global optimality guarantee: a local stopping decision can miss a cheaper later grouping.
Current candidate holding-cost sums are recomputed, giving O(T²) worst-case work and O(T) plan storage. The comparison examples measure plan quality, not runtime speed. The same capacity and lead-time limitations as Wagner–Whitin apply.

## References

- [Method comparison guide](../../examples/README.md)
- [Shared dynamic mathematics](../DP-Math-docs.md)
- [Implementation](../../dynamic_models.py)
