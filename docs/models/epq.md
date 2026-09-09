# Economic Production Quantity (EPQ)

[Model catalog](README.md) · [Shared conventions](conventions.md) · [API reference](../API_REFERENCE.md)

## Purpose

Choose a production batch size when units are produced gradually while demand consumes them.

## Assumptions

- One item with constant production rate $P$ and demand rate $D$, with $P>D$.
- Production and consumption occur simultaneously during a run.
- Setup cost and holding rate are constant; shortages are not allowed.
- Continuous quantities and a repeating cycle, without shared machine scheduling.

## Inputs and units

The formulas below describe the continuous case. Optional
[order constraints](order_constraints.md) add per-order bounds, integrality and pack multiples
through `solve(constraints=...)` and `inventory_level(..., constraints=...)`.

Use the [shared EOQ inputs and units](conventions.md#eoq-family). This example uses an annual demand period.

Additional input: `production_rate` ($P$), in units per demand period. It must be finite and greater than `demand_rate`. Here `ordering_cost` represents setup cost per production run.

## Mathematical definition

Maximum stock is $I_{max}=Q(1-D/P)$, so average stock is $I_{max}/2$.

$$C_{rel}(Q)=\frac{DK}{Q}+\frac{hQ}{2}\left(1-\frac{D}{P}\right).$$

$$Q^*=\sqrt{\frac{2DK}{h}\frac{P}{P-D}}.$$

Production lasts $Q/P$ demand periods; the full cycle lasts $Q/D$. As production rate tends to infinity, the expression tends to basic EOQ.

## Worked example

Use the same annual inputs as the basic example and production rate 200 units/year.
The stock accumulation factor is `1 − 100/200 = 0.5`.
The optimum is `sqrt(500 × 2) = 31.62278` units; maximum stock is 15.81139 units.
Setup and holding costs are each about 15.81, giving relevant cost 31.62.
The API adds the constant `price × demand` component of 1,000, giving total cost 1,031.62.

## Python usage

```python
from inventory_models import EPQ

model = EPQ(
    price=10,
    demand_rate=100,
    ordering_cost=5,
    holding_rate=0.20,
    production_rate=200,
)
result = model.solve()
print(f"Quantity: {result.order_quantity:.2f}")
print(f"Relevant cost: {result.costs.relevant_cost:.2f}")
print(f"Total cost: {result.total_cost:.2f}")
```

```text
Quantity: 31.62
Relevant cost: 31.62
Total cost: 1031.62
```

## Verification

The [independent cost-surface tests](../../tests/test_independent_optimality.py)
evaluate costs from inventory geometry over a grid of candidate quantities.
The [contract tests](../../tests/test_model_contracts.py) check cost breakdowns,
legacy API agreement, validation, and time units. The grids are bounded numerical
checks, not proofs for all possible inputs.

For the worked example, integrate the triangular stock cycle: its average must be half its 15.81139-unit peak.

## Limitations

A finite production rate is represented, but competition between products for the same machine is not. Setup time, changeovers, downtime, and variable production rates are not inputs. The shared `purchase` cost field is the constant unit-cost component in this production model.

## References

- [Formula derivations](../EOQ-Math-docs.md)
- [Implementation](../../inventory_models.py)
