# IE Models Catalog maintenance guide

## Mission and onboarding

This is both an educational inventory-model catalog and a reusable Python library.
Keep model assumptions, worked examples, and independent validation aligned with
production behavior. Agent readiness adds a discoverable execution boundary to
that library, not a second implementation of its mathematics.

Read in order:

1. This file for ownership and change policy.
2. `USE_TOOL.md` in full before invoking or changing the agent adapter.
3. `SKILL.yaml` for its canonical machine-readable contract.
4. `registry/tool_registry.json` and `registry/model_registry.json` for discovery.
5. `standards/` and the relevant guide under `docs/models/` for affected work.

## Architecture

- `inventory_models.py`: BasicEOQ, EPQ, DiscountEOQ, IncrementalDiscountEOQ, BackorderEOQ and profiles.
- `dynamic_models.py`: Wagner–Whitin and Silver–Meal, initial-stock accounting.
- `model_common.py`: numeric validation and shared cost breakdowns.
- `ie_models_agent/`: strict JSON translation, installed module/console entrypoints,
  and packaged contract resources. Public Python entrypoint: `run(request)`.
- `SKILL.yaml`: canonical operation/model metadata, schemas, limits, and contract version.
- `scripts/sync_agent_metadata.py`: generates integration copies and checks drift.
- `tests/`: numerical, independent-optimality, API, and adapter contract tests.
- `docs/models/`: common model standard and individual learning/reference guides.

Core formulas and planning algorithms must remain in the library. The adapter
must use the public API, preserve structured errors, declare units/guarantees,
and avoid plots, arbitrary file access, or dynamic execution from request data.
Plotting imports belong inside `graph()` to avoid cache creation during agent calculations.

## Contract and registry ownership

Follow `standards/CONTRACTS.md`. `SKILL.yaml` uses JSON-compatible YAML 1.2 and is
parsed with the standard library. It is a tool contract, not a provider skill.
Do not manually edit derived registries, `ie_models_agent/contract.json`, or schemas.
Regenerate them with `python scripts/sync_agent_metadata.py`.
External agent-tools metadata is a separately maintained integration copy; never
change another repository as a side effect of local generation.

When a public operation changes, update its contract, procedure, examples,
applicable model/API documentation, and tests together. Contract version and
package version have separate responsibilities. Preserve existing Python APIs
unless a compatibility change is explicitly part of the work.

## Domain invariants

- Units, horizons, included cost components, and model assumptions must be explicit.
- Quantities are continuous unless a model explicitly adds integrality constraints.
- DiscountEOQ uses all-units pricing; IncrementalDiscountEOQ uses marginal bands and average acquisition price for holding. Discounts are nondecreasing; prices affect total cost.
- Backorders represent waiting demand, not lost sales.
- Dynamic plans must cover demand with non-negative period-end stock.
- Initial inventory participates in both demand coverage and actual holding costs.
- A heuristic cannot claim global optimality merely because it matches examples.
- Agent responses must remain finite JSON and must not silently convert units.

## Model documentation and code

Follow `docs/models/TEMPLATE.md` for new models/methods. Keep common definitions in
`docs/models/conventions.md`, link actual tests, and execute worked examples.
Document public inputs, outputs, defaults, units, side effects, and limitations.
Use comments to explain mathematical or architectural choices. Prefer narrow,
typed public interfaces and named results over positional data.

## Development and quality gates

Use the project virtual environment. The development target is Python 3.12;
CI checks Python 3.11 and 3.12. Package/dependency configuration lives in
`pyproject.toml`. Install development tools with `python -m pip install -e ".[dev]"`.

```bash
.venv/bin/python scripts/check_release.py
.venv/bin/python scripts/sync_agent_metadata.py --check
.venv/bin/python -m pytest tests/ -q
.venv/bin/ruff check .
.venv/bin/ruff format --check .
git diff --check
```

Single-file test example: `.venv/bin/python -m pytest tests/test_agent_tool.py -q`.
For packaging changes, build wheel and source distribution and verify the installed
agent from outside the checkout, including bundled schemas and metadata.

Tests must cover meaningful independent numerical checks, strict invalid/boundary
requests, schema/dispatch/registry agreement, examples, exit codes, and clean JSON
stdout. Avoid tests that only duplicate a solver formula. Use existing pytest
infrastructure. Add dependencies only for a concrete benefit; keep provider SDKs
and orchestration frameworks out of the computation core.

## Change completion

Preserve existing user changes. Update the relevant model guide for domain changes,
agent contract documents for adapter changes, and generated metadata for discovery
changes. Run affected checks and required gates. State any unverified integration
or release limitation. Publication, external registry updates, and future stochastic/
capacity model work are separate tasks from maintaining this local capability.
