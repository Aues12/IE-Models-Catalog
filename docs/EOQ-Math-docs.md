# Basic EOQ: Formulation

See the [model catalog](models/README.md) for current API examples, shared units, and verification evidence. In these derivations, basic/EPQ/backorder cost formulas exclude the constant acquisition component; discount comparisons include it.

This document explains the **Basic Economic Order Quantity (EOQ)** model, its core concept, and the mathematical derivation.

---

## 1. Core Concept

The **Basic EOQ** model aims to minimize total inventory costs by balancing:

- **Ordering cost (S)** – fixed cost per order.
- **Holding cost (H)** – annual cost per unit held in inventory.

**Assumptions** include:

- Constant demand rate (D).
- Instantaneous replenishment (lead time can be included optionally for more realistic scenarios).
- No shortages allowed.

---

## 2. Total Annual Cost

Define:

- Q = order quantity per cycle

Annual costs consist of:

1. **Ordering cost:** $\frac{D S}{Q}$
    - Number of orders per year multiplied by ordering cost.
2. **Holding cost:**$\frac{H Q}{2}$
    - Average inventory is $Q/2$, multiplied by holding cost per unit.

Total cost:

$TC(Q)= \frac{D S}{Q} + \frac{H Q}{2}$

---

## 3. Optimal Order Quantity

**Minimize TC(Q)** with respect to Q:

$\frac{d TC}{d Q} = -\frac{D S}{Q^2} + \frac{H}{2} = 0$

Solve for $Q^*$:

$Q^*= \sqrt{\frac{2 D S}{H}}$

This represents the **Economic Order Quantity**, the quantity that minimizes total cost.

---

## 4. Summary

- **Optimal order quantity (Q):** $Q^* = \sqrt{2DS/H}$
- **Total annual cost at Q:** $TC(Q^*) = \frac{D S}{Q^*} + \frac{H Q^*}{2}$
- **Intuition:** EOQ balances the *trade-off*  between **ordering cost** and **holding cost**.

---

# EPQ: Formulation

This is the documentation for the **Economic Production Quantity (EPQ)** model, which extends the classic **EOQ** **model** by accounting for a finite production rate.

---

## 1. Core Concept

In **EOQ**, we assume **instantaneous replenishment** (all items arrive at once). **EPQ** modifies this assumption:

- Items are produced internally at a **finite production rate (P)**.
- **Demand (D)** occurs simultaneously during production.
- Inventory builds up gradually instead of arriving all at once.

Thus, EPQ is suitable for **manufacturing settings** where production and consumption occur together.

---

## 2. Total Cost Function

**Parameters**:

- **D** = annual demand
- **S** = setup (ordering) cost per run
- **H** = annual holding cost per unit
- **P** = production rate (units per year)

**Key relationship:** Only a portion of the production adds to inventory, since demand occurs simultaneously:

**Effective buildup rate** = $P-D$

**Maximum inventory level**:  $I_{max} = Q \left(1 - \frac{D}{P}\right)$

The inventory cycle is:

```
I_max ──────────  ← max inventory level 
              /\
rising       /  \
inventory-> /    \
           /      \
          /        \  ← falling inventory as demand occurs

```

---

## 3. Total Annual Cost

Annual costs consist of:

1. **Setup cost:** $\frac{D S}{Q}$
2. **Holding cost:** $\frac{H I_{max}}{2} = \frac{H Q}{2} \left(1 - \frac{D}{P}\right)$

**Total cost function**:

$TC(Q) = \frac{D S}{Q} + \frac{H Q}{2} \left(1 - \frac{D}{P}\right)$

- The setup cost per production run is represented by `ordering_cost` in the shared API.

---

## 4. Optimal Production Lot Size

To minimize TC(Q), differentiate with respect to Q and solve:

$Q^* = \sqrt{\frac{2 D S}{H} \cdot \frac{P}{P - D}}$

This is the **EPQ optimal lot size**.

---

## 5. Summary

- When $P \to \infty$, EPQ reduces to EOQ.
- Optimal lot size balances **setup cost vs. holding cost**, adjusted for the production rate.
- Maximum inventory is reduced compared to EOQ since demand occurs during production.

**Practical Use:** EPQ is applied in manufacturing environments where goods are produced and consumed simultaneously, unlike EOQ where replenishment is instantaneous.

---


# Backorder EOQ: Formulation

## 1. Core Concept

In a standard EOQ model, the goal is to minimize total costs by balancing:

- **Ordering cost (S)** – fixed cost per order.
- **Holding cost (H)** – annual cost per unit held in inventory.

The **Backorder EOQ** model introduces **planned shortages**, where negative inventory (backorders) is allowed. This adds:

