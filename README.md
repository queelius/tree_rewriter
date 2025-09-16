# Tree Rewriter

A minimal term rewriting system. 15 lines of code. Infinite possibilities.

## The Insight

What if we could express computational rules as simple pattern → replacement transformations? What if complex behaviors emerged from applying these simple rules repeatedly until nothing changes?

This is the essence of term rewriting—a computational paradigm at the heart of compilers, theorem provers, and computer algebra systems. Tree Rewriter distills this powerful idea to its minimal form.

## The Core

```python
def rewrite(tree, *rules):
    """Apply rules until fixed point."""
    while True:
        for rule in rules:
            new = rule(tree)
            if new != tree:
                tree = new
                break
        else:
            return tree
```

That's it. The entire rewriting engine in 10 lines. Given a tree and rules, it applies them repeatedly until reaching a fixed point.

## Trees as S-Expressions

We use S-expressions (nested tuples) for minimalism:

```python
5                    # atom: constant
'x'                  # atom: variable  
('+', 'x', 5)        # tree: x + 5
('*', 2, ('+', 'x', 5))  # tree: 2 * (x + 5)
```

## The Fluent API

Express rules as patterns with a fluent interface:

```python
from tree_rewriter import rewrite, when, _, bottom_up

# Pattern matching with wildcards
rule = when('+', 0, _).then(lambda x: x)    # 0 + x => x

# Multiple rules
rules = [
    when('+', 0, _).then(lambda x: x),      # 0 + x => x
    when('+', _, 0).then(lambda x: x),      # x + 0 => x
    when('*', 0, _).then(0),                # 0 * x => 0
    when('*', _, 0).then(0),                # x * 0 => 0
]

# Apply bottom-up
expr = ('*', ('+', 'x', 0), 1)
result = rewrite(expr, *[bottom_up(r) for r in rules])
print(result)  # 'x'
```

## Pattern Language

### Basic Patterns

- `_` matches anything and binds it to lambda parameters
- `'$name'` creates named bindings for reuse
- Literals match exactly: `when('+', 0, _)`
- Predicates match conditionally: `when('+', is_literal, is_literal)`
- Guards add conditions: `.where(lambda x: x > 0)`

### DSL Helpers

```python
# Commutative operations - write once, match both ways
commutative('+', 0, lambda x: x)  # Generates both x+0 and 0+x rules

# Type predicates for readable patterns
is_type(int, float)  # Create custom type matchers
is_literal           # Matches self-evaluating values (numbers, bools, None)

# Predicates ARE skeletal patterns!
when('+', is_literal, is_literal)  # Matches ANY addition of literals
when('*', _, is_literal)           # Matches ANY multiplication by literal
```

### Composition

Combine simple rules into complex transformations:

```python
# Rule combinators
first(rule1, rule2, rule3)   # Try in order, return first match
all(rule1, rule2)            # Apply rules in sequence to same tree

# Build complete transformations
simplifier = [
    # Identity elements
    *commutative('+', 0, lambda x: x),
    *commutative('*', 1, lambda x: x),
    
    # Constant folding
    when('+', is_literal, is_literal).then(lambda a, b: a + b),
    when('*', is_literal, is_literal).then(lambda a, b: a * b),
    
    # Algebraic identities
    when('-', '$x', '$x').then(0),  # x - x = 0
]

# Apply bottom-up for complete transformation
result = rewrite(expr, *[bottom_up(r) for r in simplifier])
```

## Example: Symbolic Math

