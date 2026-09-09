# Using IE Models Catalog as an agent tool

This guide describes invocation and result interpretation. Read it before using
or changing the JSON adapter. [SKILL.yaml](SKILL.yaml) is the canonical local
machine-readable contract; [AGENTS.md](AGENTS.md) governs maintenance.

## Discover and invoke

Install the package in a virtual environment with `python -m pip install .`.
The Python API, module entrypoint, and console command use the same adapter:

```bash
python -m ie_models_agent < examples/agent/list_models.json
ie-models-agent < examples/agent/solve_eoq.json
```

```python
from ie_models_agent import run

response = run({"operation": "list_models", "params": {}})
assert response["success"]
```

The module and console entrypoints work from a checkout or an installed wheel.
For agent-tools runtimes that invoke a script path, the checkout also provides
`python inventory_agent.py < examples/agent/list_models.json`. The wheel includes
its contract and schemas; it does not require a neighboring agent-tools checkout.
Examples, standards, and the model guides are source documentation. Use the
[source registry](registry/tool_registry.json) to discover the tool and
[model registry](registry/model_registry.json) for model-to-guide mappings.
`list_models` returns the same model descriptions and execution limits at runtime.

## Request and response

Send **one UTF-8 JSON object** on stdin, then close stdin. This is a single-request
process, not a JSON-lines server. The root keys are `operation`, `params`, and an
optional object `meta`. Both `operation` and `params` are required. Caller metadata
is not echoed or used to select an operation. Unexpected keys are rejected.

```json
{
  "operation": "solve_eoq",
  "params": {
    "model": "basic_eoq",
    "inputs": {"price": 50, "demand_rate": 1200, "ordering_cost": 75, "holding_rate": 0.2}
  }
}
```

Success has `success: true`, a short `message`, an operation-specific `result`,
and `meta` with `operation` and `contract_version: 1`. Failure has `success: false`,
`message`, and `error` containing `code`, `type`, and `message`. Stdout contains
exactly one JSON envelope; no explanation mode, chart, or debug output is mixed in.
Do not parse human-readable messages for control flow: use `success` and `error.code`.

| Exit | Meaning | Error code |
| ---: | --- | --- |
| 0 | Operation completed | None |
| 1 | Request validation failed or no feasible plan exists | `INVALID_REQUEST` / `INFEASIBLE_PLAN` |
| 2 | Empty/oversized input, invalid UTF-8/JSON, duplicate keys, or NaN/Infinity literals | `INVALID_JSON` |
| 3 | Numerical range or unexpected execution failure | `NUMERICAL_ERROR` / `EXECUTION_ERROR` |

Direct `run()` calls return envelopes and do not exit. Raw JSON parsing errors
only apply to the CLI. Exponent overflow such as `1e400` is rejected during
finite-value validation. Unexpected execution errors omit tracebacks and input data.

## Operations

| Operation | Required params | Optional params |
| --- | --- | --- |
| `list_models` | Empty object | None |
| `solve_eoq` | `model`, `inputs` | `constraints` |
| `evaluate_eoq` | `model`, `inputs`, `quantity` | None |
| `reorder_point` | `model`, `inputs`, `lead_time` | `safety_stock=0`, `days_of_operation=365` |
| `inventory_profile` | `model`, `inputs`, `times` | `days_of_operation=365`, `constraints` |
| `solve_dynamic` | `demand`, `ordering_cost`, `holding_cost` | `initial_inventory=0`, `lead_time=0`, `period_unit="period"`, `method="wagner-whitin"` |
| `compare_dynamic` | `demand`, `ordering_cost`, `holding_cost` | `initial_inventory=0`, `lead_time=0`, `period_unit="period"` |

EOQ model IDs are `basic_eoq`, `epq`, `discount_eoq`, `incremental_discount_eoq`, and `backorder_eoq`.
Their `inputs` require positive `price`, `demand_rate`, and `ordering_cost`, with
optional `holding_rate=0.25`. EPQ also requires `production_rate > demand_rate`;
backorder EOQ requires positive `shortage_cost`.

Both discount variants require `discount_tiers`, an array of objects:

```json
[
  {"minimum_quantity": 0, "discount_rate": 0},
  {"minimum_quantity": 100, "discount_rate": 0.05},
  {"minimum_quantity": 200, "discount_rate": 0.10}
]
```

The adapter translates this to the library's numeric-keyed `discount_rates`
mapping. Thresholds must be unique, finite and non-negative. Rates are in `[0,1)`
and must not decrease with quantity. This avoids ambiguous JSON numeric object
keys; do not send the Python mapping through this transport.

All numeric inputs must be finite; booleans are not numbers. `times` is a
non-empty array of non-negative operating days. A profile contains net inventory,
which can be negative for backorder EOQ. Only documented model inputs are
accepted; constructor `lead_time` is replaced by the explicit operation parameter.

