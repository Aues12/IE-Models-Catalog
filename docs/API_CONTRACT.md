# Public API contract and compatibility

[API reference](API_REFERENCE.md) · [Version policy](RELEASING.md)

## Imports and ownership

Prefer `from ie_models_catalog import BasicEOQ, OrderConstraints`. The package
exports all five EOQ models, EOQResult, DLSInput, DLSResult, DynamicLotSizing,
CostBreakdown, OrderConstraints and InfeasiblePlanError. These are the identical
classes exported by the historical modules; no formulas or wrapper classes are
copied. `inventory_models`, `dynamic_models` and `model_common` imports remain
supported. The JSON adapter remains separately accessible through `ie_models_agent`.

## Common calculations

Every EOQ variant supports `solve(constraints=None)`,
`calculate_costs(quantity)` and `calculate_total_cost(quantity)`.
The last two evaluate a proposed quantity and do not enforce order constraints.
All totals include purchases; `result.costs.relevant_cost` excludes purchases.
Dynamic totals cover ordering and actual end-stock holding; purchases are outside
that model. Do not compare totals across different horizons or cost components.

Native `result.cost_basis` returns fresh metadata with `horizon`, `periods`,
`quantity_unit="item"`, and `currency="caller_defined"`.
EOQ uses one `demand_period`; dynamic uses the complete `planning_horizon` and its
number of periods. This does not assert a calendar unit or perform conversions.
EOQ `cycle_time` is in demand periods; profile input is elapsed operating days,
converted using `days_of_operation=365` by default. Dynamic indices are one-based
in period lists and zero-based in arrays; orders are releases, receipts deliveries.
The agent contract separately fixes EOQ costs/demand to annual units.

## Saved policies

An EOQResult is a frozen snapshot containing its quantity, cost breakdown,
cycle time, stock/backlog maxima and optional EPQ production rate.
`result.inventory_level(t, days_of_operation=365)` and
`result.graph(renderer="plotly", days_of_operation=365)` use only that snapshot.
They never re-optimize, need no repeated constraints, and remain valid if the
original model changes. Profile values are net inventory; backorders are negative.
EPQ starts at zero stock, instantaneous replenishment starts at maximum stock.

```python
from ie_models_catalog import BasicEOQ, OrderConstraints

model = BasicEOQ(price=10, demand_rate=1000, ordering_cost=50, holding_rate=0.2)
result = model.solve(
    OrderConstraints(min_quantity=250, max_quantity=400, order_multiple=48)
)
print(result.order_quantity)  # 288.0
print(result.inventory_level(0))  # 288.0
print(result.cost_basis["horizon"])  # demand_period
# result.graph(days_of_operation=250)
```

Model-level `inventory_level` and `graph` still solve the current model on each
call. Prefer result-level methods when inspecting or presenting a saved plan.
The legacy dynamic result remains mutable for compatibility; no immutability or
new profile API is promised for DLSResult.

## Validation and errors

Numeric inputs must be finite real numbers. Booleans and numeric strings are not
numbers. Quantities/costs follow the positive/non-negative domains in each guide.
Profiles accept non-empty scalar/array inputs and preserve array shape, but reject
negative values, strings, booleans and non-finite entries before coercion.
Integer-valued real inputs such as `12.0` are accepted for pack multiples and
`1.0` for dynamic lead time, matching JSON Schema integer semantics. Fractions
and booleans are rejected. Pack multiples normalize to int; dynamic lead time is
normalized internally without mutating DLSInput.

Invalid inputs raise ValueError; valid constraints with no solution raise
InfeasiblePlanError (a ValueError subclass). The agent translates these into
INVALID_REQUEST and INFEASIBLE_PLAN envelopes. JSON schemas impose additional
transport limits and array shapes; Python array support is broader by design.
Numerical overflow is not a feasible-plan certificate; the agent reports
NUMERICAL_ERROR for non-finite or invalid numerical results.

## Side effects and migration

For compatibility, model solve/calculate_eoq calls update `eoq_value`, and
calculate_reorder_point stores the supplied `lead_time`. These fields are not
reused as a cached solution. Prefer a new model for changed inputs; direct mutation
of model fields is not a validated configuration API. Saved-result calculations
have no model side effects. Graph calls open the selected renderer; analysis mode
prints a human explanation, whose exact wording is not a stable API.

Legacy BackorderEOQ.calculate_cycle_metrics()["TotalCost"] continues to exclude
purchases. Prefer `solve().costs.relevant_cost` for the same value or
`solve().total_cost` for the complete cost. Discount calculate_total_cost(quantity,
price) retains its explicit flat-price interpretation; omit price for tier billing.
No existing valid call is removed or deprecated here. Tightened profile validation
intentionally rejects previously coerced strings/booleans and empty arrays.
These changes belong in the next minor release; v0.5.0 remains unchanged.

[Public API tests](../tests/test_public_api.py) exercise saved-policy isolation,
independent EPQ profile values, cross-model validation, import identity and agent
serialization compatibility. Existing independent optimization tests remain the
numerical reference for solver correctness.