```python
# Differentiation is an algorithm - write it as a function
def diff(expr, var='x'):
    if isinstance(expr, (int, float)): return 0
    if expr == var: return 1
    if isinstance(expr, str): return 0
    
    if isinstance(expr, tuple):
        op, *args = expr
        if op == '+': 
            return ('+', diff(args[0], var), diff(args[1], var))
        if op == '*':  # Product rule
            f, g = args
            return ('+', ('*', diff(f, var), g), ('*', f, diff(g, var)))
    return expr

# Simplification is pattern matching - use rules
simplify = [
    *commutative('+', 0, lambda x: x),      # x + 0 = 0 + x = x
    *commutative('*', 1, lambda x: x),      # x * 1 = 1 * x = x
    *commutative('*', 0, 0),                # x * 0 = 0 * x = 0
    when('+', is_const, is_const).then(lambda a, b: a + b),  # Constant folding
]

# Combine them
expr = ('*', 'x', 'x')  # x²
deriv = diff(expr)      # ('*', 1, 'x') + ('*', 'x', 1)
result = rewrite(deriv, *[bottom_up(r) for r in simplify])
# Result: ('+', 'x', 'x')
```

## Design Philosophy

### Minimalism
The core is ~10 lines. Complexity emerges from the rules you write, not the rewriter itself.

### Use the Right Tool
- **Algorithms** (like differentiation): Write as recursive functions
- **Pattern transformations** (like simplification): Write as rewrite rules

### Predicates as Patterns
The key insight: predicates in patterns define "skeletal structure":
- `when('+', is_literal, is_literal)` matches the pattern `('+', _, _)` where holes are literals
- `when('*', is_var, is_var)` matches multiplications of variables
- Custom predicates create custom pattern languages

## Installation

```bash
pip install tree-rewriter
```

Or just copy the single file - it's ~100 lines.

## The Beauty

- **Simple Core**: ~10 lines that handle all term rewriting
- **Readable Rules**: `when(...).then(...)` reads like math notation  
- **Just Data**: Trees are tuples, rules are functions
- **Powerful Patterns**: Predicates create skeletal pattern matching

The rewriter stays simple. Your rules encode the complexity.

## Examples

- [arithmetic_simplifier.py](examples/arithmetic_simplifier.py) - Basic arithmetic expression simplification
- [boolean_algebra.py](examples/boolean_algebra.py) - Complete boolean algebra implementation  
- [pattern_matching.py](examples/pattern_matching.py) - All pattern matching features demonstrated
- [css_optimizer.py](examples/css_optimizer.py) - Real-world CSS optimization

## Cookbook

These patterns stay out of the core API to keep it minimal, but are handy to compose powerful rewrites. Copy-paste as needed.

- Local fixed-point at a node (saturate a node before moving on):
  ```python
  def repeat(rule):
      def r(t):
          while True:
              new = rule(t)
              if new == t:
                  return t
              t = new
      return r
  ```

- Top-down traversal (pre-order apply before children):
  ```python
  def top_down(rule):
      def walk(t):
          t2 = rule(t)
          if isinstance(t2, tuple):
              t2 = (t2[0],) + tuple(walk(ch) for ch in t2[1:])
          return rule(t2)
      return walk
  ```

- Readability helpers (local):
  ```python
  var = lambda name: f"${name}"
  op = lambda name, *args: (name, *args)
  ```

- Predicates & guard combinators:
  ```python
  is_op = lambda name: (lambda t: isinstance(t, tuple) and t[0] == name)
  is_symbol = lambda x: isinstance(x, str) and not x.startswith('$')
  is_number = lambda x: isinstance(x, (int, float, complex))
  is_zero = lambda x: x == 0
  is_one = lambda x: x == 1
  def where_all(*preds):
      return lambda *xs: all(p(*xs) for p in preds)
  def where_any(*preds):
      return lambda *xs: any(p(*xs) for p in preds)
  def negate(pred):
      return lambda *xs: not pred(*xs)
  ```

- Commutative normalization (binary, opt-in canonicalization):
  ```python
  def normalize_commutative(op_name):
      return when(op_name, _, _).then(lambda a, b: (op_name,) + tuple(sorted((a, b), key=str)))
  ```

See `examples/cookbook.py` for small runnable demos of these patterns.

## Learn More

- [DESIGN.md](DESIGN.md) - Why we chose simplicity over power

---

*"Make it as simple as possible, but not simpler."* — Einstein (probably)
