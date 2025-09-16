#!/usr/bin/env python3
"""
Symbolic and Numerical Integration

Handles simple integrals symbolically, but quickly resorts to numerical methods
for anything complex. This mirrors how integration is actually done in practice!
"""

import sys
sys.path.insert(0, '../src')

from tree_rewriter import rewrite, when, _, bottom_up, is_literal
import math
from typing import Callable
import time

print("Integration: Symbolic + Numerical")
print("=" * 50)

# Numerical integration using Simpson's rule
def simpson_integrate(f: Callable[[float], float], a: float, b: float, n: int = 1000) -> float:
    """Integrate f from a to b using Simpson's rule with n intervals."""
    if n % 2 == 1:
        n += 1  # Simpson's rule needs even number of intervals
    
    h = (b - a) / n
    x = a
    sum_odd = 0
    sum_even = 0
    
    for i in range(1, n):
        x = a + i * h
        if i % 2 == 1:
            sum_odd += f(x)
        else:
            sum_even += f(x)
    
    return h / 3 * (f(a) + f(b) + 4 * sum_odd + 2 * sum_even)

# Helper for expression evaluation (reused from advanced calculus)
def eval_expr(expr, x_val):
    """Evaluate expression at given x value."""
    if isinstance(expr, (int, float)):
        return expr
    elif expr == 'x':
        return x_val
    elif isinstance(expr, str):
        if expr == 'pi':
            return math.pi
        elif expr == 'e':
            return math.e
        else:
            return 0  # Unknown constant
    elif isinstance(expr, tuple):
        op = expr[0]
        if op == '+':
            return eval_expr(expr[1], x_val) + eval_expr(expr[2], x_val)
        elif op == '-':
            if len(expr) == 2:
                return -eval_expr(expr[1], x_val)
            else:
                return eval_expr(expr[1], x_val) - eval_expr(expr[2], x_val)
        elif op == '*':
            return eval_expr(expr[1], x_val) * eval_expr(expr[2], x_val)
        elif op == '/':
            denom = eval_expr(expr[2], x_val)
            if denom == 0:
                return float('inf')
            return eval_expr(expr[1], x_val) / denom
        elif op == '^':
            base = eval_expr(expr[1], x_val)
            exp = eval_expr(expr[2], x_val)
            return base ** exp
        elif op == 'sin':
            return math.sin(eval_expr(expr[1], x_val))
        elif op == 'cos':
            return math.cos(eval_expr(expr[1], x_val))
        elif op == 'tan':
            return math.tan(eval_expr(expr[1], x_val))
        elif op == 'exp':
            return math.exp(eval_expr(expr[1], x_val))
        elif op == 'ln':
            arg = eval_expr(expr[1], x_val)
            return math.log(arg) if arg > 0 else float('-inf')
        elif op == 'sqrt':
            return math.sqrt(eval_expr(expr[1], x_val))
        elif op == 'abs':
            return abs(eval_expr(expr[1], x_val))
        else:
            return 0  # Unknown operation
    else:
        return 0

# Check if expression contains variable
def contains_var(expr, var):
    """Check if expression contains the variable."""
    if expr == var:
        return True
    elif isinstance(expr, tuple):
        return any(contains_var(sub, var) for sub in expr[1:])
    else:
        return False

# Integration rules - only the most basic cases
integration_rules = [
    # === Constants ===
    # ∫ c dx = cx + C
    when('int', lambda e: not contains_var(e, 'x'), 'x').then(
        lambda c: ('*', c, 'x')
    ),
    
    # === Power rule ===
    # ∫ x dx = x²/2 + C
    when('int', 'x', 'x').then(('/', ('^', 'x', 2), 2)),
    
    # ∫ x^n dx = x^(n+1)/(n+1) + C  (n ≠ -1)
    when('int', ('^', 'x', is_literal), 'x').where(lambda n: n != -1).then(
        lambda n: ('/', ('^', 'x', n + 1), n + 1)
    ),
    
    # ∫ 1/x dx = ln|x| + C
    when('int', ('/', 1, 'x'), 'x').then(('ln', ('abs', 'x'))),
    
    # === Basic trigonometric ===
    # ∫ sin(x) dx = -cos(x) + C
    when('int', ('sin', 'x'), 'x').then(('-', 0, ('cos', 'x'))),
    
    # ∫ cos(x) dx = sin(x) + C
    when('int', ('cos', 'x'), 'x').then(('sin', 'x')),
    
    # === Basic exponential ===
    # ∫ e^x dx = e^x + C
    when('int', ('exp', 'x'), 'x').then(('exp', 'x')),
    
    # === Sum rule ===
    # ∫ (f + g) dx = ∫f dx + ∫g dx
    when('int', ('+', _, _), '$var').then(
        lambda f, g, var: ('+', ('int', f, var), ('int', g, var))
    ),
    
    # === Constant multiple rule ===
    # ∫ c*f dx = c*∫f dx  (where c doesn't contain x)
    when('int', ('*', lambda c: not contains_var(c, 'x'), _), 'x').then(
        lambda c, f: ('*', c, ('int', f, 'x'))
    ),
    
    # === Everything else: numerical integration ===
    # For any integral we can't handle symbolically
    when('int', _, '$var').then(
        lambda f, var: ('numerical_integral', f, var)
    ),
]

