# IE Models Catalog Proposal

## Introduction

In this report, I will discuss the idea of an **“Industrial Engineering Models Catalog”**.  What is meant by this, is a **Python** library or a collection of functions written in Python programming language, that represent models widely used in **Industrial Engineering** domain. 

The main purpose of such a project is collecting various pre-written **model functions** for ease of use and utility. The idea is that the user can pick whichever model that suits their job-needs, and easily call the predefined class and function that corresponds to it.

Since we cannot write all models at once, we need to start from somewhere. But since the idea is to build a **“Catalog”**, we also want to structure our files in way that allows growth and further improvement. This makes deciding the architecture early on the project an important matter. Putting a greater emphasis on **software architecture** allows for a cleaner and more conscious writing.

In such a project, **clean code/documentation writing** and **simple user interface** offer great value.

## Inventory Models

I have seen a need to easily reach IE models, when I was doing my internship at a spare parts trading company. Whether it is a business environment or a research environment, easily accessing pre-programmed versions of these **mathematical models** would provide great benefits in terms of time and productivity.

The ideal way to start such a project would be starting from **basic** and **simpler** models, then to advance into more **complex** models with more **advanced features** and parameters. Therefore, we will build various EOQ Models based on the `BasicEOQ` superclass.

Documentation for Inventory Models can be found in this [notion page](https://understood-key-c19.notion.site/ebd/25fa928f126d804080baf9c1c5704332).

The catalog is designed to grow from these fundamentals into more advanced scenarios—extending the software architecture with each addition to keep the codebase maintainable.

## Quick Start

### BasicEOQ

The `BasicEOQ` class implements the classic Economic Order Quantity model. Instantiate it with your demand, cost, and holding parameters, then call the helper methods to calculate optimal order size and reorder point.

```python
from inventory_models import BasicEOQ

model = BasicEOQ(
    price=50.0,
    demand_rate=1200,
    ordering_cost=75,
    holding_rate=0.20,
)

eoq = model.calculate_eoq()
reorder_point = model.calculate_reorder_point(lead_time=10, safety_stock=20)

print(f"Economical Order Quantity (Q*): {round(eoq)} units")
print(f"Reorder Point: {round(reorder_point)} units")
```

The example prints the optimal batch size for replenishment and the stock level that should trigger a new order, illustrating how the catalog’s classes can be embedded in larger applications or notebooks.

### EPQ

The `EPQ` class implements the classic Economic Production Quantity model. An extension of `BasicEOQ` class, used when items are **produced gradually** rather than delivered instantly. Works pretty much the same way as its parent class.

```python
from inventory_models import EPQ

epq_model = EPQ(
    price=50.0,
    demand_rate=1000,
    ordering_cost=75,
    holding_rate=0.20,
    production_rate=1200
)

epq = epq_model.calculate_eoq()
reorder_point = model.calculate_reorder_point(lead_time=10, safety_stock=20)

print(f"Economical Order Quantity (Q*): {round(epq)} units")
print(f"Reorder Point: {round(reorder_point)} units")
```

The only difference is the `production_rate` parameter. The syntax for `calculate_eoq()` and `calculate_reorder_point()` methods is the same as `BasicEOQ`.

### BackorderEOQ

The `BackorderEOQ` class extends EOQ by allowing **shortages (backorders)** which are filled later, at a cost.

```python

# Example parameters
demand_rate = 800         # units/year
ordering_cost = 100       # currency/order
price = 200               # currency/unit
holding_rate = 0.25       # 25% of unit price per year
shortage_cost = 30        # currency/unit/year

# Create model instance
backorder_model = Backorder_EOQ(
    price=price,
    demand_rate=demand_rate,
    ordering_cost=ordering_cost,
    holding_rate=holding_rate,
    shortage_cost=shortage_cost
)

eoq = backorder_model.calculate_eoq()

# Run calculations
print("Economical Order Quantity (Q*): ", eoq)
print("Cycle Metrics:", backorder_model.calculate_cycle_metrics())
```

Introduces `shortage_cost` parameter.

`BackorderEOQ` also has a `calculate_cycle_metrics()` method that gives max inventory and max backorder levels.

