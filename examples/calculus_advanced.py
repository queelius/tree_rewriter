#!/usr/bin/env python3
"""
Advanced Differentiation - Symbolic and Numerical

When symbolic differentiation fails, we return a numerical approximation function.
This showcases the power of mixing symbolic manipulation with Python computation.
"""

import sys
sys.path.insert(0, '../src')

from tree_rewriter import rewrite, when, _, bottom_up
import math

print("Advanced Differentiation: Symbolic + Numerical")
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

# Helper to create numerical derivative function
def numerical_derivative(f, h=1e-7):
    """Returns a function that computes f'(x) numerically using central differences."""
    def df(x):
        return (f(x + h) - f(x - h)) / (2 * h)
    return df

# Helper to evaluate expression at given x value
def eval_expr(expr, x_val):
    """Evaluate expression at given x value."""
    if isinstance(expr, (int, float)):
        return expr
    elif expr == 'x':
        return x_val
    elif isinstance(expr, str):
        # Other variables/constants
        if expr == 'pi':
            return math.pi
        elif expr == 'e':
            return math.e
        else:
            raise ValueError(f"Unknown variable: {expr}")
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
            return eval_expr(expr[1], x_val) / eval_expr(expr[2], x_val)
        elif op == '^':
            base = eval_expr(expr[1], x_val)
            exp = eval_expr(expr[2], x_val)
            # Handle special cases like 0^0
            if base == 0 and exp == 0:
                return 1  # Convention
            return base ** exp
        elif op == 'sin':
            return math.sin(eval_expr(expr[1], x_val))
        elif op == 'cos':
            return math.cos(eval_expr(expr[1], x_val))
        elif op == 'exp':
            return math.exp(eval_expr(expr[1], x_val))
        elif op == 'ln':
            arg = eval_expr(expr[1], x_val)
            if arg <= 0:
                raise ValueError(f"ln of non-positive number: {arg}")
            return math.log(arg)
        elif op == 'abs':
            return abs(eval_expr(expr[1], x_val))
        elif op == 'gamma':
            return math.gamma(eval_expr(expr[1], x_val))
        elif op == 'erf':
            return math.erf(eval_expr(expr[1], x_val))
        elif op == 'sqrt':
            return math.sqrt(eval_expr(expr[1], x_val))
        elif op == 'sign':
            val = eval_expr(expr[1], x_val)
            return 1 if val > 0 else (-1 if val < 0 else 0)
        elif op == 'integral':
            # For demo, just return 0 (would need numerical integration in practice)
            return 0.0
        else:
            # For unknown operations, return 0
            return 0.0
    else:
        raise ValueError(f"Cannot evaluate: {expr}")

# Extended differentiation rules including special cases
diff_rules = [
    # === Standard rules (as before) ===
    when('d', is_const_wrt('x'), 'x').then(0),
    when('d', 'x', 'x').then(1),
    
    # Sum and product rules
    when('d', ('+', _, _), '$var').then(
        lambda u, v, var: ('+', ('d', u, var), ('d', v, var))
    ),
    when('d', ('*', _, _), '$var').then(
        lambda u, v, var: ('+', 
            ('*', u, ('d', v, var)),
            ('*', v, ('d', u, var)))
    ),
    
    # Basic functions
    when('d', ('sin', 'x'), 'x').then(('cos', 'x')),
    when('d', ('cos', 'x'), 'x').then(('-', 0, ('sin', 'x'))),
    when('d', ('exp', 'x'), 'x').then(('exp', 'x')),
    when('d', ('ln', 'x'), 'x').then(('/', 1, 'x')),
    
    # === Special functions that don't have elementary derivatives ===
    
    # Error function: erf'(x) = (2/√π) * e^(-x²)
    when('d', ('erf', 'x'), 'x').then(
        ('*', ('/', 2, ('sqrt', 'pi')), ('exp', ('-', 0, ('^', 'x', 2))))
    ),
    
    # Gamma function: Γ'(x) = Γ(x) * ψ(x) where ψ is the digamma function
    # We can't express ψ symbolically, so return a numerical function
    when('d', ('gamma', _), 'x').then(
        lambda u: ('numerical_derivative', ('gamma', u))
    ),
    
    # === Non-differentiable cases ===
    
    # Absolute value at 0 is not differentiable
    # But we can return a subgradient or numerical approximation
    when('d', ('abs', 'x'), 'x').then(
        ('sign', 'x')  # This is undefined at 0, but we'll handle it numerically
    ),
    
    # === Implicit functions and integrals ===
    
    # Derivative of integral: d/dx ∫f(t)dt from a to x = f(x) (fundamental theorem)
    when('d', ('integral', _, 'a', 'x'), 'x').then(
        lambda f, a: f  # Assuming f doesn't depend on x
    ),
    
    # For more complex cases, fall back to numerical
    when('d', ('integral', _, _, _), 'x').then(
        lambda f, a, b: ('numerical_derivative', ('integral', f, a, b))
    ),
    
    # === Fallback rule for unknown functions ===
    
    # If we don't know how to differentiate it, return numerical derivative
    when('d', _, 'x').then(
        lambda expr: ('numerical_derivative', expr)
    ),
]