- **Shortage cost (P)** – cost per backlogged unit per year of waiting; unmet demand is eventually fulfilled, not lost.

Total cost now consists of **Ordering + Holding + Shortage costs**.

---

## 2. Total Cost Function

Define:

- **Q** = order quantity per cycle
- **S_max** = maximum inventory on hand
- **B_max** = maximum backorder

The inventory cycle is:

```
S_max ──────────\         ← inventory decreases with demand
                 \
                  \
                   \      ← backorders accumulate after inventory=0 
                    \
                     \
                      B_max

```

**Relationships:**

$Q = S_{max} + B_{max}, \quad    S_{max} = \frac{P}{H + P} Q, \quad B_{max} = \frac{H}{H + P} Q$

---

## 3. Total Annual Cost

Annual costs:

1. **Ordering cost:** $\frac{D S}{Q}$
2. **Holding cost:** $\frac{H S_{max}^2}{2 Q}$
3. **Shortage cost:** $\frac{P B_{max}^2}{2 Q}$

Total cost:

$TC(Q) = \frac{D S}{Q} + \frac{H S_{max}^2}{2 Q} + \frac{P B_{max}^2}{2 Q}$

Substitute S_max and B_max:

$TC(Q)=\frac{D S}{Q} + \frac{H (\frac{P}{H+P} Q)^2}{2 Q} + \frac{P (\frac{H}{H+P} Q)^2}{2 Q}$

Simplifying:

$TC(Q) = \frac{D S}{Q} + \frac{H P}{2(H+P)} Q$

---

## 4. Optimal Order Quantity

**Minimize TC(Q)** with respect to **Q**:

$\frac{d TC}{d Q} = -\frac{D S}{Q^2} + \frac{H P}{2(H+P)} = 0$

Solve for $Q^*$:

$Q^* = \sqrt{\frac{2 D S (H+P)}{H P}}$

This matches the implementation in `BackorderEOQ.calculate_eoq`.

---

## 5. Summary

- **Maximum inventory** and **backorder** quantities:
    
    $S_{max} = \frac{P}{H+P} Q^*, \quad B_{max} = \frac{H}{H+P} Q^*$
    
- **Total annual cost** at $Q^*$:
    
    $TC(Q^*) = \frac{D S}{Q^*} + \frac{H S_{max}^2}{2 Q^*} + \frac{P B_{max}^2}{2 Q^*}$
    
- **Intuition:** The ratio of holding cost to shortage cost determines how much inventory is maintained versus backordered.

---


# Discount EOQ: Formulation

This document explains the **Economic Order Quantity (EOQ) model with quantity discounts**, its principles, and the mathematical formulation.

---

## 1. Core Concept

**Discount EOQ** extends the **Basic EOQ** by incorporating **bulk purchase discounts**. The goal remains minimizing total annual cost while considering **price breaks** for larger order quantities.

**Assumptions**:

- **Demand rate (D)** is constant.
- Lead time is instantaneous or fixed.
- Holding cost is proportional to unit cost.
- Discounts are applied at **defined quantity breakpoints**.

---

## 2. Total Cost Function

**Parameters**:

- **D** = annual demand
- **S** = ordering/setup cost per order
- **H** = annual holding cost per unit (calculated as holding_rate × unit price)
- **C(Q)** = unit price depending on order quantity Q (discounted at certain thresholds)

**Total annual cost**:

$TC(Q) = D \cdot C(Q) + \frac{D S}{Q} + \frac{H Q}{2}$

- **Purchase cost:** $D \cdot C(Q)$
- **Ordering cost:** $DS/Q$
- **Holding cost:** $HQ/2$

Since **C(Q)** decreases with higher order quantities, the total cost function may have multiple local minima at discount thresholds.

---

## 3. Optimal Order Quantity

Computation steps:

1. **Compute EOQ for each price tier:**
    
    $Q_i^*= \sqrt{\frac{2 D S}{H_i}}$ where $H_i$ = holding cost based on unit price in tier $i$.
    
2. **Check feasibility:** $Q^*_i$ must satisfy the minimum quantity for the discount tier.
3. **Check total cost at every tier**:
    1. Calculate **TC(Q)** for $Q^*_i$, and
    2. At all **minimum quantities** for discount tiers.
4. **Select optimal:** Choose the quantity that gives the lowest total cost.

---

## 4. Summary

- **Optimal order quantity** depends on both EOQ calculation and quantity discount thresholds.
- Multiple EOQ values are considered, one per price tier.
- Final choice is the feasible quantity with the **minimum total cost**.
- This approach balances ordering, holding, and purchasing costs while taking advantage of bulk discounts.

**Practical Use:** Discount EOQ is applied in procurement scenarios where suppliers offer lower unit prices for larger orders, influencing optimal inventory decisions.

---
