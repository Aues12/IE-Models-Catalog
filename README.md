# IE Models Catalog

Python inventory models for industrial engineering: calculate order quantities,
plan orders across periods, and inspect inventory costs.

The catalog includes four EOQ-family models, two dynamic lot-sizing methods,
inventory plots, and mathematical walkthroughs. It is intended for learning and
analyzing deterministic inventory scenarios.

[Quick start](#quick-start) · [Models](#choose-a-model) · [API reference](docs/API_REFERENCE.md) · [Development](docs/DEVELOPMENT.md)

## Installation

Requires **Python 3.11 or later**. CI tests Python 3.11 and 3.12.

```bash
git clone https://github.com/Aues12/IE-Models-Catalog.git
cd IE-Models-Catalog
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
```

On Windows PowerShell, activate the environment with `.venv\Scripts\Activate.ps1`.
Installation includes NumPy, Matplotlib, and Plotly.

## Quick start

Suppose an item costs 50 per unit, annual demand is 1,200 units, and each order
costs 75 to place. Annual holding cost is 20% of the item's price.

```python
from inventory_models import BasicEOQ

model = BasicEOQ(
    price=50,
    demand_rate=1200,
    ordering_cost=75,
    holding_rate=0.20,
)
result = model.solve()

print(f"Order quantity: {result.order_quantity:.2f} units")
print(f"Ordering + holding cost: {result.costs.relevant_cost:.2f} per year")
print(f"Total cost including purchases: {result.total_cost:.2f} per year")
```

```text
Order quantity: 134.16 units
Ordering + holding cost: 1341.64 per year
Total cost including purchases: 61341.64 per year
```

Under the model's assumptions, ordering approximately 134.16 units per cycle
minimizes annual ordering and holding costs. The optimum is a continuous
quantity; the library does not enforce whole-unit or pack-size constraints.

## Choose a model

| Your situation | Model or method | What it accounts for |
| --- | --- | --- |
| Constant demand, replenishment arrives at once | `BasicEOQ` | Ordering and holding costs |
| Stock builds gradually during production | `EPQ` | Production rate greater than demand |
| Larger orders receive a lower unit price | `DiscountEOQ` | All-units quantity discounts |
| Planned shortages can be filled later | `BackorderEOQ` | Holding and backorder costs |
| Known demand varies by period; you need an optimal plan | Wagner–Whitin | Exact dynamic lot sizing |
| Known demand varies by period; you want a heuristic plan | Silver–Meal | Average cost per covered period; optimality is not guaranteed |

All four EOQ-family models provide `solve()`, `calculate_reorder_point()`,
`inventory_level()`, and `graph()`. See the [API reference](docs/API_REFERENCE.md)
for constructors and examples of each variant.

## Plan orders across periods

For demand of 10, 20, and 30 units over three periods:

```python
from dynamic_models import DLSInput, DynamicLotSizing

data = DLSInput(
    demand=[10, 20, 30],
    ordering_cost=100,
    holding_cost=1,  # Cost per unit held at each period end.
)
result = DynamicLotSizing(data).solve(method="wagner-whitin")

print(result.order_quantities)  # [60.0, 0, 0]
print(result.inventory_levels)  # [50.0, 30.0, 0.0]
print(result.total_cost)  # 180.0
```

The plan orders all 60 units in period 1. One order costs 100, and carrying 50
then 30 units costs another 80. To use Silver–Meal, set `method="silver-meal"`.
Both methods support starting stock through `DLSInput(initial_inventory=...)`
when supplied alongside demand and costs.

## Understand the results

Both model families expose `result.costs`, a breakdown of purchase, ordering,
holding, and shortage costs.

- **EOQ models:** `result.total_cost` includes purchases and covers one demand
  period. If demand is annual, costs are annual and `result.cycle_time` is in years.
- **Dynamic models:** `result.total_cost` covers ordering and holding over the
  entire supplied horizon. Holding costs include any initial stock remaining at
  each period end.
- **Time units:** demand and holding costs must use the same period. Reorder
  points and inventory profiles use operating days, with 365 days per period by
  default.

Align time horizons and included cost components before comparing totals.
Detailed fields, validation rules, and compatibility notes are in the
[API reference](docs/API_REFERENCE.md#common-results-and-costs).

To view a stock profile, call `model.graph()` on an EOQ-family model. Plotly is
the default; use `model.graph(renderer="matplotlib")` for Matplotlib.

## Explore comparisons and sensitivity

Run the examples from the repository root after installation:

```bash
python -m examples.compare_methods
python -m examples.eoq_sensitivity
```

The first compares Wagner–Whitin and Silver–Meal on three shared demand scenarios.
The second changes EOQ demand, ordering cost, and holding rate one at a time,
showing the new optimum and the extra cost of keeping the original order quantity.
Both save interactive HTML reports and numeric JSON results in `examples/output/`.
The reports open locally without an internet connection.

See the [examples guide](examples/README.md) for expected results and interpretation.

## Documentation

| Guide | Contents |
| --- | --- |
| [Model catalog](docs/models/README.md) | Assumptions, units, worked examples, and verification for each model |
| [API reference](docs/API_REFERENCE.md) | Model examples, parameters, results, units, and cost conventions |
| [EOQ model guide](docs/EOQ-Model-docs.md) | Background on the EOQ family |
| [EOQ mathematics](docs/EOQ-Math-docs.md) | Formulas and derivations |
| [Dynamic lot-sizing mathematics](docs/DP-Math-docs.md) | Dynamic programming foundations |
| [Wagner–Whitin walkthrough](docs/Wagner-Whitin_Algorithm.md) | Step-by-step algorithm explanation |
| [Wagner–Whitin Türkçe anlatım](docs/Wagner-Whitin_Algorithm_TR.md) | Turkish walkthrough |
| [Development guide](docs/DEVELOPMENT.md) | Environment setup, tests, Ruff, builds, and CI |

The [original proposal](PROPOSAL.md) explains the project's motivation.
Release history is recorded in the [changelog](CHANGELOG.md).

## Development and feedback

With the virtual environment active:

```bash
python -m pip install -e ".[dev]"
python -m pytest tests/ -v
ruff check .
ruff format --check .
```

Tests include regressions and independent optimality checks. See the
[development guide](docs/DEVELOPMENT.md) for the full workflow.

Bug reports and documentation feedback are welcome through
[GitHub Issues](https://github.com/Aues12/IE-Models-Catalog/issues).
External pull requests are currently not accepted; see the
[contribution policy](CONTRIBUTING.md).

## License

[MIT](LICENSE).