# Function to convert numerical integrals to definite integral values
def evaluate_integral(expr, lower, upper):
    """Evaluate a definite integral from lower to upper."""
    if isinstance(expr, tuple) and expr[0] == 'numerical_integral':
        # Extract the integrand
        integrand = expr[1]
        
        # Create function to integrate
        def f(x):
            return eval_expr(integrand, x)
        
        # Use numerical integration
        return simpson_integrate(f, lower, upper)
    
    elif isinstance(expr, tuple):
        # For symbolic results, evaluate at upper - lower
        upper_val = eval_expr(expr, upper)
        lower_val = eval_expr(expr, lower)
        return upper_val - lower_val
    
    else:
        return float(expr) * (upper - lower)

# Test cases showing progression from symbolic to numerical
test_cases = [
    # Simple symbolic cases
    ("Constant", 5),
    ("Linear", 'x'),
    ("Quadratic", ('^', 'x', 2)),
    ("Polynomial", ('^', 'x', 5)),
    ("Reciprocal", ('/', 1, 'x')),
    
    # Basic trig/exp
    ("Sine", ('sin', 'x')),
    ("Cosine", ('cos', 'x')),
    ("Exponential", ('exp', 'x')),
    
    # Cases that require numerical integration
    ("Gaussian", ('exp', ('-', 0, ('^', 'x', 2)))),
    ("Sin(x²)", ('sin', ('^', 'x', 2))),
    ("x*sin(x)", ('*', 'x', ('sin', 'x'))),
    ("Rational", ('/', 1, ('+', 1, ('^', 'x', 2)))),
    ("Complex", ('*', ('exp', ('-', 0, 'x')), ('sin', 'x'))),
    ("Elliptic-like", ('sqrt', ('-', 1, ('^', 'x', 2)))),
]

print("\nIndefinite integrals:\n")

for name, expr in test_cases:
    integral_expr = ('int', expr, 'x')
    result = rewrite(integral_expr, *[bottom_up(r) for r in integration_rules])
    
    if isinstance(result, tuple) and result[0] == 'numerical_integral':
        print(f"{name:15} ∫ {str(expr):25} dx => [numerical integration required]")
    else:
        print(f"{name:15} ∫ {str(expr):25} dx => {result} + C")

# Definite integral examples
print("\n" + "=" * 50)
print("Definite integrals (comparing symbolic vs numerical):\n")

definite_tests = [
    # (name, expression, lower, upper, expected)
    ("Area under x²", ('^', 'x', 2), 0, 1, 1/3),
    ("Sin over period", ('sin', 'x'), 0, math.pi, 2),
    ("Gaussian", ('exp', ('-', 0, ('^', 'x', 2))), -2, 2, None),
    ("Circle area", ('sqrt', ('-', 1, ('^', 'x', 2))), -1, 1, math.pi/2),
]

for name, expr, a, b, expected in definite_tests:
    # Get indefinite integral
    integral_expr = ('int', expr, 'x')
    indefinite = rewrite(integral_expr, *[bottom_up(r) for r in integration_rules])
    
    # Evaluate definite integral
    value = evaluate_integral(indefinite, a, b)
    
    print(f"{name:20} ∫[{a},{b}] {str(expr):20} dx = {value:.6f}", end="")
    if expected:
        error = abs(value - expected)
        print(f" (error: {error:.2e})")
    else:
        print()

# Advanced example: Fourier coefficients
print("\n" + "=" * 50)
print("Advanced example: Computing Fourier coefficients\n")

def fourier_coefficient(f_expr, n, period=2*math.pi):
    """Compute the nth Fourier coefficient of f."""
    # a_n = (2/T) ∫[0,T] f(x)cos(2πnx/T) dx
    integrand = ('*', f_expr, ('cos', ('*', ('/', ('*', 2, 'pi', n), period), 'x')))
    integral = ('int', integrand, 'x')
    
    # Try symbolic first
    result = rewrite(integral, *[bottom_up(r) for r in integration_rules])
    
    # Evaluate over period
    coeff = (2/period) * evaluate_integral(result, 0, period)
    return coeff

# Square wave Fourier series
print("Fourier coefficients for square wave f(x) = sign(sin(x)):")
for n in range(0, 6):
    # For square wave, we know it's mostly numerical
    # But our system will try symbolic first
    coeff = fourier_coefficient(('sign', ('sin', 'x')), n)
    print(f"  a_{n} = {coeff:.6f}")

# Performance comparison
print("\n" + "=" * 50)
print("Performance: When to use numerical integration\n")


test_func = ('exp', ('-', 0, ('^', 'x', 2)))  # Gaussian

# Symbolic attempt
start = time.time()
integral = ('int', test_func, 'x')
symbolic_result = rewrite(integral, *[bottom_up(r) for r in integration_rules])
symbolic_time = time.time() - start

# Numerical integration
start = time.time()
numerical_result = simpson_integrate(lambda x: eval_expr(test_func, x), -3, 3)
numerical_time = time.time() - start

print("Gaussian integral ∫ e^(-x²) dx from -3 to 3:")
print(f"  Symbolic attempt: {symbolic_result}")
print(f"  Time: {symbolic_time*1000:.3f} ms")
print(f"  \nNumerical result: {numerical_result:.6f}")
print(f"  Time: {numerical_time*1000:.3f} ms")
print(f"  (Exact value: {math.sqrt(math.pi) * math.erf(3):.6f})")

print("\n" + "=" * 50)
print("Key insights:")
print("- Most integrals don't have closed forms!")
print("- Symbolic integration for simple cases")
print("- Immediate fallback to numerical for complex cases")
print("- Numerical methods are often more practical")
print("- This hybrid approach mirrors real mathematical practice")
