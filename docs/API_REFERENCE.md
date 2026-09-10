# API reference

[Back to the README](../README.md) · [Model guides](models/README.md)

The [public API contract](API_CONTRACT.md) defines imports, units, validation,
saved-policy behavior and compatibility.

This reference covers model parameters, return values, validation rules, time
units, and cost conventions. Start with the [quick start](../README.md#quick-start)
for a first calculation. Use `solve()` for structured results and
`calculate_eoq()` when you only need an order quantity.

- [Static inventory models](#static-inventory-models)
- [Dynamic lot sizing](#dynamic-lot-sizing)
- [Common results and costs](#common-results-and-costs)
- [Inventory profiles and plots](#inventory-profiles-and-plots)

## Static inventory models

All EOQ-family constructors use `price`, `demand_rate`, `ordering_cost`, and an optional `holding_rate` (default `0.25`). Holding cost is calculated as `price * holding_rate`. Core values must be finite, positive real numbers. Non-finite values and booleans are rejected. Demand and holding costs must refer to the same time period.

### Basic EOQ

`BasicEOQ` implements the classic economic order quantity model.

```python
from inventory_models import BasicEOQ

model = BasicEOQ(
    price=50.0,
    demand_rate=1200,
    ordering_cost=75,
    holding_rate=0.20,
)

quantity = model.calculate_eoq()
reorder_point = model.calculate_reorder_point(
    lead_time=10,
    safety_stock=20,
)

print(quantity)
print(reorder_point)
```

`calculate_reorder_point()` uses:

```text
reorder point = (demand_rate / days_of_operation) * lead_time + safety_stock
```

`lead_time` and `safety_stock` cannot be negative; `days_of_operation` defaults to `365` and must be positive.

### EPQ

`EPQ` models gradual replenishment during production. It adds `production_rate`, which must be greater than `demand_rate`.

```python
from inventory_models import EPQ

model = EPQ(
    price=50.0,
    demand_rate=1000,
    ordering_cost=75,
    production_rate=1200,
    holding_rate=0.20,
)

print(model.calculate_eoq())
```

### Discount EOQ

`DiscountEOQ` evaluates all supplied quantity-discount tiers and returns the order quantity with the lowest annual purchase, ordering, and holding cost. Supply `discount_rates` as `{minimum_quantity: discount_rate}`; discount rates must be in the interval `[0, 1)` and must not decrease as quantity increases. Thresholds must be finite and non-negative. Quantities are continuous: tiers are `[minimum_quantity, next_minimum_quantity)`, and the selected all-units price applies to the entire order. Optional `solve(constraints=...)` supports integer quantities and pack multiples; increasing-price tiers are not supported.

```python
from inventory_models import DiscountEOQ

model = DiscountEOQ(
    price=100,
    demand_rate=1000,
    ordering_cost=50,
    holding_rate=0.20,
    discount_rates={0: 0.0, 100: 0.05, 200: 0.10},
)

print(model.calculate_eoq())
```

### Incremental discounts and operational constraints

`IncrementalDiscountEOQ` uses the same constructor and tier mapping as
`DiscountEOQ`, but only units within each band receive its price. Holding uses
the average acquisition price of the lot; `result.unit_price` reports that average.
See the [worked model guide](models/incremental_discount_eoq.md).

All five variants accept `solve(constraints=OrderConstraints(...))`; import
`OrderConstraints` from `model_common`. Defaults preserve continuous quantities.
Inclusive `min_quantity=0`, `max_quantity=None`, `integer=False` and
`order_multiple=None` define the optional bounds and grid. An empty feasible set
raises `InfeasiblePlanError`, a `ValueError` subclass. See [constraints](models/order_constraints.md).

### EOQ with planned backorders

`BackorderEOQ` permits planned shortages. It adds a positive `shortage_cost` parameter. `calculate_cycle_metrics()` returns a dictionary containing `Q_opt`, `S_max`, `B_max`, and `TotalCost`.

```python
from inventory_models import BackorderEOQ

model = BackorderEOQ(
    price=100,
    demand_rate=500,
    ordering_cost=200,
    shortage_cost=50,
    holding_rate=0.2,
)

print(model.calculate_eoq())
print(model.calculate_cycle_metrics())
```

## Dynamic lot sizing

`DynamicLotSizing` turns a time-phased demand vector into an order plan. `solve()` returns a `DLSResult` with:

* `order_quantities`: quantity released in each period
* `receipt_quantities`, `receipt_periods`: delivery quantities and one-based delivery periods
* `total_cost`: ordering plus holding cost
* `order_periods`: one-based periods in which orders are placed
* `inventory_levels`: inventory remaining at the end of each period
* `costs`: shared `CostBreakdown` with ordering and holding components

```python
from dynamic_models import DLSInput, DynamicLotSizing

data = DLSInput(
    demand=[10, 20, 30],
    ordering_cost=100,
    holding_cost=1,
)

result = DynamicLotSizing(data).solve(method="wagner-whitin")

print(result.order_quantities)  # [60.0, 0.0, 0.0]
print(result.total_cost)  # 180
print(result.order_periods)  # [1]
```

`ordering_cost` and `holding_cost` may be scalars or lists/tuples with exactly
one finite non-negative entry per demand period. Setup cost is charged in the
release period; holding uses the actual end stock and that period's rate.
`lead_time=0` is the default; a non-negative integer shifts receipts after releases.
No pre-horizon releases or pipeline orders are modeled. Insufficient initial
stock before the first possible receipt raises `InfeasiblePlanError`.

Available methods are:

* `method="wagner-whitin"` — exact dynamic-programming solution.
* `method="silver-meal"` — feasible heuristic; it is not guaranteed to be optimal.

Demand must be a non-empty list or tuple of finite, non-negative real values. Ordering cost, holding cost, and initial inventory must also be finite and non-negative. Both methods consume `initial_inventory` before ordering for unmet demand, without modifying the input.

Holding cost is charged on actual inventory at every period end, including unused initial inventory and stock remaining at the horizon's end. Initial inventory has no acquisition cost in this model. For example, `DLSInput([10, 0], 100, 1, initial_inventory=15)` produces no orders, end inventories `[5, 5]`, and total holding cost `10`.

## Common results and costs

Every EOQ-family model provides `solve() -> EOQResult` and `calculate_costs(quantity) -> CostBreakdown`. Existing `calculate_eoq()` calls still return a number.

```python
from inventory_models import BasicEOQ

model = BasicEOQ(price=50, demand_rate=1200, ordering_cost=75, holding_rate=0.20)
result = model.solve()
print(result.order_quantity)
print(result.cycle_time)  # Fraction of one demand period; years for annual demand.
print(result.max_inventory, result.max_backorder)
print(result.unit_price)
print(result.costs.ordering, result.costs.holding)
print(result.costs.relevant_cost)  # Ordering + holding + shortage.
print(result.total_cost)  # Purchase + ordering + holding + shortage.
```

`CostBreakdown` (importable from `model_common`) is shared by EOQ and dynamic results. It contains `purchase`, `ordering`, `holding`, and `shortage`, plus computed `relevant_cost` and `total_cost` properties. EOQ costs cover one demand period; dynamic costs cover the entire supplied horizon. These totals are comparable only after aligning horizons and included cost components.

EOQ `total_cost` includes purchase cost for every variant. For backward compatibility, `BackorderEOQ.calculate_cycle_metrics()["TotalCost"]` continues to exclude purchase cost and equals `solve().costs.relevant_cost`. Dynamic purchase and shortage components are zero because those costs are not modeled. The legacy `DiscountEOQ.calculate_total_cost(quantity, price)` accepts an explicit price; use `calculate_costs(quantity)` to select the applicable tier automatically.

`holding_cost` is derived from `price * holding_rate`; configure those inputs rather than assigning a separate holding cost. For a new scenario, constructing a new model is recommended.

## Compatibility and preferred entrypoints

All five EOQ variants provide `calculate_total_cost(quantity)` as shorthand for
`calculate_costs(quantity).total_cost`, including acquisition costs. Both discount
variants also retain `calculate_total_cost(quantity, price)` for legacy callers;
that explicit-price overload deliberately bypasses automatic tier billing.
Prefer the one-argument call, especially for incremental discounts.

`BackorderEOQ.calculate_cycle_metrics(constraints=None)` delegates to `solve()`
and accepts the same per-call constraints. Its historical dictionary keys remain
unchanged, including `TotalCost` meaning ordering + holding + shortage only.
Use `solve().total_cost` for the complete cost including purchases.

Defaults and old positional calls remain supported. No legacy method is removed
or deprecated in 0.5.0. Version and migration policy: [releasing](RELEASING.md).

## Inventory profiles and plots

EOQ-family models provide `inventory_level(t, days_of_operation=365)` where `t` is a scalar or array of non-negative elapsed operating days. Use the same `days_of_operation` in reorder-point and profile calculations. Profiles accept the same optional `constraints` as `solve()` and calculate the selected optimum on each call, and `analysis_mode=True` prints explanations while still returning the same numeric result. The default `graph()` displays a 365-day profile. Pass `days_of_operation` and
`constraints` to plot the same policy and time convention as `inventory_level()`.
An unsupported renderer raises `ValueError`.

`graph()` renders an inventory profile with Plotly by default, or Matplotlib when requested:

```python
model.graph(renderer="plotly")
model.graph(renderer="matplotlib")
```
