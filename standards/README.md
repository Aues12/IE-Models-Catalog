# Agent integration standards

[Architecture overview](../docs/ARCHITECTURE_OVERVIEW.md) · [Maintenance guide](../AGENTS.md) · [Calling procedure](../USE_TOOL.md)

This is the **Modify** path: detailed rules for changing the repository.
For conceptual orientation, return to the shared overview; for an existing tool
call, use the calling procedure.

These local standards adapt the capability/interface separation of `agent-tools`
and the library-first adapter pattern used by `BookBarcode`. This repository is
an inventory library, so semantic graph schemas, barcode rules, runtime planners,
and unrelated memory/skill registries are outside its scope.

- [Architecture and ownership](ARCHITECTURE.md)
- [Contract and registry management](CONTRACTS.md)
- [Adaptation decision](ADAPTATION.md)

Model admission requirements remain in the [model catalog](../docs/models/README.md).
