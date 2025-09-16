# Repository Guidelines

## Project Structure & Module Organization
- `src/tree_rewriter/`: core library. Primary entry points: `rewrite`, `when`, `bottom_up`, `first`, `all`, and `_` (wildcard).
- `examples/`: runnable demos for manual testing and showcasing patterns.
- `README.md` and `DESIGN.md`: usage, DSL, and design rationale.
- `pyproject.toml`: packaging and dev tools config (ruff, mypy, pytest, coverage).
- Tests: create under `tests/` mirroring modules, e.g., `tests/test_rewrite.py`.

## Build, Test, and Development Commands
- Create env & install dev deps: `python -m venv .venv && source .venv/bin/activate && pip install -e .[dev]`
- Lint: `ruff check .` — fast style and import checks.
- Type-check: `mypy .` — strict settings; keep green.
- Run examples: `python examples/arithmetic_simplifier.py` (adjust file to explore others).
- Optional build: `python -m pip install build && python -m build` — produces wheel/sdist.

## Coding Style & Naming Conventions
- Python 3.10+; PEP 8; 4-space indentation. Favor small, pure functions.
- Names: functions/vars `snake_case`; classes `CapWords`; modules `snake_case`.
- Public API should stay minimal and composable; trees are S-expressions (tuples). Avoid hidden state in rules.
- Type hints where natural; keep `mypy` strict passing. Use `ruff` to maintain consistency.

## Testing Guidelines
- Framework: `pytest`. Place tests in `tests/` with `test_*.py` files.
- Aim for high coverage of edge patterns and fixed-point behavior.
- Example:
  ```python
  from tree_rewriter import rewrite, when, _, bottom_up
  def test_identity_add_zero():
      rule = bottom_up(when('+', 0, _).then(lambda x: x))
      assert rewrite(('+', 'x', 0), rule) == 'x'
  ```

## Commit & Pull Request Guidelines
- Commits: use Conventional Commits (e.g., `feat: add commutative helper`, `fix: prevent non-terminating rule`).
- PRs: include a clear description, rationale, before/after examples, reproduction steps, and any doc/example updates. Link issues (e.g., `Closes #123`).
- Pre-submit: run `ruff check .`, `mypy .`, and tests (when present) locally; ensure examples still run.

