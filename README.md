# IE Models Catalog Proposal

## Introduction

In this report, I will discuss the idea of an **“Industrial Engineering Models Catalog”**.  What is meant by this, is a **Python** library or a collection of functions written in Python programming language, that represent models widely used in **Industrial Engineering** domain. 

The main purpose of such a project is collecting various pre-written **model functions** for ease of use and utility. The idea is that the user can pick whichever model that suits their job-needs, and easily call the predefined class and function that corresponds to it.

Since we cannot write all models at once, we need to start from somewhere. But since the idea is to build a **“Catalog”**, we also want to structure our files in way that allows growth and further improvement. This makes deciding the architecture early on the project an important matter. Putting a greater emphasis on **software architecture** allows for a cleaner and more conscious writing.

In such a project, **clean code/documentation writing** and **simple user interface** offer great value.

## Inventory Models

I have seen a need to easily reach IE models, when I was doing my internship at a spare parts trading company. Whether it is a business environment or a research environment, easily accessing pre-programmed versions of these **mathematical models** would provide great benefits in terms of time and productivity.

The ideal way to start such a project would be starting from **basic** and **simpler** models, then to advance into more **complex** models with more **advanced features** and parameters. Therefore, we will build various EOQ Models based on the `BasicEOQ` superclass.

Documentation for Inventory Models can be found in this [EOQ Model Docs](https://understood-key-c19.notion.site/ebd/25fa928f126d804080baf9c1c5704332). The details of mathematical formulations are also available at [EOQ Math Docs](https://understood-key-c19.notion.site/ebd/25fa928f126d806fa746ebba2d5dcd7e?v=25fa928f126d8092983c000c2642387a).

The catalog is designed to grow from these fundamentals into more advanced scenarios—extending the software architecture with each addition to keep the codebase maintainable.

## Quick Start

### How to install

Clone the repository:
```
git clone https://github.com/Aues12/IE-Models-Catalog.git
cd IE-Models-Catalog
```
(Optional) Create and activate a virtual environment:
```
python -m venv .venv
source .venv/bin/activate
```
Install the required dependencies:
```
pip install -r requirements.txt
```
### BasicEOQ

The `BasicEOQ` class implements the classic **Economic Order Quantity** model. Instantiate it with your demand, cost, and holding parameters, then call the helper methods to calculate optimal order size and reorder point.

```python
from inventory_models import BasicEOQ

# Create model instance
eoq_model = BasicEOQ(
    price=50.0,
    demand_rate=1200,
    ordering_cost=75,
    holding_rate=0.20,
)

# Calculate economic order quantity (EOQ)
eoq = eoq_model.calculate_eoq()
# Calculate reorder point (in terms of units)
reorder_point = eoq_model.calculate_reorder_point(lead_time=10, safety_stock=20)

print(f"Economical Order Quantity (Q*): {eoq} units")
print(f"Reorder Point: {reorder_point} units")
```

The example prints the optimal batch size for replenishment and the stock level that should trigger a new order, illustrating how the catalog’s classes can be embedded in larger applications or notebooks.

### EPQ

The `EPQ` class implements the classic **Economic Production Quantity** model. It is an extension of `BasicEOQ` class, used when items are **produced gradually** rather than delivered instantly. Works pretty much the same way as its parent class.

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
reorder_point = epq_model.calculate_reorder_point(lead_time=10, safety_stock=20)

print(f"Economical Order Quantity (Q*): {epq} units")
print(f"Reorder Point: {reorder_point} units")
```

The only difference is the `production_rate` parameter. The syntax for `calculate_eoq()` and `calculate_reorder_point()` methods is the same as `BasicEOQ`.

### BackorderEOQ

The `BackorderEOQ` class extends EOQ by allowing **shortages (backorders)** which are filled later, at a cost.

```python

backorder_model = BackorderEOQ(
    price=100,
    demand_rate=500,
    ordering_cost=200,
    shortage_cost=50,
    holding_rate=0.2
    )

eoq = backorder_model.calculate_eoq()

print("Economical Order Quantity (Q*): ", eoq)
print("Cycle Metrics:", backorder_model.calculate_cycle_metrics())
```

Introduces `shortage_cost` parameter.

`BackorderEOQ` also has a `calculate_cycle_metrics()` method that gives max inventory and max backorder levels.

### DiscountEOQ

The `DiscountEOQ` class implement **EOQ with Quantity Discounts** model. This refers to a scenario where the supplier offers discounts at certain quantity levels.

Algorithm logic is available in [EOQ documentation page](https://understood-key-c19.notion.site/ebd/25fa928f126d804080baf9c1c5704332) Section 2.2. Formulation details are also documented.

```python

discount_model = DiscountEOQ(
            price=100,
            demand_rate=1000,     # annual demand
            ordering_cost=50,     # setup cost
            holding_rate=0.2,     # 20% holding cost
            discount_rates={      
                0: 0.0,           # base price
                100: 0.05,        # 5% discount if Q >= 100
                200: 0.10         # 10% discount if Q >= 200
            }    # Discount rates are given as a dictionary
        )

discount_model.calculate_eoq(analysis_mode=True)
```

`analysis_mode` is also available for `DiscountEOQ`, which prints out internal variables; good for degbugging purposes and for seeing the underlying algorithmic steps. It also prints out analytics such as Minimum Total Cost and Best Unit Price.

### Inventory Level

You can calculate the **Inventory Level** of an EOQ model at time `t` using the method `.inventory_level(t)`. Method takes time `t` in the unit of days. For example, the inventory level at tenth day is `eoq_model.inventory_level(t=10)`.


### Graphing

You can plot the EOQ function using `.graph()` method. This method is available for all 4 classes. Method uses `plotly` as the default renderer but you can optionally choose `matplotlib` as well.

```python

eoq_model.graph(renderer="plotly")
```

<img width="1063" height="450" alt="image" src="https://github.com/user-attachments/assets/b656ec01-fe5a-4931-ac3e-2c87cb504822" />

```python

epq_model.graph()
```

<img width="1063" height="450" alt="image" src="https://github.com/user-attachments/assets/ddb7252b-0cb8-4f15-bd70-6938b4dc2a87" />

```python

backorder_model.graph()
```

<img width="1063" height="450" alt="image" src="https://github.com/user-attachments/assets/b506aa6d-a564-4050-8196-eaac2453fab7" />

```python

discount_model.graph()
```

<img width="1063" height="450" alt="image" src="https://github.com/user-attachments/assets/ea32a812-7168-4f3e-a554-d09c69fd2812" />