# Function to convert numerical_derivative nodes to actual Python functions
def resolve_numerical(expr):
    """Convert ('numerical_derivative', expr) nodes to actual Python functions."""
    if isinstance(expr, tuple) and expr[0] == 'numerical_derivative':
        # Create a function that numerically differentiates the expression
        inner_expr = expr[1]
        
        def f(x):
            return eval_expr(inner_expr, x)
        
        df = numerical_derivative(f)
        
        # Return a special node that represents this function
        return ('function', df, f"d/dx[{inner_expr}]")
    
    elif isinstance(expr, tuple):
        # Recursively process subexpressions
        return (expr[0],) + tuple(resolve_numerical(e) for e in expr[1:])
    else:
        return expr

# Test cases including non-elementary derivatives
test_cases = [
    # Standard cases
    ("Polynomial", ('^', 'x', 3)),
    ("Sine", ('sin', 'x')),
    
    # Special functions
    ("Error function", ('erf', 'x')),
    ("Gamma function", ('gamma', 'x')),
    
    # Non-differentiable at points
    ("Absolute value", ('abs', 'x')),
    
    # Composite with special functions
    ("Erf composite", ('erf', ('^', 'x', 2))),
    ("Gamma composite", ('gamma', ('+', 'x', 1))),
    
    # Integral (as a function)
    ("Integral", ('integral', ('sin', 't'), 0, 'x')),
    
    # Unknown function
    ("Unknown function", ('bessel_j', 0, 'x')),
]

print("\nDifferentiating expressions:\n")

all_rules = diff_rules

for name, expr in test_cases:
    # Compute derivative
    deriv_expr = ('d', expr, 'x')
    result = rewrite(deriv_expr, *[bottom_up(r) for r in all_rules])
    result = resolve_numerical(result)
    
    if isinstance(result, tuple) and result[0] == 'function':
        print(f"{name:20} {str(expr):30} => {result[2]}")
        # Test the numerical function
        _, df, _ = result
        print(f"{'':20} {'':30}    f'(1.0) ≈ {df(1.0):.6f}")
    else:
        print(f"{name:20} {str(expr):30} => {result}")

# Example: Piecewise function that's not differentiable everywhere
print("\n" + "=" * 50)
print("Advanced example: Piecewise function\n")

# Define a custom piecewise function
def piecewise_func(x):
    if x < 0:
        return x**2
    elif x == 0:
        return 0
    else:
        return math.sin(x)

# Create numerical derivative
piecewise_deriv = numerical_derivative(piecewise_func)

print("Piecewise function f(x) = { x² if x<0, 0 if x=0, sin(x) if x>0 }")
print("\nNumerical derivatives at various points:")
test_points = [-1, -0.1, -0.001, 0.001, 0.1, 1]
for x in test_points:
    try:
        df = piecewise_deriv(x)
        print(f"  f'({x:6.3f}) ≈ {df:8.6f}")
    except Exception:
        print(f"  f'({x:6.3f}) = undefined")

print("\n" + "=" * 50)
print("Mixed symbolic/numerical example:\n")

# Expression with both symbolic and numerical parts
mixed_expr = ('+', ('sin', 'x'), ('gamma', 'x'))
print(f"f(x) = {mixed_expr}")

deriv_expr = ('d', mixed_expr, 'x')
result = rewrite(deriv_expr, *[bottom_up(r) for r in all_rules])
result = resolve_numerical(result)

print(f"f'(x) = {result}")

# The result is a sum of symbolic and numerical parts
# We can still evaluate it
def eval_mixed(expr, x_val):
    """Evaluate expression that may contain function nodes."""
    if isinstance(expr, tuple) and expr[0] == 'function':
        _, f, _ = expr
        return f(x_val)
    elif isinstance(expr, tuple) and expr[0] == '+':
        return eval_mixed(expr[1], x_val) + eval_mixed(expr[2], x_val)
    else:
        return eval_expr(expr, x_val)

print("\nEvaluating at x = 2.0:")
print(f"f'(2.0) ≈ {eval_mixed(result, 2.0):.6f}")

print("\n" + "=" * 50)
print("Key insights:")
print("- Symbolic differentiation when possible")
print("- Numerical approximation as fallback")
print("- Functions as first-class values in our tree")
print("- Seamless integration of symbolic and numerical methods")
print("- This is the power of embedding in Python!")
