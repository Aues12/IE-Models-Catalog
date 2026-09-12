# EOQ Test Learning Strategy

*Documented on: 2025-09-03*

This document outlines a practical strategy for writing structured and scalable tests for inventory models, especially those implemented in the EOQ (Economic Order Quantity) framework. The goal is not only to test correctness but to build long-term confidence in the models through good testing habits.

---

## 🔧 Goal: Learn the Structure of Testing

### 🧠 Step 1: Think like a Scientist

Testing isn't just debugging—it's a **methodology**. Each test is a hypothesis:

* What *must* this function do?
* What inputs will stress or break it?
* What guarantees am I making to myself and others?

Writing a test is formalizing **trust** in the code, just like a scientific experiment formalizes trust in a claim.

---

### 🧱 Step 2: Build a Clean Test Scaffold

We begin with clear advantages:

* Modular classes: `BasicEOQ`, `EPQ`, `DiscountEOQ`, `IncrementalDiscountEOQ`, and `BackorderEOQ`
* Pure mathematical logic: No database, no random behavior, no side effects
* Consistent structure: Every model defines `calculate_eoq()` and `calculate_reorder_point()`

This means tests can be:

* **Predictable**: Results are deterministic
* **Parameterizable**: Same test logic works across different models
* **Portable**: New models can reuse the test scaffolds

---

## 🧪 Step 3: Organize tests by responsibility

### 🔹 Layer 1: Contract and validation tests

Use shared parametrized tests for behavior that all models promise:

* finite, positive or non-negative input domains;
* result/legacy API agreement;
* profile and time-unit behavior;
* common error types and constraint semantics.

Keep these checks in `test_model_contracts.py`, `test_invalid_parameters.py`,
and `test_reorder_point.py` rather than repeating them in model-specific files.

### 🔹 Layer 2: Parametrization and scaling

Apply **pytest parametrization** to shared behavior:

* Use `@pytest.mark.parametrize` to run the same test across multiple inputs
* Feed test cases from structured data tables (even external JSON or CSV)
* Give IDs to each test case for easier debugging

This phase emphasizes **abstraction**, **reuse**, and **clarity**.

---

### 🔹 Layer 3: Model-specific and operational features

Each model has unique behavior that deserves dedicated tests:

* `DiscountEOQ` and `IncrementalDiscountEOQ`: test tier selection, billing, and total cost minimization
* `BackorderEOQ`: test `calculate_cycle_metrics()` including `S_max`, `B_max`, and total cost
* `EPQ`: enforce `production_rate > demand_rate`
* All models: test variations of `calculate_reorder_point()` under different lead time and safety stock values

This is where testing blends into **API design**. Good APIs are testable; if it's hard to test, the design may need work.

---

## Final Notes

* Every test is a safeguard *and* a piece of documentation
* Testing reveals edge cases before users do
* The better your tests, the more confidently you can improve or refactor your models

This strategy should evolve with the project—but its core principle remains: **tests are how you teach your code to be reliable**.

---

## Extending This Strategy to Dynamic Models

The repository now includes `DynamicLotSizing` in [dynamic_models.py](../dynamic_models.py), so test coverage should expand beyond the EOQ family.

Recommended additions:

* Validate both supported methods: `wagner-whitin` and `silver-meal`
* Use small hand-checkable demand sequences as regression fixtures
* Test constructor validation for empty demand, negative demand, and negative costs
* Assert returned `order_quantities`, `order_periods`, and `total_cost` together so the plan and its cost stay consistent

## Implemented independent checks

`test_independent_optimality.py` enumerates feasible integer order schedules for all
four-period demand vectors with entries 0, 1, or 2, three initial-stock levels,
and nine setup/holding-cost combinations (2,187 scenarios per solver). Its oracle
uses period stock balances and actual order counts rather than the solver's DP
recurrence. Wagner–Whitin must match the minimum cost; Silver–Meal must produce a
feasible plan with a consistent cost no lower than that minimum.

EOQ-family optima are checked against independently evaluated cost surfaces,
including a two-dimensional quantity/backorder-fraction grid for planned shortages.
These bounded grids are regression evidence, not proofs for arbitrary real inputs.

`test_model_contracts.py` checks finite input validation, continuous discount
boundaries, initial-stock accounting, analysis-mode return values, time units,
and consistency between legacy methods and the common cost/result API. The
model-specific files retain only behavior that is not already covered by these
shared contracts.

`test_public_api.py` checks the public import namespace, saved-policy isolation,
frozen result behavior, profile shape preservation, and agent serialization
compatibility.
