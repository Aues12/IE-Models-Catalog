# EOQ Test Learning Strategy

*Documented on: 2025-09-03*

This document outlines a practical strategy for learning how to write structured and scalable tests for inventory models, especially those implemented in the EOQ (Economic Order Quantity) framework. The goal is not only to test correctness but to build long-term confidence in the models through good testing habits.

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

* Modular classes: `BasicEOQ`, `EPQ`, `DiscountEOQ`, `BackorderEOQ`
* Pure mathematical logic: No database, no random behavior, no side effects
* Consistent structure: Every model defines `calculate_eoq()` and `calculate_reorder_point()`

This means tests can be:

* **Predictable**: Results are deterministic
* **Parameterizable**: Same test logic works across different models
* **Portable**: New models can reuse the test scaffolds

---

## 🧪 Step 3: Learn by Writing Tests in 3 Waves

### 🔹 Wave 1: Behavioral Core Tests

Focus: `.calculate_eoq()` across all models

* ✅ Happy path: Does the EOQ formula return expected output for known inputs?
* 🔁 Reproducibility: Does it return the same output every time it's called?
* ❌ Validation: Does it reject bad inputs like zero or negative values?

Example:

* `test_calculate_eoq_matches_formula`
* `test_invalid_parameters_raise`

---

### 🔹 Wave 2: Parametrization and Scaling

Once the base behavior is validated, apply **pytest parametrization**:

* Use `@pytest.mark.parametrize` to run the same test across multiple inputs
* Feed test cases from structured data tables (even external JSON or CSV)
* Give IDs to each test case for easier debugging

This phase emphasizes **abstraction**, **reuse**, and **clarity**.

---

### 🔹 Wave 3: Model-Specific Features

Each model has unique behavior that deserves dedicated tests:

* `DiscountEOQ`: test discount tier selection logic and total cost minimization
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
