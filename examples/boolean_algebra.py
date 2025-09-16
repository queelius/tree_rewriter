#!/usr/bin/env python3
"""
Boolean Algebra Simplification - Working Version

Shows how boolean expressions can be simplified through rewriting.
"""

import sys
sys.path.insert(0, '../src')

from tree_rewriter import rewrite, when, _, bottom_up

print("Boolean Algebra Simplification")
print("=" * 50)

# Correct boolean algebra rules - using lambdas properly!
boolean_rules = [
    # Identity laws
    when('and', True, _).then(lambda x: x),        # True ∧ x = x
    when('and', _, True).then(lambda x: x),        # x ∧ True = x
    when('or', False, _).then(lambda x: x),        # False ∨ x = x
    when('or', _, False).then(lambda x: x),        # x ∨ False = x
    
    # Domination laws
    when('and', False, _).then(False),             # False ∧ x = False
    when('and', _, False).then(False),             # x ∧ False = False
    when('or', True, _).then(True),                # True ∨ x = True
    when('or', _, True).then(True),                # x ∨ True = True
    
    # Complement laws
    when('and', '$x', ('not', '$x')).then(False),  # x ∧ ¬x = False
    when('and', ('not', '$x'), '$x').then(False),  # ¬x ∧ x = False
    when('or', '$x', ('not', '$x')).then(True),    # x ∨ ¬x = True
    when('or', ('not', '$x'), '$x').then(True),    # ¬x ∨ x = True
    
    # Double negation - FIXED: use lambda!
    when('not', ('not', '$x')).then(lambda x: x),  # ¬¬x = x
    
    # Idempotent laws - FIXED: use lambda!
    when('and', '$x', '$x').then(lambda x: x),     # x ∧ x = x
    when('or', '$x', '$x').then(lambda x: x),      # x ∨ x = x
    
    # De Morgan's laws - already correct
    when('not', ('and', '$x', '$y')).then(         # ¬(x ∧ y) = ¬x ∨ ¬y
        lambda x, y: ('or', ('not', x), ('not', y))
    ),
    when('not', ('or', '$x', '$y')).then(          # ¬(x ∨ y) = ¬x ∧ ¬y
        lambda x, y: ('and', ('not', x), ('not', y))
    ),
    
    # Absorption laws
    when('or', '$x', ('and', '$x', _)).then(lambda x, y: x),   # x ∨ (x ∧ y) = x
    when('and', '$x', ('or', '$x', _)).then(lambda x, y: x),   # x ∧ (x ∨ y) = x
]

# Test cases
test_cases = [
    # Basic tests
    ("Identity", ('and', True, 'p')),
    ("Domination", ('or', 'x', True)),
    ("Double negation", ('not', ('not', 'a'))),
    ("Idempotent", ('and', 'x', 'x')),
    ("Complement", ('and', 'x', ('not', 'x'))),
    
    # De Morgan's laws
    ("De Morgan AND", ('not', ('and', 'p', 'q'))),
    ("De Morgan OR", ('not', ('or', 'p', 'q'))),
    
    # Complex expressions
    ("Nested", ('and', ('not', ('not', 'a')), ('or', 'b', False))),
    ("Mixed", ('or', ('and', 'x', ('not', 'x')), ('and', 'y', 'y'))),
    
    # Absorption
    ("Absorption 1", ('or', 'x', ('and', 'x', 'y'))),
    ("Absorption 2", ('and', 'p', ('or', 'p', 'q'))),
]

print("\nSimplifying boolean expressions:\n")

for name, expr in test_cases:
    result = rewrite(expr, *[bottom_up(r) for r in boolean_rules])
    print(f"{name:15} {expr} => {result}")

# More complex example
print("\n" + "=" * 50)
print("Complex example:\n")

complex_expr = ('and',
    ('or', ('not', 'a'), 'b'),
    ('or', 'a', ('not', 'b')),
    ('not', ('not', ('or', 'a', 'b'))))

print("Expression:")
print(complex_expr)
print("\nStep by step simplification would show:")
print("1. ¬¬(a ∨ b) => (a ∨ b)")
print("2. The whole expression becomes: (¬a ∨ b) ∧ (a ∨ ¬b) ∧ (a ∨ b)")
print("3. Further simplification possible with distribution...")

result = rewrite(complex_expr, *[bottom_up(r) for r in boolean_rules])
print(f"\nResult: {result}")

# Example showing depth reduction
def tree_depth(tree):
    if not isinstance(tree, tuple):
        return 0
    return 1 + max([tree_depth(child) for child in tree[1:]], default=0)

print("\n" + "=" * 50)
print("Depth reduction examples:\n")

depth_examples = [
    ('not', ('not', ('not', ('not', 'x')))),
    ('and', ('and', 'a', 'b'), ('and', 'c', 'd')),
    ('or', ('and', 'p', ('not', 'p')), ('or', 'q', ('not', 'q'))),
]

for expr in depth_examples:
    result = rewrite(expr, *[bottom_up(r) for r in boolean_rules])
    print(f"Depth {tree_depth(expr)} => {tree_depth(result)}: {expr} => {result}")

print("\n" + "=" * 50)
print("Key points:")
print("- Always use lambda x: x, not '$x' in .then()")
print("- Pattern variables like '$x' capture values")
print("- The captured values are passed to the lambda")
print("- This creates a clear, explicit system with no magic")