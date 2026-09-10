# Model catalog

[Architecture overview](../ARCHITECTURE_OVERVIEW.md) · [Project README](../../README.md) · [API reference](../API_REFERENCE.md)

Each guide connects the decision problem to its assumptions, mathematics, public
API, and verification evidence. Start with Basic EOQ, then choose a guide based
on the condition you want to introduce.

| Guide | Decision / distinguishing condition | Method |
| --- | --- | --- |
| [Basic EOQ](basic_eoq.md) | Repeating orders with constant demand | Closed-form optimum |
| [EPQ](epq.md) | Gradual production while demand consumes stock | Closed-form optimum |
| [Discount EOQ](discount_eoq.md) | Lower all-units prices at quantity thresholds | Feasible tier-candidate comparison |
| [Incremental Discount EOQ](incremental_discount_eoq.md) | Marginal pricing within quantity bands | Feasible band-candidate comparison |
| [Backorder EOQ](backorder_eoq.md) | Planned waiting for later replenishment | Closed-form quantity and backlog split |
| [Wagner–Whitin](wagner_whitin.md) | Known, time-varying demand | Exact dynamic programming |
| [Silver–Meal](silver_meal.md) | Same dynamic problem with a local decision rule | Heuristic; no optimality guarantee |

Wagner–Whitin and Silver–Meal are two methods for the same dynamic problem,
not two different demand models. Their separate guides explain how their
solution rules and guarantees differ.

All EOQ variants support optional [operational order constraints](order_constraints.md).
Dynamic methods support period cost vectors and fixed delivery lead time.

Read [shared conventions](conventions.md) for symbols, units, time horizons,
initial-stock accounting, and result fields. For runnable comparisons and
sensitivity studies, see the [examples guide](../../examples/README.md).
The existing mathematical notes remain available as longer derivations.

## Standard for adding a model

Copy [TEMPLATE.md](TEMPLATE.md) and fill the same nine sections used by the guides.
A model is ready to join the catalog when:

- Its purpose, assumptions, inputs, units, and output meanings are explicit.
- The mathematical definition matches the implemented scope and guarantees.
- A self-contained example runs and its output matches a worked calculation.
- Meaningful independent verification and feasibility/boundary checks exist,
  with links to the actual tests.
- Mathematical limitations and implementation gaps are distinguished.
- Implementation, explanations, and sources can be reached from the guide.

Scale the evidence to the model: a small closed-form calculation need not have
the same documentation volume as a constrained multi-product optimizer.
A heuristic should be checked for feasibility and cost consistency; it should
not be documented as exact because it matches a few optimal examples.
