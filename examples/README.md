# Method comparison and sensitivity examples

[Back to the project README](../README.md)

These examples use synthetic, deterministic inputs to explain the implemented
models. They run the public `solve()` and `calculate_costs()` APIs and generate
reproducible reports; they do not use external datasets or estimate demand uncertainty.

## Run the examples

From the repository root, with the package installed and your virtual environment active:

```bash
python -m examples.compare_methods
python -m examples.eoq_sensitivity
```

No extra dependencies are required beyond the library's runtime dependencies.
Each command prints a short summary and writes an interactive Plotly HTML report
and the underlying numeric results as JSON to `examples/output/`.

| Example | Report | Numeric results |
| --- | --- | --- |
| Method comparison | `method_comparison.html` | `method_comparison.json` |
| EOQ sensitivity | `eoq_sensitivity.html` | `eoq_sensitivity.json` |

Open the HTML files in a browser. Hover to inspect values, click a legend entry
to hide/show a series, and use the toolbar to zoom or save a plot image. Plotly is
embedded in each HTML file, so viewing does not require an internet connection.
The commands do not open a browser automatically.

To choose another destination:

```bash
python -m examples.compare_methods --output-dir /tmp/inventory-examples
python -m examples.eoq_sensitivity --output-dir /tmp/inventory-examples
```

Rerunning a command replaces that example's HTML and JSON files in the selected
directory. The default output directory is ignored by Git; the scripts and this
guide are the reproducible source. The examples run from a repository checkout
and are not included as commands in the installed wheel.

## 1. Compare Wagner–Whitin and Silver–Meal

[Source: compare_methods.py](compare_methods.py)

For each scenario, both methods receive exactly the same demand, starting stock,
setup cost, and holding cost. Each order costs 100 and each unit remaining at the
end of a period costs 1 to hold. Purchase costs are not modeled.

| Scenario | Demand | Initial stock | Wagner–Whitin | Silver–Meal | Silver–Meal cost gap |
| --- | --- | --- | --- | --- | --- |
| Small example | `[10, 20, 30]` | 0 | 180 | 180 | 0% |
| Growing demand | `[10, 20, 30, 40, 50, 60]` | 0 | 420 | 430 | 2.38% |
| Intermittent demand + initial stock | `[15, 0, 60, 10, 0, 80]` | 35 | 250 | 250 | 0% |

The growing-demand example shows why order timing matters even when the number
of orders is the same:

- Wagner–Whitin orders `[30, 0, 70, 0, 110, 0]`: three orders cost 300 and holding costs 120.
- Silver–Meal orders `[60, 0, 0, 90, 0, 60]`: three orders cost 300 and holding costs 130.

The relative gap is `(method cost − optimal cost) / optimal cost × 100`.
Wagner–Whitin supplies the optimal cost for these uncapacitated scenarios.
A zero reference cost produces `null` in JSON and `N/A` in the summary, since a
percentage relative to zero is undefined; the absolute `cost_gap` remains available.

The report shows each method's orders alongside demand, plus end-of-period
inventory. Lines connect period-end observations; they are not a continuous
within-period inventory simulation. Initial inventory is consumed before new
orders cover unmet demand, and any stock carried from one period to the next is
included in holding cost.

Compare methods **within a scenario**. The scenarios have different demands and
horizons, so their raw total costs do not rank their efficiency. Agreement on
these examples does not guarantee that Silver–Meal is optimal on other inputs.
This is a cost/plan comparison, not a runtime benchmark.

To explore a different demand pattern, edit `SCENARIOS` in the script and rerun.
Keep three scenarios for the provided report layout.

## 2. Explore EOQ sensitivity

[Source: eoq_sensitivity.py](eoq_sensitivity.py)

The baseline is a unit price of 50, annual demand of 1,200, cost per order of 75,
and annual holding rate of 20%. The optimum is **134.16 units**, with annual
ordering plus holding cost of **1,341.64**.

The example changes one of three inputs at a time from **0.5× to 2×** its baseline
value, in 31 steps (93 scenarios total). All other inputs stay fixed. Holding
rate changes from 10% to 40%; 2× means doubling the rate, not adding two percentage points.

For every scenario, the example:

1. Recalculates the optimal quantity for the changed input.
2. Evaluates the original 134.16-unit policy under the **same changed input**.
3. Reports its extra ordering and holding cost relative to the new optimum.

| Changed input | Multiplier | New optimal quantity | Extra cost of original quantity |
| --- | --- | --- | --- |
| Annual demand | 0.5× | 94.87 | 6.07% |
| Annual demand | 2× | 189.74 | 6.07% |
| Ordering cost | 0.5× | 94.87 | 6.07% |
| Ordering cost | 2× | 189.74 | 6.07% |
| Holding rate | 0.5× | 189.74 | 6.07% |
| Holding rate | 2× | 94.87 | 6.07% |

Higher demand or ordering cost increases the optimal order quantity; a higher
holding rate decreases it. The relationship follows a square root, so doubling
an input does not double the optimum. The modest cost penalty illustrates that
the basic EOQ cost curve is relatively flat near its minimum.

The first chart normalizes quantities by the baseline optimum. Demand and
ordering-cost curves overlap. All three percentage cost-penalty curves in the
second chart overlap: under basic EOQ, changing any one of these inputs by a
factor `m` gives an old-policy cost ratio of `(sqrt(m) + 1/sqrt(m)) / 2`.
Toggle series with the legend to inspect them separately.

Cost percentages exclude purchases, which do not change with order quantity
within a basic EOQ scenario. This keeps the policy penalty from being obscured
by acquisition spending. The comparison is between two policies for the changed
scenario, not between costs before and after the input change.

To explore another baseline, edit `BASELINE`. This example assumes continuous
order quantities, constant demand, and no capacity, pack-size, or service-level
constraints. It is a deterministic sensitivity exercise, not a forecast or a
probability-based risk analysis.

See the [API reference](../docs/API_REFERENCE.md) for result fields and cost conventions.
