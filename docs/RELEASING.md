# Versioning and releases

[Development](DEVELOPMENT.md) · [Changelog](../CHANGELOG.md) · [API](API_REFERENCE.md)

The package follows [Semantic Versioning 2.0.0](https://semver.org/).
`pyproject.toml` is the single source of the distribution version; installed users
can read it with `importlib.metadata.version("ie-models-catalog")`.
The agent's `contract_version` is a separate transport compatibility number.

## Version policy

During 0.x development, use a minor increment for new capabilities or incompatible
API changes, and a patch increment for compatible corrections. Document breaking
changes and migration explicitly; keep patch releases compatible. At 1.0, the
public API becomes stable: incompatible changes increment major, compatible
features increment minor, and compatible fixes increment patch.

The public surface comprises the documented model constructors, calculation and
profile methods, result fields, cost/time semantics, plus the agent operations,
envelopes and CLI exit codes. Underscore-prefixed helpers and internal metadata
generation details are not public API. Existing legacy overloads remain supported;
see [API compatibility](API_REFERENCE.md#compatibility-and-preferred-entrypoints).

The current release tooling intentionally accepts stable `X.Y.Z` versions only.
Prerelease support needs an explicit extension covering both SemVer and Python
package version normalization before a prerelease is issued.

## Historical reconciliation

Before this release, package metadata still said 0.1.0 while the changelog recorded
retrospective milestones through 0.4.1. Neither local nor remote tags existed at
the September 9, 2026 audit. Version 0.5.0 aligns the current package with that
history and includes the subsequent model, documentation and agent additions.
Historical entries remain labeled retrospective; do not invent release tags for them.

## Release procedure

1. Put ongoing changes under `Unreleased`. At release time choose the next version,
   update `pyproject.toml`, and move the notes into `## [X.Y.Z] - YYYY-MM-DD`.
   Leave an empty `Unreleased` section at the top.
2. Run the quality gates below and review the diff. Build into an empty output
   directory; install the wheel in a separate environment and test outside the checkout.
3. Commit the release changes. Create an annotated local tag with
   `git tag -a vX.Y.Z -m "Release X.Y.Z"`; never move an existing released tag.
4. Run `python scripts/check_release.py --tag vX.Y.Z` to check the annotated tag,
   HEAD, package version and changelog agreement.
5. Push the reviewed branch and exact tag when publication is intended. Tag CI
   repeats metadata, lint, tests and installed-wheel checks. It does not publish
   to PyPI or create a GitHub Release automatically.

```bash
python scripts/check_release.py
python scripts/sync_agent_metadata.py --check
python -m pytest tests/ -q
ruff check .
ruff format --check .
git diff --check
python -m build
```

Normal branch checks allow pending `Unreleased` notes. Tag checks require those
notes to be incorporated into the release. The checker verifies existing local
tags; it never creates tags, fetches from GitHub or publishes artifacts.
