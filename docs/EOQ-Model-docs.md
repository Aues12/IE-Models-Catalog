## 1. Basic EOQ

`Basic_EOQ` class of `inventory_models.py`.

- **Definition**: Economic Order Quantity (EOQ) is the simplest inventory model.
- **Assumption**: Instant delivery, constant demand.
- **Formula**:
    
    $Q^* = \sqrt{\frac{2DS}{H}}$
    
    Where:
    
    - **D**: Demand rate
    - **S**: Ordering cost
    - **H**: Holding cost per unit

This model is the **foundation**. All variations build upon it.

---

## 2. EOQ Variations

### 2.1 EPQ (Economic Production Quantity)

`EPQ` class of `inventory_models.py`.

- **Definition**: An extension of EOQ used when items are **produced gradually** rather than delivered instantly.
- **Assumptions**:
    - Production occurs at a finite rate (P).
    - Demand (d) is consumed simultaneously while producing.
    - No shortages allowed.
- **Formula**:
    
    $Q^* = \sqrt{\frac{2DS}{H} \cdot \frac{P}{P - d}}$
    
    Where:
    
    - **P**: Production rate
    - **D**: Demand rate
- **Key Difference**: Inventory builds up gradually during production and is consumed at the same time.

---

### 2.2 EOQ with Quantity Discounts

`Discount_EOQ` class of `inventory_models.py`.

- **Definition**: Applies when suppliers offer **price breaks** for larger order sizes.
- **Assumptions**:
    - Multiple unit price levels depending on order quantity.
    - Trade-off between lower purchase cost and higher holding cost.
- **Logic**:
    1. **Compute EOQ** for each price level.
    2. Check feasibility (i.e., whether EOQ falls in that discount range).
    3. Compare total costs (purchase + ordering + holding).
    4. Choose the order quantity with the lowest total cost.
- **Formula** (EOQ step before comparison):
    
    $Q^* = \sqrt{\frac{2DS}{H}}$  (calculated per price tier)
    
- **Key Difference**: Unlike Basic EOQ, the optimal solution is not only about holding/ordering costs but also **purchase price**.

---

### 2.3 EOQ with Backordering

`Backorder_EOQ` class of `inventory_models.py`.

- **Definition**: Extends EOQ by allowing **shortages** (backorders) which are filled later, at a cost.
- **Assumptions**:
    - Unmet demand is backordered (not lost).
    - Backordering incurs a penalty or shortage cost (π).
- **Formula**:
    
    $Q^* = \sqrt{\frac{2DS}{H}} \cdot \sqrt{\frac{H+P}{P}}$
    
    Where:
    
    - **P**: Shortage (backorder) cost per unit per year.
- **Key Difference**: Balances holding costs with backordering costs to find an optimal mix.

---

### 2.4 EOQ with Multiple Items & Constraints

*(Not yet available.)*

- **Definition**: Considers multiple products competing for **limited resources** such as budget or storage space.
- **Assumptions**:
    - Shared constraints (e.g., total budget, total storage capacity).
    - Objective is to minimize total cost while satisfying constraints.
- **Formula**:
    - No single closed-form EOQ formula.
    - Typically solved using **mathematical programming** (e.g., Lagrangian multipliers, linear/integer programming).
- **Key Difference**: Optimization is **multi-item, resource-constrained**, making it more complex than single-item models.