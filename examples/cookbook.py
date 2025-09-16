#!/usr/bin/env python3
"""
Cookbook: Patterns that keep the core tight while adding expressiveness.
This file demonstrates small helpers with tiny assertions.
"""

from tree_rewriter import rewrite, when, _, bottom_up, first, all


# --- Helpers ---

def repeat(rule):
    """Apply a rule at a node until it stops changing that node."""
    def r(t):
        while True:
            new = rule(t)
            if new == t:
                return t
            t = new
    return r


def top_down(rule):
    """Apply rule pre-order (before visiting children), then again after children."""
    def walk(t):
        t2 = rule(t)
        if isinstance(t2, tuple):
            t2 = (t2[0],) + tuple(walk(ch) for ch in t2[1:])
        return rule(t2)
    return walk


def var(name):
    return f"${name}"


def op(name, *args):
    return (name, *args)


def is_op(name):
    return lambda t: isinstance(t, tuple) and t[0] == name


def is_symbol(x):
    return isinstance(x, str) and not x.startswith('$')


def is_number(x):
    return isinstance(x, (int, float, complex))


def is_zero(x):
    return x == 0


def is_one(x):
    return x == 1


def where_all(*preds):
    return lambda *xs: all(p(*xs) for p in preds)


def where_any(*preds):
    return lambda *xs: any(p(*xs) for p in preds)


def negate(pred):
    return lambda *xs: not pred(*xs)


def normalize_commutative(op_name):
    return when(op_name, _, _).then(lambda a, b: (op_name,) + tuple(sorted((a, b), key=str)))


# --- Demos ---

def demo_repeat_flatten():
    # Flatten nested binary '*' into a wider tuple using a local, convergent transformation
    flatten_left = when('*', ('*', _, _), _).then(lambda a, b, c: ('*', a, b, c))
    flatten_right = when('*', _, ('*', _, _)).then(lambda a, b, c: ('*', a, b, c))
    flattener = repeat(first(flatten_left, flatten_right))
    expr = ('*', ('*', 'a', ('*', 'b', 'c')), 'd')
    out = rewrite(expr, bottom_up(flattener))
    assert out == ('*', 'a', 'b', 'c', 'd')


def demo_top_down_normalize():
    # Normalize order for '+' pairs before descending
    norm_plus = normalize_commutative('+')
    expr = ('+', 'y', ('+', 'b', 'a'))
    out = rewrite(expr, top_down(norm_plus))
    assert out == ('+', 'y', ('+', 'a', 'b'))


def demo_var_op_readability():
    # Use var/op to make patterns and trees more readable
    rule = when('+', var('x'), 0).then(lambda x: x)
    expr = op('+', 'z', 0)
    assert rewrite(expr, bottom_up(rule)) == 'z'


def demo_predicates_and_guards():
    # Double positive integers only
    rule = when(var('x')).where(where_all(lambda x: isinstance(x, int), lambda x: x > 0)).then(
        lambda x: x * 2
    )
    assert rewrite(5, rule) == 10
    assert rewrite(-3, rule) == -3


def demo_commutative_normalization():
    # Canonicalize '*' argument order, then match a specific pattern more reliably
    norm_mul = normalize_commutative('*')
    # After normalization, ('*', 'x', 2) and ('*', 2, 'x') both become ('*', 2, 'x')
    rule = when('*', 2, 'x').then(lambda: ('+', 'x', 'x'))
    pipeline = all(top_down(norm_mul), bottom_up(rule))
    assert rewrite(('*', 'x', 2), pipeline) == ('+', 'x', 'x')
    assert rewrite(('*', 2, 'x'), pipeline) == ('+', 'x', 'x')


if __name__ == '__main__':
    demo_repeat_flatten()
    demo_top_down_normalize()
    demo_var_op_readability()
    demo_predicates_and_guards()
    demo_commutative_normalization()
    print('Cookbook demos passed.')
