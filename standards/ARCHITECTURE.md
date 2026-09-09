# Architecture and ownership

One implementation serves humans and agents:

```text
Python users / examples ──────────────┐
                                     v
JSON CLI → adapter validation → inventory_models / dynamic_models
             ↑                       ↓
       bundled schemas         model_common costs
                                     ↓
                         adapter JSON serialization
```

- `inventory_models.py` owns static formulas, inventory profiles, and optional plots.
- `dynamic_models.py` owns demand netting, planning, and period cost accounting.
- `model_common.py` owns shared numeric validation and cost records.
- `inventory_agent.py` is a checkout-only script wrapper for agent-tools runtimes.
- `ie_models_agent/tool.py` owns JSON validation, model dispatch, tier translation,
  serialization, result labels, and the single-request process boundary.
- `SKILL.yaml` owns interfaces, operations, supported models, schemas, limits,
  side-effect declarations, and the independent adapter contract version.
- `scripts/sync_agent_metadata.py` owns derivation of local integration copies.

Adapters must call the public library API; they must not copy EOQ formulas or DP
recurrences. Core modules must not import the adapter, manifest, JSON Schema
validator, or a provider-specific runtime. Plot imports stay inside `graph()`.
The new `jsonschema` dependency enforces Draft 2020-12 contracts at the adapter
boundary; it is not a new optimization engine and does not change model mathematics.

Request metadata has no authority to select Python classes, file paths, or
commands. Dispatch is an explicit allowlist. No dynamic imports from input,
evaluation of expressions, or generic file/plot operations are exposed.

Cost horizons and model guarantees belong in responses. A transport success is
not a proof that a model fits the caller's business context. Preserve the distinction
between exact mathematical models, heuristics, and implementation bounds.
