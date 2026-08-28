# Changelog

All notable changes to this project are documented here.

The project does not yet use release tags, so entries are grouped by the date of the relevant commits. Dates before the first tagged release should not be interpreted as package versions.

## Unreleased

### Fixed

* Made both dynamic lot-sizing methods skip leading and all-zero demand periods without creating a zero-quantity order or charging an unnecessary setup cost.
* Made `EPQ`, `DiscountEOQ`, and `BackorderEOQ` retain their calculated order quantity consistently with `BasicEOQ`.

### Changed

* Expanded continuous integration to test Python 3.11 and 3.12.
* Added Ruff linting, formatting, and continuous-integration checks.
* Added an English Wagner–Whitin walkthrough and retained the Turkish original with a `_TR` suffix.

## 2026-08-29

### Fixed

* Ensured `DiscountEOQ` always evaluates the undiscounted base-price tier, even when callers omit the `0` quantity break.
* Avoided mutating the `discount_rates` mapping supplied by callers.
* Added a regression test for a discount threshold that is too high to be economical.

### Documentation

* Refreshed the README with the current inventory-model scope, dynamic lot-sizing API, validation rules, examples, and test command.

## 2026-06-30

### Documentation

* Added notes for the dynamic inventory models.

## 2026-04-27 to 2026-04-30

### Added

* Added `DynamicLotSizing`, `DLSInput`, and `DLSResult` for time-phased demand planning.
* Added the exact Wagner–Whitin solver and the Silver–Meal heuristic.
* Added dynamic lot-sizing tests and mathematical walkthroughs.
* Added EOQ model and mathematical documentation, plus the original project proposal.

### Changed

* Added explicit `method` selection to the dynamic lot-sizing solver.
* Updated README, requirements, and testing documentation for the dynamic-model scope.

## 2026-01-15 to 2026-03-06

### Added

* Added inventory-level calculations and graphing support for the EOQ-family models.
* Added EPQ inventory-level support.

### Changed

* Changed `DiscountEOQ.calculate_eoq()` to return the chosen order quantity; detailed output is available through `analysis_mode=True`.
* Added NumPy, Plotly, and Matplotlib to the project requirements.
* Updated README examples and installation instructions.

## 2025-09-02 to 2025-11-29

### Added

* Added reorder-point calculation and parameter validation across the EOQ-family models.
* Added automated tests for EOQ calculations, reorder points, invalid parameters, and model-specific behaviour.
* Added a pytest GitHub Actions workflow and project dependency list.
* Added contribution guidance and test strategy documentation.

### Changed

* Renamed inventory model classes to CapWords style.
* Updated continuous integration to run against the `core` branch.

## 2025-08-19 to 2025-08-31

### Added

* Introduced the project under the MIT License.
* Added the original EOQ implementation and project README.
* Renamed the main implementation module to `inventory_models.py`.
* Added the EPQ, quantity-discount EOQ, and planned-backorder EOQ model variants.
