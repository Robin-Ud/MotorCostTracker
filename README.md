# MotoRegis

A minimalist command-line tool for tracking vehicle fuel, maintenance, and costs. Zero dependencies — pure Python standard library.

[![CI](https://github.com/Robin-Ud/MotorCostTracker/actions/workflows/ci.yml/badge.svg)](https://github.com/Robin-Ud/MotorCostTracker/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

---

## What it does

MotoRegis logs vehicle events to a plain CSV file — fuel fills, scheduled maintenance, accessories, corrective repairs, and bureaucracy (taxes, licensing). After each entry it checks whether any maintenance item is overdue by mileage, months, or days, and alerts you immediately.

Data lives in `~/.motoregis/` and is never locked into a proprietary format. Bring your own analysis tool (pandas, Excel, anything).

---

## Install

```bash
pip install motoregis
```

Then run:

```bash
motoregis
```

---

## First-time setup

MotoRegis stores your configuration and data in `~/.motoregis/`. On first run, if no config is found, the tool will print setup instructions.

```bash
# 1. Create the data directory
mkdir -p ~/.motoregis/veiculos

# 2. Copy the example config and edit it
cp configs.example.json ~/.motoregis/configs.json

# 3. Copy the example vehicle config and edit it
cp veiculos/example_vehicle.json ~/.motoregis/veiculos/my_vehicle.json
```

Edit `~/.motoregis/configs.json` to point to your vehicle file:

```json
{
  "veiculos_index": {
    "My Motorcycle": "veiculos/my_vehicle.json"
  },
  "combustiveis": ["gasoline", "premium", "ethanol"],
  "categorias_menu": [
    "Fuel", "Scheduled Maintenance", "Accessories / Upgrades",
    "Corrective Maintenance", "Bureaucracy", "Change Vehicle", "Change Date"
  ],
  "git_sync": false
}
```

Set `"git_sync": true` if you want automatic git commit and push after each record (requires `~/.motoregis/` to be a git repository).

---

## Vehicle config

Each vehicle has its own JSON file defining maintenance intervals:

```json
{
  "veiculo": "My Motorcycle",
  "ano": 2022,
  "nomes_display": {
    "oil_change": "Oil & filter",
    "tire_pressure": "Tire pressure"
  },
  "manutencoes": {
    "por_quilometragem": {
      "oil_change": 5000
    },
    "por_tempo_meses": {
      "oil_change": 6
    },
    "por_tempo_dias": {
      "tire_pressure": 15
    }
  }
}
```

Keys in `nomes_display` map internal identifiers to human-readable labels shown in the menu and alerts. All three interval types (`por_quilometragem`, `por_tempo_meses`, `por_tempo_dias`) are optional.

---

## CSV schema

All records are appended to `~/.motoregis/veiculos/<vehicle>.csv`:

| Column | Type | Description | Example |
|---|---|---|---|
| `date` | String | Record date (YYYY-MM-DD) | 2026-04-17 |
| `odometer` | Int | Current odometer reading (km) | 15400 |
| `category` | Int | 1=Fuel, 2=Scheduled, 3=Accessories, 4=Corrective, 5=Bureaucracy | 1 |
| `cost` | Float | Total cost | 85.50 |
| `liters` | Float | Liters filled (fuel entries only, else 0.00) | 14.20 |
| `details` | String | Fuel type or maintenance identifier | oil_change |

---

## Architecture

The source is organized into four zones, all in `motoregis.py`:

| Zone | Responsibility |
|---|---|
| Zone 1 — Data engines | `load_json`, `read_csv`, `append_record`, `git_sync` — pure I/O, no logic |
| Zone 2 — Validators | `get_int`, `get_float`, `select_index` — isolated from business logic |
| Zone 3 — Orchestration | maintenance checks, odometer prompts, record flows |
| Zone 4 — Interface | main menu loop |

This separation means the CLI layer can be replaced with a TUI or GUI without touching the data or business logic.

---

## Contributing

```bash
git clone https://github.com/Robin-Ud/MotorCostTracker
cd MotorCostTracker
pip install -e .
pip install pytest
pytest tests/ -v
```

Code style:
- PEP 8
- Type hints required on all new functions
- No external dependencies — stdlib only
- Commit messages follow `feat:`, `fix:`, `chore:` convention
