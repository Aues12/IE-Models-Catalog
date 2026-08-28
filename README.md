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

The current test suite contains **58 tests** and was last verified with `pytest` successfully completing all of them.

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

All EOQ-family constructors use `price`, `demand_rate`, `ordering_cost`, and an optional `holding_rate` (default `0.25`). Holding cost is calculated as `price * holding_rate`. Core values must be positive.

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

`DiscountEOQ` evaluates all supplied quantity-discount tiers and returns the order quantity with the lowest annual purchase, ordering, and holding cost. Supply `discount_rates` as `{minimum_quantity: discount_rate}`; discount rates must be in the interval `[0, 1)`.

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

Demand must be a non-empty list of non-negative values. Ordering and holding costs must be non-negative. `DLSInput` also exposes `initial_inventory`, but the current solver does not yet use it; plans are therefore calculated without an initial-stock adjustment.

## Inventory profiles and plots

EOQ-family models provide `inventory_level(t)` where `t` is in days. Call `calculate_eoq()` first if you want to retain the calculated value explicitly; otherwise the profile method calculates it as needed.

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
