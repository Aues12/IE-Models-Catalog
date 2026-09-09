# Incremental Discount EOQ

[Model catalog](README.md) · [Shared conventions](conventions.md)

## Purpose

Choose a repeating order quantity when cheaper prices apply only to the units
inside each price band. Use `DiscountEOQ` instead when the selected discount
applies to every unit in the order.

## Assumptions

Known constant demand, instantaneous replenishment, no shortages, positive costs,
and nondecreasing discounts. Holding uses the **average acquisition price of the
whole lot**, rather than tracking depletion of separately priced units.

## Inputs and units

The [shared EOQ inputs](conventions.md#eoq-family) apply.
`discount_rates` maps quantity thresholds to discounts in `[0, 1)`.
An omitted zero threshold is inserted at the base price. Thresholds may be
fractional. Optional `solve(constraints=...)` accepts [order constraints](order_constraints.md).

## Mathematical definition

Within a band with marginal price $c_j$, the lot's purchase bill is
$B(Q)=c_jQ+a_j$, where $a_j$ preserves the bills for earlier bands.
The average price is $B(Q)/Q$. The total cost per demand period is

$$C(Q)=D B(Q)/Q+DK/Q+iB(Q)/2.$$

A band's stationary quantity is $\sqrt{2D(K+a_j)/(ic_j)}$.
Compare feasible stationary points and band boundaries using the complete cost.
For integer/pack constraints compare neighboring feasible multiples within each
band. This is an exact candidate comparison under the stated valuation convention.

## Worked example

Let `D=1000`, `K=50`, base price `10`, and `i=0.2`. The first 100 units cost
10 each, the next 100 cost 9, and units above 200 cost 8.
Above 200, the bill is `B(Q)=8Q+300`; therefore
`Q=sqrt(2*1000*(50+300)/(0.2*8))=661.437828`.
Comparison with the earlier bands gives this optimum. Average price is about
8.45356, and total cost is 9088.300524 per demand period.
At `Q=250`, the bill is `1000+900+400=2300`, not `250*8=2000`.

## Python usage

```python
from inventory_models import IncrementalDiscountEOQ

result = IncrementalDiscountEOQ(
    price=10,
    demand_rate=1000,
    ordering_cost=50,
    holding_rate=0.2,
    discount_rates={100: 0.1, 200: 0.2},
).solve()
print(f"Quantity: {result.order_quantity:.2f}; total: {result.total_cost:.2f}")
# Quantity: 661.44; total: 9088.30
```

`result.unit_price` is the average acquisition price, not the marginal band's price.
Use `calculate_costs(quantity)` to evaluate a proposed lot with automatic billing.

## Verification

[Operational tests](../../tests/test_practical_models.py) reconstruct bills by
summing band quantities, check continuity at thresholds, compare a dense grid
with the continuous optimum, and exhaustively compare allowed pack quantities.
These numerical checks supplement the convex objective within each band.

## Limitations

No increasing marginal prices, freight tiers, tax, shortage, or joint capacity.
Average-price holding is an explicit accounting choice; it does not model FIFO
or LIFO depletion of cost layers. The inherited `holding_cost` property describes
the base price; result costs account for actual average price.

## References

- [Implementation](../../inventory_models.py)
- [All-units alternative](discount_eoq.md)
- [Runnable operational comparison](../../examples/practical_models.py)
