# Contract and registry management

[Architecture overview](../docs/ARCHITECTURE_OVERVIEW.md) · [Calling procedure](../USE_TOOL.md) · [Maintenance guide](../AGENTS.md)

This page governs interface and discovery changes. To invoke an existing operation,
use the calling procedure; synchronization is a maintainer responsibility.
Introductory documents summarize and link these rules without redefining them.

## Sources of truth

| Concern | Canonical source | Derived / consuming surface |
| --- | --- | --- |
| Mathematical behavior | Library code, model guides, independent tests | Adapter results |
| Agent operations and schemas | Root `SKILL.yaml` | Packaged `contract.json`, request/response JSON Schemas |
| Tool and model discovery | Root `SKILL.yaml` | `registry/tool_registry.json`, `registry/model_registry.json` |
| Calling procedure | `USE_TOOL.md` | Examples and caller workflows |
| Maintenance policy | `AGENTS.md`, these standards | Reviews and CI |
| Package version | `pyproject.toml` | Distribution metadata |

`SKILL.yaml` is serialized in the JSON subset of YAML 1.2. Keep it parseable with
`json.loads`; this is an intentional local format convention. It is a tool
manifest, not an installed Codex skill. Its parameter/return definitions use
JSON Schema Draft 2020-12, not agent-tools-specific pseudo-types.

Schema checks validate structure. Cross-field invariants such as production rate
above demand, nondecreasing discounts, and finite numerical results are also
validated by the adapter/library. Schema defaults are annotations and do not mutate
caller input; the adapter applies defaults explicitly.

## Synchronization

Run `python scripts/sync_agent_metadata.py` after a manifest change and commit all
resulting files together. `--check` compares the expected artifacts byte for byte,
returns nonzero on drift, and writes nothing. CI runs this check along with tests
that verify dispatch, schema validity, registry links, example execution, and packaging.
There is no wall-clock timestamp or absolute local path in generated metadata.

The generated tool registry has the `version`/`tools` discovery shape used by
agent-tools. It is local to this repository. External integrations must remap
checkout paths and review their metadata separately. Never overwrite an external
registry as a side effect of synchronization here.

## Change classification

- **Model change:** update its guide, meaningful independent tests, and API docs.
- **Adapter change:** update manifest, procedure, request examples, and envelope tests.
- **Discovery change:** regenerate metadata and check every guide/entrypoint path.
- **Packaging change:** build wheel and source archive and run the installed adapter
  outside the checkout, checking bundled schemas and metadata.

Contract version 1 defines the initial agent surface; it is independent of the
package version. Adding required parameters, removing fields, changing units,
defaults, error meanings, or guarantees is a breaking contract change. Increment
the contract version and document migration when compatibility cannot be retained.
For additive optional behavior, retain compatible operation semantics and update
all generated contracts/tests. Decide the package release version in release work;
do not derive it from historical changelog headings.

## Required gates

```bash
python scripts/sync_agent_metadata.py --check
python -m pytest tests/ -q
ruff check .
ruff format --check .
git diff --check
python -m build
```

A change is complete when examples execute, intended behavior is tested, schema
and registry checks pass, affected documentation agrees, and packaging changes
work outside the source tree. Schema compliance alone is not numerical correctness.
