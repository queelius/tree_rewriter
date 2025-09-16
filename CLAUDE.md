# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Tree Rewriter is a minimal term rewriting system implemented in ~100 lines of Python. It provides pattern matching and transformation of tree structures (S-expressions) with a fluent API.

## Core Architecture

The system consists of:

1. **Core Rewrite Engine** (`src/tree_rewriter/tree_rewriter.py`):
   - `rewrite()`: Main engine that applies rules until fixed point (10 lines)
   - `when` class: Fluent API for building pattern → transformation rules
   - Pattern matching supports wildcards (`_`), named variables (`$x`), predicates, and guards
   - Trees are represented as nested tuples (S-expressions)

2. **Public API** (`src/tree_rewriter/__init__.py`):
   - `rewrite`, `when`, `_`, `bottom_up`, `commutative`
   - `is_literal`, `is_type`, `first`, `all`

## Development Commands

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_rewrite.py

# Run with coverage
coverage run -m pytest
coverage report
coverage html  # Generate HTML report

# Run a single test
pytest tests/test_rewrite.py::test_commutative_add_zero
```

### Linting and Type Checking
```bash
# Type checking with mypy
mypy .

# Linting with ruff
ruff check .
ruff format .
```

### Installation
```bash
# Install for development (includes dev dependencies)
pip install -e ".[dev]"

# Build package
python -m build
```

## Key Design Principles

1. **Minimalism Over Features**: The core rewrite engine is ~10 lines. Complexity emerges from user-defined rules, not the framework.

2. **Python-Native Patterns**: Predicates are Python functions, allowing arbitrary logic in patterns without learning a separate pattern language.

3. **No Unification**: Pattern variables like `$x` bind on first occurrence but don't enforce equality across occurrences. This keeps matching simple and debuggable.

4. **Composition Over Complexity**: Complex behaviors (like commutative rules) are built by composing simple rules rather than adding framework features.

## Common Patterns

### Writing Rules
```python
# Basic pattern → replacement
rule = when('+', 0, _).then(lambda x: x)  # 0 + x => x

# Named variables for reuse
rule = when('+', '$x', '$x').then(lambda x: ('*', 2, x))  # x + x => 2*x

# Predicates in patterns
rule = when('+', is_literal, is_literal).then(lambda a, b: a + b)

# Guards for additional conditions
rule = when('val', _).where(lambda x: x > 0).then(lambda x: x * 2)
```

### Applying Rules
```python
# Bottom-up traversal (most common)
result = rewrite(expr, *[bottom_up(r) for r in rules])

# Direct application
result = rewrite(expr, rule1, rule2, rule3)
```

## Testing Strategy

Tests follow patterns in `tests/test_rewrite.py`:
- Test individual rules in isolation
- Test rule composition and combinators
- Test pattern matching edge cases (wildcards, named vars, predicates)
- Use simple examples that clearly demonstrate the transformation

## Examples

The `examples/` directory contains working demonstrations:
- `arithmetic_simplifier.py`: Basic expression simplification
- `boolean_algebra.py`: Complete boolean algebra system
- `pattern_matching.py`: All pattern features demonstrated
- `calculus_*.py`: Symbolic differentiation and integration
- `css_optimizer.py`: Real-world CSS optimization

## File Structure

```
tree_rewriter/
├── src/tree_rewriter/
│   ├── __init__.py          # Public API exports
│   └── tree_rewriter.py     # Core implementation (~100 lines)
├── tests/
│   └── test_rewrite.py      # Test suite
├── examples/                # Usage demonstrations
└── pyproject.toml           # Project configuration
```