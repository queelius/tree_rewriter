#!/usr/bin/env python3
"""
Symbolic Differentiation - First Year Calculus

Complete implementation of differentiation rules using tree rewriting.
"""

import sys
sys.path.insert(0, '../src')

from tree_rewriter import rewrite, when, _, bottom_up, is_literal

print("Symbolic Differentiation")
print("=" * 50)

# Helper to check if something is constant with respect to variable
def is_const_wrt(var):
    """Returns predicate that checks if expression is constant w.r.t. var"""
    def check(expr):
        if expr == var:
            return False
        if isinstance(expr, (int, float)):
            return True
        if isinstance(expr, str) and expr != var:
            return True
        if isinstance(expr, tuple):
            # Recursively check all subexpressions
            return all(check(sub) for sub in expr[1:])
        return True
    return check

# Differentiation rules for d/dx
# We'll use ('d', expr, var) to represent d(expr)/d(var)
diff_rules = [
    # === Basic Rules ===
    
    # Constant rule: d(c)/dx = 0
    when('d', is_const_wrt('x'), 'x').then(0),
    
    # Variable rule: d(x)/dx = 1
    when('d', 'x', 'x').then(1),
    
    # === Arithmetic Rules ===
    
    # Sum rule: d(u + v)/dx = du/dx + dv/dx
    when('d', ('+', _, _), '$var').then(
        lambda u, v, var: ('+', ('d', u, var), ('d', v, var))
    ),
    
    # Difference rule: d(u - v)/dx = du/dx - dv/dx
    when('d', ('-', _, _), '$var').then(
        lambda u, v, var: ('-', ('d', u, var), ('d', v, var))
    ),
    
    # Product rule: d(u * v)/dx = u * dv/dx + v * du/dx
    when('d', ('*', _, _), '$var').then(
        lambda u, v, var: ('+', 
            ('*', u, ('d', v, var)),
            ('*', v, ('d', u, var)))
    ),
    
    # Quotient rule: d(u/v)/dx = (v * du/dx - u * dv/dx) / v²
    when('d', ('/', _, _), '$var').then(
        lambda u, v, var: ('/', 
            ('-',
                ('*', v, ('d', u, var)),
                ('*', u, ('d', v, var))),
            ('^', v, 2))
    ),
    
    # Power rule: d(x^n)/dx = n * x^(n-1) where n is constant
    when('d', ('^', 'x', is_literal), 'x').then(
        lambda n: ('*', n, ('^', 'x', n - 1))
    ),
    
    # General power rule: d(u^n)/dx = n * u^(n-1) * du/dx
    when('d', ('^', _, is_literal), '$var').then(
        lambda u, n, var: ('*', 
            ('*', n, ('^', u, n - 1)),
            ('d', u, var))
    ),
    
    # === Exponential and Logarithmic ===
    
    # d(e^x)/dx = e^x
    when('d', ('exp', 'x'), 'x').then(('exp', 'x')),
    
    # d(e^u)/dx = e^u * du/dx
    when('d', ('exp', _), '$var').then(
        lambda u, var: ('*', ('exp', u), ('d', u, var))
    ),
    
    # d(ln(x))/dx = 1/x
    when('d', ('ln', 'x'), 'x').then(('/', 1, 'x')),
    
    # d(ln(u))/dx = (1/u) * du/dx
    when('d', ('ln', _), '$var').then(
        lambda u, var: ('*', ('/', 1, u), ('d', u, var))
    ),
    
    # d(a^x)/dx = a^x * ln(a) where a is constant
    when('d', ('^', is_const_wrt('x'), 'x'), 'x').then(
        lambda a: ('*', ('^', a, 'x'), ('ln', a))
    ),
    
    # === Trigonometric Functions ===
    
    # d(sin(x))/dx = cos(x)
    when('d', ('sin', 'x'), 'x').then(('cos', 'x')),
    
    # d(cos(x))/dx = -sin(x)
    when('d', ('cos', 'x'), 'x').then(('-', 0, ('sin', 'x'))),
    
    # d(tan(x))/dx = sec²(x) = 1/cos²(x)
    when('d', ('tan', 'x'), 'x').then(('/', 1, ('^', ('cos', 'x'), 2))),
    
    # Chain rule versions for trig
    when('d', ('sin', _), '$var').then(
        lambda u, var: ('*', ('cos', u), ('d', u, var))
    ),
    
    when('d', ('cos', _), '$var').then(
        lambda u, var: ('*', ('-', 0, ('sin', u)), ('d', u, var))
    ),
    
    when('d', ('tan', _), '$var').then(
        lambda u, var: ('*', ('/', 1, ('^', ('cos', u), 2)), ('d', u, var))
    ),
    
    # === Inverse Trigonometric ===
    
    # d(arcsin(x))/dx = 1/√(1-x²)
    when('d', ('arcsin', 'x'), 'x').then(
        ('/', 1, ('sqrt', ('-', 1, ('^', 'x', 2))))
    ),
    
    # d(arccos(x))/dx = -1/√(1-x²)
    when('d', ('arccos', 'x'), 'x').then(
        ('-', 0, ('/', 1, ('sqrt', ('-', 1, ('^', 'x', 2)))))
    ),
    
    # d(arctan(x))/dx = 1/(1+x²)
    when('d', ('arctan', 'x'), 'x').then(
        ('/', 1, ('+', 1, ('^', 'x', 2)))
    ),
    
    # === Special Functions ===
    
    # d(sqrt(x))/dx = 1/(2*sqrt(x))
    when('d', ('sqrt', 'x'), 'x').then(
        ('/', 1, ('*', 2, ('sqrt', 'x')))
    ),
    
    # d(sqrt(u))/dx = 1/(2*sqrt(u)) * du/dx
    when('d', ('sqrt', _), '$var').then(
        lambda u, var: ('*', ('/', 1, ('*', 2, ('sqrt', u))), ('d', u, var))
    ),
    
    # d(abs(x))/dx = x/abs(x) = sign(x) for x ≠ 0
    when('d', ('abs', 'x'), 'x').then(('sign', 'x')),
]

