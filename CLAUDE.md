# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install in development mode
pip install -e .

# Run the app
motoregis

# Run all tests
pytest tests/ -v

# Run a single test module
pytest tests/test_data_engine.py -v
pytest tests/test_validators.py -v
pytest tests/test_maintenance.py -v
```

CI runs `pip install pytest && pip install -e . && pytest tests/ -v` against Python 3.10, 3.11, and 3.12.

## Architecture

The entire application lives in a single file, `motoregis.py` (~312 lines), organized into four explicitly numbered zones:

| Zone | Role | Examples |
|------|------|---------|
| 1 — Data Engines | Pure I/O, no business logic | `load_json`, `read_csv`, `append_record`, `git_sync` |
| 2 — Validators | Input validation, isolated from I/O | `get_int`, `get_float`, `select_index` |
| 3 — Orchestration | Business logic combining Zones 1 & 2 | `check_maintenance`, `record_fuel`, `select_vehicle`, `_finalize` |
| 4 — Interface | Main menu loop only | `main()` |

**Data flow:** `main()` → `select_vehicle()` → record function → `_finalize()` → `check_maintenance()` → optional `git_sync()`.

**Storage** lives in `~/.motoregis/` (user-owned, no lock-in):
- `configs.json` — global config: vehicle index, fuel types, menu labels, `git_sync` flag
- `veiculos/<name>.json` — per-vehicle metadata and maintenance intervals
- `veiculos/<name>.csv` — append-only record log with columns: `date, odometer, category, cost, liters, details`

CSV categories: `1`=Fuel, `2`=Scheduled maintenance, `3`=Accessories, `4`=Corrective, `5`=Bureaucracy.

**Maintenance intervals** are defined per vehicle in JSON (km-based, month-based, day-based). `check_maintenance()` scans category-2 records to find the last occurrence of each task, falls back to the first record if no history, and returns overdue items for display.

**Fuel consumption** is calculated from the odometer delta since the last category-1 record that has `liters > 0`.

**Git sync** (optional, `git_sync: true` in config) commits and pushes `~/.motoregis/` after every record with message `record: <vehicle> | <date> | <odometer>km`. Failures are silent.

## Key Constraints

- **Zero external dependencies** — stdlib only (`csv`, `json`, `os`, `subprocess`, `datetime`).
- **Python 3.10+** — use `X | Y` union syntax, not `Optional[X]`.
- Type hints are required on all function signatures.
- Commit messages follow the `feat:` / `fix:` / `chore:` prefix convention.
