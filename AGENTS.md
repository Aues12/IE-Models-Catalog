# AGENTS.md

## Project Overview

Python library for inventory management models (EOQ, EPQ, Discount, Backorder).

## Key Commands

- **Run tests**: `.venv/bin/python -m pytest tests/ -v`
- **Run single test file**: `.venv/bin/python -m pytest tests/test_eoq_logic.py`

## Structure

- Main module: `inventory_models.py` (contains classes: `BasicEOQ`, `EPQ`, `DiscountEOQ`, `BackorderEOQ`)
- Tests: `tests/`

## Environment

- Python 3.12 in `.venv`
- Dependencies: numpy, matplotlib, plotly, pytest
- Package metadata and Ruff configuration: `pyproject.toml`
- Shared result costs and numeric validation: `model_common.py`
- Dynamic models: `dynamic_models.py` (Wagner–Whitin and Silver–Meal)

## Testing Notes

- Tests use pytest
- Test files import directly from `inventory_models`
- Include regression and independent optimality checks when changing model logic.
- Quality checks: `.venv/bin/ruff check .` and `.venv/bin/ruff format --check .`
