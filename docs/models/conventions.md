# Shared model conventions

[Model catalog](README.md) · [API reference](../API_REFERENCE.md)

This page defines common symbols, units, and cost accounting. Individual guides
state the additional assumptions that make their equations applicable.

## EOQ family

All four EOQ constructors use these inputs:

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
in demand periods. Quantity is continuous unless a future model explicitly
states otherwise. `calculate_eoq()` remains available for a numeric quantity.

## Dynamic lot sizing

Both dynamic methods receive `DLSInput` through `DynamicLotSizing`:

| Input | Symbol | Meaning and unit | Default / domain |
| --- | --- | --- | --- |
| `demand` | $d_t$ | Items needed in each equal-duration period | Required, non-empty list or tuple |
| `ordering_cost` | $K$ | Monetary units per positive order | Required, non-negative |
| `holding_cost` | $h$ | Monetary units per item held at a period end | Required, non-negative |
| `initial_inventory` | $I_0$ | Stock available before period 1 | 0, non-negative |

Demand entries and all costs/stocks must be finite, non-negative real numbers.
Fractional quantities are accepted. All-zero demand and zero costs are valid.
Orders are available before their period's demand is served.

Initial stock is consumed against demands in chronological order. Remaining net
demands $d'_t$ are planned by the chosen method. Inputs are not modified.
The result then accounts for physical stock using the original demand:

$$I_t=I_{t-1}+q_t-d_t.$$

The full-horizon cost is:

$$C=K\sum_{t=1}^{T}\mathbf{1}_{q_t>0}+h\sum_{t=1}^{T}I_t.$$

Holding includes initial stock still present at period end and any stock left
at the end of the horizon. Initial-stock acquisition costs and salvage values
are not modeled. For example, demand `[10, 0]`, initial stock 15, and holding cost
1 require no orders but incur holding cost `5 + 5 = 10`.

`solve()` returns `DLSResult`: `order_quantities`, `order_periods`,
`inventory_levels`, `total_cost`, and `costs`. Period labels are **one-based**;
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
