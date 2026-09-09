# IE Models Catalog

A small Python catalog of inventory-management models for industrial engineering. It currently provides four EOQ-family models and two dynamic lot-sizing methods, together with mathematical notes and an automated test suite.

## Current status

The implemented, tested scope is:

| Area | Models and methods |
| --- | --- |
| Static inventory | `BasicEOQ`, `EPQ`, `DiscountEOQ`, `BackorderEOQ` |
| Reorder point | `calculate_reorder_point()` on every EOQ-family model |
| Inventory profiles | `inventory_level(t)` and `graph()` on every EOQ-family model |
| Dynamic lot sizing | Exact Wagner–Whitin and Silver–Meal heuristic |

The test suite includes regression checks, shared result-contract checks, and independent optimality checks against exhaustive small planning problems.

## Installation

The repository's development target is Python 3.12. Continuous integration tests Python 3.11 and 3.12. Install the package in a virtual environment:

```bash
git clone https://github.com/Aues12/IE-Models-Catalog.git
cd IE-Models-Catalog
python3 -m venv .venv
source .venv/bin/activate
pip install .
```

The package installs its runtime dependencies: `numpy`, `matplotlib`, and `plotly`. Existing imports remain unchanged:

```python
from dynamic_models import DynamicLotSizing
from inventory_models import BasicEOQ
```

For local development, including tests, builds, and Ruff, install the `dev` extra:

```bash
pip install -e ".[dev]"
```

Run the full test suite with:

```bash
.venv/bin/python -m pytest tests/ -v
```

## Code quality with Ruff

Ruff is the project's linter and formatter. It is installed through the `dev` extra.

Check for lint issues and formatting changes without modifying files:

```bash
ruff check .
ruff format --check .
```

Apply Ruff's safe automatic fixes and format the code:

```bash
ruff check . --fix
ruff format .
```

The configuration in [`pyproject.toml`](pyproject.toml) targets Python 3.11 syntax and checks import order plus core error and undefined-name rules. GitHub Actions runs the non-modifying commands on every relevant push and pull request.

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

`DiscountEOQ` evaluates all supplied quantity-discount tiers and returns the order quantity with the lowest annual purchase, ordering, and holding cost. Supply `discount_rates` as `{minimum_quantity: discount_rate}`; discount rates must be in the interval `[0, 1)` and must not decrease as quantity increases. Thresholds must be finite and non-negative. Quantities are continuous: tiers are `[minimum_quantity, next_minimum_quantity)`, and the selected all-units price applies to the entire order. Integer order quantities and increasing-price tiers are not supported.

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

* `order_quantities`: quantity ordered in each period
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

print(result.order_quantities)  # [60, 0, 0]
print(result.total_cost)  # 180
print(result.order_periods)  # [1]
```

Available methods are:

* `method="wagner-whitin"` — exact dynamic-programming solution.
* `method="silver-meal"` — feasible heuristic; it is not guaranteed to be optimal.

Demand must be a non-empty list or tuple of finite, non-negative real values. Ordering cost, holding cost, and initial inventory must also be finite and non-negative. Both methods consume `initial_inventory` before ordering for unmet demand, without modifying the input.

Holding cost is charged on actual inventory at every period end, including unused initial inventory and stock remaining at the horizon's end. Initial inventory has no acquisition cost in this model. For example, `DLSInput([10, 0], 100, 1, initial_inventory=15)` produces no orders, end inventories `[5, 5]`, and total holding cost `10`.

## Common results and costs

Every EOQ-family model now provides `solve() -> EOQResult` and `calculate_costs(quantity) -> CostBreakdown`. Existing `calculate_eoq()` calls still return a number.

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

## Inventory profiles and plots

EOQ-family models provide `inventory_level(t, days_of_operation=365)` where `t` is a scalar or array of non-negative elapsed operating days. Use the same `days_of_operation` in reorder-point and profile calculations. Profiles calculate the current optimum on each call, and `analysis_mode=True` prints explanations while still returning the same numeric result. The default `graph()` displays a 365-day profile.

`graph()` renders an inventory profile with Plotly by default, or Matplotlib when requested:

```python
model.graph(renderer="plotly")
model.graph(renderer="matplotlib")
```

## Documentation

Further explanations and derivations are available under [`docs/`](docs/):

* [EOQ model guide](docs/EOQ-Model-docs.md)
* [EOQ mathematics](docs/EOQ-Math-docs.md)
* [Dynamic lot sizing mathematics](docs/DP-Math-docs.md)
* [Wagner–Whitin walkthrough (English)](docs/Wagner-Whitin_Algorithm.md)
* [Wagner–Whitin walkthrough (Turkish)](docs/Wagner-Whitin_Algorithm_TR.md)

The original project rationale is retained in [PROPOSAL.md](PROPOSAL.md). Contribution policy is described in [CONTRIBUTING.md](CONTRIBUTING.md).
