# EOQ with Planned Backorders

[Model catalog](README.md) · [Shared conventions](conventions.md) · [API reference](../API_REFERENCE.md)

## Purpose

Choose a repeating order quantity and planned backlog when customers can wait for a later replenishment.

## Assumptions

- Constant, known demand for one item with complete batch replenishment.
- Unmet demand is backlogged and eventually fulfilled; it is not lost sales.
- Backlog incurs a cost proportional to quantity and waiting duration.
- No backlog cap, service-level requirement, or capacity constraint.

## Inputs and units

Use the [shared EOQ inputs and units](conventions.md#eoq-family). This example uses an annual demand period.

Additional input: `shortage_cost` ($p$), a finite, positive cost per backlogged unit per demand period. It is not a one-time charge per missed sale.
Here $p$ denotes backlog cost; production rate $P$ belongs to the EPQ guide.

## Mathematical definition

For order quantity $Q$, let $I_{max}$ be maximum on-hand stock and $B_{max}$ maximum backlog:

$$I_{max}=\frac{pQ}{h+p},\qquad B_{max}=\frac{hQ}{h+p},\qquad I_{max}+B_{max}=Q.$$

$$C_{rel}(Q)=\frac{DK}{Q}+\frac{hI_{max}^2}{2Q}+\frac{pB_{max}^2}{2Q}.$$

$$Q^*=\sqrt{\frac{2DK(h+p)}{hp}}.$$

Total cost adds $Dc$. The average positive stock is $I_{max}^2/(2Q)$, not $I_{max}/2$, because part of the cycle is spent in backlog.

## Worked example

Use price 10, annual demand 100, ordering cost 5, holding rate 20%, and backlog cost 3 per unit-year.
Then `h = 2` and `Q = sqrt(1000 × 5 / 6) = 28.86751`.
Maximum stock is `3/5 × Q = 17.32051`; maximum backlog is `2/5 × Q = 11.54701`.
Ordering, holding, and shortage costs are approximately 17.32051, 10.39230, and 6.92820.
Relevant cost is 34.64 and total cost is 1,034.64. Calculations use unrounded values.

## Python usage

```python
from inventory_models import BackorderEOQ

model = BackorderEOQ(
    price=10,
    demand_rate=100,
    ordering_cost=5,
    holding_rate=0.20,
    shortage_cost=3,
)
result = model.solve()
print(f"Quantity: {result.order_quantity:.2f}")
print(f"Relevant cost: {result.costs.relevant_cost:.2f}")
print(f"Total cost: {result.total_cost:.2f}")
print(f"Maximum stock: {result.max_inventory:.2f}")
print(f"Maximum backlog: {result.max_backorder:.2f}")
```

```text
Quantity: 28.87
Relevant cost: 34.64
Total cost: 1034.64
Maximum stock: 17.32
Maximum backlog: 11.55
```

## Verification

The [independent cost-surface tests](../../tests/test_independent_optimality.py)
evaluate costs from inventory geometry over a grid of candidate quantities.
The [contract tests](../../tests/test_model_contracts.py) check cost breakdowns,
legacy API agreement, validation, and time units. The grids are bounded numerical
checks, not proofs for all possible inputs.

The independent oracle varies both quantity and backlog fraction. The contract suite checks legacy cycle metrics against the structured result.

## Limitations

This model represents planned waiting, not random stockouts or lost customers. `inventory_level()` returns net inventory and can be negative.
For compatibility, `calculate_cycle_metrics()["TotalCost"]` excludes purchases; `solve().total_cost` includes them. See [cost conventions](conventions.md#time-and-cost-comparisons).

## References

- [Formula derivations](../EOQ-Math-docs.md)
- [Implementation](../../inventory_models.py)
