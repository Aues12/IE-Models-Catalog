# Development guide

[Back to the README](../README.md)

The development target is Python 3.12. Continuous integration tests Python 3.11
and 3.12. Clone the repository and activate a virtual environment using the
[installation instructions](../README.md#installation) before running these commands.

## Development environment

For local development, including tests, builds, and Ruff, install the `dev` extra:

```bash
pip install -e ".[dev]"
```

Run the full test suite with:

```bash
.venv/bin/python -m pytest tests/ -v
```

## Code quality with Ruff

Ruff is the project's linter and formatter. It is installed through the `dev` extra.

Check for lint issues and formatting changes without modifying files:

```bash
ruff check .
ruff format --check .
```

Apply Ruff's safe automatic fixes and format the code:

```bash
ruff check . --fix
ruff format .
```

The configuration in [`pyproject.toml`](../pyproject.toml) targets Python 3.11 syntax and checks import order plus core error and undefined-name rules. GitHub Actions runs the non-modifying commands on every relevant push and pull request.

## Build the package

```bash
python -m build
```

Distributions are written to `dist/`. Package metadata, runtime dependencies,
and development dependencies are defined in [pyproject.toml](../pyproject.toml).
The installed modules are `inventory_models`, `dynamic_models`, and `model_common`.

## Verification strategy

The suite includes model regressions, shared result-contract checks, and
independent optimality checks against exhaustive small planning problems.
See the [testing strategy](../tests/TESTING_STRATEGY.md) for details.

The [CI workflow](../.github/workflows/python-tests.yml) runs lint and formatting
checks, tests both supported Python versions, builds the package, and checks
imports from the installed wheel. It is triggered by pushes and pull requests
targeting `core`, and version-tag pushes.

## Contribution policy

Bug reports and documentation feedback are welcome. External pull requests are
currently not accepted; see [CONTRIBUTING.md](../CONTRIBUTING.md).

## Agent contracts

Run `python scripts/sync_agent_metadata.py --check` to detect contract/registry drift.
After changing `SKILL.yaml`, regenerate with `python scripts/sync_agent_metadata.py`.
The pytest suite includes adapter, subprocess, schema, and registry checks.
See [contract management](../standards/CONTRACTS.md) for the full change workflow.

## Versioning

Run `python scripts/check_release.py` to verify package/changelog agreement.
For annotated release-tag checks and the SemVer policy, see [releasing](RELEASING.md).
