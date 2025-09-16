"""Tree Rewriter - A minimal term rewriting system

The essence: Apply rules to trees until nothing changes.

Core concepts:
- Trees are nested tuples (S-expressions) or atomic values
- Rules are functions that transform trees
- Rewriting applies rules until a fixed point is reached
- Pattern matching uses wildcards (_) and named variables ($x)
"""

from typing import Any, Callable, Dict, Final, List, Optional, Tuple, Union, cast

# === Type Definitions ===
# Trees are either atomic values or nested tuples (S-expressions)
Atom = Union[str, int, float, bool, complex, None]
Tree = Union[Atom, Tuple[Any, ...]]
Rule = Callable[[Tree], Tree]
Predicate = Callable[[Tree], bool]


# === Core Rewriting Engine ===

def rewrite(tree: Tree, *rules: Rule) -> Tree:
    """Apply rules to a tree until no more changes occur (fixed point).

    This is the heart of term rewriting: repeatedly apply transformation rules
    until the tree stabilizes. Rules are tried in order, and whenever one
    succeeds, we restart from the first rule.

    Args:
        tree: The tree to transform
        *rules: Transformation rules to apply

    Returns:
        The tree after all possible transformations
    """
    while True:
        for rule in rules:
            new_tree = rule(tree)
            if new_tree != tree:
                tree = new_tree
                break
        else:
            # No rule changed the tree - we've reached a fixed point
            return tree


# === Tree Traversal Strategies ===

def bottom_up(rule: Rule) -> Rule:
    """Apply a rule bottom-up through the tree structure.

    First recursively transforms all subtrees, then applies the rule
    to the current node. This ensures inner transformations happen
    before outer ones.

    Args:
        rule: The rule to apply at each node

    Returns:
        A new rule that applies the original rule bottom-up
    """
    def transform(tree: Tree) -> Tree:
        # First, recursively transform all children
        if isinstance(tree, tuple) and tree:
            head = tree[0]
            children = tuple(transform(child) for child in tree[1:])
            tree = (head,) + children

        # Then apply the rule to this node
        return rule(tree)

    return transform


# === Pattern Matching and Rule Construction ===

class when:
    """Build transformation rules with a fluent interface.

    The when/then pattern makes rules read like natural language:

    Examples:
        when('+', 0, _).then(lambda x: x)     # 0 + x => x
        when('+', _, 0).then(lambda x: x)     # x + 0 => x
        when('*', 0, _).then(0)               # 0 * x => 0
        when('*', _, 0).then(0)               # x * 0 => 0

    Pattern elements:
        _ : wildcard, matches anything
        $var : named variable, must match consistently
        literal : exact match
        callable : predicate function
    """
    def __init__(self, *pattern: Any) -> None:
        self.pattern: Tuple[Any, ...] = pattern
        self.guard: Optional[Predicate] = None
        self.transform: Optional[Callable[..., Tree]] = None
    
    def where(self, predicate: Predicate) -> "when":
        """Add a guard condition that must be satisfied for the rule to apply.

        Args:
            predicate: Function that takes bound variables and returns bool

        Returns:
            Self for method chaining
        """
        self.guard = predicate
        return self
    
    def then(self, result: Union[Callable[..., Tree], Tree]) -> "when":
        """Define what to produce when the pattern matches.

        Args:
            result: Either a constant value or a function taking bound variables

        Returns:
            Self for method chaining
        """
        if callable(result):
            self.transform = result
        else:
            self.transform = lambda *_: result
        return self
    
    def __call__(self, tree: Tree) -> Tree:
        """Apply this rule to a tree.

        Args:
            tree: The tree to potentially transform

        Returns:
            Either the transformed tree or the original tree if no match
        """
        bindings = self._match(self.pattern, tree)
        if bindings is not None:
            # Pattern matched - check guard condition if present
            if self.guard is None or self.guard(*bindings.values()):
                # Guard passed - apply transformation if defined
                if self.transform is not None:
                    return self.transform(*bindings.values())

        # No match, guard failed, or no transformation - return unchanged
        return tree
    
    def _match(
        self, pattern: Any, tree: Tree, bindings: Optional[Dict[str, Tree]] = None
    ) -> Optional[Dict[str, Tree]]:
        """Match pattern against tree, collecting variable bindings.

        Args:
            pattern: The pattern to match (can contain wildcards, variables, literals)
            tree: The tree to match against
            bindings: Existing variable bindings (for recursive calls)

        Returns:
            Dict of variable bindings if match succeeds, None if it fails
        """
        if bindings is None:
            bindings = {}

        # Predicate patterns: callable functions that test the tree
        if callable(pattern) and not isinstance(pattern, type):
            predicate = cast(Predicate, pattern)
            if predicate(tree):
                # Generate anonymous binding for predicate matches
                binding_name = f"_{len(bindings)}"
                bindings[binding_name] = tree
                return bindings
            return None

        # Wildcard patterns: _ matches anything
        if pattern is _ or pattern == "_":
            binding_name = f"_{len(bindings)}"
            bindings[binding_name] = tree
            return bindings

        # Named variable patterns: $name must match consistently
        if isinstance(pattern, str) and pattern.startswith("$"):
            if pattern in bindings:
                # Variable already bound - must match the same value
                return bindings if bindings[pattern] == tree else None
            else:
                # First occurrence - bind the variable
                bindings[pattern] = tree
                return bindings

        # Literal patterns: exact equality
        if pattern == tree:
            return bindings

        # Tuple patterns: recursive matching of structure
        if isinstance(pattern, tuple) and isinstance(tree, tuple):
            if len(pattern) != len(tree):
                return None
            # All sub-patterns must match
            for pattern_elem, tree_elem in zip(pattern, tree):
                if self._match(pattern_elem, tree_elem, bindings) is None:
                    return None
            return bindings

        # No match
        return None


