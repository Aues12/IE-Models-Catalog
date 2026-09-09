# Decision: make inventory models discoverable agent capabilities

## Context

The library is both a learning catalog and a reusable decision component. The
agent-tools repository demonstrates bounded capabilities, separate interfaces and
operations, JSON envelopes, discoverable registries, and explicit side effects.
BookBarcode demonstrates keeping algorithms in a reusable library and placing a
thin JSON adapter above it.

## Adopted

- A canonical `SKILL.yaml`, procedural `USE_TOOL.md`, and maintenance `AGENTS.md`.
- Distinct interface and operation records, a `run(request)` Python boundary,
  and a one-request JSON stdin/stdout process.
- Local registry copies and explicit side-effect declarations.
- Library-owned algorithms, strict adapter validation, examples and contract tests.

## Local choices

The seven initial operations cover discovery, EOQ optimization/costs/thresholds/
profiles, and dynamic solving/comparison. All are computational: plotting and
artifact generation remain separate examples. The adapter is included in the
wheel with its schemas and discovery metadata, and also provides a console script.
This is deliberately broader installation support than the checkout-only JSON
adapter described in BookBarcode's `USE_TOOL.md`.

Root `SKILL.yaml` is canonical; checked-in copies are generated for runtime and
registry consumption. JSON-compatible YAML avoids a second manifest parser.
A maintained JSON Schema validator was chosen over a custom partial validator;
this adds `jsonschema` as a runtime dependency, used only by the adapter.

The transport uses annual EOQ inputs and explicit cost-basis fields. Discount
tiers are arrays rather than JSON objects with numeric-looking keys. Bounded
requests avoid unbounded cubic dynamic-planning work. No mathematical solver is
added, and the pre-existing Python call signatures stay available.

## Not adopted

Semantic pipeline schemas, barcode-specific validation/atomic writers, planners,
provider-specific plugins, and empty skill/memory directories would not serve the
current inventory scope. No external registry or reference repository is modified.

## References inspected

- `agent-tools`: `AGENTS.md`, `USE_TOOL.md`, `standards/TOOL_SPEC.md`,
  `standards/INTERFACE_SPEC.md`, `standards/SCHEMA_SPEC.md`,
  `standards/AGENT_SPEC.md`, `registry/tool_registry.json`.
- `BookBarcode`: `AGENTS.md`, full `USE_TOOL.md`, `SKILL.yaml`, `tool.py`,
  `isbn_barcode.py`, and package metadata.

These are design references, not runtime dependencies. Local contracts take
precedence for this adapter; external standards are not copied wholesale.