# Simplification rules to clean up results
simplify_rules = [
    # Arithmetic
    when('+', 0, _).then(lambda x: x),
    when('+', _, 0).then(lambda x: x),
    when('*', 0, _).then(0),
    when('*', _, 0).then(0),
    when('*', 1, _).then(lambda x: x),
    when('*', _, 1).then(lambda x: x),
    when('-', _, 0).then(lambda x: x),
    when('-', 0, _).then(lambda x: ('-', x)),
    when('/', _, 1).then(lambda x: x),
    when('^', _, 0).then(1),
    when('^', _, 1).then(lambda x: x),
    
    # Constant folding
    when('+', is_literal, is_literal).then(lambda a, b: a + b),
    when('-', is_literal, is_literal).then(lambda a, b: a - b),
    when('*', is_literal, is_literal).then(lambda a, b: a * b),
    when('/', is_literal, is_literal).where(lambda a, b: b != 0).then(lambda a, b: a / b),
    
    # Negation
    when('-', _).then(lambda x: ('*', -1, x)),
]

# Test cases from a first-year calculus book
test_cases = [
    # Basic
    ("Constant", 5),
    ("Variable", 'x'),
    ("Other variable", 'y'),
    
    # Polynomials
    ("Linear", ('+', ('*', 3, 'x'), 5)),
    ("Quadratic", ('+', ('^', 'x', 2), ('*', 3, 'x'))),
    ("Cubic", ('^', 'x', 3)),
    ("Polynomial", ('+', ('*', 2, ('^', 'x', 3)), ('-', ('^', 'x', 2), 'x'))),
    
    # Products and quotients
    ("Product", ('*', 'x', ('sin', 'x'))),
    ("Quotient", ('/', 'x', ('+', 'x', 1))),
    ("Complex product", ('*', ('^', 'x', 2), ('exp', 'x'))),
    
    # Exponentials and logs
    ("Exponential", ('exp', 'x')),
    ("Natural log", ('ln', 'x')),
    ("Exponential chain", ('exp', ('^', 'x', 2))),
    ("Log chain", ('ln', ('+', 'x', 1))),
    
    # Trigonometric
    ("Sine", ('sin', 'x')),
    ("Cosine", ('cos', 'x')),
    ("Tangent", ('tan', 'x')),
    ("Trig chain", ('sin', ('*', 2, 'x'))),
    ("Complex trig", ('*', 'x', ('cos', ('^', 'x', 2)))),
    
    # Inverse trig
    ("Arcsine", ('arcsin', 'x')),
    ("Arctangent", ('arctan', 'x')),
    
    # Special functions
    ("Square root", ('sqrt', 'x')),
    ("Root of polynomial", ('sqrt', ('+', ('^', 'x', 2), 1))),
]

print("\nDifferentiating expressions (d/dx):\n")

all_rules = diff_rules + simplify_rules

for name, expr in test_cases:
    # Compute derivative
    deriv_expr = ('d', expr, 'x')
    result = rewrite(deriv_expr, *[bottom_up(r) for r in all_rules])
    
    print(f"{name:20} {str(expr):30} => {result}")

# More complex example
print("\n" + "=" * 50)
print("Complex example: Quotient rule with chain rule\n")

complex_expr = ('/', 
    ('sin', ('*', 2, 'x')),
    ('+', ('^', 'x', 2), 1))

print(f"f(x) = {complex_expr}")
print(f"\nf'(x) = {rewrite(('d', complex_expr, 'x'), *[bottom_up(r) for r in all_rules])}")

print("\n" + "=" * 50)
print("Key insights:")
print("- All standard differentiation rules can be expressed as patterns")
print("- Chain rule emerges naturally from bottom-up evaluation")
print("- Pattern matching handles the case analysis")
print("- Could extend with more functions (sinh, cosh, etc.)")
print("- Simplification rules clean up the output")