"""Tree Rewriter - A minimal term rewriting system."""

__version__ = '0.1.0'

from .tree_rewriter import (
    rewrite, when, _, bottom_up, commutative,
    is_literal, is_type,
    first, all
)

__all__ = [
    'rewrite', 'when', '_', 'bottom_up', 'commutative',
    'is_literal', 'is_type',
    'first', 'all'
]
