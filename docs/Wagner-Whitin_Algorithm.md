# Wagner-Whitin Algorithm

Here is a simplified overview of the **Dynamic Lot Sizing (Wagner-Whitin)** workflow:

1. **Read the input**

   Demand, setup cost (`K`), and holding cost (`h`).

2. **Determine the number of periods**

   `T = len(demand)`

3. **Define the cost function**

   The cost of ordering in period `i` and covering demand through period `j`.

4. **Initialize the DP table**

   Begin with `F[t] = 0` for the initial minimum-cost state.

5. **Calculate forward with dynamic programming**

   For each `t`:

   - try earlier ordering periods `i`;
   - choose the lowest-cost option.

6. **Find the optimal cost**

   `F[T]`

7. **Backtrack**

   Recover the periods in which orders are placed.

8. **Build the result**

   Order quantities plus total cost.

---

## 1. What does the DP table look like?

In dynamic lot sizing, we generally consider two values:

- **`C(i, j)`**: the cost of ordering in period `i` and covering demand through period `j`;
- **`F(t)`**: the minimum total cost through period `t`.

For a three-period example, the shape is:

### `C(i, j)` cost matrix

```text
        j=1    j=2    j=3
i=1     C11    C12    C13
i=2      -     C22    C23
i=3      -      -     C33
```

- The lower triangle is empty because `i > j` is not meaningful.
- Example interpretations:
  - `C12`: order in period 1 and cover periods 1 and 2;
  - `C13`: order in period 1 and hold inventory through period 3.

### `F(t)` DP vector

```text
t:    0    1    2    3
F:    0   F1   F2   F3
```

The calculations are:

```text
F(1) = min{ F(0) + C(1,1) }

F(2) = min{
    F(0) + C(1,2),
    F(1) + C(2,2)
}

F(3) = min{
    F(0) + C(1,3),
    F(1) + C(2,3),
    F(2) + C(3,3)
}
```

---

## 2. Forward calculation versus backtracking

### Forward calculation (DP)

- **Goal:** find the minimum cost.
- **Direction:** `1 → T`.
- **What it does:**
  - calculates the best cost for each `t`;
  - fills the `F(t)` values.

It answers: “What is the cost of the cheapest plan?”

### Backtracking

- **Goal:** determine how that cost was achieved.
- **Direction:** `T → 0`.
- **What it does:**
  - follows the selected ordering period `i`;
  - recovers the order periods.

It answers: “In which periods should I order?”

## Summary

- `C(i, j)`: local decision costs.
- `F(t)`: globally optimal cost.
- Forward pass: calculates costs.
- Backward pass: recovers the plan.

---

## Example data

Use a small, clear example:

- Demand: `[10, 20, 30]`
- Setup cost: `K = 100`
- Holding cost: `h = 1` per unit per period

## 1. `C(i, j)` matrix

The logic is: if an order placed in `i` covers demand through `j`, every unit held for a future period incurs time × `h`.

### Calculations

- `C11 = 100`
- `C12 = 100 + (20 × 1) = 120`
- `C13 = 100 + (20 × 1 + 30 × 2) = 100 + 20 + 60 = 180`
- `C22 = 100`
- `C23 = 100 + (30 × 1) = 130`
- `C33 = 100`

### Table

```text
        j=1    j=2    j=3
i=1     100    120    180
i=2      -     100    130
i=3      -      -     100
```

## 2. Forward calculation

```text
F(0) = 0

F(1) = F(0) + C(1,1) = 100

F(2) = min(
    F(0) + C(1,2) = 120,
    F(1) + C(2,2) = 100 + 100 = 200
) = 120

F(3) = min(
    F(0) + C(1,3) = 180,
    F(1) + C(2,3) = 100 + 130 = 230,
    F(2) + C(3,3) = 120 + 100 = 220
) = 180
```

**Minimum total cost = 180**

## 3. Backtracking

`F(3) = 180` comes from:

```text
F(0) + C(1,3)
```

Therefore, order in period 1 and cover demand through period 3.

## 4. Final decision

- Place an order only in period 1.
- Quantity: `10 + 20 + 30 = 60`.
- Do not place orders in the other periods.

## Intuition

- High setup cost means fewer orders are preferable.
- Low holding cost makes carrying inventory more attractive.
