#!/usr/bin/env python3
"""
Pattern Matching Examples

Demonstrates the various pattern matching capabilities of the tree rewriter.
"""

import sys
sys.path.insert(0, '../src')

from tree_rewriter import rewrite, when, _, is_literal, is_type

print("Pattern Matching Examples")
print("=" * 50)

# 1. Basic patterns
print("\n1. Basic Patterns")
print("-" * 30)

basic_rules = [
    when('foo', 42).then('matched exact 42'),
    when('bar', _).then(lambda x: f'matched any: {x}'),
    when('baz', _, _).then(lambda a, b: f'matched two args: {a}, {b}'),
]

test_basic = [
    ('foo', 42),
    ('foo', 43),
    ('bar', 'hello'),
    ('baz', 10, 20),
]

for expr in test_basic:
    result = rewrite(expr, *basic_rules)
    print(f"{str(expr):20} => {result}")

# 2. Named patterns
print("\n\n2. Named Patterns")
print("-" * 30)

named_rules = [
    when('swap', '$x', '$y').then(lambda x, y: ('swap', y, x)),
    when('dup', '$x').then(lambda x: ('pair', x, x)),
    when('equal', '$x', '$x').then(lambda x: True),  # Both must be same
    when('equal', _, _).then(False),  # Different values
]

test_named = [
    ('swap', 'a', 'b'),
    ('dup', 'hello'),
    ('equal', 5, 5),
    ('equal', 5, 6),
]

for expr in test_named:
    result = rewrite(expr, *named_rules)
    print(f"{str(expr):20} => {result}")

# 3. Predicate patterns
print("\n\n3. Predicate Patterns")
print("-" * 30)

predicate_rules = [
    when('classify', is_literal).then(lambda x: f'{x} is a literal'),
    when('classify', is_type(str)).then(lambda x: f'{x} is a string'),
    when('classify', lambda x: isinstance(x, tuple)).then('is a tuple'),
    when('sum', is_type(int), is_type(int)).then(lambda a, b: a + b),
]

test_predicates = [
    ('classify', 42),
    ('classify', 'hello'),
    ('classify', ('nested', 'tuple')),
    ('sum', 10, 20),
    ('sum', 'a', 'b'),  # Won't match
]

for expr in test_predicates:
    result = rewrite(expr, *predicate_rules)
    print(f"{str(expr):30} => {result}")

# 4. Guards (where clauses)
print("\n\n4. Guards (where clauses)")
print("-" * 30)

guard_rules = [
    when('div', _, _).where(lambda a, b: b != 0).then(lambda a, b: a / b),
    when('div', _, _).then('error: division by zero'),
    when('sqrt', _).where(lambda x: x >= 0).then(lambda x: x ** 0.5),
    when('sqrt', _).then('error: negative number'),
]

test_guards = [
    ('div', 10, 2),
    ('div', 10, 0),
    ('sqrt', 16),
    ('sqrt', -4),
]

for expr in test_guards:
    result = rewrite(expr, *guard_rules)
    print(f"{str(expr):20} => {result}")

# 5. Nested patterns
print("\n\n5. Nested Patterns")
print("-" * 30)

nested_rules = [
    when('first', (_, _, _)).then(lambda a, b, c: a),
    when('flatten', ('pair', _, _)).then(lambda a, b: ('list', a, b)),
    when('extract', ('point', '$x', '$y')).then(
        lambda x, y: {'x': x, 'y': y}
    ),
    when('match-shape', ('op', _, ('op', _, _))).then(
        'nested operation detected'
    ),
]

test_nested = [
    ('first', ('a', 'b', 'c')),
    ('flatten', ('pair', 10, 20)),
    ('extract', ('point', 5, 7)),
    ('match-shape', ('op', 1, ('op', 2, 3))),
]

for expr in test_nested:
    result = rewrite(expr, *nested_rules)
    print(f"{str(expr):35} => {result}")

# 6. Complex combinations
print("\n\n6. Complex Combinations")
print("-" * 30)

complex_rules = [
    # Mix of named patterns, predicates, and guards
    when('process', '$op', is_literal, is_literal).where(
        lambda op, a, b: op in ['+', '-', '*', '/']
    ).then(
        lambda op, a, b: {
            '+': a + b,
            '-': a - b,
            '*': a * b,
            '/': a / b if b != 0 else 'error'
        }[op]
    ),
    
    # Nested pattern with mixed matching
    when('transform', ('data', '$type', _)).where(
        lambda type, val: type in ['int', 'float']
    ).then(
        lambda type, val: ('typed', type, val)
    ),
]

test_complex = [
    ('process', '+', 10, 20),
    ('process', '*', 3, 4),
    ('process', '/', 10, 0),
    ('process', 'concat', 'a', 'b'),  # Won't match
    ('transform', ('data', 'int', 42)),
    ('transform', ('data', 'string', 'hello')),  # Won't match
]

for expr in test_complex:
    result = rewrite(expr, *complex_rules)
    print(f"{str(expr):40} => {result}")

print("\n" + "=" * 50)
print("Pattern matching summary:")
print("- _ matches anything")
print("- $name creates named bindings")
print("- Predicates (functions) test values")
print("- .where() adds guard conditions")
print("- Patterns can be arbitrarily nested")
print("- All features compose naturally")