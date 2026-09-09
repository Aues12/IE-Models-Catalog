# Shared model conventions

[Model catalog](README.md) · [API reference](../API_REFERENCE.md)

This page defines common symbols, units, and cost accounting. Individual guides
state the additional assumptions that make their equations applicable.

## EOQ family

All five EOQ constructors use these inputs:

| Input | Symbol | Meaning and unit | Default / domain |
| --- | --- | --- | --- |
| `price` | $c$ | Monetary units per item | Required, positive |
| `demand_rate` | $D$ | Items per demand period | Required, positive |
| `ordering_cost` | $K$ | Monetary units per order or production setup | Required, positive |
| `holding_rate` | $i$ | Carrying charge per unit value per demand period | 0.25, positive |
| `lead_time` | $L$ | Operating days; stored for reorder-point use | `None`, otherwise non-negative |

Values must be finite real numbers; booleans are not valid numeric inputs.
The holding cost per item per demand period is $h=ci$. `holding_cost` is derived
from `price` and `holding_rate`, not an independently assignable EOQ input.
An annual 20% carrying charge is entered as `0.20`.

`solve()` returns an `EOQResult` with order quantity, unit price, cycle time,
maximum inventory, maximum backlog, and a `CostBreakdown`. Cycle time is measured
in demand periods. Quantity is continuous by default; `solve(constraints=OrderConstraints(...))`
enforces [bounds, integrality and pack multiples](order_constraints.md). `calculate_eoq()` remains available for a numeric quantity.

## Dynamic lot sizing

Both dynamic methods receive `DLSInput` through `DynamicLotSizing`:

| Input | Symbol | Meaning and unit | Default / domain |
| --- | --- | --- | --- |
| `demand` | $d_t$ | Items needed in each equal-duration period | Required, non-empty list or tuple |
| `ordering_cost` | $K_t$ | Monetary units per positive order release | Required, non-negative scalar or full-horizon list |
| `holding_cost` | $h_t$ | Monetary units per item held at a period end | Required, non-negative scalar or full-horizon list |
| `initial_inventory` | $I_0$ | Stock available before period 1 | 0, non-negative |
| `lead_time` | $L$ | Whole periods between release and receipt | 0, non-negative integer |

Demand entries and all costs/stocks must be finite, non-negative real numbers.
Fractional quantities are accepted. All-zero demand and zero costs are valid.
An order released in period $t$ arrives before demand in period $t+L$.
Cost lists must have exactly one entry per demand period. There are no releases
before period 1 or pre-existing pipeline orders. Initial stock must cover the
first $L$ periods; otherwise `InfeasiblePlanError` is raised. No in-transit
holding cost is charged.

Initial stock is consumed against demands in chronological order. Remaining net
demands $d'_t$ are planned by the chosen method. Inputs are not modified.
The result then accounts for physical stock using the original demand:

$$I_t=I_{t-1}+r_t-d_t,\qquad r_t=q_{t-L}.$$

Here $q_t$ is a release and $r_t$ a receipt; releases outside the horizon are zero.

The full-horizon cost is:

$$C=\sum_{t=1}^{T}K_t\mathbf{1}_{q_t>0}+\sum_{t=1}^{T}h_t I_t.$$

Holding includes initial stock still present at period end and any stock left
at the end of the horizon. Initial-stock acquisition costs and salvage values
are not modeled. For example, demand `[10, 0]`, initial stock 15, and holding cost
1 require no orders but incur holding cost `5 + 5 = 10`.

`solve()` returns `DLSResult`: `order_quantities`, `order_periods`,
`receipt_quantities`, `receipt_periods`, `inventory_levels`, `total_cost`, and `costs`.
Order fields describe releases; receipt fields describe deliveries. Period labels are **one-based**;
list indices are zero-based. Inventory levels are period-end balances.

## Time and cost comparisons

Demand and holding costs must describe the same time period. EOQ result costs
cover one demand period; dynamic result costs cover the entire input horizon.
Use one consistent currency per scenario; the library does not convert units or currencies.

`CostBreakdown` contains `purchase`, `ordering`, `holding`, and `shortage`.
`relevant_cost` is ordering + holding + shortage; `total_cost` adds purchase cost.
EOQ totals include the unit acquisition-cost component. Dynamic purchase and
shortage components are zero because those costs are outside these models.
For discount EOQ, purchases vary with the selected price tier and must be
included when choosing a quantity.

For historical compatibility, `BackorderEOQ.calculate_cycle_metrics()["TotalCost"]`
means relevant cost, whereas `solve().total_cost` includes purchases.

EOQ `calculate_reorder_point(lead_time, safety_stock=0, days_of_operation=365)`
returns `demand_rate / days_of_operation * lead_time + safety_stock`.
Pass lead time explicitly, even if it was stored at construction. Its interpretation
is a reorder threshold for inventory position; the function does not track
on-hand stock, outstanding orders, or backlog over time.

`inventory_level(t, days_of_operation=365)` takes elapsed operating days.
Use the same number of operating days per demand period in both methods.
Profiles recalculate the optimum and return numeric values even when
`analysis_mode=True`. The default `graph()` displays a 365-day profile with
Plotly; `renderer="matplotlib"` selects Matplotlib.

See the [API reference](../API_REFERENCE.md) for further parameter and compatibility details.