Dynamic demand is a non-empty array of non-negative quantities. Costs and initial
stock may be zero. `period_unit` is one of `day`, `week`, `month`, `year`, `period`.
It labels the input periods and performs no conversion. `method` is either
`wagner-whitin` or `silver-meal`.

Optional `constraints` on `solve_eoq` and `inventory_profile` accepts
`min_quantity` (default 0), `max_quantity` (default null), `integer` (default false),
and `order_multiple` (default null, otherwise a positive integer). Bounds are
inclusive; a pack multiple implies whole items. `solve_eoq` echoes normalized
constraints when supplied. `evaluate_eoq` evaluates any positive supplied quantity
without checking such constraints. See [constraint semantics](docs/models/order_constraints.md).

`discount_eoq` prices the entire lot at the selected tier. `incremental_discount_eoq`
prices only units within each band and values holding at average acquisition price;
its `unit_price` is that average, not the last band's price.

Dynamic costs may be scalars or arrays of exactly the demand horizon's length.
`lead_time` is a non-negative integer in input periods. Setup is charged at release,
holding on actual period-end stock. Initial inventory must cover demand until the
first possible receipt; pre-horizon and pipeline orders are not supported.

## Result interpretation

- `solve_eoq`: quantity, unit price, cycle time, stock/backlog maxima, costs,
  `total_cost`, `model`, `guarantee`, and `cost_basis`.
- `evaluate_eoq`: supplied quantity and its costs, not a new optimum. Backorder
  cost evaluation uses the library's optimal backlog split for that quantity.
- `reorder_point`: threshold in items, lead time in operating days, and operating days/year.
- `inventory_profile`: times and corresponding net inventory arrays, with units.
- `solve_dynamic`: release `order_quantities`/`order_periods`, delivery
  `receipt_quantities`/`receipt_periods` (periods are one-based), period-end stock,
  costs, method, guarantee, and cost basis.
- `compare_dynamic`: two complete plans, the Wagner–Whitin reference, absolute
  cost gap, and relative gap percentage. Relative gap is `null` if reference cost
  is zero; inspect the absolute gap instead.

The EOQ adapter uses **annual demand and holding/shortage rates**, annual cost,
and cycle time in years. Unlike the more general Python API, this transport
fixes that convention so an agent can interpret results unambiguously.
`days_of_operation` changes the conversion to operating days, not the cost horizon.

Costs contain purchase, ordering, holding, shortage, relevant cost, and total cost.
EOQ total cost includes purchases. Dynamic totals cover the supplied horizon and
include ordering plus actual period-end holding, including remaining initial stock.
The `currency` label is `caller_defined`; no currency conversion occurs.

`success` means computation completed, not that the user's real-world assumptions
are correct. `exact_under_assumptions` applies only to the documented model;
`heuristic` carries no optimality guarantee. Follow the linked [model guides](docs/models/README.md).

## Bounds and side effects

Requests are limited to 1 MiB, dynamic horizons to 120 periods, profiles to 1,000
points, and discount schedules to 256 tiers. Limits are adapter-specific; the
Python API has no such request-size limits. The dynamic bound limits the quadratic
cost-matrix allocation. Runtimes may impose additional time/memory limits.

The adapter does not read caller files, write artifacts, launch processes, use
network services, or open plots. It reads bundled contract resources and imports
library modules. Python itself may write bytecode caches unless disabled.
Plotting libraries are loaded only when the library's separate `graph()` is used.
For report generation, use the explicit [examples](examples/README.md).

## Recovery and maintenance

For `INFEASIBLE_PLAN`, review bounds/pack compatibility or the stock needed before
the first receipt; do not silently relax constraints. For `INVALID_REQUEST`, inspect the operation's schema and model assumptions before
retrying; do not silently change units or round quantities. For `NUMERICAL_ERROR`,
inspect input scale and arithmetic range. For `EXECUTION_ERROR`, report a minimal
reproducer instead of repeatedly retrying unchanged input.

Machine schemas are in [ie_models_agent/schemas](ie_models_agent/schemas).
Defaults are annotations and are applied explicitly by the adapter, not injected
by the JSON Schema validator. The full manifest is JSON-compatible YAML 1.2,
allowing standard-library parsing without adding a YAML runtime dependency.

After changing the canonical manifest:

```bash
python scripts/sync_agent_metadata.py
python scripts/sync_agent_metadata.py --check
python -m pytest tests/ -q
```

Generated registries, packaged contract, and schemas must not be edited manually.
See [standards](standards/README.md) for ownership and compatibility rules.
An external agent-tools registry is a separately reviewed integration copy;
this repository never writes to it automatically.
