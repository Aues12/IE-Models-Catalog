# AGENTS.md

## Project Overview

Python library for inventory management models (EOQ, EPQ, Discount, Backorder).

## Key Commands

- **Run tests**: `.venv/bin/python -m pytest Tests/ -v`
- **Run single test file**: `.venv/bin/python -m pytest Tests/test_eoq_logic.py`

## Structure

- Main module: `inventory_models.py` (contains classes: `BasicEOQ`, `EPQ`, `DiscountEOQ`, `BackorderEOQ`)
- Tests: `Tests/`

## Environment

- Python 3.12 in `.venv`
- Dependencies: numpy, matplotlib, plotly, pytest
- No pyproject.toml - uses simple module structure

## Testing Notes

- Tests use pytest
- Test files import directly from `inventory_models`
- All 46 tests pass