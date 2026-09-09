# Wagner–Whitin Dynamic Lot Sizing

[Model catalog](README.md) · [Shared conventions](conventions.md) · [API reference](../API_REFERENCE.md)

## Purpose

Find a minimum-cost ordering plan when demand is known but varies from period to period.

## Assumptions

- Known demand over a finite horizon; one item and equal-duration periods.
- Fixed integer lead time; orders arrive before demand in their receipt period.
- Non-negative setup and holding costs, constant or specified per period; unlimited ordering and storage capacity.
- All demand must be met; initial inventory must cover demand before the first possible receipt. No pre-horizon releases or pipeline orders.

## Inputs and units

Use the [shared dynamic inputs and units](conventions.md#dynamic-lot-sizing). Periods must have a consistent duration. Select `method="wagner-whitin"`. Results use one-based order periods.

## Mathematical definition

First consume initial stock against successive demands to obtain net demands $d'_t$; see [initial-stock accounting](conventions.md#dynamic-lot-sizing).
For a receipt at $j$ (released at $j-L$) covering through $t$, define:

$$A(j,t)=K_{j-L}+\sum_{k=j}^{t}d'_k\sum_{u=j}^{k-1}h_u.$$

With $F(0)=0$, for a positive net-demand period:

$$F(t)=\min_{L+1\le j\le t}\{F(j-1)+A(j,t)\}.$$

When $d'_t=0$, the implementation uses $F(t)=F(t-1)$ and a no-order backtracking transition.
Backtracking recovers order starts; each order covers net demand until the next start.
Initial-stock holding cost does not change the choice of net-demand plan; the public result recomputes costs from actual inventory.

## Worked example

Demand is `[10, 20, 30]`, setup cost is 100, holding cost is 1, and starting stock is zero.
The four ways to partition these positive demands into replenishment cycles have costs:

| Orders by period | Setup | Holding | Total |
| --- | ---: | ---: | ---: |
| `[60, 0, 0]` | 100 | 50 + 30 = 80 | 180 |
| `[10, 50, 0]` | 200 | 30 | 230 |
| `[30, 0, 30]` | 200 | 20 | 220 |
| `[10, 20, 30]` | 300 | 0 | 300 |

Ordering 60 in period 1 is optimal. The DP costs are `F(1)=100`, `F(2)=120`, and `F(3)=180`.

## Python usage

```python
from dynamic_models import DLSInput, DynamicLotSizing

model = DynamicLotSizing(
    DLSInput(demand=[10, 20, 30], ordering_cost=100, holding_cost=1)
)
result = model.solve(method="wagner-whitin")
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

[Operational tests](../../tests/test_practical_models.py) independently enumerate
release schedules with varying costs, lead times and initial stock, then reconstruct
receipt timing, stock balances and cost.

The [independent schedule tests](../../tests/test_independent_optimality.py)
enumerate feasible integer orders for 2,187 small scenarios per method and
reconstruct costs from stock balances. The [contract tests](../../tests/test_model_contracts.py)
cover initial inventory, fractional demand, and invalid inputs.

Wagner–Whitin must match the enumerated minimum cost. Tests separately check non-negative balances, order totals, period indices, and agreement between returned costs and the plan.

## Limitations

Optimality applies to the stated uncapacitated deterministic problem. Capacity, minimum lots, pack multiples, variable lead times and pipeline orders are not supported.
Cost-matrix preparation and the recurrence each take O(T²) time, with O(T²) storage. Equal-cost plans may have different order periods. Receipt starts may fall in zero-net-demand periods when an earlier setup is cheaper.

## References

- [DP mathematics](../DP-Math-docs.md)
- [English walkthrough](../Wagner-Whitin_Algorithm.md)
- [Turkish walkthrough](../Wagner-Whitin_Algorithm_TR.md)
- [Implementation](../../dynamic_models.py)
