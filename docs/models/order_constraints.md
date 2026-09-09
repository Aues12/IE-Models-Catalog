# Operational order constraints

[Model catalog](README.md) · [API reference](../API_REFERENCE.md)

## Purpose

Turn a continuous EOQ recommendation into a quantity that meets a supplier's
minimum order, maximum order, or whole-item pack requirement.

## Assumptions

All five EOQ variants accept the same constraints. Their original demand,
replenishment and cost assumptions still apply. Bounds limit each order quantity;
they do not represent storage capacity or capacity shared by products.

## Inputs and units

`OrderConstraints` is imported from `model_common`:

| Field | Default | Meaning |
| --- | --- | --- |
| `min_quantity` | `0` | Inclusive lower bound, finite and non-negative |
| `max_quantity` | `None` | Inclusive positive upper bound, or no upper bound |
| `integer` | `False` | Require whole-item quantities |
| `order_multiple` | `None` | Positive integer pack size; also implies integrality |

Order quantities remain strictly positive. A pack size of 12 means 12, 24, 36, …;
a minimum of 25 does not shift this grid to 25, 37, 49, ….

## Mathematical definition

Minimize the model's complete cost over the intersection of the quantity bounds
and optional discrete grid. Within each convex price region, evaluate feasible
neighbors of the continuous optimum and necessary boundaries. Compare all price
regions. This avoids rounding an optimum across a discount threshold without
checking the resulting cost. An empty feasible set raises `InfeasiblePlanError`.

## Worked example

For `D=1000`, `K=50`, `c=10`, `i=0.2`, continuous EOQ is 223.6068.
With minimum 250, maximum 400 and packs of 48, candidates are 288, 336 and 384.
The optimum is 288, with total cost `10000+50000/288+288=10461.6111`.
Minimum 25, maximum 30 and packs of 12 admit no feasible quantity.

## Python usage

```python
from inventory_models import BasicEOQ
from model_common import OrderConstraints

model = BasicEOQ(price=10, demand_rate=1000, ordering_cost=50, holding_rate=0.2)
constraints = OrderConstraints(min_quantity=250, max_quantity=400, order_multiple=48)
result = model.solve(constraints=constraints)
print(result.order_quantity)  # 288.0
print(model.inventory_level(0, constraints=constraints))  # 288.0
```

## Verification

[Operational tests](../../tests/test_practical_models.py) enumerate every feasible
lot in bounded examples across all five variants. Their independently reconstructed
purchase, holding, ordering and shortage costs determine the comparison optimum.
Tests also cover exact bounds, fractional thresholds, invalid and infeasible inputs.

## Limitations

Constraints are passed per call; `calculate_eoq()` and calls without constraints
retain the continuous behavior. `graph(constraints=..., days_of_operation=...)`
and backorder `calculate_cycle_metrics(constraints=...)` use the same constrained policy. Pass the same constraints to
`inventory_level()` to inspect the constrained policy. `calculate_costs(quantity)`
and the agent's `evaluate_eoq` evaluate a supplied lot without enforcing constraints.
Backorder stock/backlog splits remain continuous even for whole-item order quantities.
Dynamic minimum lots and pack constraints are not supported.

## References

- [Shared implementation](../../model_common.py)
- [EOQ implementations](../../inventory_models.py)
