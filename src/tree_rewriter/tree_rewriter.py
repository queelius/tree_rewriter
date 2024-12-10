import copy
from typing import List, Dict, Any

def tree_rewriter(node: Any,
             ctx: Dict,
             rules: List):
    """
    Rewrite a tree node by applying a sequence of rewrite rules until a fixed
    point is reached.

    A rule is a function that takes a node, a context (whatever that is for
    your application), and returns a new node. This is a low-level way of
    rewriting, but it has the advantage of being flexible and works
    with any tree structure that can be traversed with the `children` property
    or attribute.   

    :param node: a node
    :param ctx: a context
    :param rules: a list of rules
    :return: a new tree
    """

    while not stable:
        stable = True
        for rule in rules:
            new_node = copy.deepcopy(node)
            for child in new_node.children():
                rule(child, ctx)
            
            new_node = rule(new_node, ctx)
            # if str(node1) == str(node2):
            if new_node != node:
                stable = False

            node = new_node

    return node

