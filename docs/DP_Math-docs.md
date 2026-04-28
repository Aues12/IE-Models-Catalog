# Dynamic Lot Sizing Mathematics

## 1. Purpose of Dynamic Lot Sizing

Dynamic Lot Sizing (DLS) is used when demand changes from period to period.

Unlike EOQ, which gives one fixed order quantity, DLS creates an ordering plan over multiple periods.

The main question is:

> In which periods should we place orders, and how much should we order each time?

The goal is to minimize the total cost of:

* ordering / setup cost
* holding cost

## 2. Basic Setting

Assume there are T periods:

```text
1, 2, 3, ..., T
```

Demand in each period is known:

```text
d1, d2, d3, ..., dT
```

Parameters:

| Symbol | Meaning                          |
| ------ | -------------------------------- |
| dt     | demand in period t               |
| K      | fixed ordering / setup cost      |
| h      | holding cost per unit per period |
| T      | number of periods                |

Assumption:

> Demand is deterministic, meaning it is known in advance.

This is why DLS is often used together with forecasting in real systems.

## 3. Main Trade-Off

There are two opposite cost pressures.

### Ordering frequently

If we order every period:

* holding cost is low
* ordering cost is high

### Ordering in larger batches

If we order once for several future periods:

* ordering cost is lower
* holding cost is higher

DLS tries to find the best balance between these two.

## 4. Cost of One Order Covering Multiple Periods

Suppose we place an order in period j.

That order may cover demand from period j to period t:

```text
j, j+1, ..., t
```

The order quantity is:

```text
Q(j,t) = dj + d(j+1) + ... + dt
```

The setup cost is paid once:

```text
K
```

But items needed for later periods must be stored.

For example:

* demand in period j is used immediately → no holding cost
* demand in period j+1 is held for 1 period
* demand in period j+2 is held for 2 periods
* demand in period t is held for t-j periods

So the holding cost is:

```text
C(j,t) = h * [d(j+1)*1 + d(j+2)*2 + ... + dt*(t-j)]
```

More compactly:

```text
C(j,t) = Σ from k=j to t of [dk * h * (k-j)]
```

The total cost of one order placed in j to cover up to t is:

```text
K + C(j,t)
```

## 5. Dynamic Programming Idea

Dynamic Programming means solving a large problem by using smaller already-solved subproblems.

Define:

```text
F(t) = minimum total cost required to satisfy demand from period 1 to period t
```

Now ask:

> What if the last order before period t was placed in period j?

Then:

* periods 1 to j-1 are already solved by F(j-1)
* one new order is placed at period j
* that order covers demand from j to t

So the cost of this option is:

```text
F(j-1) + K + C(j,t)
```

Since j can be any period from 1 to t, we choose the cheapest option:

```text
F(t) = min over j ≤ t of [F(j-1) + K + C(j,t)]
```

Base case:

```text
F(0) = 0
```

This means there is no cost before the first period.

## 6. Interpretation of the Formula

At each period t, the algorithm asks:

> Where should the last order have been placed so that total cost up to period t is minimized?

It checks every possible last order point:

```text
j = 1, 2, ..., t
```

Then it chooses the best one.

This is why the algorithm evaluates possible previous ordering points to construct the optimal plan.

## 7. Step-by-Step Algorithm

### Step 1: Prepare demand data

Input demand values:

```text
d = [d1, d2, ..., dT]
```

### Step 2: Initialize arrays

Create:

```text
F[0] = 0
F[1], F[2], ..., F[T] = infinity
last_order[1], ..., last_order[T]
```

F stores the minimum cost up to each period.

last_order stores the best previous order period.

### Step 3: Iterate over each period t

For each t from 1 to T:

```text
for t in 1..T:
```

### Step 4: Test every possible last order period j

For each j from 1 to t:

```text
for j in 1..t:
```

Calculate:

```text
candidate_cost = F[j-1] + K + C(j,t)
```

If this candidate is cheaper than the current F[t], update:

```text
F[t] = candidate_cost
last_order[t] = j
```

### Step 5: Recover the order plan

After calculating F(T), we know the minimum total cost.

But we still need the actual order schedule.

This is found by backtracking:

1. Start from t = T
2. Look at last_order[t]
3. Suppose last_order[t] = j
4. Then one order is placed in period j to cover demand from j to t
5. Move to t = j-1
6. Repeat until t = 0

## 8. Simple Example

Suppose demand is:

| Period | Demand |
| ------ | -----: |
| 1      |     10 |
| 2      |     20 |
| 3      |     15 |

Let:

```text
K = 100
h = 2
```

### For period 1

Only option:

```text
order at 1, cover 1
```

Cost:

```text
F(1) = 100
```

### For period 2

Option A:

```text
order at 2, cover 2
```

Cost:

```text
F(1) + 100 = 200
```

Option B:

```text
order at 1, cover 1 and 2
```

Demand of period 2 is held for 1 period:

```text
100 + 20*2*1 = 140
```

So:

```text
F(2) = 140
```

### For period 3

Possible last order points:

```text
j = 1, 2, 3
```

The algorithm compares:

```text
F(0) + K + C(1,3)
F(1) + K + C(2,3)
F(2) + K + C(3,3)
```

Then it chooses the minimum.

## 9. Output of the Algorithm

The algorithm produces:

1. minimum total cost
2. order periods
3. order quantities

Example output format:

```text
Minimum total cost: 190
Orders:
- Period 1: order 30 units
- Period 3: order 15 units
```

## 10. Complexity

The Wagner-Whitin algorithm checks each period t and each possible previous order point j.

Therefore, the basic implementation has:

```text
Time complexity: O(T²)
```

This is usually acceptable for small and medium-sized planning horizons.

## 11. Relation to Rolling Horizon

DLS assumes future demand is known.

In real life, future demand is usually forecasted.

Rolling Horizon makes DLS more practical:

1. Forecast the next k periods
2. Run DLS on that forecast
3. Apply only the first decision
4. Update data
5. Repeat

So:

> DLS is the optimizer. Rolling Horizon is the controller that repeatedly uses it.

## 12. Key Summary

Dynamic Lot Sizing answers:

> When should we order, and how much should we order over time?

Wagner-Whitin solves this by asking:

> For each period, where should the last order have been placed?

Dynamic Programming makes this efficient by storing the best cost up to each period and reusing it.
