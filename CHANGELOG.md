# Changelog

All notable changes to this project are documented here.

The project did not historically use release tags. Versions through `0.4.1` were assigned retrospectively from Git history when Semantic Versioning was adopted; their dates mark the end of each development milestone rather than an original tagged release.

## Unreleased

## [0.5.0] - 2026-09-09

### API compatibility

* Standardized `calculate_total_cost(quantity)` across all EOQ variants; the discount models retain the legacy explicit-price overload.
* Added constraints and operating-day selection to `graph()`, and constraints to backorder cycle metrics. Unknown renderers now raise `ValueError`.
* Preserved legacy backorder `TotalCost` as relevant cost; `solve().total_cost` includes purchases.

### Release management

* Reconciled package metadata with the historical changelog at 0.5.0; earlier changelog versions remain retrospective, untagged milestones.
* Added automated package/changelog/tag agreement checks and a documented SemVer policy.


### Added

* Added shared EOQ results and cost breakdowns, independent optimality checks, model guides, method comparisons and sensitivity examples.
* Added optional EOQ minimum/maximum quantities, integer orders and pack multiples across all five variants.
* Added IncrementalDiscountEOQ with marginal-band billing and average-acquisition-price holding.
* Added period-varying dynamic costs, fixed lead time, explicit release/receipt results, and infeasible-plan errors.
* Added operational model guides, runnable comparisons, exhaustive release-schedule and independent lot-billing checks.

* Added the version-1 JSON agent interface with discovery, EOQ calculations, and dynamic solving/comparison, available as `python -m ie_models_agent` and `ie-models-agent`.
* Added a canonical `SKILL.yaml`, generated tool/model registries and JSON schemas, an invocation guide, and local architecture/contract standards.
* Added strict request/response validation with `jsonschema`, bounded inputs, structured errors, executable request examples, and contract/registry drift checks in CI.
* Included agent metadata and schemas in the wheel and the integration documentation in source distributions.


### Changed

* Reduced Wagner–Whitin cost-matrix preparation to quadratic time and Silver–Meal cost accumulation to linear time.

* Expanded continuous integration to test Python 3.11 and 3.12.
* Added Ruff linting, formatting, and continuous-integration checks.
* Added an English Wagner–Whitin walkthrough and retained the Turkish original with a `_TR` suffix.
* Added package build metadata while preserving the existing `inventory_models` and `dynamic_models` imports.

## [0.4.1] - 2026-08-29

### Fixed

* Ensured `DiscountEOQ` always evaluates the undiscounted base-price tier, even when callers omit the `0` quantity break.
* Avoided mutating the `discount_rates` mapping supplied by callers.
* Added a regression test for a discount threshold that is too high to be economical.
* Made both dynamic lot-sizing methods skip leading and all-zero demand periods without creating a zero-quantity order or charging an unnecessary setup cost.
* Made `EPQ`, `DiscountEOQ`, and `BackorderEOQ` retain their calculated order quantity consistently with `BasicEOQ`.

### Documentation

* Refreshed the README with the current inventory-model scope, dynamic lot-sizing API, validation rules, examples, and test command.

## [0.4.0] - 2026-06-30

### Documentation

* Added notes for the dynamic inventory models.

### Added (2026-04-27 to 2026-04-30)

* Added `DynamicLotSizing`, `DLSInput`, and `DLSResult` for time-phased demand planning.
* Added the exact Wagner–Whitin solver and the Silver–Meal heuristic.
* Added dynamic lot-sizing tests and mathematical walkthroughs.
* Added EOQ model and mathematical documentation, plus the original project proposal.

### Changed

* Added explicit `method` selection to the dynamic lot-sizing solver.
* Updated README, requirements, and testing documentation for the dynamic-model scope.

## [0.3.0] - 2026-03-06

_Changes developed from 2026-01-15 to 2026-03-06._

### Added

* Added inventory-level calculations and graphing support for the EOQ-family models.
* Added EPQ inventory-level support.

### Changed

* Changed `DiscountEOQ.calculate_eoq()` in a backward-incompatible API update to return the chosen order quantity; detailed output is available through `analysis_mode=True`.
* Added NumPy, Plotly, and Matplotlib to the project requirements.
* Updated README examples and installation instructions.

## [0.2.0] - 2025-11-29

_Changes developed from 2025-09-02 to 2025-11-29._

### Added

* Added reorder-point calculation and parameter validation across the EOQ-family models.
* Added automated tests for EOQ calculations, reorder points, invalid parameters, and model-specific behaviour.
* Added a pytest GitHub Actions workflow and project dependency list.
* Added contribution guidance and test strategy documentation.

### Changed

* Renamed the public inventory model classes from `Basic_EOQ`, `Discount_EOQ`, and `Backorder_EOQ` to the backward-incompatible CapWords names `BasicEOQ`, `DiscountEOQ`, and `BackorderEOQ`.
* Updated continuous integration to run against the `core` branch.

## [0.1.0] - 2025-08-31

_Changes developed from 2025-08-19 to 2025-08-31._

### Added

* Introduced the project under the MIT License.
* Added the original EOQ implementation and project README.
* Renamed the main implementation module to `inventory_models.py`.
* Added the EPQ, quantity-discount EOQ, and planned-backorder EOQ model variants.
