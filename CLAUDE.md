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

The entire application lives in a single file, `motoregis.py` (~363 lines), organized into four explicitly numbered zones:

| Zone | Role | Examples |
|------|------|---------|
| 1 — Data Engines | Pure I/O, no business logic | `load_json`, `read_csv`, `append_record`, `git_sync` |
| 2 — Validators | Input validation, isolated from I/O | `get_int`, `get_float`, `select_index` |
| 3 — Orchestration | Business logic combining Zones 1 & 2 | `check_maintenance`, `record_fuel`, `select_vehicle`, `_finalize` |
| 4 — Interface | Main menu loop only | `main()` |

**Data flow:** `main()` auto-selects `vehicles[0]` on startup → user picks a category → record function → `_finalize()` → `check_maintenance()` → optional `git_sync()`. `select_vehicle()` is only called when the user picks option 6 (Change Vehicle) from the menu.

**Storage** lives in `~/motoregis/` (user-owned, no lock-in):
- `configs.json` — global config: `veiculos_index`, `combustiveis`, `categorias_menu`, `git_sync`, `git_remote`, `currency_symbol`, `daily_km_threshold`
- `<path>.json` — per-vehicle metadata and maintenance intervals; path is the value in `veiculos_index` and is relative to `~/motoregis/` (flat layout, no enforced subdirectory)
- `<path>.csv` — append-only record log (same base path as JSON, `.csv` extension); columns: `date, odometer, category, cost, liters, details`

**Vehicle JSON fields:** `veiculo` (display name), `ano` (year), `nomes_display` (map of internal key → human-readable label used by `display_name()`), `manutencoes` (maintenance intervals split into `por_quilometragem`, `por_tempo_meses`, `por_tempo_dias`).

CSV categories: `1`=Fuel, `2`=Scheduled maintenance, `3`=Accessories, `4`=Corrective, `5`=Bureaucracy.

**Maintenance intervals** are defined per vehicle in JSON (km-based, month-based, day-based). `check_maintenance()` scans category-2 records to find the last occurrence of each task, falls back to the first record if no history, and prints overdue items directly (returns `None`). Note: `record_scheduled_maintenance()` only shows `por_quilometragem` tasks as menu choices; month- and day-based tasks can trigger alerts but cannot be proactively recorded via the menu.

**Fuel consumption** is calculated from the odometer delta since the last category-1 record that has `liters > 0`.

**Git sync** (optional) is enabled by `git_sync: true` plus a `git_remote` URL in `configs.json`. After every record it commits and pushes `~/motoregis/` with message `record: <vehicle> | <date> | <odometer>km`. Failures are silent. The in-app "Setup Sync" option (menu item 8) configures both keys and does the initial push.

**Menu options:** 1–5 map to the five CSV categories (Fuel, Scheduled Maintenance, Accessories, Corrective, Bureaucracy). Option 6 = Change Vehicle (`select_vehicle()`), option 7 = Change Date, option 8 = Setup Sync (`setup_sync()`).

## Key Constraints

- **Zero external dependencies** — stdlib only (`csv`, `json`, `os`, `subprocess`, `datetime`).
- **Python 3.10+** — use `X | Y` union syntax, not `Optional[X]`.
- Type hints are required on all function signatures.
- Commit messages follow the `feat:` / `fix:` / `chore:` prefix convention.
