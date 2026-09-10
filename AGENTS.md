# IE Models Catalog maintenance guide

## Mission and onboarding

This is both an educational inventory-model catalog and a reusable Python library.
Keep model assumptions, worked examples, and independent validation aligned with
production behavior. Agent readiness adds a discoverable execution boundary to
that library, not a second implementation of its mathematics.

## Establish meaning, then select task context

First read the shared [architecture overview](docs/ARCHITECTURE_OVERVIEW.md):
purpose, model families, library/adapter relationship and the distinction between
schema validity and mathematical correctness. Humans and agents use the same
conceptual model. This overview provides orientation; this guide and the standards
remain authoritative for maintenance.

Then classify the task and load the additional context below. Do not replace
repository understanding with an isolated file-level instruction.

| Task | Additional context |
| --- | --- |
| Model or mathematical change | Relevant implementation, [model guide](docs/models/README.md), [shared conventions](docs/models/conventions.md), independent numerical tests |
| Public Python API change | [API contract](docs/API_CONTRACT.md), affected models and public API/compatibility tests |
| Agent call or adapter change | Read [USE_TOOL.md](USE_TOOL.md) in full before invoking or changing the adapter; relevant operations in [SKILL.yaml](SKILL.yaml), adapter implementation and tests |
| Contract/interface change | [Contract rules](standards/CONTRACTS.md), canonical manifest, generator and schema/dispatch tests |
| Discovery metadata change | [Registry ownership and synchronization](standards/CONTRACTS.md#synchronization), generator and relevant generated registry |
| Release/package change | [Release guide](docs/RELEASING.md), pyproject.toml, release checks and installed-package verification |
| Documentation change | Reader-intent paths in [README](README.md#find-your-path), overview, and the affected authoritative references |

Keep meaning context stable; replace task context as the work changes. If a local
choice raises architectural uncertainty, return to the overview and
[architecture rules](standards/ARCHITECTURE.md), reinterpret the task, then continue.
Read additional rows when a change crosses responsibilities.

## Architectural constraints

The library owns mathematics; the adapter calls its public API. Preserve this
separation, declared units/guarantees, and bounded execution. Detailed ownership,
dependency and request-boundary rules are in [standards/ARCHITECTURE.md](standards/ARCHITECTURE.md).
Public Python behavior and compatibility are defined in [docs/API_CONTRACT.md](docs/API_CONTRACT.md).

## Contract and registry ownership

[SKILL.yaml](SKILL.yaml) is the canonical machine-readable contract. Follow
[standards/CONTRACTS.md](standards/CONTRACTS.md) for its format, ownership and maintenance rules.
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