class Wildcard:
    """Represents a wildcard pattern that matches anything."""

    def __repr__(self) -> str:
        return "_"

_: Final[Wildcard] = Wildcard()


# === Rule Construction Helpers ===


def commutative(op: Any, value: Any, result: Union[Callable[..., Tree], Tree]) -> List[Rule]:
    """Create rules for commutative binary operations.

    Generates two rules: (op, value, _) and (op, _, value) both producing the same result.
    This handles the fact that commutative operators like + and * work both ways.

    Args:
        op: The operator (typically a string like '+' or '*')
        value: The special value to match
        result: What to produce when the pattern matches

    Returns:
        List of two rules covering both orders

    Example:
        commutative('+', 0, lambda x: x)  # Creates rules for 0+x and x+0 => x
    """
    return [when(op, value, _).then(result), when(op, _, value).then(result)]


# Type matching helper
def is_type(*types: type[Any]) -> Predicate:
    """Create a predicate that matches any of the given types.

    Args:
        *types: One or more types to match against

    Returns:
        A predicate function that returns True if the value is any of those types

    Example:
        is_number = is_type(int, float)  # Matches integers or floats
    """
    return lambda x: isinstance(x, types)


# Common predicates
is_literal: Predicate = is_type(int, float, bool, complex, type(None))
"""Predicate that matches self-evaluating values (literals)."""


# === Composition helpers ===

def first(*rules: Rule) -> Rule:
    """Try rules in order, return result from first that changes the tree.

    This implements 'choice' - apply the first rule that produces a different result.
    Useful for trying alternative transformations in order of preference.

    Args:
        *rules: Rules to try in order

    Returns:
        A rule that applies the first successful transformation
    """
    def combined(tree: Tree) -> Tree:
        for rule in rules:
            result = rule(tree)
            if result != tree:
                return result
        return tree

    return combined


def all(*rules: Rule) -> Rule:
    """Apply all rules in sequence (composition).

    Each rule receives the result of the previous rule. This implements
    sequential composition of transformations.

    Args:
        *rules: Rules to apply in order

    Returns:
        A rule that applies all transformations sequentially
    """
    def combined(tree: Tree) -> Tree:
        for rule in rules:
            tree = rule(tree)
        return tree

    return combined


