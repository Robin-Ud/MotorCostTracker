# Contributing to MotoRegis

## Dev setup

```bash
git clone https://github.com/Robin-Ud/MotorCostTracker
cd MotorCostTracker
pip install -e .
pip install pytest
```

## Running tests

```bash
pytest tests/ -v
```

All 29 tests must pass before submitting a PR.

## Code conventions

- **Python 3.10+** — use `X | Y` union syntax, not `Optional[X]`
- **Type hints** on every function signature
- **No external dependencies** — stdlib only
- **No comments** unless the why is non-obvious

## Code zones

The source (`motoregis.py`) is split into four zones — keep new code in the right zone:

| Zone | What belongs here |
|---|---|
| Zone 1 — Data engines | Functions that only read or write files. No decisions. |
| Zone 2 — Validators | Functions that validate and return user input. No I/O. |
| Zone 3 — Orchestration | Functions that combine zones 1 and 2 into a complete flow. |
| Zone 4 — Interface | The main menu loop only. |

## Commit messages

Follow the convention already in the history:

```
feat: short description of new feature
fix: short description of bug fix
chore: maintenance, deps, config
```
