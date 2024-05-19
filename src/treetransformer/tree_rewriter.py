import treenode as tn
from copy import deepcopy
from functools import reduce
import random
import logging


def rewrite(rules = [
        rewrite_repeated_application({'+': '*', '*': '**'}),
        simplify_identities({'+': 0, '*': 1, 'max': -float('inf')}),
        simplify_reduce({'+': sum, 'max': max,
                         '*': lambda x: reduce(lambda x, y: x * y, x, 1)}),
        make_substitutions],
        max_rewrites=int(1e5),
        randomize=False):
    
    """
    Rewrite a tree using a set of rewrite rules.

    This function is a generator that takes a set of rewrite rules and
    returns a function that takes a NestedTree node and a context, and
    applies the set of rewrite rules to the node until a fixed point is reached.
    
    It is used to rewrite expressions, where the rewrite rules are functions
    that take a node and a context and return a new node.

    This is to be used with the `visit` method of `NestedTree`. The order
    of the traversal of nodes can be specified with the `order` parameter.
    If doing a tree rewrite, it is common to use a pre-order traversal for
    top-down rewrites, but post-order traversal can also be used for bottom-up
    rewrites, such as simplifying a tree by applying a set of rules to the
    leaves first. The most aggressive rewrite would be to reduce an entire
    tree to a single node that permits no further rewrites. Here, we focus
    on top-down rewrite rules that rewrite a tree to some canonical form,
    such as simplifying algebraic expressions.

    :param rules: a list of rewrite rules
    :param max_rewrites: the maximum number of rewrites to apply. This
                         can be useful in various ways, such as preventing
                            infinite loops, composing it with other rewrite
                            systems (such as a random rewrite system that
                            may look for a goal node in a search space), etc.
    :param randomize: whether to randomly select the order of the rules to apply
    
    :return: a function that takes a node and a context 
    """

    def _rewrite(node, ctx): 

        rewrite_count = 0
        while True:
            new_node = deepcopy(node)
            if randomize:
                random.shuffle(rules)
            for rule in rules:
                if rewrite_count >= max_rewrites:
                    logging.debug(f"Max rewrites reached: {max_rewrites}")
                    return new_node
                new_node = rule(new_node, ctx)
                if new_node != node:
                    logging.debug(f"Rewrite: {rule.__name__}")
                    rewrite_count += 1

            if new_node == node:
                return node
            
            node = new_node

    return _rewrite
    

