#!/usr/bin/env python3
"""
Arithmetic Expression Simplifier

Shows how to build a simple arithmetic simplifier using tree rewriting.
"""

import sys
sys.path.insert(0, '../src')

from tree_rewriter import rewrite, when, _, bottom_up, commutative, is_literal

print("Arithmetic Expression Simplifier")
print("=" * 50)

# Arithmetic simplification rules
arithmetic_rules = [
    # Identity elements
    *commutative('+', 0, lambda x: x),      # x + 0 = 0 + x = x
    *commutative('*', 1, lambda x: x),      # x * 1 = 1 * x = x
    
    # Absorbing elements
    *commutative('*', 0, 0),                # x * 0 = 0 * x = 0
    
    # Constant folding
    when('+', is_literal, is_literal).then(lambda a, b: a + b),
    when('-', is_literal, is_literal).then(lambda a, b: a - b),
    when('*', is_literal, is_literal).then(lambda a, b: a * b),
    when('/', is_literal, is_literal).where(lambda a, b: b != 0).then(lambda a, b: a / b),
    
    # Algebraic identities
    when('-', '$x', '$x').then(0),          # x - x = 0
    when('/', '$x', '$x').where(lambda x: x != 0).then(1),  # x / x = 1 (x ≠ 0)
    
    # Strength reduction
    when('*', 2, _).then(lambda x: ('+', x, x)),     # 2 * x = x + x
    when('*', _, 2).then(lambda x: ('+', x, x)),     # x * 2 = x + x
]

# Test cases
test_expressions = [
    # Basic simplifications
    ('+', 'x', 0),
    ('*', 1, 'y'),
    ('*', 0, ('+', 'a', 'b')),
    
    # Constant folding
    ('+', 2, 3),
    ('*', 4, 5),
    ('-', 10, 7),
    
    # Algebraic identities
    ('-', 'x', 'x'),
    ('/', 'y', 'y'),
    
    # Nested expressions
    ('+', ('*', 2, 3), ('*', 4, 5)),
    ('*', ('+', 'x', 0), ('-', 5, 5)),
    
    # Strength reduction
    ('*', 2, 'z'),
]

print("\nSimplifying expressions:\n")

for expr in test_expressions:
    result = rewrite(expr, *[bottom_up(r) for r in arithmetic_rules])
    print(f"{str(expr):30} => {result}")

# More complex example
print("\n" + "=" * 50)
print("Complex expression:\n")

complex_expr = ('*', 
    ('+', 'x', 0),
    ('-', 
        ('*', 2, 5),
        ('+', 3, 7)))

print(f"Original: {complex_expr}")
result = rewrite(complex_expr, *[bottom_up(r) for r in arithmetic_rules])
print(f"Simplified: {result}")

print("\n" + "=" * 50)
print("Key insights:")
print("- Simple rules compose to handle complex expressions")
print("- bottom_up() ensures we simplify inner expressions first")
print("- Pattern matching makes rules readable and declarative")
print("- Could easily extend with more algebraic identities")