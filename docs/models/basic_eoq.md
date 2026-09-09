# Basic EOQ

[Model catalog](README.md) · [Shared conventions](conventions.md) · [API reference](../API_REFERENCE.md)

## Purpose

Choose a repeating order quantity that balances the cost of ordering frequently against the cost of holding larger stocks.

## Assumptions

- One item, with constant, known demand.
- Each replenishment arrives as a complete batch; shortages are not allowed.
- Unit price and cost rates are constant; quantities are continuous.
- No shared capacity, minimum order, or pack-size constraint.

## Inputs and units

The formulas below describe the continuous case. Optional
[order constraints](order_constraints.md) add per-order bounds, integrality and pack multiples
through `solve(constraints=...)` and `inventory_level(..., constraints=...)`.

Use the [shared EOQ inputs and units](conventions.md#eoq-family). This example uses an annual demand period. No additional constructor parameters are required.

## Mathematical definition

Let $D$ be demand, $K$ ordering cost, $c$ unit price, and $h=ci$ holding cost per unit per demand period. For quantity $Q>0$:

$$C_{rel}(Q)=\frac{DK}{Q}+\frac{hQ}{2},\qquad Q^*=\sqrt{\frac{2DK}{h}}.$$

Total cost is $Dc+C_{rel}(Q)$. Since purchase cost is constant in $Q$, it does not change the optimum. The cycle length is $Q/D$ demand periods and maximum inventory is $Q$.

## Worked example

An item costs 10, annual demand is 100, each order costs 5, and the annual holding rate is 20%.
Holding cost per unit is therefore 2. The optimum is `sqrt(2 × 100 × 5 / 2) = 22.36068` units.
Annual ordering and holding costs are each about 22.36: relevant cost is 44.72 and total cost including 1,000 of purchases is 1,044.72.

The cycle is about 0.22361 years. This is a continuous optimum; it is not a recommendation to round without comparing feasible alternatives.

## Python usage

```python
from inventory_models import BasicEOQ

model = BasicEOQ(
    price=10,
    demand_rate=100,
    ordering_cost=5,
    holding_rate=0.20,
)
result = model.solve()
print(f"Quantity: {result.order_quantity:.2f}")
print(f"Relevant cost: {result.costs.relevant_cost:.2f}")
print(f"Total cost: {result.total_cost:.2f}")
```

```text
Quantity: 22.36
Relevant cost: 44.72
Total cost: 1044.72
```

## Verification

The [independent cost-surface tests](../../tests/test_independent_optimality.py)
evaluate costs from inventory geometry over a grid of candidate quantities.
The [contract tests](../../tests/test_model_contracts.py) check cost breakdowns,
legacy API agreement, validation, and time units. The grids are bounded numerical
checks, not proofs for all possible inputs.

The equal ordering/holding components in the worked example provide an additional hand check at the unconstrained optimum.

## Limitations

The model does not forecast demand or calculate safety stock. The inherited reorder-point method accepts supplied lead time and safety stock; it does not simulate deliveries. See [time conventions](conventions.md#time-and-cost-comparisons).

## References

- [Formula derivations](../EOQ-Math-docs.md)
- [Implementation](../../inventory_models.py)
- [Sensitivity examples](../../examples/README.md)
