class PostorderRewriter:
    """
    Applies a function to the nodes in the tree using some traversal strategy.
    Conceptually, it is a function of type

        PostorderRewriter[fn] : Tree -> Tree

    where Tree is a tree data structure that supports:
    
    - `children()` method that returns a list of child nodes.
    - `add_child(node)` method that adds a child node.

    The function `fn` is of type `Node -> Node`, where Node is
    a node in the tree (often, the node itself models the conept of a tree).
    """

    def __init__(self, fn, max_depth=None):
        """
        `fn` is a function of type `Node -> Node`, where Node
        is a node in the tree. Note that the children of the node are not
        affected by the parent node, because the function is applied in postorder.
        The parent is affected by the children.

        We assume that `fn` is a pure function, i.e., it does not have side effects.
        Also, we assume that `fn` will not modify a parent of the input node,
        otherwise the behavior is undefined (it could even model a different
        traversal strategy like pre-order).

        :param fn: Function to apply to each node. Should accept two arguments: the node and the context.
        :param max_depth: Maximum depth to traverse. If None, traverses the entire tree.
        """
        self.fn = fn
        self.max_depth = max_depth

    def visit(self, node, depth=0):
        """
        Visit a node in the tree and apply the function to it and its children
        recursively, in postorder (bottom-up) strategy.

        :param node: The node to visit.
        :param depth: The depth of the current node in the tree.
        :return: The new node after applying the function recursively, bottom-up.
        """
        if self.max_depth is not None and depth > self.max_depth:
            return node
        
        childs = [self.visit(child, depth + 1) for child in node.children()]
        
        # we need to apply the function after visiting the children, but note
        # that we need up first update the children of the node so that the
        # function can access the updated children.

        # so, first, we need to remove the old children
        for child in node.children():
            node.remove_child(child)
        for child in childs:
            node.add_child(child)
        return self.fn(node)
    
    def __call__(self, tree, ctx=None):
        return self.visit(tree, ctx, 0)