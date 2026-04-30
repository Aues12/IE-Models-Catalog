# IE Models Catalog

Python library for industrial engineering inventory models. The repository currently includes classical EOQ-based models and dynamic lot sizing algorithms, with usage examples, mathematical notes, and tests.

The original project proposal text is preserved in [PROPOSAL.md](PROPOSAL.md).

## Project Scope

The catalog currently covers two model groups:

1. Static inventory models in [inventory_models.py](inventory_models.py)
2. Dynamic lot sizing models in [dynamic_models.py](dynamic_models.py)

### Static inventory models

* `BasicEOQ`
* `EPQ`
* `BackorderEOQ`
* `DiscountEOQ`

### Dynamic lot sizing models

* `DynamicLotSizing.solve(method="wagner-whitin")`
* `DynamicLotSizing.solve(method="silver-meal")`

## Documentation

Repository documentation is kept in Markdown under [`docs/`](docs/):

* [EOQ model guide](docs/EOQ-Model-docs.md)
* [EOQ mathematics](docs/EOQ-Math-docs.md)
* [Dynamic lot sizing mathematics](docs/DP-Math-docs.md)
* [Wagner-Whitin walkthrough](docs/Wagner-Whitin_Algorithm.md)

## Quick Start

### Requirements

* Python `3.12` is the expected development version in this repository.
* `numpy` is required for the model implementations.
* `matplotlib` and `plotly` are used by graphing methods.
* `pytest` is used for the test suite.

### Installation

Clone the repository:

```bash
git clone https://github.com/Aues12/IE-Models-Catalog.git
cd IE-Models-Catalog
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the tests:

```bash
python -m pytest -q
```

## Usage

### BasicEOQ

The `BasicEOQ` class implements the classic **Economic Order Quantity** model. Instantiate it with demand, price, ordering cost, and holding rate, then use helper methods to compute the optimal order quantity and reorder point.

```python
from inventory_models import BasicEOQ

eoq_model = BasicEOQ(
    price=50.0,
    demand_rate=1200,
    ordering_cost=75,
    holding_rate=0.20,
)

eoq = eoq_model.calculate_eoq()
reorder_point = eoq_model.calculate_reorder_point(lead_time=10, safety_stock=20)

print(f"Economic Order Quantity (Q*): {eoq} units")
print(f"Reorder Point: {reorder_point} units")
```

### EPQ

`EPQ` is an extension of `BasicEOQ` for cases where items are produced gradually instead of arriving all at once. The additional required parameter is `production_rate`, and it must be greater than `demand_rate`.

```python
from inventory_models import EPQ

epq_model = EPQ(
    price=50.0,
    demand_rate=1000,
    ordering_cost=75,
    production_rate=1200,
    holding_rate=0.20,
)

epq = epq_model.calculate_eoq()
reorder_point = epq_model.calculate_reorder_point(lead_time=10, safety_stock=20)

print(f"Economic Production Quantity (Q*): {epq} units")
print(f"Reorder Point: {reorder_point} units")
```

### BackorderEOQ

The `BackorderEOQ` class extends EOQ by allowing **shortages (backorders)** and adds the required `shortage_cost` parameter.

```python
from inventory_models import BackorderEOQ

backorder_model = BackorderEOQ(
    price=100,
    demand_rate=500,
    ordering_cost=200,
    shortage_cost=50,
    holding_rate=0.2,
)

eoq = backorder_model.calculate_eoq()
cycle_metrics = backorder_model.calculate_cycle_metrics()

print(f"Economic Order Quantity (Q*): {eoq}")
print("Cycle Metrics:", cycle_metrics)
```

### DiscountEOQ

The `DiscountEOQ` class refers to a scenario where the supplier offers discounts at certain quantity levels.

 `DiscountEOQ` evaluates quantity discount tiers and selects the order quantity with the lowest total annual cost. 

```python
from inventory_models import DiscountEOQ

discount_model = DiscountEOQ(
    price=100,
    demand_rate=1000,
    ordering_cost=50,
    holding_rate=0.2,
    discount_rates={
        0: 0.0,
        100: 0.05,
        200: 0.10,
    },
)

best_quantity = discount_model.calculate_eoq(analysis_mode=True)
print("Best Order Quantity:", best_quantity)
```

### DynamicLotSizing

`DynamicLotSizing` handles time-phased demand. It currently supports the exact `wagner-whitin` method and the `silver-meal` heuristic.

```python
from dynamic_models import DLSInput, DynamicLotSizing

data = DLSInput(
    demand=[10, 20, 30],
    ordering_cost=100,
    holding_cost=1,
)

result = DynamicLotSizing(data).solve(method="wagner-whitin")

print("Order quantities:", result.order_quantities)
print("Total cost:", result.total_cost)
print("Order periods:", result.order_periods)
```

## Inventory Level and Graphing

All EOQ-family classes has `.inventory_level(t)` and `.graph()` methods.

You can plot the EOQ function using `.graph()` method. This method is available for all EOQ-family classes. Method uses `plotly` as the default renderer but you can optionally choose `matplotlib` as well.

* `inventory_level(t)` expects `t` in days.
* `.graph()` uses `plotly` by default.
* You can also set `renderer="matplotlib"`.

```python
eoq_model.graph(renderer="plotly")
```
<img width="1063" height="450" alt="image" src="https://github.com/user-attachments/assets/b656ec01-fe5a-4931-ac3e-2c87cb504822" />

```python
epq_model.graph(renderer="matplotlib")
```

## Repository Notes

* The project is currently closed to external feature contributions; see [CONTRIBUTING.md](CONTRIBUTING.md).
