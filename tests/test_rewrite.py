from tree_rewriter import (
    rewrite,
    when,
    _,
    bottom_up,
    commutative,
    is_type,
    is_literal,
    first,
    all,
)


def test_commutative_add_zero():
    rules = [bottom_up(r) for r in commutative('+', 0, lambda x: x)]
    assert rewrite(('+', 0, 'x'), *rules) == 'x'
    assert rewrite(('+', 'x', 0), *rules) == 'x'


def test_bottom_up_recursive_simplification():
    # Simplify nested additions with zero to the inner variable
    rule = bottom_up(when('+', 0, _).then(lambda x: x))
    expr = ('+', 0, ('+', 0, 'x'))
    assert rewrite(expr, rule) == 'x'


def test_first_and_all_combinators():
    r_inc = when('n', is_type(int)).then(lambda n: ('n', n + 1))
    r_double = when('n', is_type(int)).then(lambda n: ('n', n * 2))

    use_first = first(r_double, r_inc)  # r_double applies first
    use_all = all(r_inc, r_double)  # (n + 1) * 2

    assert use_first(('n', 3)) == ('n', 6)
    assert use_all(('n', 3)) == ('n', 8)


def test_where_guard_and_named_vars():
    # Only match positive ints and return their square; transform to a new tag to avoid re-matching
    rule = when('val', '$x').where(lambda x: isinstance(x, int) and x > 0).then(
        lambda x: ('val2', x * x)
    )
    assert rewrite(('val', 5), rule) == ('val2', 25)
    assert rewrite(('val', -2), rule) == ('val', -2)  # guard fails, unchanged


def test_named_variable_must_match_twice():
    # x + x -> 2 * x, but y + z unchanged
    rule = when('+', '$x', '$x').then(lambda x: ('*', 2, x))
    assert rewrite(('+', 'y', 'y'), rule) == ('*', 2, 'y')
    assert rewrite(('+', 'y', 'z'), rule) == ('+', 'y', 'z')


def test_is_type_and_is_literal_predicates():
    num_pred = is_type(int, float)
    assert num_pred(3)
    assert num_pred(2.5)
    assert not num_pred('x')

    assert is_literal(0)
    assert is_literal(1.0)
    assert not is_literal('x')


def test_wildcard_repr_and_non_match_returns_input():
    assert repr(_) == '_'
    # Rule that never matches leaves input unchanged
    never = when('nope').then(42)
    assert rewrite(('ok',), never) == ('ok',)


def test_rewrite_fixed_point_chaining():
    # a -> b, b -> c; fixed-point ends at c
    r1 = when('a').then(('b',))
    r2 = when('b').then(('c',))
    assert rewrite(('a',), r1, r2) == ('c',)


def test_predicate_swap_and_binding_order():
    # Use wildcards to capture both operands and swap; call rule directly to avoid infinite toggling
    swap = when('+', _, _).then(lambda a, b: ('+', b, a))
    assert swap(('+', 1, 2)) == ('+', 2, 1)


def test_literal_addition_simplification():
    # Simplify literal + literal into computed number via bottom_up
    add_lits = when('+', is_literal, is_literal).then(lambda a, b: a + b)
    assert rewrite(('+', 2, 3), bottom_up(add_lits)) == 5


def test_named_var_match_across_subtrees():
    # x + (2*x) -> 3*x
    rule = when('+', '$x', ('*', 2, '$x')).then(lambda x: ('*', 3, x))
    assert rewrite(('+', 'y', ('*', 2, 'y')), rule) == ('*', 3, 'y')


def test_commutative_value_result_mult_by_zero():
    # Multiplication by zero collapses to 0 anywhere in tree
    rules = [bottom_up(r) for r in commutative('*', 0, 0)]
    expr = ('*', 'x', ('*', 0, 'y'))
    assert rewrite(expr, *rules) == 0


def test_when_without_then_is_noop():
    # A rule constructed without then() should be a no-op
    rule = when('tag', _)
    assert rewrite(('tag', 1), rule) == ('tag', 1)


def test_tuple_arity_mismatch_does_not_match():
    # Pattern ('+', _, _) should not match a unary '+'
    rule = when('+', _, _).then(0)
    assert rewrite(('+', 1), rule) == ('+', 1)


def test_predicate_pattern_fails():
    # Test predicate pattern that fails - should return None and leave tree unchanged
    is_negative = lambda x: isinstance(x, int) and x < 0
    rule = when(is_negative).then(0)
    assert rewrite(5, rule) == 5  # Positive number, predicate fails


def test_first_combinator_no_match():
    # Test first() when no rule matches - should return original tree
    r1 = when('never').then('matched1')
    r2 = when('also_never').then('matched2')
    combined = first(r1, r2)
    assert combined(('other',)) == ('other',)


def test_empty_tuple_handling():
    # Test that empty tuples are handled correctly
    rule = when().then('empty')  # Empty pattern matches empty tuple
    assert rewrite((), rule) == 'empty'


def test_bottom_up_with_empty_tuple():
    # Test bottom_up with empty tuple
    rule = bottom_up(when().then('empty'))
    assert rewrite((), rule) == 'empty'


def test_complex_nested_rewriting():
    # Test more complex nested structure rewriting
    # Transform (f (g x)) -> (h x) where both f and g are present
    rule = when('f', ('g', '$x')).then(lambda x: ('h', x))
    tree = ('f', ('g', 'y'))
    assert rewrite(tree, rule) == ('h', 'y')


def test_rule_with_multiple_wildcards():
    # Test a rule with multiple wildcards gets them in correct order
    swap_ends = when('op', _, '$mid', _).then(lambda a, mid, b: ('op', b, mid, a))
    tree = ('op', 1, 'keep', 2)
    result = swap_ends(tree)
    assert result == ('op', 2, 'keep', 1)
