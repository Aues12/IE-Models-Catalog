# Architecture and ownership

[Shared architecture overview](../docs/ARCHITECTURE_OVERVIEW.md) · [Maintenance guide](../AGENTS.md) · [Contract rules](CONTRACTS.md)

This is the maintenance reference for architectural boundaries. Start with the
shared overview for purpose and concepts; use this page when deciding where a
change belongs. One mathematical implementation serves both humans and agents.

## Responsibility and dependency boundaries

| Layer | Responsibility | Implementation |
| --- | --- | --- |
| Static mathematical models | EOQ formulas, saved policy results, profiles and optional plots | `inventory_models.py` |
| Dynamic mathematical models | Demand netting, planning, result records and period cost accounting | `dynamic_models.py` |
| Shared domain structures | Numeric validation, constraints and cost records | `model_common.py` |
| Public library entrypoint | Re-export existing public classes without copying formulas | `ie_models_catalog/__init__.py` |
| Agent boundary | JSON validation, allowlisted dispatch, tier translation, serialization, result labels and single-request execution | `ie_models_agent/tool.py` |
| Checkout invocation wrapper | Script entrypoint for agent-tools runtimes | `inventory_agent.py` |
| Canonical machine interface | Interfaces, operations, models, schemas, limits, side effects and adapter contract version | `SKILL.yaml` |
| Derived integration artifacts | Generate schema and registry copies from the canonical contract | `scripts/sync_agent_metadata.py`; ownership rules in [CONTRACTS.md](CONTRACTS.md) |

Adapters must call the public library API; they must not copy EOQ formulas or DP
recurrences. Core modules must not import the adapter, manifest, JSON Schema
validator, or a provider-specific runtime. Plot imports stay inside `graph()`.
The `jsonschema` dependency enforces Draft 2020-12 contracts at the adapter
boundary; it is not a new optimization engine and does not change model mathematics.

## Request boundary

Request metadata has no authority to select Python classes, file paths, or
commands. Dispatch is an explicit allowlist. No dynamic imports from input,
evaluation of expressions, or generic file/plot operations are exposed.

Cost horizons and model guarantees belong in responses. A transport success is
not a proof that a model fits the caller's business context. Preserve the distinction
between exact mathematical models, heuristics, and implementation bounds.
