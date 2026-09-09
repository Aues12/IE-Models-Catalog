# All-units Discount EOQ

[Model catalog](README.md) · [Shared conventions](conventions.md) · [API reference](../API_REFERENCE.md)

## Purpose

Choose an order quantity when crossing a supplier threshold reduces the price of every unit in the order.

## Assumptions

- Constant, known demand for one item; replenishment arrives as a batch.
- All-units discounts, with nondecreasing discount rates as quantity increases.
- Holding cost is proportional to the applicable discounted unit price.
- No shortages; continuous quantities and no capacity constraints.

## Inputs and units

The formulas below describe the continuous case. Optional
[order constraints](order_constraints.md) add per-order bounds, integrality and pack multiples
through `solve(constraints=...)` and `inventory_level(..., constraints=...)`.

Use the [shared EOQ inputs and units](conventions.md#eoq-family). This example uses an annual demand period.

Additional input: `discount_rates`, a non-empty mapping `{minimum_quantity: discount_fraction}`.
Thresholds are finite, non-negative quantities. Rates are finite and in `[0, 1)`.
An undiscounted zero threshold is inserted when omitted; an explicitly supplied zero threshold takes precedence.
For example, `{25.5: 0.02, 50: 0.10}` means a 2% discount from 25.5 units and 10% from 50 units.

## Mathematical definition

For tier $j$, unit price is $c_j=c(1-r_j)$ and $h_j=c_j i$.

$$TC_j(Q)=Dc_j+\frac{DK}{Q}+\frac{h_jQ}{2}.$$

Compute $q_j=\sqrt{2DK/h_j}$, then the candidate $Q_j=\max(q_j,b_j)$ for minimum threshold $b_j$.
Keep the candidate only if $Q_j<b_{j+1}$; tiers are $[b_j,b_{j+1})$ and the last tier has no upper bound.
Compare total costs of the retained candidates. With nondecreasing discounts, a candidate beyond a tier is dominated by an option in a later tier.
Purchase cost varies by tier and must participate in the comparison.

## Worked example

Use price 10, annual demand 100, ordering cost 5, holding rate 20%, and thresholds `{25.5: 0.02, 50: 0.10}`.

| Tier minimum | Unit price | Feasible candidate | Total annual cost |
| --- | ---: | ---: | ---: |
| 0 | 10.00 | 22.36068 | 1044.72 |
| 25.5 | 9.80 | 25.50000 | 1024.60 |
| 50 | 9.00 | 50.00000 | 955.00 |

At 50 units, purchases cost 900, ordering costs 10, and holding costs 45.
The selected quantity is 50, although ordering plus holding alone is lower in the base tier.

## Python usage

```python
from inventory_models import DiscountEOQ

model = DiscountEOQ(
    price=10,
    demand_rate=100,
    ordering_cost=5,
    holding_rate=0.20,
    discount_rates={25.5: 0.02, 50: 0.10},
)
result = model.solve()
print(f"Quantity: {result.order_quantity:.2f}")
print(f"Relevant cost: {result.costs.relevant_cost:.2f}")
print(f"Total cost: {result.total_cost:.2f}")
```

```text
Quantity: 50.00
Relevant cost: 55.00
Total cost: 955.00
```

## Verification

The [independent cost-surface tests](../../tests/test_independent_optimality.py)
evaluate costs from inventory geometry over a grid of candidate quantities.
The [contract tests](../../tests/test_model_contracts.py) check cost breakdowns,
legacy API agreement, validation, and time units. The grids are bounded numerical
checks, not proofs for all possible inputs.

The contract suite also checks fractional thresholds, exact threshold prices, and the regression where a one-unit threshold previously allowed a zero order.

## Limitations

Use [IncrementalDiscountEOQ](incremental_discount_eoq.md) when discounts apply only to units in each band. Optional [order constraints](order_constraints.md) enforce bounds, integers and pack multiples. Increasing-price tiers are rejected. Use `calculate_costs(quantity)` for automatic tier selection; legacy `calculate_total_cost(quantity, price)` uses the price supplied by the caller.

## References

- [Formula background](../EOQ-Math-docs.md)
- [Implementation](../../inventory_models.py)
- [API compatibility details](../API_REFERENCE.md#common-results-and-costs)
